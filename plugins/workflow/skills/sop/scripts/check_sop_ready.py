#!/usr/bin/env python3
"""Lightweight readiness checks for an SOP Markdown file."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sop_file", type=Path)
    args = parser.parse_args()

    path = args.sop_file
    if not path.exists():
        print(f"missing SOP file: {path}", file=sys.stderr)
        return 1
    if not path.is_file():
        print(f"SOP path is not a file: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    visible_text = strip_fenced_blocks(text)
    errors: list[str] = []

    placeholders = PLACEHOLDER_RE.findall(visible_text)
    if placeholders:
        preview = ", ".join(sorted(set(placeholders))[:10])
        errors.append(f"unresolved placeholders outside code fences: {preview}")

    required_patterns = {
        "summary": r"(?m)^##\s*(摘要|Summary)\b",
        "trigger": r"(?m)^##\s*(触发条件|Trigger)\b",
        "preconditions": r"(?m)^##\s*(前置条件|Preconditions)\b",
        "working directory": r"(?m)^##\s*(工作目录|Working Directory)\b",
        "inputs": r"(?m)^##\s*(输入|Inputs)\b",
        "execution harness": r"(?m)^##\s*(Execution Harness|执行 Harness|执行约束)\b",
        "allowed actions": r"(?m)^##\s*(允许动作|Allowed Actions)\b",
        "forbidden actions": r"(?m)^##\s*(禁止动作|Forbidden Actions)\b",
        "steps": r"(?m)^##\s*(标准步骤|Steps)\b",
        "validation": r"(?m)^##\s*(验证标准|Validation)\b",
        "output contract": r"(?m)^##\s*(输出合同|Output Contract)\b",
        "stop conditions": r"(?m)^##\s*(停止条件|Stop Conditions)\b",
        "update rules": r"(?m)^##\s*(更新规则|Update Rules)\b",
        "reuse prompt": r"(?m)^##\s*(复用 Prompt|Reuse Prompt)\b",
    }
    for label, pattern in required_patterns.items():
        if not re.search(pattern, visible_text):
            errors.append(f"missing required section: {label}")

    status_lines = [
        line
        for line in visible_text.splitlines()
        if re.search(r"(?i)\bstatus\b|状态", line)
    ]
    joined_status = "\n".join(status_lines[:20])
    if not re.search(r"(?i)\b(ready|draft|in progress|closed)\b|Ready|Draft|进行中|已关闭", joined_status):
        errors.append("no recognizable status line found")

    if errors:
        for error in errors:
            print(f"{path}: {error}", file=sys.stderr)
        return 1

    print(f"{path}: SOP readiness checks OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
