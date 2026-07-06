#!/usr/bin/env python3
"""Unified Watcher CLI for doc and skill runtime domains."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parent
COMMANDS = {
    "skill": {
        "report": SCRIPT_ROOT / "skill" / "generate_report.py",
        "summarize": SCRIPT_ROOT / "skill" / "summarize_logs.py",
        "propose": SCRIPT_ROOT / "skill" / "propose_skill_patch.py",
        "validate": SCRIPT_ROOT / "skill" / "validate_candidate.py",
        "collect-event": SCRIPT_ROOT / "skill" / "collect_event.py",
        "redact-event": SCRIPT_ROOT / "skill" / "redact_event.py",
        "install-hook": SCRIPT_ROOT / "skill" / "install_codex_hook.py",
        "uninstall-hook": SCRIPT_ROOT / "skill" / "uninstall_codex_hook.py",
        "doctor": SCRIPT_ROOT / "skill" / "doctor.py",
        "reset-schema": SCRIPT_ROOT / "skill" / "migrate_skill_watcher_schema.py",
    },
    "doc": {
        "audit": SCRIPT_ROOT / "doc" / "audit_repo.py",
        "commit-counter": SCRIPT_ROOT / "doc" / "commit_counter.py",
        "report": SCRIPT_ROOT / "doc" / "generate_report.py",
        "doctor": SCRIPT_ROOT / "doc" / "doctor.py",
    },
}


@dataclass(frozen=True)
class RuntimeDomain:
    name: str
    legacy_dir_name: str
    target_dir_name: str


RUNTIME_DOMAINS = {
    "skill": RuntimeDomain("skill", "skill-watcher", "skill"),
    "doc": RuntimeDomain("doc", "doc-watcher", "doc"),
}


def expand_path(raw: str | Path) -> Path:
    return Path(os.path.expandvars(str(raw))).expanduser()


def default_codex_home() -> Path:
    return expand_path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))


def print_top_level_help() -> None:
    print(
        "\n".join(
            [
                "usage: watcher <domain> <command> [args...]",
                "       watcher migrate-state [--domain all|skill|doc] [--dry-run|--apply] [--codex-home PATH]",
                "",
                "domains:",
                "  skill          skill usage logs, reports, hooks, and proposals",
                "  doc            documentation audit reports and commit counters",
                "",
                "commands:",
                "  migrate-state  move legacy runtime roots into $CODEX_HOME/watcher/",
                "",
                "run `watcher <domain> --help` to list domain commands.",
            ]
        )
    )


def print_domain_help(domain: str) -> None:
    commands = COMMANDS[domain]
    print(f"usage: watcher {domain} <command> [args...]")
    print()
    print("commands:")
    for name in sorted(commands):
        print(f"  {name}")


def run_script(script: Path, args: list[str]) -> int:
    if not script.is_file():
        print(f"watcher: command target missing: {script}", file=sys.stderr)
        return 1
    result = subprocess.run([sys.executable, str(script), *args])
    return int(result.returncode)


def selected_runtime_domains(raw_domain: str) -> list[RuntimeDomain]:
    if raw_domain == "all":
        return [RUNTIME_DOMAINS["skill"], RUNTIME_DOMAINS["doc"]]
    return [RUNTIME_DOMAINS[raw_domain]]


def source_target_for(codex_home: Path, domain: RuntimeDomain) -> tuple[Path, Path]:
    return codex_home / domain.legacy_dir_name, codex_home / "watcher" / domain.target_dir_name


def run_migrate_state(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="watcher migrate-state",
        description="Move legacy Watcher runtime roots into $CODEX_HOME/watcher/.",
    )
    parser.add_argument("--domain", choices=("all", "skill", "doc"), default="all")
    parser.add_argument("--codex-home", default=str(default_codex_home()))
    parser.add_argument("--dry-run", action="store_true", help="Print planned moves without writing. This is the default.")
    parser.add_argument("--apply", action="store_true", help="Move runtime directories.")
    args = parser.parse_args(argv)

    if args.dry_run and args.apply:
        raise SystemExit("choose only one of --dry-run or --apply")

    dry_run = not args.apply
    codex_home = expand_path(args.codex_home)
    domains = selected_runtime_domains(args.domain)
    planned: list[tuple[RuntimeDomain, Path, Path]] = []
    errors: list[str] = []

    for domain in domains:
        source, target = source_target_for(codex_home, domain)
        if not source.exists():
            if target.exists():
                print(f"ok: {domain.name} target exists and legacy source is absent: {target}")
            else:
                print(f"skip: {domain.name} legacy source missing: {source}")
            continue
        if target.exists():
            errors.append(f"{domain.name}: target already exists; refusing to merge {source} into {target}")
            continue
        planned.append((domain, source, target))

    if errors:
        for error in errors:
            print(f"fail: {error}", file=sys.stderr)
        return 1

    if not planned:
        print("no runtime directories to migrate")
        return 0

    for domain, source, target in planned:
        print(f"{'would move' if dry_run else 'move'}: {domain.name}: {source} -> {target}")

    if dry_run:
        print("dry-run only; no changes written")
        return 0

    for _domain, source, target in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(source), str(target))
        except OSError as exc:
            print(f"failed to move {source} to {target}: {exc}", file=sys.stderr)
            return 1
    print("runtime migration complete")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print_top_level_help()
        return 0

    command = args[0]
    if command == "migrate-state":
        return run_migrate_state(args[1:])

    if command not in COMMANDS:
        print(f"watcher: unknown domain or command: {command}", file=sys.stderr)
        print_top_level_help()
        return 2

    domain = command
    if len(args) == 1 or args[1] in {"-h", "--help"}:
        print_domain_help(domain)
        return 0

    domain_command = args[1]
    script = COMMANDS[domain].get(domain_command)
    if script is None:
        print(f"watcher: unknown {domain} command: {domain_command}", file=sys.stderr)
        print_domain_help(domain)
        return 2
    return run_script(script, args[2:])


if __name__ == "__main__":
    raise SystemExit(main())
