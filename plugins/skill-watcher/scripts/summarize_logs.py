#!/usr/bin/env python3
"""Summarize Skill Watcher JSONL logs as Markdown."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path.home() / ".codex" / "skill-watcher"


def state_dir_from_env_or_arg(raw_state_dir: str | None) -> Path:
    return Path(raw_state_dir or os.environ.get("SKILL_WATCHER_STATE_DIR") or DEFAULT_STATE_DIR).expanduser()


def parse_timestamp(raw: str) -> datetime | None:
    if not isinstance(raw, str) or not raw:
        return None
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_since(raw: str | None) -> datetime | None:
    if raw is None:
        return None
    value = raw.strip()
    if not value:
        return None
    now = datetime.now(timezone.utc)
    unit = value[-1].lower()
    amount = value[:-1]
    if unit in {"h", "d", "w"} and amount.isdigit():
        count = int(amount)
        if unit == "h":
            return now - timedelta(hours=count)
        if unit == "d":
            return now - timedelta(days=count)
        return now - timedelta(weeks=count)
    parsed = parse_timestamp(value)
    if parsed is not None:
        return parsed
    raise SystemExit(f"invalid --since value {raw!r}; use forms like 12h, 7d, 2w, or ISO timestamp")


def read_events(log_file: Path) -> list[dict[str, Any]]:
    if not log_file.exists():
        return []
    events: list[dict[str, Any]] = []
    try:
        with log_file.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise SystemExit(
                        f"invalid JSONL in {log_file} at line {line_number}: "
                        f"line {exc.lineno}, column {exc.colno}"
                    ) from exc
                if not isinstance(payload, dict):
                    raise SystemExit(f"invalid JSONL in {log_file} at line {line_number}: event must be an object")
                events.append(payload)
    except OSError as exc:
        raise SystemExit(f"failed to read log file {log_file}: {exc}") from exc
    return events


def filter_events(
    events: list[dict[str, Any]],
    *,
    skill: str | None,
    since: datetime | None,
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for event in events:
        if skill and event.get("skill_name") != skill:
            continue
        if since is not None:
            timestamp = parse_timestamp(str(event.get("timestamp", "")))
            if timestamp is None or timestamp < since:
                continue
        filtered.append(event)
    return filtered


def count_values(events: list[dict[str, Any]], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for event in events:
        value = event.get(key)
        if isinstance(value, str) and value:
            counter[value] += 1
        elif value:
            counter[str(value)] += 1
    return counter


def render_counter(counter: Counter[str]) -> list[str]:
    if not counter:
        return ["- none"]
    return [f"- `{key}`: {count}" for key, count in sorted(counter.items())]


def render_samples(events: list[dict[str, Any]], key: str, *, limit: int = 5) -> list[str]:
    samples: list[str] = []
    for event in events:
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            samples.append(f"- {value.strip()}")
        if len(samples) >= limit:
            break
    return samples or ["- none"]


def build_report(
    events: list[dict[str, Any]],
    *,
    skill: str | None,
    since_raw: str | None,
    log_file: Path,
) -> str:
    outcome_counts = count_values(events, "outcome")
    failure_counts = count_values(events, "failure_type")
    event_type_counts = count_values(events, "event_type")
    failed_events = [event for event in events if event.get("outcome") == "failure" or event.get("failure_type")]
    feedback_events = [event for event in events if event.get("user_feedback")]

    lines = [
        "# Skill Watcher Report",
        "",
        f"- Log file: `{log_file}`",
        f"- Skill filter: `{skill or 'all'}`",
        f"- Since: `{since_raw or 'all'}`",
        f"- Event count: {len(events)}",
        "",
        "## Event Types",
        *render_counter(event_type_counts),
        "",
        "## Outcome Distribution",
        *render_counter(outcome_counts),
        "",
        "## Failure Summary",
        *render_counter(failure_counts),
        "",
        "## Failure Notes",
        *render_samples(failed_events, "notes"),
        "",
        "## User Feedback",
        *render_samples(feedback_events, "user_feedback"),
        "",
    ]
    return "\n".join(lines)


def default_report_path(state_dir: Path, skill: str | None) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = skill or "all"
    safe_name = "".join(char if char.isalnum() or char in "-_" else "-" for char in name).strip("-") or "all"
    return state_dir / "reports" / f"{timestamp}-{safe_name}-report.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize Skill Watcher JSONL logs.")
    parser.add_argument("--skill", help="Filter by skill_name.")
    parser.add_argument("--since", help="Filter by relative time such as 1d or ISO timestamp.")
    parser.add_argument("--state-dir", help="Runtime state directory. Defaults to ~/.codex/skill-watcher.")
    parser.add_argument("--log-file", help="Explicit JSONL log path. Overrides --state-dir logs/events.jsonl.")
    parser.add_argument("--output", help="Write Markdown report to this path.")
    parser.add_argument("--write-report", action="store_true", help="Also write a timestamped report under state reports/.")
    args = parser.parse_args()

    state_dir = state_dir_from_env_or_arg(args.state_dir)
    log_file = Path(args.log_file).expanduser() if args.log_file else state_dir / "logs" / "events.jsonl"
    since = parse_since(args.since)
    events = filter_events(read_events(log_file), skill=args.skill, since=since)
    report = build_report(events, skill=args.skill, since_raw=args.since, log_file=log_file)

    output_path: Path | None = None
    if args.output:
        output_path = Path(args.output).expanduser()
    elif args.write_report:
        output_path = default_report_path(state_dir, args.skill)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report + "\n", encoding="utf-8")
        print(f"wrote report to {output_path}", file=sys.stderr)

    print(report)


if __name__ == "__main__":
    main()
