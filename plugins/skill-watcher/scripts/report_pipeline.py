#!/usr/bin/env python3
"""Shared Skill Watcher report pipeline."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from runtime_paths import report_state_path, reports_dir, safe_slug, utc_now


DEFAULT_OVERLAP_MINUTES = 5


@dataclass(frozen=True)
class ReportQuery:
    state_dir: Path
    log_file: Path
    skill: str | None = None
    since_raw: str | None = None
    incremental: bool = False
    overlap_minutes: int = DEFAULT_OVERLAP_MINUTES
    display_since_raw: bool = False


@dataclass(frozen=True)
class ReportOutputPolicy:
    output: Path | None = None
    write_output: bool = False


@dataclass(frozen=True)
class ReportResult:
    report: str
    output: Path | None
    state_path: Path | None
    window_since: datetime | None
    window_until: datetime
    events: list[dict[str, Any]]
    outcome_counts: Counter[str]

    @property
    def event_count(self) -> int:
        return len(self.events)


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


def format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_event_line(log_file: Path, line: str, *, line_number: int | None = None) -> dict[str, Any]:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError as exc:
        location = f" at line {line_number}" if line_number is not None else ""
        raise SystemExit(
            f"invalid JSONL in {log_file}{location}: "
            f"line {exc.lineno}, column {exc.colno}"
        ) from exc
    if not isinstance(payload, dict):
        location = f" at line {line_number}" if line_number is not None else ""
        raise SystemExit(f"invalid JSONL in {log_file}{location}: event must be an object")
    return payload


def read_events(log_file: Path) -> list[dict[str, Any]]:
    if not log_file.exists():
        return []
    events: list[dict[str, Any]] = []
    try:
        with log_file.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                events.append(parse_event_line(log_file, line, line_number=line_number))
    except OSError as exc:
        raise SystemExit(f"failed to read log file {log_file}: {exc}") from exc
    return events


def read_events_since(log_file: Path, since: datetime | None, *, block_size: int = 65536) -> list[dict[str, Any]]:
    if since is None:
        return read_events(log_file)
    if not log_file.exists():
        return []

    events: list[dict[str, Any]] = []
    carry = b""
    try:
        with log_file.open("rb") as handle:
            position = handle.seek(0, os.SEEK_END)
            while position > 0:
                size = min(block_size, position)
                position -= size
                handle.seek(position)
                data = handle.read(size)
                lines = (data + carry).splitlines()
                if position > 0:
                    carry = lines[0] if lines else b""
                    complete_lines = lines[1:]
                else:
                    carry = b""
                    complete_lines = lines

                should_stop = False
                for raw_line in reversed(complete_lines):
                    if not raw_line.strip():
                        continue
                    line = raw_line.decode("utf-8", errors="replace")
                    event = parse_event_line(log_file, line)
                    timestamp = parse_timestamp(str(event.get("timestamp", "")))
                    if timestamp is not None and timestamp < since:
                        should_stop = True
                        break
                    events.append(event)
                if should_stop:
                    break
    except OSError as exc:
        raise SystemExit(f"failed to read log file {log_file}: {exc}") from exc
    return list(reversed(events))


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


def count_codex_values(events: list[dict[str, Any]], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for event in events:
        codex = event.get("codex")
        if not isinstance(codex, dict):
            continue
        value = codex.get(key)
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


def render_skill_context_samples(events: list[dict[str, Any]], *, limit: int = 5) -> list[str]:
    samples: list[str] = []
    for event in events:
        codex = event.get("codex")
        if not isinstance(codex, dict):
            continue
        contexts = []
        if isinstance(codex.get("user_skill_context"), dict):
            contexts.append(codex["user_skill_context"])
        turn_summary = codex.get("turn_summary")
        if isinstance(turn_summary, dict) and isinstance(turn_summary.get("user_skill_context"), dict):
            contexts.append(turn_summary["user_skill_context"])
        for context in contexts:
            summary = context.get("summary")
            if isinstance(summary, str) and summary.strip():
                samples.append(f"- {summary.strip()}")
                break
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
    attribution_counts = count_codex_values(events, "skill_attribution")
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
        "## Skill Attribution",
        *render_counter(attribution_counts),
        "",
        "## Failure Notes",
        *render_samples(failed_events, "notes"),
        "",
        "## User Feedback",
        *render_samples(feedback_events, "user_feedback"),
        "",
        "## User Skill Context",
        *render_skill_context_samples(events),
        "",
    ]
    return "\n".join(lines)


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
    return safe_slug(skill or "all", fallback="all")


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
    return reports_dir(state_dir) / f"{timestamp}-{safe_slug(skill or 'all', fallback='all')}-report.md"


def report_since_display(query: ReportQuery, since: datetime | None) -> str | None:
    if query.display_since_raw:
        return query.since_raw
    if since is not None:
        return format_timestamp(since)
    return query.since_raw


def write_report(output: Path, report: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        output.write_text(report + "\n", encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to write report {output}: {exc}") from exc


def select_report_events(
    query: ReportQuery,
    *,
    since: datetime | None,
    until: datetime,
    last_until: datetime | None,
    seen_hashes: set[str],
) -> list[dict[str, Any]]:
    raw_events = filter_events(read_events_since(query.log_file, since), skill=query.skill, since=since)
    events: list[dict[str, Any]] = []
    for event in raw_events:
        timestamp = parse_timestamp(str(event.get("timestamp", "")))
        if timestamp is None or timestamp > until:
            continue
        if last_until is not None and timestamp <= last_until and event_hash(event) in seen_hashes:
            continue
        events.append(event)
    return events


def generate_report(query: ReportQuery, output_policy: ReportOutputPolicy) -> ReportResult:
    fallback_since = parse_since(query.since_raw)
    state = load_report_state(query.state_dir) if query.incremental else None
    key = report_state_key(query.skill)
    last_until = state_since(state, key) if state is not None else None
    seen_hashes = recent_event_hashes(state, key) if state is not None else set()
    if last_until is not None:
        since = last_until - timedelta(minutes=max(query.overlap_minutes, 0))
    else:
        since = fallback_since
    until = utc_now()
    events = select_report_events(
        query,
        since=since,
        until=until,
        last_until=last_until,
        seen_hashes=seen_hashes,
    )
    report = build_report(
        events,
        skill=query.skill,
        since_raw=report_since_display(query, since),
        log_file=query.log_file,
    )

    output = output_policy.output
    if output is None and output_policy.write_output:
        output = default_report_path(query.state_dir, query.skill)
    if output is not None:
        write_report(output, report)

    state_path: Path | None = None
    if state is not None:
        if output is None:
            raise SystemExit("incremental reports require an output path")
        update_report_state(
            state,
            key=key,
            since=since,
            until=until,
            event_count=len(events),
            output=output,
            recent_hashes=merge_recent_hashes(seen_hashes, events),
        )
        save_report_state(query.state_dir, state)
        state_path = report_state_path(query.state_dir)

    return ReportResult(
        report=report,
        output=output,
        state_path=state_path,
        window_since=since,
        window_until=until,
        events=events,
        outcome_counts=outcome_counts(events),
    )
