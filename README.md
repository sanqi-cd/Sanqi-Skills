<div align="center">

**中文** · [English](./README.en.md)

# 🧰 Sanqi Skills
#### 我自己日常使用的一些 AI 技能，开源在这里

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-5-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)
![OpenCode](https://img.shields.io/badge/OpenCode-Skill-3B82F6?style=flat-square)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-8B5CF6?style=flat-square)

</div>

都是自己在项目里跑通了一段时间、确实省事的东西，才整理出来开源。没什么花活，就是实用的工具。

- **Skills** — Agent 能直接加载的结构化指令集，遵循 [Agent Skills](https://agentskills.io) 开放标准。Claude Code、Codex、OpenCode、OpenClaw 都能装

---

## 📋 目录

### Skills

| 名字 | 一句话 | 平台 |
|---|---|---|
| 🧭 [**learning-path-designer**](#-learning-path-designer) | 当用户想学习某个领域、技能、工具、课程、考试、证书、职业能力或知识体系，并需要个性化学习路径、学习计... | Claude Code · Codex · OpenCode · OpenClaw |
| 📄 [**paper-explainer**](#-paper-explainer) | 当用户上传论文 PDF 或提供 arXiv 链接并请求解读时使用。 触发："帮我解读这篇论文""解读... | Claude Code · Codex · OpenCode · OpenClaw |
| 📦 [**skill-builder**](#-skill-builder) | 当用户想创建一个新的 Skill 但需求模糊、不完整或过于宽泛时使用。 典型触发："帮我写一个写公众... | Claude Code · Codex · OpenCode · OpenClaw |
| 📦 [**xhs-image-text-generator**](#-xhs-image-text-generator) | 当用户想把 HTML 网页、Markdown 文章、纯文本、访谈记录、产品资料或一个主题改造成可直接... | Claude Code · Codex · OpenCode · OpenClaw |
| 📦 [**youtube-podcast-to-md**](#-youtube-podcast-to-md) | 将 YouTube 播客视频字幕提取并整理为中文 Markdown 笔记，默认针对英文播客优化，支持... | Claude Code · Codex · OpenCode · OpenClaw |

---

## 📦 安装方式

在 Claude Code、Codex、OpenClaw 等支持 Skill 的 Agent 里，直接说：

```
帮我安装这个 skill：https://github.com/sanqi-cd/Sanqi-Skills/tree/main/<skill-name>
```

把 `<skill-name>` 换成你想装的那个，比如 `youtube-podcast-to-md`。Agent 会自己 clone 到对应目录，不用你操心路径。

---

## ✨ Skills

<!-- SKILLS_DETAIL_START -->
<table>
<tr><td>

### 🧭 learning-path-designer

这个 Skill 先诊断用户的学习目标、基础、时间、职业场景和约束，再选择最匹配的学习方法论组合，生成可执行、可验证、可复盘的个性化学习路径。 完整输出优先生成一个单文件 HTML 学习成长地图，包含起点终点、阶段站点、知识树、任务树、行动卡、产出物、通关标准和复盘机制。

→ [SKILL.md](./learning-path-designer/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📄 paper-explainer

按「引言/方法/实验/结论」拆解论文，用通俗类比解读核心思想，标注可复现细节 （数据集、超参、环境），输出结构化 Markdown 笔记。

→ [SKILL.md](./paper-explainer/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📦 skill-builder

把模糊的 Skill 想法，通过结构化访谈收敛为可执行任务卡，再生成高质量 SKILL.md。

→ [SKILL.md](./skill-builder/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📦 xhs-image-text-generator

这个 Skill 帮用户从素材中提炼选题、人群、卖点和视觉结构，生成一套最终可交付的小红书图文发布包。 核心产出包括标题、封面方案、分页脚本、可复制正文、标签、置顶评论/回复、生图提示词、图片页和发布前质量检查。 执行过程中会在必要时询问缺失上下文；需要生图时默认直接调用可用生图模型。

→ [SKILL.md](./xhs-image-text-generator/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📦 youtube-podcast-to-md

将 YouTube 播客视频的字幕提取，整理为高质量中文 Markdown 文档，默认针对英文播客优化；其他语言也可尽力处理。两种输出模式：

- **精简版（summary）**：提取核心观点、关键数据、结构化摘要，过滤闲聊和重复表达
- **完整版（full）**：高保真还原整个对话，保留对话结构、论述逻辑和信息完整性，经轻度书面化处理后呈现为自然流畅的中文对话

→ [SKILL.md](./youtube-podcast-to-md/SKILL.md)

</td></tr>
</table>
<!-- SKILLS_DETAIL_END -->

---

## 🌟 关于

我是 sanqi，这些 skill 都是自己日常在用的，开源出来如果对你有帮助，给个 ⭐ 就行。有问题或建议，欢迎在 Issues / Discussions 里交流。

---

<div align="center">

[MIT License](./LICENSE) · 自由使用 / 修改 / 再分发
Made by [@sanqi-cd](https://github.com/sanqi-cd)

</div>
