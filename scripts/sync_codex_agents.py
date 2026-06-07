#!/usr/bin/env python3
"""Sync my-codex custom agents into a Codex agents directory."""

from __future__ import annotations

import argparse
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = REPO_ROOT / "codex-home" / "agents"
DEFAULT_CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
BUILTIN_AGENT_NAMES = {"default", "worker", "explorer"}
MANAGED_MARKER = "Managed by my-codex scripts/sync_codex_agents.py."


@dataclass(frozen=True)
class AgentSource:
    path: Path
    name: str
    text: str


def expand_path(raw: str | Path) -> Path:
    return Path(os.path.expandvars(str(raw))).expanduser()


def load_toml(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f"invalid TOML: {path}: {exc}") from exc
    except OSError as exc:
        raise SystemExit(f"cannot read TOML: {path}: {exc}") from exc


def required_string(data: dict, path: Path, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"{path}: required field `{key}` must be a non-empty string")
    return value


def validate_agent(path: Path, *, allow_write_capable: bool) -> AgentSource:
    text = path.read_text(encoding="utf-8")
    data = load_toml(path)
    name = required_string(data, path, "name")
    required_string(data, path, "description")
    required_string(data, path, "developer_instructions")

    if name in BUILTIN_AGENT_NAMES:
        raise SystemExit(f"{path}: custom agent name must not override built-in agent `{name}`")
    if name != path.stem:
        raise SystemExit(f"{path}: agent name `{name}` must match filename stem `{path.stem}`")
    if not allow_write_capable and data.get("sandbox_mode") != "read-only":
        raise SystemExit(f"{path}: sandbox_mode must be `read-only` unless --allow-write-capable is used")

    return AgentSource(path=path, name=name, text=text)


def load_sources(source_root: Path, *, allow_write_capable: bool) -> list[AgentSource]:
    if not source_root.is_dir():
        raise SystemExit(f"agent source directory does not exist: {source_root}")

    sources = [
        validate_agent(path, allow_write_capable=allow_write_capable)
        for path in sorted(source_root.glob("*.toml"))
    ]
    if not sources:
        raise SystemExit(f"agent source directory contains no TOML files: {source_root}")

    seen: set[str] = set()
    for source in sources:
        if source.name in seen:
            raise SystemExit(f"duplicate agent name: {source.name}")
        seen.add(source.name)
    return sources


def managed_text(source: AgentSource) -> str:
    body = source.text
    if not body.endswith("\n"):
        body += "\n"
    return "\n".join(managed_header(source.path.name)) + "\n\n" + body


def managed_header(source_name: str) -> list[str]:
    return [
        f"# {MANAGED_MARKER}",
        f"# Source: codex-home/agents/{source_name}",
        "# Do not edit this target file directly.",
    ]


def is_managed(path: Path) -> bool:
    try:
        first_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[:3]
    except OSError:
        return False
    if len(first_lines) < 3:
        return False
    return (
        first_lines[0] == managed_header("<source>")[0]
        and first_lines[1].startswith("# Source: codex-home/agents/")
        and first_lines[2] == managed_header("<source>")[2]
    )


def target_root_from_args(args: argparse.Namespace) -> Path:
    if args.target_root:
        return expand_path(args.target_root)
    return expand_path(args.codex_home) / "agents"


def print_plan(action: str, path: Path) -> None:
    print(f"{action}: {path}")


def sync_sources(
    sources: list[AgentSource],
    *,
    target_root: Path,
    dry_run: bool,
    check: bool,
    prune: bool,
    force: bool,
) -> int:
    expected_names = {source.path.name for source in sources}
    failures = 0

    if check:
        for source in sources:
            target = target_root / source.path.name
            expected = managed_text(source)
            if not target.exists():
                print_plan("missing", target)
                failures += 1
                continue
            actual = target.read_text(encoding="utf-8", errors="replace")
            if actual != expected:
                if not is_managed(target):
                    print_plan("unmanaged-drift", target)
                else:
                    print_plan("drift", target)
                failures += 1
            else:
                print_plan("ok", target)

        if prune and target_root.exists():
            for target in sorted(target_root.glob("*.toml")):
                if target.name not in expected_names and is_managed(target):
                    print_plan("extra-managed", target)
                    failures += 1

        if failures:
            print(f"agent sync check failed with {failures} issue(s)")
            return 1
        print("agent sync check OK")
        return 0

    if not dry_run:
        target_root.mkdir(parents=True, exist_ok=True)

    for source in sources:
        target = target_root / source.path.name
        expected = managed_text(source)
        if target.exists():
            actual = target.read_text(encoding="utf-8", errors="replace")
            if actual == expected:
                print_plan("up-to-date", target)
                continue
            if not is_managed(target) and not force:
                raise SystemExit(
                    f"refusing to overwrite unmanaged target file: {target}; "
                    "use --force only after reviewing the file"
                )
            print_plan("would update" if dry_run else "update", target)
        else:
            print_plan("would write" if dry_run else "write", target)

        if not dry_run:
            target.write_text(expected, encoding="utf-8")

    if prune and target_root.exists():
        for target in sorted(target_root.glob("*.toml")):
            if target.name in expected_names:
                continue
            if not is_managed(target):
                print_plan("keep unmanaged", target)
                continue
            print_plan("would prune" if dry_run else "prune", target)
            if not dry_run:
                target.unlink()

    if dry_run:
        print("dry-run only; no agent files written")
    else:
        print("agent sync complete")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync repo-managed Codex custom agents.")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT), help="Source directory containing agent TOML files.")
    parser.add_argument("--codex-home", default=str(DEFAULT_CODEX_HOME), help="Codex home directory; target is <codex-home>/agents.")
    parser.add_argument("--target-root", help="Override the target agents directory.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned writes without modifying the target.")
    parser.add_argument("--check", action="store_true", help="Fail if target managed files are missing or out of sync.")
    parser.add_argument("--prune", action="store_true", help="Remove managed target TOML files that no longer have source files.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting unmanaged target files with matching names.")
    parser.add_argument(
        "--allow-write-capable",
        action="store_true",
        help="Allow source agents whose sandbox_mode is not read-only.",
    )
    args = parser.parse_args()

    source_root = expand_path(args.source_root)
    target_root = target_root_from_args(args)
    sources = load_sources(source_root, allow_write_capable=args.allow_write_capable)
    return sync_sources(
        sources,
        target_root=target_root,
        dry_run=args.dry_run,
        check=args.check,
        prune=args.prune,
        force=args.force,
    )


if __name__ == "__main__":
    raise SystemExit(main())
