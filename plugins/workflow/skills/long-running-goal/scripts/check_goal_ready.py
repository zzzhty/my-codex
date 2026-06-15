#!/usr/bin/env python3
"""Lightweight readiness checks for a long-running-goal Markdown file."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")


def strip_fenced_blocks(text: str) -> str:
    lines = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("goal_file", type=Path)
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="Allow Draft status while still checking placeholders and structure.",
    )
    args = parser.parse_args()

    path = args.goal_file
    if not path.exists():
        print(f"missing goal file: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    visible_text = strip_fenced_blocks(text)
    errors: list[str] = []

    placeholders = PLACEHOLDER_RE.findall(visible_text)
    if placeholders:
        preview = ", ".join(sorted(set(placeholders))[:10])
        errors.append(f"unresolved placeholders outside code fences: {preview}")

    required_patterns = {
        "M0 milestone": r"\bM0\b",
        "review gate": r"(?i)\breview\s*gate\b|Review gate|评审|验收",
        "checkpoint evidence": r"(?i)\bcheckpoint\b|检查点",
        "rollback path": r"(?i)\brollback\b|回滚",
        "close/archive procedure": r"(?i)\b(close|archive)\b|关闭|归档",
        "validation evidence": r"(?i)\b(validation|verify|test)\b|验证|测试",
        "failure handling": r"(?i)\b(fail|failure|breakpoint|blocked)\b|失败|断点|阻塞",
        "continuation contract": r"(?i)\bcontinuation\s+contract\b|Continuation contract|继续执行的关键约束",
        "reusable prompt": r"(?i)\b(prompt)\b|推荐.*Prompt",
    }
    for label, pattern in required_patterns.items():
        if not re.search(pattern, visible_text):
            errors.append(f"missing required section signal: {label}")

    if not args.allow_draft:
        status_lines = [
            line
            for line in visible_text.splitlines()
            if re.search(r"(?i)\b(status|状态)\b", line)
        ]
        joined_status = "\n".join(status_lines[:20])
        if not re.search(r"(?i)\b(ready|in progress|closed)\b|Ready|进行中|已关闭", joined_status):
            errors.append("no Ready/In Progress/Closed status found in status lines")

    if errors:
        for error in errors:
            print(f"{path}: {error}", file=sys.stderr)
        return 1

    print(f"{path}: goal readiness checks OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
