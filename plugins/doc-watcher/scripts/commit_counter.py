#!/usr/bin/env python3
"""Report commit-threshold trigger status for configured DocWatcher repos."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from audit_repo import AuditFailure, expand_path, require_git_repo, resolve_state_dir, run_git

DEFAULT_CONFIG = Path("config/repos.json")
CONFIG_HASH_KEYS = (
    "path",
    "docs",
    "source_of_truth",
    "watch_terms",
    "recent_limit",
    "since_ref",
    "commit_threshold",
)


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AuditFailure(f"config file does not exist: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AuditFailure(f"invalid JSON config {path}: line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("repos"), list):
        raise AuditFailure(f"config {path} must contain a top-level repos array")
    config_dir = path.parent.resolve()
    for repo in data["repos"]:
        if not isinstance(repo, dict):
            raise AuditFailure(f"config {path} repos entries must be objects")
        raw_path = repo.get("path")
        if isinstance(raw_path, str):
            repo_path = expand_path(raw_path)
            if not repo_path.is_absolute():
                repo_path = (config_dir / repo_path).resolve()
            repo["path"] = str(repo_path)
    return data


def state_path(state_dir: Path) -> Path:
    return state_dir / "repo-state.json"


def normalized_repo_config(repo_config: dict[str, Any]) -> dict[str, Any]:
    return {key: repo_config.get(key) for key in CONFIG_HASH_KEYS if key in repo_config}


def repo_config_hash(repo_config: dict[str, Any]) -> str:
    payload = json.dumps(normalized_repo_config(repo_config), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_state(state_dir: Path) -> dict[str, Any]:
    path = state_path(state_dir)
    if not path.exists():
        return {"repos": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AuditFailure(f"invalid state JSON {path}: line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(data, dict):
        raise AuditFailure(f"state file must contain an object: {path}")
    data.setdefault("repos", {})
    return data


def save_state(state_dir: Path, state: dict[str, Any]) -> None:
    path = state_path(state_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        raise AuditFailure(f"failed to write state file {path}: {exc}") from exc


def count_since(repo: Path, last_revision: str | None) -> int:
    if not last_revision:
        output = run_git(repo, ["rev-list", "--count", "HEAD"])
        return int(output or "0")
    output = run_git(repo, ["rev-list", "--count", f"{last_revision}..HEAD"], allow_failure=True)
    if output.strip().isdigit():
        return int(output)
    total = run_git(repo, ["rev-list", "--count", "HEAD"])
    return int(total or "0")


def repo_status(repo_config: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    name = str(repo_config.get("name") or Path(str(repo_config.get("path", ""))).name)
    path_raw = repo_config.get("path")
    if not path_raw:
        raise AuditFailure(f"repo {name} is missing required path")
    repo = require_git_repo(expand_path(str(path_raw)))
    head = run_git(repo, ["rev-parse", "HEAD"])
    threshold = int(repo_config.get("commit_threshold") or 0)
    repo_state = state.get("repos", {}).get(name, {})
    last = repo_state.get("last_audited_revision")
    current_config_hash = repo_config_hash(repo_config)
    last_config_hash = repo_state.get("config_hash")
    config_changed = last_config_hash != current_config_hash
    count = count_since(repo, last)
    due = threshold <= 0 or count >= threshold or not last or config_changed
    return {
        "name": name,
        "path": str(repo),
        "head": head,
        "last_audited_revision": last,
        "config_hash": current_config_hash,
        "last_config_hash": last_config_hash,
        "config_changed": config_changed,
        "commit_threshold": threshold,
        "commits_since_audit": count,
        "due": due,
    }


def mark_current(
    state_dir: Path,
    state: dict[str, Any],
    statuses: list[dict[str, Any]],
    findings_by_name: dict[str, list[dict[str, str]]] | None = None,
) -> None:
    repos = state.setdefault("repos", {})
    timestamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    for item in statuses:
        previous = repos.get(item["name"], {})
        repos[item["name"]] = {
            "path": item["path"],
            "last_audited_revision": item["head"],
            "config_hash": item.get("config_hash"),
            "updated_at": timestamp,
        }
        if findings_by_name is not None and item["name"] in findings_by_name:
            repos[item["name"]]["findings"] = findings_by_name[item["name"]]
        elif isinstance(previous, dict) and "findings" in previous:
            repos[item["name"]]["findings"] = previous["findings"]
    save_state(state_dir, state)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show commit-threshold trigger status for configured repos.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Repo config JSON path.")
    parser.add_argument("--state-dir", help="Runtime state directory. Defaults to $CODEX_HOME/doc-watcher.")
    parser.add_argument("--mark-current", action="store_true", help="Mark current HEAD as audited for all configured repos.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    config = load_config(expand_path(args.config))
    state_dir = resolve_state_dir(args.state_dir)
    state = load_state(state_dir)
    statuses = [repo_status(repo, state) for repo in config["repos"]]

    print("# DocWatcher Commit Counter")
    print()
    for item in statuses:
        due = "due" if item["due"] else "skip"
        print(
            f"- {item['name']}: {due}; commits_since_audit={item['commits_since_audit']}; "
            f"threshold={item['commit_threshold']}; config_changed={item['config_changed']}; "
            f"head={item['head'][:12]}"
        )
    if args.mark_current:
        mark_current(state_dir, state, statuses)
        print()
        print(f"updated state: {state_path(state_dir)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditFailure as exc:
        raise SystemExit(str(exc)) from exc
