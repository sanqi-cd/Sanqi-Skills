#!/usr/bin/env python3
"""Render a structured learning plan JSON file as a standalone HTML growth map."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


REQUIRED_TEXT = ("title", "learner", "start_state", "goal_state", "time_budget", "today_win")
REQUIRED_PHASE_TEXT = ("id", "title", "duration", "ability", "deliverable", "pass_criteria")


def validate_plan(plan: dict) -> list[str]:
    errors: list[str] = []
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
        if not isinstance(tasks, list) or not tasks or not all(isinstance(item, str) and item.strip() for item in tasks):
            errors.append(f"phase {index}.tasks must contain non-empty strings")
    for key in ("methodologies", "review_rules"):
        value = plan.get(key)
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{key} must contain non-empty strings")
    return errors


def render(plan: dict) -> str:
    data = json.dumps(plan, ensure_ascii=False).replace("<", "\\u003c")
    title = html.escape(plan["title"])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{--ink:#17211b;--paper:#f7f8f4;--line:#d7ddd7;--green:#26734d;--yellow:#f2c94c;--blue:#2869a8}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 system-ui,-apple-system,"PingFang SC",sans-serif}}
main{{width:min(1040px,calc(100% - 32px));margin:0 auto;padding:48px 0 72px}}
header{{border-bottom:2px solid var(--ink);padding-bottom:28px}} h1{{font-size:clamp(32px,5vw,58px);line-height:1.12;margin:8px 0 18px;letter-spacing:0}}
.eyebrow{{font-weight:700;color:var(--green)}} .states{{display:grid;grid-template-columns:1fr auto 1fr;gap:16px;align-items:center;margin-top:26px}}
.state,.phase{{border:1px solid var(--line);background:#fff;padding:20px;border-radius:6px}} .arrow{{font-size:24px;color:var(--green)}}
.meta{{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0}} .meta span{{border-bottom:2px solid var(--yellow)}}
.progress{{height:10px;background:#e4e8e3;margin:34px 0 10px}} .progress>div{{height:100%;width:0;background:var(--green);transition:width .2s}}
.phase-list{{display:grid;gap:18px;margin-top:30px}} .phase{{display:grid;grid-template-columns:48px 1fr;gap:14px}}
.index{{width:40px;height:40px;display:grid;place-items:center;background:var(--ink);color:#fff;font-weight:800}}
.phase h2{{font-size:22px;margin:0}} .duration{{color:var(--blue);font-weight:700}} ul{{padding-left:20px}}
label{{display:flex;gap:10px;align-items:flex-start;margin:8px 0}} input{{margin-top:6px;width:18px;height:18px;accent-color:var(--green)}}
.evidence{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px;padding-top:14px;border-top:1px solid var(--line)}}
.win{{margin:28px 0;padding:22px;border-left:6px solid var(--yellow);background:#fff}} footer{{margin-top:36px;border-top:2px solid var(--ink);padding-top:20px}}
@media(max-width:680px){{main{{width:min(100% - 22px,1040px);padding-top:24px}}.states{{grid-template-columns:1fr}}.arrow{{transform:rotate(90deg);text-align:center}}.phase{{grid-template-columns:1fr}}.evidence{{grid-template-columns:1fr}}}}
@media print{{body{{background:#fff}}main{{width:100%;padding:0}}input{{display:none}}}}
</style>
</head>
<body><main id="app"></main>
<script id="learning-plan-data" type="application/json">{data}</script>
<script>
const plan=JSON.parse(document.getElementById('learning-plan-data').textContent);const app=document.getElementById('app');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const key='learning-path:'+plan.title;const saved=JSON.parse(localStorage.getItem(key)||'{{}}');
const phaseHtml=plan.phases.map((p,i)=>`<section class="phase"><div class="index">${{i+1}}</div><div><div class="duration">${{esc(p.duration)}}</div><h2>${{esc(p.title)}}</h2><p><strong>解锁能力：</strong>${{esc(p.ability)}}</p>${{p.tasks.map((t,j)=>`<label><input type="checkbox" data-id="${{esc(p.id)}}-${{j}}"> <span>${{esc(t)}}</span></label>`).join('')}}<div class="evidence"><div><strong>本站作品</strong><br>${{esc(p.deliverable)}}</div><div><strong>通关标准</strong><br>${{esc(p.pass_criteria)}}</div></div></div></section>`).join('');
app.innerHTML=`<header><div class="eyebrow">个性化学习成长地图</div><h1>${{esc(plan.title)}}</h1><div class="meta"><span>${{esc(plan.learner)}}</span><span>${{esc(plan.time_budget)}}</span></div><div class="states"><div class="state"><strong>起点</strong><br>${{esc(plan.start_state)}}</div><div class="arrow">→</div><div class="state"><strong>终点</strong><br>${{esc(plan.goal_state)}}</div></div></header><div class="progress"><div id="bar"></div></div><div id="progressText"></div><div class="win"><strong>今天的小胜利</strong><br>${{esc(plan.today_win)}}</div><div class="phase-list">${{phaseHtml}}</div><footer><h2>复盘与升级</h2><ul>${{plan.review_rules.map(x=>`<li>${{esc(x)}}</li>`).join('')}}</ul><p><strong>方法组合：</strong>${{plan.methodologies.map(esc).join(' · ')}}</p></footer>`;
const boxes=[...document.querySelectorAll('input[type=checkbox]')];function update(){{boxes.forEach(b=>b.checked=!!saved[b.dataset.id]);const done=boxes.filter(b=>b.checked).length;document.getElementById('bar').style.width=(boxes.length?done/boxes.length*100:0)+'%';document.getElementById('progressText').textContent=`已完成 ${{done}} / ${{boxes.length}} 项`;localStorage.setItem(key,JSON.stringify(saved));}}
boxes.forEach(b=>{{b.checked=!!saved[b.dataset.id];b.addEventListener('change',()=>{{saved[b.dataset.id]=b.checked;update();}})}});update();
</script></body></html>"""


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
