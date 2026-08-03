<div align="center">

**中文** · [English](./README.en.md)

# 🧰 Sanqi Skills
#### 我自己日常使用的一些 AI 技能，开源在这里

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-5-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)
[![Validate skills](https://github.com/sanqi-cd/Sanqi-Skills/actions/workflows/validate.yml/badge.svg)](https://github.com/sanqi-cd/Sanqi-Skills/actions/workflows/validate.yml)

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
| 🧭 [**learning-path-designer**](#-learning-path-designer) | 根据目标、基础、约束和应用场景设计个性化学习路径，并输出可交互的 HTML 成长地图。 | Claude Code · Codex · OpenCode · OpenClaw |
| 📄 [**paper-explainer**](#-paper-explainer) | 准确、通俗地解释论文的方法、公式、实验、创新与局限，并明确证据边界。 | Claude Code · Codex · OpenCode · OpenClaw |
| 🧰 [**skill-builder**](#-skill-builder) | 把模糊想法打磨成符合规范、可执行、可维护、可评测的 Agent Skill。 | Claude Code · Codex · OpenCode · OpenClaw |
| 📦 [**xhs-image-text-generator**](#-xhs-image-text-generator) | 将主题或文章转化为内容清晰、视觉统一、可直接发布的小红书图文轮播。 | Claude Code · Codex · OpenCode · OpenClaw |
| 🎙️ [**youtube-podcast-to-md**](#-youtube-podcast-to-md) | 提取 YouTube 长视频字幕并生成带来源溯源的中文 Markdown 摘要或高保真对话稿。 | Claude Code · Codex · OpenCode · OpenClaw |

---

## 📦 安装方式

在 Claude Code、Codex、OpenClaw 等支持 Skill 的 Agent 里，直接说：

```
帮我安装这个 skill：https://github.com/sanqi-cd/Sanqi-Skills/tree/main/<skill-name>
```

把 `<skill-name>` 换成你想装的那个，比如 `youtube-podcast-to-md`。Agent 会自己 clone 到对应目录，不用你操心路径。

默认链接跟随 `main` 获取最新版本；需要固定行为时，可将 URL 中的 `main` 替换为已发布版本，例如 [`v1.0.0`](https://github.com/sanqi-cd/Sanqi-Skills/releases/tag/v1.0.0)。

---

## ✅ 质量保证

每个 Skill 都包含统一的标准元数据、客户端入口、触发评测和输出评测。仓库会在每次 push 和 Pull Request 时自动检查：

- `SKILL.md` 元数据、目录命名和本地引用
- `agents/openai.yaml` 客户端入口
- Python 脚本语法与单元测试
- 评测数据结构、README 同步状态和仓库卫生

本地完整验证：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_repository.py
```

质量门槛与贡献规范见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

---

## ✨ Skills

<!-- SKILLS_DETAIL_START -->
<table>
<tr><td>

### 🧭 learning-path-designer

将模糊的学习目标转化为可执行、可验证、可复盘的成长地图。

→ [SKILL.md](./learning-path-designer/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📄 paper-explainer

把陌生论文讲成有主线、有证据边界、能真正学会的研究笔记。

→ [SKILL.md](./paper-explainer/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 🧰 skill-builder

从需求到实现与评测，完整构建高质量 Agent Skill。

→ [SKILL.md](./skill-builder/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📦 xhs-image-text-generator

覆盖内容提炼、分页编排、视觉设计、批量生图与交付校验。

→ [SKILL.md](./xhs-image-text-generator/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 🎙️ youtube-podcast-to-md

从字幕获取、清洗、翻译到结构化输出，提供可降级、可验证的完整流程。

→ [SKILL.md](./youtube-podcast-to-md/SKILL.md)

</td></tr>
</table>
<!-- SKILLS_DETAIL_END -->

---

## 🌟 关于

我是 sanqi，这些 skill 都是自己日常在用的，开源出来如果对你有帮助，给个 ⭐ 就行。有问题或建议，欢迎在 Issues 里交流。

---

<div align="center">

[MIT License](./LICENSE) · 自由使用 / 修改 / 再分发
Made by [@sanqi-cd](https://github.com/sanqi-cd)

</div>
