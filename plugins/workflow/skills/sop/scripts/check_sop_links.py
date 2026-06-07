#!/usr/bin/env python3
"""Check relative Markdown links under an SOP directory or in one SOP file."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def iter_markdown(path: Path):
    if path.is_file():
        if path.suffix.lower() == ".md":
            yield path
        return
    yield from path.rglob("*.md")


def is_external(target: str) -> bool:
    lower = target.lower()
    return (
        not target
        or target.startswith("#")
        or lower.startswith(("http://", "https://", "mailto:", "tel:"))
        or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) is not None
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    root = args.path
    if not root.exists():
        print(f"missing path: {root}", file=sys.stderr)
        return 1

    missing: list[tuple[Path, int, str]] = []
    for file_path in iter_markdown(root):
        text = file_path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip()
            if is_external(target):
                continue
            path_only = target.split("#", 1)[0]
            if not path_only:
                continue
            if path_only.startswith("<") and path_only.endswith(">"):
                path_only = path_only[1:-1]
            resolved = (file_path.parent / path_only).resolve()
            ok = resolved.is_dir() if path_only.endswith(("/", "\\")) else resolved.exists()
            if not ok:
                line = text[: match.start()].count("\n") + 1
                missing.append((file_path, line, target))

    if missing:
        for file_path, line, target in missing:
            print(f"{file_path}:{line}: missing {target}", file=sys.stderr)
        return 1

    print(f"{root}: SOP markdown relative links OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
