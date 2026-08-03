#!/usr/bin/env python3
"""Render repository examples and capture their README preview images."""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
XHS_RENDERER = ROOT / "xhs-image-text-generator" / "scripts" / "render_carousel_html.py"
LEARNING_RENDERER = ROOT / "learning-path-designer" / "scripts" / "render_growth_map.py"


def find_chrome(explicit: str | None) -> Path:
    candidates = [
        explicit,
        os.environ.get("CHROME_BIN"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise SystemExit("Chrome/Chromium not found; pass --chrome or set CHROME_BIN")


def render_examples() -> list[tuple[Path, Path, tuple[int, int]]]:
    captures: list[tuple[Path, Path, tuple[int, int]]] = []
    xhs_root = ROOT / "examples" / "xhs-image-text-generator"
    for source in sorted(xhs_root.glob("*/carousel.json")):
        html = source.with_name("cards.html")
        subprocess.run(["python3", str(XHS_RENDERER), str(source), str(html)], check=True)
        captures.append((html, source.with_name("preview.png"), (1600, 1040)))

    learning_root = ROOT / "examples" / "learning-path-designer"
    for source in sorted(learning_root.glob("*/learning-plan.json")):
        html = source.with_name("growth-map.html")
        subprocess.run(["python3", str(LEARNING_RENDERER), str(source), str(html)], check=True)
        captures.append((html, source.with_name("preview.png"), (1440, 1200)))
    return captures


def capture(chrome: Path, source: Path, output: Path, size: tuple[int, int]) -> None:
    output.unlink(missing_ok=True)
    width, height = size
    with tempfile.TemporaryDirectory(prefix="sanqi-chrome-") as profile:
        command = [
            str(chrome),
            "--headless=new",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-extensions",
            "--disable-gpu",
            "--disable-sync",
            "--hide-scrollbars",
            "--no-default-browser-check",
            "--no-first-run",
            "--force-device-scale-factor=1",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=1000",
            f"--user-data-dir={profile}",
            f"--window-size={width},{height}",
            f"--screenshot={output}",
            source.resolve().as_uri(),
        ]
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        deadline = time.monotonic() + 15
        previous_size = -1
        stable_checks = 0
        try:
            while time.monotonic() < deadline:
                if output.is_file() and output.stat().st_size > 0:
                    current_size = output.stat().st_size
                    stable_checks = stable_checks + 1 if current_size == previous_size else 0
                    previous_size = current_size
                    if stable_checks >= 2:
                        break
                if process.poll() is not None and not output.is_file():
                    raise RuntimeError(f"Chrome exited before capturing {source}")
                time.sleep(0.2)
            else:
                raise RuntimeError(f"timed out capturing {source}")
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
    print(output.relative_to(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chrome", help="Path to a Chrome or Chromium executable")
    args = parser.parse_args()
    chrome = find_chrome(args.chrome)
    for source, output, size in render_examples():
        capture(chrome, source, output, size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
