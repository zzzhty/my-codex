#!/usr/bin/env python3
"""Generate a report-only DocWatcher audit summary for configured repos."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path
from typing import Any

from audit_repo import AuditFailure, audit_repository, expand_path, render_report, resolve_state_dir, safe_slug
from commit_counter import load_config, load_state, mark_current, repo_status, state_path

DEFAULT_CONFIG = Path("config/repos.json")


def default_report_path(state_dir: Path) -> Path:
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    return state_dir / "reports" / f"{timestamp}-all-daily-audit.md"


def write_report(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(report, encoding="utf-8")
    except OSError as exc:
        raise AuditFailure(f"failed to write daily report {path}: {exc}") from exc


def audit_repo_from_config(repo_config: dict[str, Any]) -> dict[str, Any]:
    path_raw = repo_config.get("path")
    if not path_raw:
        raise AuditFailure(f"configured repo is missing required path: {repo_config}")
    path = expand_path(str(path_raw))
    name = str(repo_config.get("name") or path.name)
    return audit_repository(
        repo=path,
        name=name,
        docs=list(repo_config.get("docs") or []),
        source_of_truth=list(repo_config.get("source_of_truth") or []),
        watch_terms=list(repo_config.get("watch_terms") or []),
        recent_limit=int(repo_config.get("recent_limit") or 5),
        since_ref=repo_config.get("since_ref"),
    )


def render_daily_report(
    *,
    generated_at: str,
    config_path: Path,
    reports: list[tuple[str, str]],
    skipped: list[str],
    failures: list[str],
) -> str:
    lines = [
        "# DocWatcher Daily Audit",
        "",
        f"- Generated: {generated_at}",
        f"- Config: `{config_path}`",
        f"- Audited repos: {len(reports)}",
        f"- Skipped repos: {len(skipped)}",
        f"- Failed repos: {len(failures)}",
        "",
    ]
    if skipped:
        lines.extend(["## Skipped", ""])
        lines.extend(f"- {item}" for item in skipped)
        lines.append("")
    if failures:
        lines.extend(["## Failures", ""])
        lines.extend(f"- {item}" for item in failures)
        lines.append("")
    for name, report in reports:
        lines.extend([f"## Repo: {name}", ""])
        body = report.strip().splitlines()
        if body and body[0].startswith("# "):
            body = body[1:]
        lines.extend(body)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a report-only DocWatcher daily audit under state reports/.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Repo config JSON path.")
    parser.add_argument("--state-dir", help="Runtime state directory. Defaults to $CODEX_HOME/doc-watcher.")
    parser.add_argument(
        "--mode",
        choices=("daily", "commit-dependent"),
        default="daily",
        help="daily audits all configured repos; commit-dependent audits only repos whose threshold is due.",
    )
    parser.add_argument("--mark-audited", action="store_true", help="After successful audits, mark audited repos at current HEAD.")
    parser.add_argument("--output", help="Explicit report output path.")
    parser.add_argument("--print-report", action="store_true", help="Also print the full report to stdout.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    config_path = expand_path(args.config)
    config = load_config(config_path)
    state_dir = resolve_state_dir(args.state_dir)
    state = load_state(state_dir)
    audited_statuses: list[dict[str, Any]] = []
    reports: list[tuple[str, str]] = []
    skipped: list[str] = []
    failures: list[str] = []

    for repo_config in config["repos"]:
        name = str(repo_config.get("name") or Path(str(repo_config.get("path", "repo"))).name)
        try:
            status = repo_status(repo_config, state)
            if args.mode == "commit-dependent" and not status["due"]:
                skipped.append(
                    f"{name}: commits_since_audit={status['commits_since_audit']} "
                    f"threshold={status['commit_threshold']}"
                )
                continue
            result = audit_repo_from_config(repo_config)
            reports.append((name, render_report(result)))
            audited_statuses.append(status)
        except AuditFailure as exc:
            failures.append(f"{name}: {exc}")

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    report = render_daily_report(
        generated_at=generated_at,
        config_path=config_path,
        reports=reports,
        skipped=skipped,
        failures=failures,
    )
    output = expand_path(args.output) if args.output else default_report_path(state_dir)
    write_report(output, report)
    print(f"report: {output}")
    print(f"audited: {len(reports)}")
    print(f"skipped: {len(skipped)}")
    print(f"failures: {len(failures)}")

    if args.mark_audited and audited_statuses and not failures:
        mark_current(state_dir, state, audited_statuses)
        print(f"updated state: {state_path(state_dir)}")
    elif args.mark_audited and failures:
        print("state not updated because at least one audit failed")

    if args.print_report:
        print()
        print(report, end="")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
