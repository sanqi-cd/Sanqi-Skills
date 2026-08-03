#!/usr/bin/env python3
"""Validate a generated YouTube podcast Markdown note."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


METADATA_LABELS = ("原标题", "频道", "时长", "链接", "整理模式", "字幕来源", "字幕语言")
SECTION_NAMES = ("核心摘要", "内容目录", "关键要点", "精彩金句")


def validate_output(content: str, mode: str) -> list[str]:
    errors: list[str] = []
    if len(re.findall(r"^#\s+\S", content, re.MULTILINE)) != 1:
        errors.append("document must contain exactly one level-one title")
    for label in METADATA_LABELS:
        if not re.search(rf"^>.*{label}[：:]\s*\S", content, re.MULTILINE):
            errors.append(f"missing metadata: {label}")
    headings = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
    for section in SECTION_NAMES:
        if not any(section in heading for heading in headings):
            errors.append(f"missing section: {section}")
    if not re.search(r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)/", content):
        errors.append("missing YouTube source URL")
    if not re.search(r">\s*(?:🕐\s*)?\d{2}:\d{2}(?::\d{2})?\s*-\s*\d{2}:\d{2}", content):
        errors.append("missing subsection timestamp range")
    if "准确性说明" not in content:
        errors.append("missing accuracy statement")
    if mode == "summary" and not re.search(r"\[→\d{2}:\d{2}(?::\d{2})?\]", content):
        errors.append("summary mode requires at least one point-level timestamp")
    if mode == "full" and not re.search(r"\*\*[^*：:]{1,30}[：:]\*\*", content):
        errors.append("full mode requires speaker-labelled dialogue")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--mode", choices=("summary", "full"), required=True)
    args = parser.parse_args()
    try:
        content = args.markdown.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    errors = validate_output(content, args.mode)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS: {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
