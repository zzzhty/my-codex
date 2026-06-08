#!/usr/bin/env python3
"""Validate a summary-in-html artifact and local asset references."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


IMG_SRC_RE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)
LOCAL_HREF_RE = re.compile(r"<a\b[^>]*\bhref=[\"']([^\"']+)[\"']", re.IGNORECASE)


def is_external(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(("http://", "https://", "mailto:", "tel:", "data:"))


def local_path(base: Path, value: str) -> Path | None:
    if not value or value.startswith("#") or is_external(value):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    return (base / path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file", type=Path)
    args = parser.parse_args()

    path = args.html_file
    if not path.exists():
        print(f"missing HTML file: {path}", file=sys.stderr)
        return 1
    if not path.is_file():
        print(f"HTML path is not a file: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    lower = text.lower()
    if "<!doctype html>" not in lower:
        errors.append("missing <!doctype html>")
    if "<html" not in lower or "</html>" not in lower:
        errors.append("missing html root tags")
    if "<main" not in lower:
        errors.append("missing main element")
    if "<h1" not in lower:
        errors.append("missing h1 heading")
    if lower.count("<section") < 1:
        errors.append("missing section content")
    if "{{" in text or "}}" in text:
        errors.append("unresolved template braces")
    if "__TITLE__" in text or "__BODY__" in text:
        errors.append("unresolved template placeholder")

    base = path.parent
    for src in IMG_SRC_RE.findall(text):
        target = local_path(base, src)
        if target and not target.exists():
            errors.append(f"missing local image asset: {src}")

    for href in LOCAL_HREF_RE.findall(text):
        target = local_path(base, href)
        if target and not target.exists():
            errors.append(f"missing local link target: {href}")

    if errors:
        for error in errors:
            print(f"{path}: {error}", file=sys.stderr)
        return 1

    print(f"{path}: HTML checks OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
