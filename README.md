<div align="center">

**中文** · [English](./README.en.md)

# 🧰 Sanqi Skills
#### 我自己日常使用的一些 AI 技能，开源在这里

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-2-10B981?style=for-the-badge)](#-skills)
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
| 📦 [**skill-builder**](#-skill-builder) | > | Claude Code · Codex · OpenCode · OpenClaw |
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

### 📦 skill-builder

→ [SKILL.md](./skill-builder/SKILL.md)

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
