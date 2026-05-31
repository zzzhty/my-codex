#!/usr/bin/env python3
"""Remove only Skill Watcher handlers from a Codex hooks.json file."""

from __future__ import annotations

import argparse

from codex_hook_config import (
    DEFAULT_STATE_DIR,
    DEFAULT_TARGET,
    backup_existing_file,
    expand_path,
    load_config,
    remove_skill_watcher_hooks,
    render_diff,
    write_config,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Uninstall Skill Watcher handlers from $CODEX_HOME/hooks.json.")
    parser.add_argument("--target", default=str(DEFAULT_TARGET), help="Hook config path. Defaults to $CODEX_HOME/hooks.json.")
    parser.add_argument("--dry-run", action="store_true", help="Show the diff without writing.")
    parser.add_argument("--apply", action="store_true", help="Write the hook config.")
    args = parser.parse_args()

    if args.dry_run and args.apply:
        raise SystemExit("choose only one of --dry-run or --apply")

    target = expand_path(args.target)
    before = load_config(target)
    after, removed = remove_skill_watcher_hooks(before)

    print(f"target: {target}")
    print(f"Skill Watcher handlers matched: {removed}")
    print(render_diff(before if target.exists() else None, after, target), end="")

    if not args.apply:
        print("dry-run only; no changes written")
        return
    if not target.exists():
        print(f"hook config does not exist: {target}")
        return

    backup_path = backup_existing_file(target, state_dir=DEFAULT_STATE_DIR)
    write_config(target, after)
    if backup_path is not None:
        print(f"backup: {backup_path}")
    print(f"removed Skill Watcher hooks from {target}")


if __name__ == "__main__":
    main()
