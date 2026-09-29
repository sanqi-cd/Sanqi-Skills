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
    "结论": ("结论", "总结与结论"),
    "局限": ("局限", "局限与边界", "未解决的问题"),
    "证据边界": ("证据边界", "来源与证据边界"),
}
LOCATOR = re.compile(r"\[(?:p\.\s*\d+|§\s*[\d.]+|(?:Figure|Fig\.|Table|Eq\.|Appendix)\s*[A-Za-z0-9.-]+)\]", re.I)


def validate_note(content: str, page_count: int | None = None) -> list[str]:
    errors: list[str] = []
    sections = re.findall(r"^##\s+(.+?)\s*$\n(.*?)(?=^##\s+|\Z)", content, re.MULTILINE | re.DOTALL)
    headings = {heading for heading, _ in sections}
    for label, alternatives in HEADING_GROUPS.items():
        if not any(any(option in heading for option in alternatives) for heading in headings):
            errors.append(f"missing section: {label}")
    locators = set(LOCATOR.findall(content))
    if len(locators) < 3:
        errors.append("include at least three distinct page, section, figure, table, equation, or appendix locators")
    for label in ("方法", "实验"):
        body = next((body for heading, body in sections if any(option in heading for option in HEADING_GROUPS[label])), "")
        if not body.strip() or not LOCATOR.search(body):
            errors.append(f"{label} section needs a source locator")
    if page_count is not None:
        for match in re.finditer(r"\[p\.\s*(\d+)\]", content, re.I):
            if not 1 <= int(match.group(1)) <= page_count:
                errors.append(f"page locator {match.group(0)} exceeds source page count {page_count}")
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
    parser.add_argument("--page-count", type=int, help="Optional PDF page count for page-locator range checks")
    args = parser.parse_args()
    try:
        content = args.note.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    if args.page_count is not None and args.page_count < 1:
        parser.error("--page-count must be positive")
    errors = validate_note(content, args.page_count)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS: {args.note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
