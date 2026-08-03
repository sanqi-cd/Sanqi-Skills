#!/usr/bin/env python3
"""Validate the completeness and consistency of a Xiaohongshu delivery package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from render_carousel_html import validate_carousel


REQUIRED_FILES = (
    "manifest.md",
    "caption.txt",
    "hashtags.txt",
    "comments.txt",
    "image-prompts.md",
    "quality-check.md",
    "carousel.json",
)


def validate_package(root: Path, allow_html: bool = False) -> list[str]:
    errors: list[str] = []
    for filename in REQUIRED_FILES:
        path = root / filename
        if not path.is_file():
            errors.append(f"missing {filename}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty {filename}")
    carousel_path = root / "carousel.json"
    page_count = 0
    if carousel_path.is_file():
        try:
            data = json.loads(carousel_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid carousel.json: {exc}")
        else:
            if not isinstance(data, dict):
                errors.append("carousel.json root must be an object")
            else:
                errors.extend(validate_carousel(data))
                page_count = len(data.get("pages", [])) if isinstance(data.get("pages"), list) else 0
    image_dir = root / "images"
    images = sorted(path for path in image_dir.glob("page-*.*") if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}) if image_dir.is_dir() else []
    if len(images) != page_count:
        if not (allow_html and (root / "cards.html").is_file()):
            errors.append(f"expected {page_count} final image pages, found {len(images)}")
    joined = "\n".join((root / filename).read_text(encoding="utf-8") for filename in REQUIRED_FILES if (root / filename).is_file())
    if "TODO" in joined or "待填充" in joined:
        errors.append("unresolved placeholder found")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--allow-html", action="store_true", help="Accept cards.html instead of final image files")
    args = parser.parse_args()
    errors = validate_package(args.package, args.allow_html)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS: {args.package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
