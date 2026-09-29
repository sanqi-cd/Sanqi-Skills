#!/usr/bin/env python3
"""Validate a rendered learning growth map without external dependencies."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from render_growth_map import validate_plan


REQUIRED_MARKERS = (
    "learning-plan-data",
    "起点",
    "终点",
    "今天的小胜利",
    "学习诊断",
    "成长路线",
    "全周期行动卡",
    "知识树",
    "任务树",
    "成果展台",
    "学习装备",
    "本站作品",
    "通关标准",
    "localStorage",
    "@media(max-width:760px)",
)


def validate_html(content: str) -> list[str]:
    errors = [f"missing marker: {marker}" for marker in REQUIRED_MARKERS if marker not in content]
    if not content.lstrip().lower().startswith("<!doctype html>"):
        errors.append("document must start with an HTML5 doctype")
    if re.search(r"(?:src|href)=[\"']https?://", content, re.I):
        errors.append("external dependencies are not allowed")
    if "TODO" in content or "__PLACEHOLDER__" in content:
        errors.append("unresolved placeholder found")
    match = re.search(
        r'<script id="learning-plan-data" type="application/json">(.*?)</script>',
        content,
        re.S,
    )
    if match is None:
        errors.append("embedded learning plan data is missing")
    else:
        try:
            plan = json.loads(match.group(1))
        except json.JSONDecodeError:
            errors.append("embedded learning plan data is invalid JSON")
        else:
            if not isinstance(plan, dict):
                errors.append("embedded learning plan must be an object")
            else:
                errors.extend(validate_plan(plan))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    args = parser.parse_args()
    try:
        content = args.html.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    errors = validate_html(content)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS: {args.html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
