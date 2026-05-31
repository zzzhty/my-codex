#!/usr/bin/env python3
"""Update proposal frontmatter status and record rejected proposals."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path.home() / ".codex" / "skill-watcher"
ALLOWED_STATUSES = {"draft", "needs-validation", "accepted", "rejected"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def state_dir_from_env_or_arg(raw_state_dir: str | None) -> Path:
    return Path(raw_state_dir or os.environ.get("SKILL_WATCHER_STATE_DIR") or DEFAULT_STATE_DIR).expanduser()


def load_yaml_module():
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "PyYAML is required for proposal status updates. "
            "Run `python3 /Users/max/Projects/my-codex/scripts/bootstrap_tooling_env.py`."
        ) from exc
    return yaml


def split_frontmatter(contents: str, path: Path) -> tuple[str, str]:
    if not contents.startswith("---\n"):
        raise SystemExit(f"{path} must start with YAML frontmatter")
    end = contents.find("\n---", 4)
    if end == -1:
        raise SystemExit(f"{path} frontmatter is not closed")
    return contents[4:end], contents[end + 4 :]


def load_proposal(path: Path) -> tuple[dict[str, Any], str]:
    try:
        contents = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to read proposal {path}: {exc}") from exc
    frontmatter_text, body = split_frontmatter(contents, path)
    yaml = load_yaml_module()
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        raise SystemExit(f"{path} frontmatter is invalid YAML: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise SystemExit(f"{path} frontmatter must be a YAML object")
    return frontmatter, body


def write_proposal(path: Path, frontmatter: dict[str, Any], body: str) -> None:
    yaml = load_yaml_module()
    rendered = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True) + "---" + body
    try:
        path.write_text(rendered, encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to write proposal {path}: {exc}") from exc


def record_rejected(path: Path, frontmatter: dict[str, Any], state_dir: Path, previous_status: str, reason: str) -> Path:
    rejected_dir = state_dir / "rejected"
    rejected_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    proposal_id = str(frontmatter.get("proposal_id") or path.stem)
    safe_id = "".join(char if char.isalnum() or char in "-_" else "-" for char in proposal_id).strip("-") or "proposal"
    output = rejected_dir / f"{timestamp}-{safe_id}.json"
    payload = {
        "timestamp": utc_now(),
        "proposal": str(path),
        "proposal_id": proposal_id,
        "skill_name": frontmatter.get("skill_name"),
        "previous_status": previous_status,
        "status": "rejected",
        "reason": reason,
    }
    try:
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to write rejected proposal buffer {output}: {exc}") from exc
    return output


def update_status(path: Path, status: str, *, state_dir: Path, reason: str = "") -> tuple[str, Path | None]:
    if status not in ALLOWED_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_STATUSES))
        raise SystemExit(f"invalid status {status!r}; expected one of: {allowed}")
    frontmatter, body = load_proposal(path)
    previous_status = str(frontmatter.get("status") or "")
    frontmatter["status"] = status
    frontmatter["status_updated_at"] = utc_now()
    if reason:
        frontmatter["status_reason"] = reason
    rejected_path = None
    if status == "rejected":
        rejected_path = record_rejected(path, frontmatter, state_dir, previous_status, reason)
    write_proposal(path, frontmatter, body)
    return previous_status, rejected_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Update a Skill Watcher proposal status.")
    parser.add_argument("--proposal", required=True, help="Proposal Markdown path.")
    parser.add_argument("--status", required=True, choices=sorted(ALLOWED_STATUSES))
    parser.add_argument("--reason", default="", help="Short reason to record in frontmatter and rejected buffer.")
    parser.add_argument("--state-dir", help="Runtime state directory. Defaults to ~/.codex/skill-watcher.")
    args = parser.parse_args()

    proposal = Path(args.proposal).expanduser().resolve()
    state_dir = state_dir_from_env_or_arg(args.state_dir)
    previous_status, rejected_path = update_status(proposal, args.status, state_dir=state_dir, reason=args.reason)
    print(f"updated {proposal}: {previous_status or 'unset'} -> {args.status}")
    if rejected_path is not None:
        print(f"rejected buffer: {rejected_path}")


if __name__ == "__main__":
    main()
