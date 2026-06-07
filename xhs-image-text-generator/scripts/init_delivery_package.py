#!/usr/bin/env python3
"""Create a xhs-image-text-generator delivery package folder."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FILES = {
    "manifest.md": "# 小红书图文交付清单\n\n",
    "caption.txt": "",
    "hashtags.txt": "",
    "comments.txt": "",
    "image-prompts.md": "# 生图提示词\n\n",
    "quality-check.md": "# 发布前质量检查\n\n",
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "xhs-package"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Package name or topic")
    parser.add_argument("--output-root", default="xhs-output")
    parser.add_argument("--pages", type=int, default=8)
    args = parser.parse_args()

    root = Path(args.output_root) / slugify(args.name)
    images = root / "images"
    images.mkdir(parents=True, exist_ok=True)

    for filename, content in FILES.items():
        path = root / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")

    manifest = root / "manifest.md"
    if manifest.read_text(encoding="utf-8").strip() == "# 小红书图文交付清单":
        pages = "\n".join(f"- [ ] page-{i:02d}.png" for i in range(1, args.pages + 1))
        manifest.write_text(
            "# 小红书图文交付清单\n\n"
            f"- 主题：{args.name}\n"
            f"- 页面数：{args.pages}\n"
            "- 状态：待填充\n\n"
            "## 图片页\n\n"
            f"{pages}\n",
            encoding="utf-8",
        )

    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
