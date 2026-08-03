#!/usr/bin/env python3
"""Render carousel.json into printable 1080 x 1350 HTML cards."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def validate_carousel(data: dict) -> list[str]:
    errors: list[str] = []
    for key in ("topic", "audience", "angle"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} must be a non-empty string")
    visual = data.get("visual_system")
    if not isinstance(visual, dict):
        errors.append("visual_system must be an object")
    else:
        for key in ("background", "foreground", "accent"):
            if not isinstance(visual.get(key), str) or not HEX.fullmatch(visual[key]):
                errors.append(f"visual_system.{key} must be a six-digit hex color")
    pages = data.get("pages")
    if not isinstance(pages, list) or not 6 <= len(pages) <= 10:
        errors.append("pages must contain 6-10 items")
        pages = []
    roles: list[str] = []
    for index, page in enumerate(pages, 1):
        if not isinstance(page, dict):
            errors.append(f"page {index} must be an object")
            continue
        if page.get("number") != index:
            errors.append(f"page {index}.number must be {index}")
        role = page.get("role")
        if not isinstance(role, str) or not role:
            errors.append(f"page {index}.role must be a non-empty string")
        else:
            roles.append(role)
        for key, limit in (("title", 28), ("subtitle", 44), ("visual_note", 120)):
            value = page.get(key, "")
            if not isinstance(value, str):
                errors.append(f"page {index}.{key} must be a string")
            elif key == "title" and not value.strip():
                errors.append(f"page {index}.title must not be empty")
            elif len(value) > limit:
                errors.append(f"page {index}.{key} exceeds {limit} characters")
        bullets = page.get("bullets", [])
        if not isinstance(bullets, list) or len(bullets) > 6:
            errors.append(f"page {index}.bullets must contain at most 6 items")
        elif any(not isinstance(item, str) or not item.strip() or len(item) > 48 for item in bullets):
            errors.append(f"page {index}.bullets contain an invalid item")
    if roles and roles.count("cover") != 1:
        errors.append("pages must contain exactly one cover role")
    if roles and roles[-1] not in {"cta", "summary"}:
        errors.append("last page role must be cta or summary")
    if "TODO" in json.dumps(data, ensure_ascii=False):
        errors.append("unresolved TODO placeholder found")
    return errors


def render(data: dict) -> str:
    esc = lambda value: html.escape(str(value))
    visual = data["visual_system"]
    cards = []
    for page in data["pages"]:
        bullets = "".join(f"<li>{esc(item)}</li>" for item in page.get("bullets", []))
        source = f'<div class="source">来源：{esc(page["source_note"])}</div>' if page.get("source_note") else ""
        cards.append(
            f'<article class="card role-{esc(page["role"])}">'
            f'<div class="top"><span>{page["number"]:02d}</span><span>{esc(data["topic"])}</span></div>'
            f'<div class="content"><div class="role">{esc(page["role"])}</div><h1>{esc(page["title"])}</h1>'
            f'<p class="subtitle">{esc(page.get("subtitle", ""))}</p><ul>{bullets}</ul></div>'
            f'{source}<div class="foot">{esc(data["audience"])}</div></article>'
        )
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(data['topic'])}</title>
<style>
:root{{--bg:{visual['background']};--fg:{visual['foreground']};--accent:{visual['accent']}}}*{{box-sizing:border-box}}body{{margin:0;background:#d9ddd9;color:var(--fg);font-family:system-ui,-apple-system,"PingFang SC",sans-serif;letter-spacing:0}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:24px;padding:24px}}.card{{position:relative;aspect-ratio:4/5;overflow:hidden;background:var(--bg);padding:7%;display:flex;flex-direction:column;border-top:18px solid var(--accent)}}.top,.foot{{display:flex;justify-content:space-between;font-size:clamp(11px,1.2vw,16px);font-weight:700}}.content{{margin:auto 0}}.role{{color:var(--accent);font-weight:800;text-transform:uppercase}}h1{{font-size:clamp(30px,4.2vw,58px);line-height:1.12;margin:16px 0;letter-spacing:0;overflow-wrap:anywhere}}.subtitle{{font-size:clamp(16px,2vw,28px)}}ul{{padding-left:1.2em;font-size:clamp(15px,1.7vw,24px);line-height:1.55}}li{{margin:.5em 0}}.source{{font-size:12px;border-top:1px solid currentColor;padding-top:8px;margin-bottom:12px}}.role-cover{{border-top-width:48px}}@media print{{body{{background:#fff}}main{{display:block;padding:0}}.card{{width:1080px;height:1350px;break-after:page}}}}@media(max-width:500px){{main{{padding:10px;gap:10px}}}}
</style></head><body><main>{''.join(cards)}</main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carousel", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.carousel.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    if not isinstance(data, dict):
        parser.error("carousel JSON root must be an object")
    errors = validate_carousel(data)
    if errors:
        parser.error("invalid carousel: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data), encoding="utf-8")
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
