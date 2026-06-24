#!/usr/bin/env python3
"""Shared Markdown contract checks for Workflow skills."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


@dataclass(frozen=True)
class LinkIssue:
    file_path: Path
    line: int
    target: str


def strip_fenced_blocks(text: str) -> str:
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def placeholder_errors(visible_text: str) -> list[str]:
    placeholders = PLACEHOLDER_RE.findall(visible_text)
    if not placeholders:
        return []
    preview = ", ".join(sorted(set(placeholders))[:10])
    return [f"unresolved placeholders outside code fences: {preview}"]


def missing_required_pattern_errors(
    visible_text: str,
    required_patterns: dict[str, str],
    *,
    message: str,
) -> list[str]:
    errors: list[str] = []
    for label, pattern in required_patterns.items():
        if not re.search(pattern, visible_text):
            errors.append(f"{message}: {label}")
    return errors


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


def missing_relative_links(root: Path) -> list[LinkIssue]:
    missing: list[LinkIssue] = []
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
                missing.append(LinkIssue(file_path=file_path, line=line, target=target))
    return missing


def render_errors(path: Path, errors: list[str], *, stderr: TextIO | None = None) -> int:
    stream = stderr or sys.stderr
    for error in errors:
        print(f"{path}: {error}", file=stream)
    return 1 if errors else 0


def render_link_errors(issues: list[LinkIssue], *, stderr: TextIO | None = None) -> int:
    stream = stderr or sys.stderr
    for issue in issues:
        print(f"{issue.file_path}:{issue.line}: missing {issue.target}", file=stream)
    return 1 if issues else 0
