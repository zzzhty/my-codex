#!/usr/bin/env python3
"""Generate a report-only Skill Watcher usage report."""

from __future__ import annotations

import argparse
import sys

from report_pipeline import (
    DEFAULT_OVERLAP_MINUTES,
    ReportOutputPolicy,
    ReportQuery,
    default_report_path,
    event_hash,
    format_timestamp,
    generate_report as run_report,
    load_report_state,
    merge_recent_hashes,
    outcome_counts,
    recent_event_hashes,
    report_state_entry,
    report_state_key,
    save_report_state,
    state_since,
    update_report_state,
    utc_now,
)
from runtime_paths import (
    CODEX_HOME,
    DEFAULT_STATE_DIR,
    expand_path,
    log_file_path,
    report_state_path,
    state_dir_from_env_or_arg,
)


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
    log_file = log_file_path(state_dir, args.log_file)
    result = run_report(
        ReportQuery(
            state_dir=state_dir,
            log_file=log_file,
            skill=args.skill,
            since_raw=args.since,
            incremental=args.incremental,
            overlap_minutes=args.overlap_minutes,
        ),
        ReportOutputPolicy(
            output=expand_path(args.output) if args.output else None,
            write_output=True,
        ),
    )

    print(f"report: {result.output}")
    print(f"window_since: {format_timestamp(result.window_since) if result.window_since is not None else 'all'}")
    print(f"window_until: {format_timestamp(result.window_until)}")
    print(f"events: {result.event_count}")
    print(
        "outcomes: " + ", ".join(f"{name}={count}" for name, count in sorted(result.outcome_counts.items()))
        if result.outcome_counts
        else "outcomes: none"
    )
    if result.state_path is not None:
        print(f"state: {result.state_path}")

    if args.print_report:
        print("", file=sys.stdout)
        print(result.report)


__all__ = [
    "CODEX_HOME",
    "DEFAULT_OVERLAP_MINUTES",
    "DEFAULT_STATE_DIR",
    "ReportOutputPolicy",
    "ReportQuery",
    "default_report_path",
    "event_hash",
    "format_timestamp",
    "load_report_state",
    "merge_recent_hashes",
    "outcome_counts",
    "recent_event_hashes",
    "report_state_entry",
    "report_state_key",
    "report_state_path",
    "save_report_state",
    "state_since",
    "update_report_state",
    "utc_now",
]


if __name__ == "__main__":
    main()
