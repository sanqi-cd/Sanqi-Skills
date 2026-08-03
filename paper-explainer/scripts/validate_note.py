#!/usr/bin/env python3
"""Check a paper explanation Markdown file for structure and evidence markers."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HEADING_GROUPS = {
    "快速结论": ("一句话速读", "快速结论"),
    "问题与背景": ("引言", "问题与背景"),
    "方法": ("方法", "核心方法"),
    "实验": ("实验", "实验与结果"),
    "局限": ("局限", "局限与边界", "未解决的问题"),
    "证据边界": ("证据边界", "来源与证据边界"),
}
LOCATOR = re.compile(r"\[(?:p\.\s*\d+|§\s*[\d.]+|(?:Figure|Fig\.|Table|Eq\.|Appendix)\s*[A-Za-z0-9.-]+)\]", re.I)


def validate_note(content: str) -> list[str]:
    errors: list[str] = []
    headings = set(re.findall(r"^##+\s+(.+?)\s*$", content, re.MULTILINE))
    for label, alternatives in HEADING_GROUPS.items():
        if not any(any(option in heading for option in alternatives) for heading in headings):
            errors.append(f"missing section: {label}")
    if len(LOCATOR.findall(content)) < 3:
        errors.append("include at least three page, section, figure, table, equation, or appendix locators")
    for label in ("作者陈述", "论文证据", "解读"):
        if label not in content:
            errors.append(f"missing attribution label: {label}")
    if not re.search(r"\*\*作者\*\*|\*\*作者\*\*:|作者[：:]", content):
        errors.append("missing paper author metadata")
    if not re.search(r"https?://|DOI", content, re.I):
        errors.append("missing source URL or DOI")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("note", type=Path)
    args = parser.parse_args()
    try:
        content = args.note.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    errors = validate_note(content)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS: {args.note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
