#!/usr/bin/env python3
"""Render a structured learning plan JSON file as a standalone HTML growth map."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


REQUIRED_TEXT = ("title", "learner", "start_state", "goal_state", "time_budget", "today_win")
REQUIRED_LISTS = (
    "methodologies",
    "diagnosis",
    "knowledge_tree",
    "task_tree",
    "final_deliverables",
    "toolbelt",
    "validation_standards",
    "review_rules",
)
REQUIRED_PHASE_TEXT = ("id", "title", "duration", "ability", "deliverable", "pass_criteria")


def validate_plan(plan: dict) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    total_days = plan.get("total_days")
    if not isinstance(total_days, int) or isinstance(total_days, bool) or total_days < 1:
        errors.append("total_days must be a positive integer")
    for key in REQUIRED_TEXT:
        if not isinstance(plan.get(key), str) or not plan[key].strip():
            errors.append(f"{key} must be a non-empty string")

    phases = plan.get("phases")
    if not isinstance(phases, list) or not 4 <= len(phases) <= 6:
        errors.append("phases must contain 4-6 items")
        phases = []
    ids: set[str] = set()
    for index, phase in enumerate(phases, 1):
        if not isinstance(phase, dict):
            errors.append(f"phase {index} must be an object")
            continue
        for key in REQUIRED_PHASE_TEXT:
            if not isinstance(phase.get(key), str) or not phase[key].strip():
                errors.append(f"phase {index}.{key} must be a non-empty string")
        phase_id = phase.get("id")
        if isinstance(phase_id, str):
            if phase_id in ids:
                errors.append(f"phase id {phase_id!r} is duplicated")
            ids.add(phase_id)
        tasks = phase.get("tasks")
        if not isinstance(tasks, list) or not tasks or not all(
            isinstance(item, str) and item.strip() for item in tasks
        ):
            errors.append(f"phase {index}.tasks must contain non-empty strings")

    for key in REQUIRED_LISTS:
        value = plan.get(key)
        if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            errors.append(f"{key} must contain non-empty strings")
    groups = plan.get("action_groups")
    if not isinstance(groups, list) or not groups:
        errors.append("action_groups must contain at least one group")
        groups = []
    expected_start = 1
    for index, group in enumerate(groups, 1):
        if not isinstance(group, dict):
            errors.append(f"action group {index} must be an object")
            continue
        if not isinstance(group.get("label"), str) or not group["label"].strip():
            errors.append(f"action group {index}.label must be a non-empty string")
        start, end = group.get("start_day"), group.get("end_day")
        if not isinstance(start, int) or isinstance(start, bool) or start != expected_start:
            errors.append(f"action group {index}.start_day must be {expected_start}")
        if not isinstance(end, int) or isinstance(end, bool) or not isinstance(start, int) or end < start:
            errors.append(f"action group {index}.end_day must be at least start_day")
        elif isinstance(total_days, int) and end > total_days:
            errors.append(f"action group {index}.end_day exceeds total_days")
        if isinstance(end, int) and not isinstance(end, bool):
            expected_start = end + 1
        tasks = group.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            errors.append(f"action group {index}.tasks must contain tasks")
            continue
        for task_index, task in enumerate(tasks, 1):
            if not isinstance(task, dict):
                errors.append(f"action group {index} task {task_index} must be an object")
                continue
            for key in ("title", "output", "check"):
                if not isinstance(task.get(key), str) or not task[key].strip():
                    errors.append(f"action group {index} task {task_index}.{key} must be a non-empty string")
            minutes = task.get("minutes")
            if not isinstance(minutes, int) or isinstance(minutes, bool) or minutes < 1:
                errors.append(f"action group {index} task {task_index}.minutes must be positive")
    if isinstance(total_days, int) and not isinstance(total_days, bool) and expected_start != total_days + 1:
        errors.append("action_groups must cover every day through total_days")
    review = plan.get("review_questions")
    if not isinstance(review, dict) or any(not isinstance(review.get(key), str) or not review[key].strip() for key in ("daily", "weekly")):
        errors.append("review_questions must include daily and weekly questions")
    return errors


def render(plan: dict) -> str:
    data = json.dumps(plan, ensure_ascii=False).replace("<", "\\u003c")
    title = html.escape(plan["title"])
    template = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--ink:#17211b;--muted:#66706a;--paper:#f5f7f3;--panel:#fff;--line:#d8ded8;--green:#26734d;--yellow:#f2c94c;--blue:#2869a8;--red:#c84a43}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 system-ui,-apple-system,"PingFang SC",sans-serif;letter-spacing:0}
button,input{font:inherit}.shell{width:min(1120px,calc(100% - 32px));margin:0 auto;padding:40px 0 72px}.panel{background:var(--panel);border:1px solid var(--line);border-radius:6px}
.hero{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(300px,.55fr);border-top:8px solid var(--green);overflow:hidden}.hero-main{padding:34px}.eyebrow{margin:0;color:var(--green);font-weight:800}.hero h1{font-size:clamp(34px,5vw,60px);line-height:1.08;margin:10px 0 18px;letter-spacing:0}.meta{display:flex;gap:16px;flex-wrap:wrap;color:var(--muted)}
.states{display:grid;background:#eef3ee}.state{padding:26px;border-left:1px solid var(--line)}.state strong{display:block;color:var(--blue);margin-bottom:6px}.state.goal strong{color:var(--red)}
.section{margin-top:18px;padding:24px}.section h2{font-size:23px;margin:0 0 16px;letter-spacing:0}.progress-row{display:flex;align-items:center;gap:14px;margin-top:18px}.progress{height:10px;flex:1;background:#e4e8e3;overflow:hidden}.progress>div{height:100%;width:0;background:var(--green);transition:width .2s}.progress-copy{min-width:110px;text-align:right;font-weight:800}
.win{margin-top:18px;padding:20px 24px;border-left:6px solid var(--yellow);background:#fff}.win strong{color:#765b00}.stage-tabs,.phase-tabs{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px}.stage-tab,.phase-tab{border:1px solid var(--line);background:#fff;color:var(--ink);padding:10px 13px;cursor:pointer;white-space:nowrap}.stage-tab.active{background:var(--ink);color:#fff;border-color:var(--ink)}.phase-tab.active{background:#eaf2f8;color:#174f7f;border-color:var(--blue)}
.stage-detail{margin-top:14px;display:grid;grid-template-columns:90px minmax(0,1fr);gap:20px;padding:22px;background:#fbfcfa;border:1px solid var(--line)}.stage-index{width:64px;height:64px;display:grid;place-items:center;background:var(--yellow);font-size:24px;font-weight:900}.duration{color:var(--blue);font-weight:800}.stage-detail h3{font-size:26px;line-height:1.2;margin:3px 0 10px}.evidence{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}.evidence>div{padding:14px;border-left:4px solid var(--green);background:#fff}.evidence>div:last-child{border-left-color:var(--red)}
.task-list{display:grid;gap:10px;margin-top:14px}.task{display:grid;grid-template-columns:auto 1fr;gap:11px;align-items:start;padding:13px;border:1px solid var(--line);background:#fff}.task input{width:19px;height:19px;margin-top:4px;accent-color:var(--green)}.task.done .task-title{text-decoration:line-through;color:var(--muted)}.task-meta{display:block;color:var(--muted);font-size:14px}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:18px}.tree-list{display:grid;gap:9px}.tree-item{display:grid;grid-template-columns:30px 1fr;gap:10px;align-items:start}.tree-item b{width:28px;height:28px;display:grid;place-items:center;background:var(--ink);color:#fff;font-size:13px}.deliverables{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.deliverable{padding:16px;border-top:4px solid var(--blue);background:#fff;border-left:1px solid var(--line);border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.deliverable:nth-child(3n+2){border-top-color:var(--green)}.deliverable:nth-child(3n){border-top-color:var(--yellow)}
.method-list{display:flex;flex-wrap:wrap;gap:8px}.method{padding:7px 11px;background:#edf3ef;border:1px solid #c8d8ce}.review-toggle{border:0;background:var(--blue);color:#fff;padding:10px 14px;cursor:pointer}.review{display:none;margin-top:14px}.review.open{display:block}.review li{margin:8px 0}ul{padding-left:20px}
@media(max-width:760px){.shell{width:min(100% - 22px,1120px);padding-top:18px}.hero,.two-col{grid-template-columns:1fr}.states{grid-template-columns:1fr 1fr}.state{border-left:0;border-top:1px solid var(--line)}.stage-detail{grid-template-columns:1fr}.evidence,.deliverables{grid-template-columns:1fr}.hero h1{font-size:36px}}
@media print{body{background:#fff}.shell{width:100%;padding:0}.panel{break-inside:avoid}.stage-tabs,.phase-tabs{overflow:visible}.review{display:block}}
</style>
</head>
<body><main class="shell" id="app"></main>
<script id="learning-plan-data" type="application/json">__DATA__</script>
<script>
const plan=JSON.parse(document.getElementById('learning-plan-data').textContent);const app=document.getElementById('app');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const storageKey='learning-path:v2:'+plan.title;let saved={};try{saved=JSON.parse(localStorage.getItem(storageKey)||'{}')}catch(e){saved={}}let activeStage=0;let activePhase=0;
const numbered=items=>items.map((item,index)=>`<div class="tree-item"><b>${index+1}</b><span>${esc(item)}</span></div>`).join('');
app.innerHTML=`<header class="hero panel"><div class="hero-main"><p class="eyebrow">个性化学习成长地图</p><h1>${esc(plan.title)}</h1><div class="meta"><span>${esc(plan.learner)}</span><span>${esc(plan.time_budget)}</span></div><div class="progress-row"><div class="progress"><div id="globalBar"></div></div><div class="progress-copy" id="globalProgress">0 / 0</div></div></div><div class="states"><div class="state"><strong>起点</strong>${esc(plan.start_state)}</div><div class="state goal"><strong>终点</strong>${esc(plan.goal_state)}</div></div></header><section class="win"><strong>今天的小胜利</strong><br>${esc(plan.today_win)}</section><section class="panel section"><h2>学习诊断</h2><div class="tree-list">${numbered(plan.diagnosis)}</div><p><strong>方法组合：</strong>${plan.methodologies.map(esc).join(' · ')}</p></section><section class="panel section"><h2>成长路线</h2><div class="stage-tabs" id="stageTabs"></div><div id="stageDetail"></div></section><section class="panel section"><h2>全周期行动卡</h2><div class="phase-tabs" id="phaseTabs"></div><div class="progress-row"><div class="progress"><div id="phaseBar"></div></div><div class="progress-copy" id="phaseProgress">0 / 0</div></div><div class="task-list" id="taskList"></div></section><section class="two-col"><div class="panel section"><h2>知识树</h2><div class="tree-list">${numbered(plan.knowledge_tree)}</div></div><div class="panel section"><h2>任务树</h2><div class="tree-list">${numbered(plan.task_tree)}</div></div></section><section class="panel section"><h2>成果展台</h2><div class="deliverables">${plan.final_deliverables.map(x=>`<div class="deliverable">${esc(x)}</div>`).join('')}</div></section><section class="panel section"><h2>学习装备</h2><div class="method-list">${plan.toolbelt.map(x=>`<span class="method">${esc(x)}</span>`).join('')}</div></section><section class="panel section"><h2>通关标准</h2><div class="tree-list">${numbered(plan.validation_standards)}</div></section><section class="panel section"><h2>复盘与升级</h2><button class="review-toggle" id="reviewToggle" type="button">显示复盘问题</button><div class="review" id="review"><p><strong>每日：</strong>${esc(plan.review_questions.daily)}</p><p><strong>每周：</strong>${esc(plan.review_questions.weekly)}</p><ul>${plan.review_rules.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div></section>`;
function renderStage(){const tabs=document.getElementById('stageTabs');tabs.innerHTML=plan.phases.map((p,i)=>`<button class="stage-tab ${i===activeStage?'active':''}" data-stage="${i}" type="button">${i+1}. ${esc(p.title)}</button>`).join('');const p=plan.phases[activeStage];document.getElementById('stageDetail').innerHTML=`<article class="stage-detail"><div class="stage-index">${activeStage+1}</div><div><div class="duration">${esc(p.duration)}</div><h3>${esc(p.title)}</h3><p><strong>解锁能力：</strong>${esc(p.ability)}</p><p><strong>核心任务：</strong>${p.tasks.map(esc).join(' · ')}</p><div class="evidence"><div><strong>本站作品</strong><br>${esc(p.deliverable)}</div><div><strong>通关标准</strong><br>${esc(p.pass_criteria)}</div></div></div></article>`;tabs.querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>{activeStage=Number(button.dataset.stage);renderStage()}))}
function taskId(groupIndex,taskIndex){return `${plan.action_groups[groupIndex].start_day}-${taskIndex}`}
function updateProgress(){const all=[];plan.action_groups.forEach((g,gi)=>g.tasks.forEach((_,ti)=>all.push(taskId(gi,ti))));const done=all.filter(id=>saved[id]).length;document.getElementById('globalBar').style.width=(all.length?done/all.length*100:0)+'%';document.getElementById('globalProgress').textContent=`${done} / ${all.length} 项`;const group=plan.action_groups[activePhase];const groupDone=group.tasks.filter((_,ti)=>saved[taskId(activePhase,ti)]).length;document.getElementById('phaseBar').style.width=(group.tasks.length?groupDone/group.tasks.length*100:0)+'%';document.getElementById('phaseProgress').textContent=`${groupDone} / ${group.tasks.length} 项`;try{localStorage.setItem(storageKey,JSON.stringify(saved))}catch(e){}}
function renderTasks(){const tabs=document.getElementById('phaseTabs');tabs.innerHTML=plan.action_groups.map((g,i)=>`<button class="phase-tab ${i===activePhase?'active':''}" data-phase="${i}" type="button">${esc(g.label)}</button>`).join('');const group=plan.action_groups[activePhase];document.getElementById('taskList').innerHTML=group.tasks.map((task,i)=>{const id=taskId(activePhase,i);return `<label class="task ${saved[id]?'done':''}"><input type="checkbox" data-id="${esc(id)}" ${saved[id]?'checked':''}><span><strong class="task-title">${esc(task.title)}</strong><span class="task-meta">${task.minutes} 分钟 · 产出：${esc(task.output)} · 检查：${esc(task.check)}</span></span></label>`}).join('');tabs.querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>{activePhase=Number(button.dataset.phase);renderTasks()}));document.querySelectorAll('.task input').forEach(box=>box.addEventListener('change',()=>{saved[box.dataset.id]=box.checked;box.closest('.task').classList.toggle('done',box.checked);updateProgress()}));updateProgress()}
document.getElementById('reviewToggle').addEventListener('click',event=>{const review=document.getElementById('review');review.classList.toggle('open');event.currentTarget.textContent=review.classList.contains('open')?'收起复盘问题':'显示复盘问题'});renderStage();renderTasks();
</script></body></html>"""
    return template.replace("__TITLE__", title).replace("__DATA__", data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Learning plan JSON file")
    parser.add_argument("output", type=Path, help="Destination HTML file")
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"cannot read plan JSON: {exc}")
    if not isinstance(plan, dict):
        parser.error("plan JSON root must be an object")
    errors = validate_plan(plan)
    if errors:
        parser.error("invalid plan: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(plan), encoding="utf-8")
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
