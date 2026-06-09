# HTML 学习成长地图模板

本文件用于生成完整学习路径的默认展示形态。目标不是把 Markdown 塞进网页，而是把学习计划设计成一个让用户愿意进入的「成长地图」。

## 目录

- 使用时机
- 体验原则
- 页面结构
- 交互要求
- 数据生成要求
- HTML 骨架
- 输出后的说明

## 使用时机

- 用户背景已经足够生成完整学习路径。
- 用户希望学习计划更直观、更动态、更有进入感。
- 默认完整学习路径输出应优先使用本模板。

如果当前环境可以写文件，创建一个独立 `.html` 文件并返回路径。优先写入当前工作区的 `learning-path-outputs/` 目录，文件名使用学习主题 slug，例如 `vibe-coding-growth-map.html`。不要把用户生成的 HTML 运行产物写进 Skill 包目录。如果不能写文件，输出完整 HTML 代码块。

## 体验原则

- 先让用户看到未来的自己，再展示任务。
- 用「站点」「解锁能力」「作品」「通关标准」替代生硬的阶段清单。
- 每屏都要能回答一个问题：我现在在哪、下一步做什么、学完得到什么。
- 视觉要清爽、有层次、有行动感，不要过度热血、不要空泛鼓励。
- 不使用外部 CDN、图片、字体或框架；HTML、CSS、JavaScript 全部内联。
- 页面必须响应式，手机和桌面都可读。

## 页面结构

生成的 HTML 必须包含以下模块：

1. **旅程封面**
   - 学习旅程标题，例如「30 天从 AI 小白到拥有个人 AI 工作流」。
   - 用户起点：当前基础、主要困难。
   - 目标终点：学习完成后能做什么。
   - 关键承诺：本路径会产出的作品或能力证明。

2. **诊断面板**
   - 学习任务类型。
   - 领域特征。
   - 当前阶段。
   - 推荐方法论组合。
   - 暂时不优先的方法和原因。

3. **成长路线**
   - 4-6 个站点。
   - 每个站点包含：站点名、解锁能力、核心任务、本站作品、通关标准。
   - 站点可点击，点击后显示对应详情。

4. **全周期行动卡**
   - 必须覆盖用户给出的完整周期，例如 7 天给 7 天任务，30 天给 4 周或 30 天任务，90 天给 12 周任务。
   - 可以默认显示当前周，但必须提供周/阶段切换。
   - 每个任务包含预计投入时间、产出物和检查方式。
   - 勾选框用于记录完成状态，每个周/阶段独立计算进度。
   - 切换周/阶段后，已经勾选的任务状态不能丢失。

5. **知识树与任务树**
   - 用两列展示。
   - 知识树回答「我要理解什么」。
   - 任务树回答「我要完成什么」。

6. **成果展台**
   - 展示用户最终会获得的产出物。
   - 例如：知识地图、提示词库、案例库、作品集、项目 Demo、复盘报告。

7. **通关标准**
   - 最低合格标准。
   - 良好掌握标准。
   - 高阶迁移标准。

8. **复盘与升级**
   - 每日复盘问题。
   - 每周复盘问题。
   - 太难时如何降级。
   - 太简单时如何升级。
   - 坚持不下去时如何缩小任务。
   - 想加速时如何增加挑战。

9. **今天的小胜利**
   - 一个 15-30 分钟可以完成的任务。
   - 必须具体到行动和产出。
   - 让用户完成后能立刻拥有第一个学习证据。

## 交互要求

最少实现以下交互：

- 点击阶段站点切换详情。
- 勾选行动卡任务后更新当前周/阶段进度条。
- 如果学习周期超过 7 天，提供周/阶段切换按钮，不能只展示第 1 周任务。
- 勾选状态应尽量用 `localStorage` 持久化；如果环境不支持，再退化为当前页面会话状态。
- 点击「显示复盘问题」展开复盘区。
- 页面顶部或侧边显示当前学习进度。

不需要复杂框架，不要引入构建工具。使用少量原生 JavaScript 即可。

## 数据生成要求

先根据用户真实背景生成以下结构，再填入 HTML：

```text
learningJourney:
  title
  startState
  endState
  promise
  diagnosis
  methods
  stages[]
    name
    unlockAbility
    coreTasks[]
    deliverables[]
    passCriteria[]
    risk
  actionGroups[]
    title
    goal
    tasks[]
      day
      task
      method
      time
      output
      check
  knowledgeTree[]
  taskTree[]
  finalDeliverables[]
  toolbelt[]
  validationStandards[]
  reviewQuestions
  firstSmallWin
```

## HTML 骨架

生成时可以使用下列骨架，并替换所有中文占位内容。不要留下占位符。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>学习成长地图</title>
  <style>
    :root {
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #667085;
      --line: #d9e0ea;
      --blue: #2563eb;
      --green: #16a34a;
      --amber: #d97706;
      --red: #dc2626;
      --shadow: 0 12px 32px rgba(23, 32, 51, 0.10);
      --radius: 8px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }
    .shell { max-width: 1180px; margin: 0 auto; padding: 28px 18px 48px; }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.6fr);
      gap: 18px;
      align-items: stretch;
      margin-bottom: 18px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    .hero-main { padding: 28px; }
    .eyebrow { color: var(--blue); font-size: 14px; font-weight: 700; margin: 0 0 8px; }
    h1 { margin: 0 0 12px; font-size: clamp(28px, 4vw, 48px); line-height: 1.12; letter-spacing: 0; }
    h2 { margin: 0 0 14px; font-size: 22px; letter-spacing: 0; }
    h3 { margin: 0 0 10px; font-size: 17px; letter-spacing: 0; }
    p { margin: 0 0 10px; }
    .muted { color: var(--muted); }
    .journey-points { display: grid; gap: 10px; padding: 18px; }
    .point { border-left: 4px solid var(--blue); padding: 10px 12px; background: #f8fbff; border-radius: 6px; }
    .grid { display: grid; grid-template-columns: 0.9fr 1.1fr; gap: 18px; }
    .section { margin-top: 18px; padding: 22px; }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .chip { border: 1px solid var(--line); background: #f8fafc; border-radius: 999px; padding: 6px 10px; font-size: 14px; }
    .roadmap { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 16px; }
    .stage-list { display: grid; gap: 10px; }
    .stage-button {
      width: 100%;
      border: 1px solid var(--line);
      background: #fff;
      border-radius: var(--radius);
      padding: 12px;
      text-align: left;
      cursor: pointer;
      color: var(--ink);
    }
    .stage-button.active { border-color: var(--blue); box-shadow: inset 0 0 0 1px var(--blue); }
    .stage-detail { padding: 18px; min-height: 280px; }
    .detail-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px; }
    .mini { border: 1px solid var(--line); border-radius: var(--radius); padding: 12px; background: #fbfcff; }
    ul { margin: 8px 0 0 20px; padding: 0; }
    .progress-wrap { display: flex; align-items: center; gap: 12px; margin: 12px 0 16px; }
    .progress { flex: 1; height: 10px; background: #e8edf5; border-radius: 999px; overflow: hidden; }
    .bar { height: 100%; width: 0%; background: var(--green); transition: width 180ms ease; }
    .week-tabs { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 14px; }
    .week-tab {
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 999px;
      padding: 8px 12px;
      cursor: pointer;
      color: var(--ink);
      font-weight: 650;
    }
    .week-tab.active { border-color: var(--blue); background: #eff6ff; color: #1d4ed8; }
    .tasks { display: grid; gap: 10px; }
    .task {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 10px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 12px;
      background: #fff;
    }
    .trees { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .deliverables { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
    .deliverable { border: 1px solid var(--line); border-radius: var(--radius); padding: 14px; background: #fff; }
    .review-toggle {
      border: 0;
      background: var(--blue);
      color: #fff;
      border-radius: 6px;
      padding: 10px 14px;
      cursor: pointer;
    }
    .review { display: none; margin-top: 14px; }
    .review.open { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
    .small-win { border-left: 5px solid var(--green); background: #f0fdf4; }
    @media (max-width: 820px) {
      .hero, .grid, .roadmap, .trees, .deliverables, .review.open { grid-template-columns: 1fr; }
      .detail-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="panel hero-main">
        <p class="eyebrow">你的学习成长地图</p>
        <h1 id="journeyTitle">替换为学习旅程标题</h1>
        <p class="muted" id="journeyPromise">替换为关键承诺。</p>
      </div>
      <aside class="panel journey-points">
        <div class="point"><strong>起点</strong><p id="startState">替换为起点。</p></div>
        <div class="point"><strong>终点</strong><p id="endState">替换为终点。</p></div>
      </aside>
    </section>

    <section class="panel section">
      <h2>诊断结果</h2>
      <div class="chips" id="diagnosisChips"></div>
    </section>

    <section class="panel section">
      <h2>成长路线</h2>
      <div class="roadmap">
        <div class="stage-list" id="stageList"></div>
        <article class="stage-detail panel" id="stageDetail"></article>
      </div>
    </section>

    <section class="panel section">
      <h2>全周期行动卡</h2>
      <p class="muted" id="actionGroupGoal"></p>
      <div class="week-tabs" id="actionGroupTabs"></div>
      <div class="progress-wrap">
        <div class="progress"><div class="bar" id="progressBar"></div></div>
        <strong id="progressText">0%</strong>
      </div>
      <div class="tasks" id="weeklyTasks"></div>
    </section>

    <section class="grid">
      <div class="panel section">
        <h2>知识树</h2>
        <div id="knowledgeTree"></div>
      </div>
      <div class="panel section">
        <h2>任务树</h2>
        <div id="taskTree"></div>
      </div>
    </section>

    <section class="panel section">
      <h2>成果展台</h2>
      <div class="deliverables" id="deliverables"></div>
    </section>

    <section class="panel section">
      <h2>学习装备</h2>
      <div class="deliverables" id="toolbelt"></div>
    </section>

    <section class="panel section">
      <h2>通关标准</h2>
      <div class="deliverables" id="validationStandards"></div>
    </section>

    <section class="panel section">
      <h2>复盘与升级</h2>
      <button class="review-toggle" id="reviewToggle">显示复盘问题</button>
      <div class="review" id="reviewPanel"></div>
    </section>

    <section class="panel section small-win">
      <h2>今天的小胜利</h2>
      <div id="firstSmallWin">替换为 15-30 分钟可完成的启动任务。</div>
    </section>
  </main>

  <script>
    const data = {
      title: "替换为学习旅程标题",
      promise: "替换为关键承诺",
      startState: "替换为起点",
      endState: "替换为终点",
      diagnosis: ["任务类型：替换", "领域特征：替换", "当前阶段：替换", "方法组合：替换"],
      stages: [
        {
          name: "第 1 站：替换为站点名称",
          unlockAbility: "替换为解锁能力",
          coreTasks: ["替换为任务 1", "替换为任务 2"],
          deliverables: ["替换为本站作品"],
          passCriteria: ["替换为通关标准"],
          risk: "替换为常见风险"
        }
      ],
      actionGroups: [
        {
          title: "第 1 周",
          goal: "替换为本周或本阶段目标",
          tasks: [
            { day: "Day 1", task: "替换为任务", method: "替换为方法", time: "30 分钟", output: "替换为产出", check: "替换为检查方式" }
          ]
        }
      ],
      knowledgeTree: ["替换为知识模块"],
      taskTree: ["替换为任务模块"],
      finalDeliverables: ["替换为最终产出物"],
      toolbelt: ["替换为推荐方法、工具或资料类型"],
      validationStandards: ["替换为最低合格标准", "替换为良好掌握标准", "替换为高阶迁移标准"],
      reviewQuestions: {
        daily: ["今天产出了什么？", "哪里卡住了？"],
        weekly: ["本周完成了哪些作品？", "下周要调整什么？"],
        adjustments: ["太难时：缩小任务。", "太简单时：增加真实项目。"]
      },
      firstSmallWin: "替换为今天的小胜利"
    };

    function list(items) {
      return `<ul>${items.map(item => `<li>${item}</li>`).join("")}</ul>`;
    }

    function renderStage(index) {
      const stage = data.stages[index];
      document.querySelectorAll(".stage-button").forEach((button, i) => {
        button.classList.toggle("active", i === index);
      });
      document.getElementById("stageDetail").innerHTML = `
        <h3>${stage.name}</h3>
        <p><strong>解锁能力：</strong>${stage.unlockAbility}</p>
        <div class="detail-grid">
          <div class="mini"><strong>核心任务</strong>${list(stage.coreTasks)}</div>
          <div class="mini"><strong>本站作品</strong>${list(stage.deliverables)}</div>
          <div class="mini"><strong>通关标准</strong>${list(stage.passCriteria)}</div>
        </div>
        <p class="muted" style="margin-top:12px;"><strong>常见风险：</strong>${stage.risk}</p>
      `;
    }

    const storageKey = `learning-growth-map-progress:${data.title}`;
    let completionState = {};
    try {
      completionState = JSON.parse(localStorage.getItem(storageKey) || "{}");
    } catch (error) {
      completionState = {};
    }

    function updateProgress() {
      const checks = [...document.querySelectorAll(".task-check")];
      checks.forEach(item => {
        completionState[`${item.dataset.group}-${item.dataset.task}`] = item.checked;
      });
      try {
        localStorage.setItem(storageKey, JSON.stringify(completionState));
      } catch (error) {}
      const done = checks.filter(item => item.checked).length;
      const percent = checks.length ? Math.round(done / checks.length * 100) : 0;
      document.getElementById("progressBar").style.width = `${percent}%`;
      document.getElementById("progressText").textContent = `${percent}%`;
    }

    function renderActionGroup(index) {
      const group = data.actionGroups[index];
      document.querySelectorAll(".week-tab").forEach((button, i) => {
        button.classList.toggle("active", i === index);
      });
      document.getElementById("actionGroupGoal").textContent = group.goal;
      document.getElementById("weeklyTasks").innerHTML = group.tasks.map((item, taskIndex) => `
        <label class="task">
          <input class="task-check" type="checkbox" data-group="${index}" data-task="${taskIndex}" ${completionState[`${index}-${taskIndex}`] ? "checked" : ""} onchange="updateProgress()">
          <span>
            <strong>${item.day}：${item.task}</strong><br>
            <span class="muted">方法：${item.method} ｜ 时间：${item.time} ｜ 产出：${item.output} ｜ 检查：${item.check}</span>
          </span>
        </label>
      `).join("");
      updateProgress();
    }

    function init() {
      document.title = data.title;
      document.getElementById("journeyTitle").textContent = data.title;
      document.getElementById("journeyPromise").textContent = data.promise;
      document.getElementById("startState").textContent = data.startState;
      document.getElementById("endState").textContent = data.endState;
      document.getElementById("diagnosisChips").innerHTML = data.diagnosis.map(item => `<span class="chip">${item}</span>`).join("");
      document.getElementById("stageList").innerHTML = data.stages.map((stage, index) => `
        <button class="stage-button" type="button" onclick="renderStage(${index})">
          <strong>${stage.name}</strong><br><span class="muted">${stage.unlockAbility}</span>
        </button>
      `).join("");
      document.getElementById("actionGroupTabs").innerHTML = data.actionGroups.map((group, index) => `
        <button class="week-tab" type="button" onclick="renderActionGroup(${index})">${group.title}</button>
      `).join("");
      document.getElementById("knowledgeTree").innerHTML = list(data.knowledgeTree);
      document.getElementById("taskTree").innerHTML = list(data.taskTree);
      document.getElementById("deliverables").innerHTML = data.finalDeliverables.map(item => `<div class="deliverable">${item}</div>`).join("");
      document.getElementById("toolbelt").innerHTML = data.toolbelt.map(item => `<div class="deliverable">${item}</div>`).join("");
      document.getElementById("validationStandards").innerHTML = data.validationStandards.map(item => `<div class="deliverable">${item}</div>`).join("");
      document.getElementById("reviewPanel").innerHTML = `
        <div class="mini"><strong>每日复盘</strong>${list(data.reviewQuestions.daily)}</div>
        <div class="mini"><strong>每周复盘</strong>${list(data.reviewQuestions.weekly)}</div>
        <div class="mini"><strong>调整规则</strong>${list(data.reviewQuestions.adjustments)}</div>
      `;
      document.getElementById("firstSmallWin").textContent = data.firstSmallWin;
      document.getElementById("reviewToggle").addEventListener("click", () => {
        document.getElementById("reviewPanel").classList.toggle("open");
      });
      renderStage(0);
      renderActionGroup(0);
    }

    init();
  </script>
</body>
</html>
```

## 输出后的说明

生成 HTML 后，只用简短文字告诉用户：

- 文件已生成在哪里，或 HTML 代码如下。
- 这个页面可以点击阶段、勾选任务、查看进度和展开复盘问题。
- 如果用户补充学习反馈，可以继续基于该成长地图调整。
