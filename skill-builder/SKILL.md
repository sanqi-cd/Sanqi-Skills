---
name: skill-builder
description: >
  通过渐进式需求澄清、工作流设计、资源拆分、实现和评测，创建或优化高质量 Agent Skill。适用于“创建一个 skill”“把工作流封装成 skill”“优化 SKILL.md”“补充 scripts、references、assets 或 evals”等请求。Use when a user wants a standards-compliant, maintainable, testable Agent Skill package rather than prompt text alone.
license: MIT
compatibility: Requires local filesystem access and Python 3 for repository validation; optional external tools depend on the skill being built.
metadata:
  author: "sanqi-cd"
  version: "1.0.0"
  emoji: "🧰"
  description_zh: "把模糊想法打磨成符合规范、可执行、可维护、可评测的 Agent Skill。"
  description_en: "Turn a rough idea into a standards-compliant, executable, maintainable, and evaluable Agent Skill."
  overview_zh: "从需求到实现与评测，完整构建高质量 Agent Skill。"
  overview_en: "Build high-quality Agent Skills from requirements through implementation and evaluation."
  platforms: "Claude Code · Codex · OpenCode · OpenClaw"
---

# Agent Skill 构建器

## 目标

把一个想法或已有 Skill 直接推进到结构合规、指令清晰、资源克制、脚本可靠、评测可复现的完整能力包。除非关键信息确实无法推断，不要停在建议或模板阶段。

## 核心原则

- 先读现状：修改已有 Skill 时，先完整读取 `SKILL.md`、已引用资源、脚本、测试和仓库约定。
- 只问阻塞问题：能从上下文合理推断的内容直接处理；必须提问时每轮不超过 3 个。
- 渐进披露：主文件保留触发、决策、流程和质量门槛，长知识放 references，确定性操作放 scripts。
- 验证比例随风险增长：至少覆盖正常输入、缺失输入和边界输入；共享脚本需要单元测试。
- 描述决定发现：`description` 同时写清任务、典型触发、边界和交付结果，不塞入完整工作流。
- 自动推进：用户已经授权实施时，各阶段通过后直接进入下一阶段，不重复索要确认。

## 工作流程

### 1. 建立任务契约

从用户输入和现有文件中提取：

- 用户要反复完成的具体任务。
- 典型触发话术与相邻但不应触发的请求。
- 必需输入、可选输入和合理默认值。
- 最终交付物、保存位置和完成信号。
- 依赖的工具、网络、凭据、运行时或应用。
- 至少 3 条可判定的质量标准和主要失败模式。

只有触发边界、交付格式或高风险行为仍不明确时才提问。用户给出完整规格时直接进入设计；用户只给一句模糊想法时，优先询问“最终交付什么”“谁会在什么场景触发”“什么算成功”。

产出一份内部任务契约。只有存在会改变实现方向的互斥选择时才展示给用户确认，不把确认仪式当成固定门槛。

### 2. 设计最小能力包

默认结构：

```text
skill-name/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/       # 仅在确定性操作能提高可靠性时添加
├── references/    # 仅放按需读取的领域知识或长规范
├── assets/        # 仅放最终输出会直接使用的模板或素材
└── evals/
    ├── evals.json
    └── trigger-evals.json
```

不要为了目录完整而创建空目录。脚本、引用和资产必须在主文件中说明何时使用；每个引用从 `SKILL.md` 直接链接，避免多层引用链。

选择适合的工作流模式时读取 `references/design-patterns.md`。

### 3. 编写标准元数据

顶层只使用 Agent Skills 标准字段：

```yaml
---
name: skill-name
description: >
  [做什么；用户何时会需要；典型话术；相邻边界；最终交付什么。]
license: MIT
compatibility: [运行时、工具、网络或应用要求。]
metadata:
  author: "author-name"
  version: "1.0.0"
---
```

要求：

- `name` 与目录名完全一致，只含小写字母、数字和单连字符，长度不超过 64。
- `description` 非空且不超过 1024 字符，使用具体名词和用户话术，不依赖只有作者懂的简称。
- 自定义展示信息放进 `metadata`，所有值使用字符串。
- 仅在 Skill 确实需要时声明 `allowed-tools`；不要用它掩盖未说明的依赖。

为支持相应客户端的仓库补充 `agents/openai.yaml`。所有字符串加引号，`default_prompt` 必须明确提到 `$skill-name`；只有用户或项目规范明确要求时才加入品牌色等可选字段。

### 4. 编写可执行指令

正文使用祈使语气，包含：

1. 一句话目标。
2. 开始条件和输入缺失策略。
3. 有顺序、分支和产出物的工作流。
4. 错误、降级、重试和停止条件。
5. 可用“通过/不通过”判断的质量标准。
6. 最终交付内容、文件路径和已知局限。

避免重复常识、空泛角色扮演和无法验证的“高质量”“深入分析”。正文接近 500 行时必须拆分；引用文件只保留完成任务所需的信息。

### 5. 实现确定性资源

以下内容优先写成脚本：解析、转换、命名、批处理、结构验证、统计和可重复渲染。脚本必须：

- 使用明确参数和非零失败码。
- 不依赖作者机器上的固定绝对路径。
- 对覆盖文件、网络失败、无效输入和缺失依赖给出可执行错误信息。
- 在至少一个正常案例和一个失败案例上实际运行。

领域知识、API 规范、长模板和评分量表放 references。输出模板或二进制素材放 assets。删除未被工作流使用的资源。

### 6. 建立评测

每个 Skill 至少提供：

- 触发评测：不少于 6 个正例和 6 个难负例，覆盖中英文、口语化请求和相邻能力混淆。
- 输出评测：不少于 3 个案例，包含标准场景、缺口场景和失败/边界场景。
- 每个输出案例包含可观察 assertions，不以“看起来不错”作为标准。

条件允许时，对代表性案例做启用 Skill 与不启用 Skill 的对照运行，记录成功率、遗漏和副作用。没有模型或凭据时仍要校验评测 JSON 的结构，并明确说明尚未运行模型评测。

### 7. 验证并回修

按仓库已有工具优先执行：

1. 官方或仓库级 Skill 结构校验。
2. 所有脚本的语法检查和单元测试。
3. 所有本地引用路径存在性检查。
4. 评测数据 schema 检查。
5. README、目录或清单同步检查。
6. Git diff 审查，确认没有缓存、密钥、用户产物和无关改动。

任一确定性门禁失败时直接回修并重跑。外部服务、凭据或视觉人工判断无法自动验证时，列为残余风险，不伪造通过结果。

## 质量标准

- [ ] 触发描述能区分至少一个相邻但不应触发的请求。
- [ ] 顶层元数据符合开放标准，名称与目录一致。
- [ ] 主流程、降级路径、失败条件和最终交付都明确。
- [ ] 所有引用存在，脚本可独立执行且有失败码。
- [ ] 至少 12 个触发案例和 3 个输出案例通过结构校验。
- [ ] 确定性测试与仓库发布门禁全部通过。
- [ ] 最终报告区分“已验证”“需外部环境验证”和“已知局限”。

## 最终反馈

向用户报告 Skill 名称、实际改动、关键设计决策、测试命令与结果、未运行的模型/外部集成评测，以及生成文件的完整路径。不要重复整份任务契约，也不要在任务已经完成后强制追加确认步骤。
