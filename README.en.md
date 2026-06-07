<div align="center">

**中文** · [English](./README.en.md)

# 🧰 Sanqi Skills
#### A collection of AI skills I use daily, open-sourced here

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-4-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)
![OpenCode](https://img.shields.io/badge/OpenCode-Skill-3B82F6?style=flat-square)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-8B5CF6?style=flat-square)

</div>

These are tools I've tested in my own projects and found genuinely useful before open-sourcing. Nothing fancy, just practical stuff.

- **Skills** — Structured instruction sets that Agents can load directly, following the [Agent Skills](https://agentskills.io) open standard. Works with Claude Code, Codex, OpenCode, OpenClaw.

---

## 📋 Table of Contents

### Skills

| Name | One-liner | Platforms |
|---|---|---|
| 📄 [**paper-explainer**](#-paper-explainer) | When the user uploads a paper PDF or provides an arXiv link and requests interpretation. T... | Claude Code · Codex · OpenCode · OpenClaw |
| 📦 [**skill-builder**](#-skill-builder) | Guide vague Skill ideas into executable task cards and high-quality SKILL.md files | Claude Code · Codex · OpenCode · OpenClaw |
| 📦 [**xhs-image-text-generator**](#-xhs-image-text-generator) | Use when the user wants to turn an HTML page, Markdown article, plain text, interview note... | Claude Code · Codex · OpenCode · OpenClaw |
| 🎬 [**youtube-podcast-to-md**](#-youtube-podcast-to-md) | Extract YouTube podcast videos and organize into Chinese Markdown notes | Claude Code · Codex · OpenCode · OpenClaw |

---

## 📦 Installation

In Claude Code, Codex, OpenClaw or any Agent that supports Skills, just say:

```
Install this skill: https://github.com/sanqi-cd/Sanqi-Skills/tree/main/<skill-name>
```

Replace `<skill-name>` with the one you want, e.g. `youtube-podcast-to-md`. The Agent will clone it to the appropriate directory automatically.

---

## ✨ Skills

<!-- SKILLS_DETAIL_START -->
<table>
<tr><td>

### 📄 paper-explainer

Breaks down papers into Introduction / Method / Experiment / Conclusion sections, explains core ideas with layman analogies, annotates reproducibility details (datasets, hyperparameters, environment),...

→ [SKILL.md](./paper-explainer/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📦 skill-builder

Turns vague Skill ideas into executable task cards through structured interviews, then generates high-quality SKILL.md files.

→ [SKILL.md](./skill-builder/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📦 xhs-image-text-generator

This Skill helps users extract the topic, audience, hook, and visual structure from source material and produce a publish-ready Xiaohongshu/RedNote carousel package. The final output includes titles, ...

→ [SKILL.md](./xhs-image-text-generator/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 🎬 youtube-podcast-to-md

Extract subtitles from YouTube podcast videos and organize them into high-quality Chinese Markdown documents, optimized for English podcasts by default. Two output modes:
- **Summary mode**: Extract core insights, key data, and structured summaries, filtering out small talk and repetition
- **Full mode**: High-fidelity restoration of the entire conversation, preserving dialogue structure and reasoning logic...

**Workflow:**

1. Step 1: Confirm input parameters
2. Step 2: Environment setup
3. Step 3: Fetch subtitles
4. Step 4: Clean and chunk subtitles
5. Step 5: Model content reconstruction (core step)

→ [SKILL.md](./youtube-podcast-to-md/SKILL.md)

</td></tr>
</table>
<!-- SKILLS_DETAIL_END -->

---

## 🌟 About

I'm sanqi. These are skills I use daily. If they help you, give it a ⭐. Questions or suggestions? Feel free to open an Issue or Discussion.

---

<div align="center">

[MIT License](./LICENSE) · Free to use / modify / redistribute
Made by [@sanqi-cd](https://github.com/sanqi-cd)

</div>
