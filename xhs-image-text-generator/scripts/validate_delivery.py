#!/usr/bin/env python3
"""Validate the completeness and consistency of a Xiaohongshu delivery package."""

from __future__ import annotations

import argparse
import json
import re
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
    html_path = root / "cards.html"
    html_fallback = allow_html and html_path.is_file() and not images
    if html_fallback:
        html_content = html_path.read_text(encoding="utf-8")
        if html_content.count('<article class="card') != page_count:
            errors.append(f"cards.html must contain {page_count} rendered pages")
    if len(images) != page_count and not html_fallback:
        errors.append(f"expected {page_count} final image pages, found {len(images)}")
    if images:
        try:
            from PIL import Image, UnidentifiedImageError
        except ImportError:
            errors.append("Pillow is required to validate final images; install xhs-image-text-generator/requirements.txt")
        else:
            actual = set()
            for path in images:
                match = re.fullmatch(r"page-(\d{2})\.(?:png|jpg|jpeg|webp)", path.name, re.I)
                if not match:
                    errors.append(f"invalid image filename: {path.name}")
                    continue
                number = int(match.group(1))
                if number in actual:
                    errors.append(f"duplicate image page: {number:02d}")
                actual.add(number)
                try:
                    with Image.open(path) as image:
                        width, height = image.size
                        image.verify()
                    with Image.open(path) as image:
                        image.load()
                    ratio_ok = min(abs(width / height - 0.75), abs(width / height - 0.8)) <= 0.01
                    if width < 720 or not ratio_ok:
                        errors.append(f"{path.name}: expected a portrait 3:4 or 4:5 image at least 720px wide, got {width}x{height}")
                except (OSError, ValueError, UnidentifiedImageError) as exc:
                    errors.append(f"{path.name}: unreadable image: {exc}")
            if actual != set(range(1, page_count + 1)):
                errors.append("image page numbers must be consecutive from 01 to the carousel page count")
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
