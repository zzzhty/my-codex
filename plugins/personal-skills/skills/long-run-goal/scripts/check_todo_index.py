#!/usr/bin/env python3
"""Verify that a goal file is referenced by active TODO/README indexes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("goal_file", type=Path)
    parser.add_argument("indexes", nargs="+", type=Path)
    args = parser.parse_args()

    goal = args.goal_file
    if not goal.exists():
        print(f"missing goal file: {goal}", file=sys.stderr)
        return 1

    goal_name = goal.name
    errors: list[str] = []
    for index in args.indexes:
        if not index.exists():
            errors.append(f"missing index: {index}")
            continue
        text = index.read_text(encoding="utf-8")
        if goal_name not in text and str(goal).replace("\\", "/") not in text.replace("\\", "/"):
            errors.append(f"{index}: does not reference {goal_name}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"{goal_name}: referenced by {len(args.indexes)} index file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
