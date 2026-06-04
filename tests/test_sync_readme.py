import tempfile
import unittest
from pathlib import Path

from scripts import sync_readme


ZH_README = """# Demo

### Skills

| 名字 | 一句话 | 平台 |
|---|---|---|
| old | old | old |

---

<!-- SKILLS_DETAIL_START -->
old detail
<!-- SKILLS_DETAIL_END -->
"""


EN_README = """# Demo

### Skills

| Name | One-liner | Platforms |
|---|---|---|
| 🎬 [**youtube-podcast-to-md**](#-youtube-podcast-to-md) | Extract YouTube podcast videos and organize into Chinese Markdown notes | Claude Code · Codex · OpenCode · OpenClaw |

---

<!-- SKILLS_DETAIL_START -->
<table>
<tr><td>

### 🎬 youtube-podcast-to-md

Existing English detail body.

→ [SKILL.md](./youtube-podcast-to-md/SKILL.md)

</td></tr>
</table>
<!-- SKILLS_DETAIL_END -->
"""


class SyncReadmeTest(unittest.TestCase):
    def test_syncs_chinese_and_english_readmes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(ZH_README, encoding="utf-8")
            (root / "README.en.md").write_text(EN_README, encoding="utf-8")

            skill_dir = root / "skill-builder"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                """---
name: skill-builder
description: >
  当用户想创建一个新的 Skill 但需求模糊、不完整或过于宽泛时使用。
description_en: >
  Guide vague Skill ideas into executable task cards and high-quality SKILL.md files.
overview_en: >
  Turns vague Skill ideas into executable task cards through structured interviews.
---

# Skill Builder

## 目标

把模糊的 Skill 想法收敛为可执行任务卡。
""",
                encoding="utf-8",
            )

            youtube_dir = root / "youtube-podcast-to-md"
            youtube_dir.mkdir()
            (youtube_dir / "SKILL.md").write_text(
                """---
name: youtube-podcast-to-md
description: 将 YouTube 播客视频字幕提取并整理为中文 Markdown 笔记
---

# YouTube 播客

## 概述

将 YouTube 播客视频字幕提取并整理为中文 Markdown 笔记。
""",
                encoding="utf-8",
            )

            sync_readme.sync_readmes(root, dry_run=False)

            zh_content = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("| 名字 | 一句话 | 平台 |", zh_content)
            self.assertIn("[**skill-builder**]", zh_content)
            self.assertIn("把模糊的 Skill 想法收敛为可执行任务卡。", zh_content)

            en_content = (root / "README.en.md").read_text(encoding="utf-8")
            self.assertIn("| Name | One-liner | Platforms |", en_content)
            self.assertIn("[**skill-builder**]", en_content)
            self.assertIn(
                "Guide vague Skill ideas into executable task cards and high-quality SKILL.md files.",
                en_content,
            )
            self.assertIn(
                "Turns vague Skill ideas into executable task cards through structured interviews.",
                en_content,
            )
            self.assertNotIn("把模糊的 Skill 想法收敛为可执行任务卡。", en_content)
            self.assertIn(
                "| 🎬 [**youtube-podcast-to-md**](#-youtube-podcast-to-md) | Extract YouTube podcast videos and organize into Chinese Markdown notes |",
                en_content,
            )
            self.assertIn("### 🎬 youtube-podcast-to-md", en_content)
            self.assertIn("Existing English detail body.", en_content)


if __name__ == "__main__":
    unittest.main()
