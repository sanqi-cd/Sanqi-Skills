<div align="center">

[中文](./README.md) · **English**

# 🧰 Sanqi Skills
#### A collection of AI skills I use daily, open-sourced here

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-5-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)
[![Validate skills](https://github.com/sanqi-cd/Sanqi-Skills/actions/workflows/validate.yml/badge.svg)](https://github.com/sanqi-cd/Sanqi-Skills/actions/workflows/validate.yml)

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
| 🧭 [**learning-path-designer**](#-learning-path-designer) | Design a personalized path from beginner to practical mastery and deliver it as an interac... | Claude Code · Codex · OpenCode · OpenClaw |
| 📄 [**paper-explainer**](#-paper-explainer) | Explain papers accurately and accessibly while separating source claims, evidence, and int... | Claude Code · Codex · OpenCode · OpenClaw |
| 🧰 [**skill-builder**](#-skill-builder) | Turn a rough idea into a standards-compliant, executable, maintainable, and evaluable Agen... | Claude Code · Codex · OpenCode · OpenClaw |
| 📦 [**xhs-image-text-generator**](#-xhs-image-text-generator) | Turn source content into a coherent, publication-ready Xiaohongshu image carousel. | Claude Code · Codex · OpenCode · OpenClaw |
| 🎙️ [**youtube-podcast-to-md**](#-youtube-podcast-to-md) | Convert YouTube transcripts into source-grounded Chinese Markdown summaries or faithful di... | Claude Code · Codex · OpenCode · OpenClaw |

---

## 📦 Installation

In Claude Code, Codex, OpenClaw or any Agent that supports Skills, just say:

```
Install this skill: https://github.com/sanqi-cd/Sanqi-Skills/tree/main/<skill-name>
```

Replace `<skill-name>` with the one you want, e.g. `youtube-podcast-to-md`. The Agent will clone it to the appropriate directory automatically.

---

## ✅ Quality Gates

Every skill includes consistent standard metadata, client metadata, trigger evals, and output evals. Each push and pull request checks:

- `SKILL.md` metadata, directory names, and local references
- `agents/openai.yaml` client metadata
- Python syntax and unit tests
- Eval schemas, README synchronization, and repository hygiene

Run the complete local verification:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_repository.py
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for quality gates and contribution rules.

---

## ✨ Skills

<!-- SKILLS_DETAIL_START -->
<table>
<tr><td>

### 🧭 learning-path-designer

Turn a fuzzy learning goal into an executable, verifiable, and reviewable growth map.

→ [SKILL.md](./learning-path-designer/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📄 paper-explainer

Turn an unfamiliar paper into a clear, evidence-bounded study note.

→ [SKILL.md](./paper-explainer/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 🧰 skill-builder

Build high-quality Agent Skills from requirements through implementation and evaluation.

→ [SKILL.md](./skill-builder/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📦 xhs-image-text-generator

Cover content distillation, pagination, visual design, batch generation, and delivery validation.

→ [SKILL.md](./xhs-image-text-generator/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 🎙️ youtube-podcast-to-md

Provide a resilient and verifiable workflow from transcript retrieval to structured notes.

→ [SKILL.md](./youtube-podcast-to-md/SKILL.md)

</td></tr>
</table>
<!-- SKILLS_DETAIL_END -->

---

## 🌟 About

I'm sanqi. These are skills I use daily. If they help you, give it a ⭐. Questions or suggestions? Feel free to open an Issue.

---

<div align="center">

[MIT License](./LICENSE) · Free to use / modify / redistribute
Made by [@sanqi-cd](https://github.com/sanqi-cd)

</div>
