#!/usr/bin/env python3
"""Normalize URL, HTML, Markdown, or text into a compact Markdown source file."""

from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


MAX_DOWNLOAD_BYTES = 5 * 1024 * 1024


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg", "canvas"}:
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
            return
        if tag in {"p", "div", "section", "article", "br", "li", "h1", "h2", "h3", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg", "canvas"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if tag in {"p", "div", "section", "article", "li", "h1", "h2", "h3", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title += text
        else:
            self.parts.append(text)

    def text(self) -> str:
        return clean_text("\n".join(self.parts))


def is_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def read_input(source: str) -> tuple[str, str]:
    if source == "-":
        return sys.stdin.read(), "stdin"
    if is_url(source):
        request = urllib.request.Request(
            source,
            headers={"User-Agent": "Mozilla/5.0 xhs-image-text-generator"},
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_DOWNLOAD_BYTES:
                raise ValueError("remote input exceeds the 5 MB safety limit")
            charset = response.headers.get_content_charset() or "utf-8"
            payload = response.read(MAX_DOWNLOAD_BYTES + 1)
            if len(payload) > MAX_DOWNLOAD_BYTES:
                raise ValueError("remote input exceeds the 5 MB safety limit")
            return payload.decode(charset, errors="replace"), source
    path = Path(source)
    return path.read_text(encoding="utf-8", errors="replace"), str(path)


def detect_format(raw: str, source: str, explicit: str) -> str:
    if explicit != "auto":
        return explicit
    suffix = Path(source).suffix.lower()
    if suffix in {".html", ".htm"} or re.search(r"<html|<body|<article|<p[\s>]", raw, re.I):
        return "html"
    if suffix in {".md", ".markdown"} or re.search(r"(^|\n)#{1,6}\s+|```|\[[^\]]+\]\([^)]+\)", raw):
        return "markdown"
    return "text"


def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_markdown(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`{1,3}", "", text)
    return clean_text(text)


def normalize_html(raw: str) -> tuple[str, str]:
    parser = TextExtractor()
    parser.feed(raw)
    return clean_text(parser.title), parser.text()


def trim_lines(lines: Iterable[str], max_chars: int) -> str:
    result: list[str] = []
    count = 0
    for line in lines:
        if count >= max_chars:
            break
        remaining = max_chars - count
        if len(line) > remaining:
            line = line[:remaining]
        result.append(line)
        count += len(line) + 1
    return "\n".join(result).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="URL, local file path, or '-' for stdin")
    parser.add_argument("--format", choices=["auto", "html", "markdown", "text"], default="auto")
    parser.add_argument("--output", help="Write normalized Markdown to this path")
    parser.add_argument("--max-chars", type=int, default=20000)
    args = parser.parse_args()

    try:
        raw, source = read_input(args.input)
    except (OSError, ValueError) as exc:
        parser.error(f"cannot read input: {exc}")
    input_format = detect_format(raw, source, args.format)

    title = ""
    if input_format == "html":
        title, body = normalize_html(raw)
    elif input_format == "markdown":
        body = normalize_markdown(raw)
    else:
        body = clean_text(raw)

    body = trim_lines(body.splitlines(), args.max_chars)
    output = (
        "# Normalized Source\n\n"
        f"- Source: {source}\n"
        f"- Detected format: {input_format}\n"
        + (f"- HTML title: {title}\n" if title else "")
        + "\n## Extracted Content\n\n"
        + body
        + "\n"
    )

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
