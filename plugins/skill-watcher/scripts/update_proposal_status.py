#!/usr/bin/env python3
"""Update proposal frontmatter status and record rejected proposals."""

from __future__ import annotations

import argparse

from proposal_artifact import ALLOWED_STATUSES, update_status, utc_now
from runtime_paths import CODEX_HOME, DEFAULT_STATE_DIR, expand_path, state_dir_from_env_or_arg


def main() -> None:
    parser = argparse.ArgumentParser(description="Update a Skill Watcher proposal status.")
    parser.add_argument("--proposal", required=True, help="Proposal Markdown path.")
    parser.add_argument("--status", required=True, choices=sorted(ALLOWED_STATUSES))
    parser.add_argument("--reason", default="", help="Short reason to record in frontmatter and rejected buffer.")
    parser.add_argument("--state-dir", help="Runtime state directory. Defaults to $CODEX_HOME/skill-watcher.")
    args = parser.parse_args()

    proposal = expand_path(args.proposal).resolve()
    state_dir = state_dir_from_env_or_arg(args.state_dir)
    previous_status, rejected_path = update_status(proposal, args.status, state_dir=state_dir, reason=args.reason)
    print(f"updated {proposal}: {previous_status or 'unset'} -> {args.status}")
    if rejected_path is not None:
        print(f"rejected buffer: {rejected_path}")


__all__ = [
    "ALLOWED_STATUSES",
    "CODEX_HOME",
    "DEFAULT_STATE_DIR",
    "update_status",
    "utc_now",
]


if __name__ == "__main__":
    main()
