#!/usr/bin/env python3
"""Generate a report-only Skill Watcher usage report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from summarize_logs import build_report, expand_path, filter_events, parse_since, parse_timestamp, read_events_since


CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
DEFAULT_STATE_DIR = CODEX_HOME / "skill-watcher"
DEFAULT_OVERLAP_MINUTES = 5


def state_dir_from_env_or_arg(raw_state_dir: str | None) -> Path:
    return expand_path(raw_state_dir or os.environ.get("SKILL_WATCHER_STATE_DIR") or DEFAULT_STATE_DIR)


def safe_slug(value: str) -> str:
    slug = "".join(char if char.isalnum() or char in "-_" else "-" for char in value).strip("-")
    return slug or "all"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def report_state_path(state_dir: Path) -> Path:
    return state_dir / "report-state.json"


def load_report_state(state_dir: Path) -> dict[str, Any]:
    path = report_state_path(state_dir)
    if not path.exists():
        return {"version": 1, "reports": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid report state JSON {path}: line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"report state must contain an object: {path}")
    data.setdefault("version", 1)
    data.setdefault("reports", {})
    if not isinstance(data["reports"], dict):
        raise SystemExit(f"report state reports must be an object: {path}")
    return data


def save_report_state(state_dir: Path, state: dict[str, Any]) -> None:
    path = report_state_path(state_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to write report state {path}: {exc}") from exc


def report_state_key(skill: str | None) -> str:
    return safe_slug(skill or "all")


def report_state_entry(state: dict[str, Any], key: str) -> dict[str, Any]:
    reports = state.get("reports")
    if not isinstance(reports, dict):
        return {}
    entry = reports.get(key)
    return entry if isinstance(entry, dict) else {}


def state_since(state: dict[str, Any], key: str) -> datetime | None:
    entry = report_state_entry(state, key)
    raw = entry.get("last_successful_report_until")
    return parse_since(raw) if isinstance(raw, str) and raw else None


def event_hash(event: dict[str, Any]) -> str:
    payload = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def recent_event_hashes(state: dict[str, Any], key: str) -> set[str]:
    raw_hashes = report_state_entry(state, key).get("recent_event_hashes")
    if not isinstance(raw_hashes, list):
        return set()
    return {item for item in raw_hashes if isinstance(item, str) and item}


def merge_recent_hashes(existing: set[str], events: list[dict[str, Any]], *, limit: int = 500) -> list[str]:
    hashes = sorted(existing | {event_hash(event) for event in events})
    return hashes[-limit:]


def update_report_state(
    state: dict[str, Any],
    *,
    key: str,
    since: datetime | None,
    until: datetime,
    event_count: int,
    output: Path,
    recent_hashes: list[str],
) -> None:
    reports = state.setdefault("reports", {})
    reports[key] = {
        "last_successful_report_since": format_timestamp(since) if since is not None else None,
        "last_successful_report_until": format_timestamp(until),
        "last_event_count": event_count,
        "last_report_path": str(output),
        "recent_event_hashes": recent_hashes,
        "updated_at": format_timestamp(utc_now()),
    }


def outcome_counts(events: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for event in events:
        outcome = str(event.get("outcome") or "unknown")
        counter[outcome] += 1
    return counter


def default_report_path(state_dir: Path, skill: str | None) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return state_dir / "reports" / f"{timestamp}-{safe_slug(skill or 'all')}-report.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a Skill Watcher usage report under state reports/.")
    parser.add_argument("--skill", help="Filter by skill_name. Defaults to all skills.")
    parser.add_argument("--since", default="1d", help="Evidence window such as 1d, 24h, or ISO timestamp.")
    parser.add_argument("--state-dir", help="Runtime state directory. Defaults to $CODEX_HOME/skill-watcher.")
    parser.add_argument("--log-file", help="Explicit JSONL log path. Overrides --state-dir logs/events.jsonl.")
    parser.add_argument("--output", help="Explicit report output path.")
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Use and update report-state.json; --since is only the first-run fallback window.",
    )
    parser.add_argument(
        "--overlap-minutes",
        type=int,
        default=DEFAULT_OVERLAP_MINUTES,
        help="Incremental safety overlap for late-arriving events. Defaults to 5 minutes.",
    )
    parser.add_argument("--print-report", action="store_true", help="Also print the full report to stdout.")
    args = parser.parse_args()

    state_dir = state_dir_from_env_or_arg(args.state_dir)
    log_file = expand_path(args.log_file) if args.log_file else state_dir / "logs" / "events.jsonl"
    fallback_since = parse_since(args.since)
    state = load_report_state(state_dir) if args.incremental else None
    key = report_state_key(args.skill)
    last_until = state_since(state, key) if state is not None else None
    seen_hashes = recent_event_hashes(state, key) if state is not None else set()
    if last_until is not None:
        since = last_until - timedelta(minutes=max(args.overlap_minutes, 0))
    else:
        since = fallback_since
    until = utc_now()
    raw_events = filter_events(read_events_since(log_file, since), skill=args.skill, since=since)
    events: list[dict[str, Any]] = []
    for event in raw_events:
        timestamp = parse_timestamp(str(event.get("timestamp", "")))
        if timestamp is None or timestamp > until:
            continue
        if last_until is not None and timestamp <= last_until and event_hash(event) in seen_hashes:
            continue
        events.append(event)
    since_raw = format_timestamp(since) if since is not None else args.since
    report = build_report(events, skill=args.skill, since_raw=since_raw, log_file=log_file)

    output = expand_path(args.output) if args.output else default_report_path(state_dir, args.skill)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        output.write_text(report + "\n", encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to write report {output}: {exc}") from exc

    counts = outcome_counts(events)
    print(f"report: {output}")
    print(f"window_since: {format_timestamp(since) if since is not None else 'all'}")
    print(f"window_until: {format_timestamp(until)}")
    print(f"events: {len(events)}")
    print("outcomes: " + ", ".join(f"{name}={count}" for name, count in sorted(counts.items())) if counts else "outcomes: none")
    if state is not None:
        update_report_state(
            state,
            key=key,
            since=since,
            until=until,
            event_count=len(events),
            output=output,
            recent_hashes=merge_recent_hashes(seen_hashes, events),
        )
        save_report_state(state_dir, state)
        print(f"state: {report_state_path(state_dir)}")

    if args.print_report:
        print("", file=sys.stdout)
        print(report)


if __name__ == "__main__":
    main()
