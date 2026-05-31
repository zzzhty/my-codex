#!/usr/bin/env python3
"""Generate a report-only Skill Watcher daily report."""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from summarize_logs import build_report, filter_events, parse_since, read_events


DEFAULT_STATE_DIR = Path.home() / ".codex" / "skill-watcher"


def state_dir_from_env_or_arg(raw_state_dir: str | None) -> Path:
    return Path(raw_state_dir or os.environ.get("SKILL_WATCHER_STATE_DIR") or DEFAULT_STATE_DIR).expanduser()


def safe_slug(value: str) -> str:
    slug = "".join(char if char.isalnum() or char in "-_" else "-" for char in value).strip("-")
    return slug or "all"


def outcome_counts(events: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for event in events:
        outcome = str(event.get("outcome") or "unknown")
        counter[outcome] += 1
    return counter


def default_daily_report_path(state_dir: Path, skill: str | None) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return state_dir / "reports" / f"{timestamp}-{safe_slug(skill or 'all')}-daily-report.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a Skill Watcher daily report under state reports/.")
    parser.add_argument("--skill", help="Filter by skill_name. Defaults to all skills.")
    parser.add_argument("--since", default="1d", help="Evidence window such as 1d, 24h, or ISO timestamp.")
    parser.add_argument("--state-dir", help="Runtime state directory. Defaults to ~/.codex/skill-watcher.")
    parser.add_argument("--log-file", help="Explicit JSONL log path. Overrides --state-dir logs/events.jsonl.")
    parser.add_argument("--output", help="Explicit report output path.")
    parser.add_argument("--print-report", action="store_true", help="Also print the full report to stdout.")
    args = parser.parse_args()

    state_dir = state_dir_from_env_or_arg(args.state_dir)
    log_file = Path(args.log_file).expanduser() if args.log_file else state_dir / "logs" / "events.jsonl"
    since = parse_since(args.since)
    events = filter_events(read_events(log_file), skill=args.skill, since=since)
    report = build_report(events, skill=args.skill, since_raw=args.since, log_file=log_file)

    output = Path(args.output).expanduser() if args.output else default_daily_report_path(state_dir, args.skill)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        output.write_text(report + "\n", encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to write daily report {output}: {exc}") from exc

    counts = outcome_counts(events)
    print(f"report: {output}")
    print(f"events: {len(events)}")
    print("outcomes: " + ", ".join(f"{name}={count}" for name, count in sorted(counts.items())) if counts else "outcomes: none")

    if args.print_report:
        print("", file=sys.stdout)
        print(report)


if __name__ == "__main__":
    main()
