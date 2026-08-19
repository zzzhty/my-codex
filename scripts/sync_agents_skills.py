#!/usr/bin/env python3
"""Expose my-codex plugin skills as user-level agent skills under ~/.agents/skills.

Harnesses that natively scan ``~/.agents/skills`` (for example ZCode) pick the
skills up from there, while Codex keeps serving the same source directories
through the my-codex marketplace. Each skill is exposed as a symlink so the
repository stays the single source of truth.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_FILE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
DEFAULT_TARGET_ROOT = Path.home() / ".agents" / "skills"


@dataclass(frozen=True)
class SkillSource:
    plugin: str
    name: str
    path: Path


@dataclass(frozen=True)
class SkillCatalog:
    sources: list[SkillSource]
    plugins_root: Path


def expand_path(raw: str | Path) -> Path:
    return Path(os.path.expandvars(str(raw))).expanduser()


def load_marketplace_plugins(marketplace_file: Path, *, repo_root: Path) -> list[tuple[str, Path]]:
    if not marketplace_file.is_file():
        raise SystemExit(f"marketplace file does not exist: {marketplace_file}")
    try:
        payload = json.loads(marketplace_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read marketplace file: {marketplace_file}: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("plugins"), list):
        raise SystemExit(f"marketplace file must contain a plugins list: {marketplace_file}")

    plugins: list[tuple[str, Path]] = []
    for record in payload["plugins"]:
        if not isinstance(record, dict):
            raise SystemExit(f"malformed marketplace plugin entry: {record!r}")
        name = record.get("name")
        source = record.get("source")
        if not isinstance(name, str) or not name:
            raise SystemExit(f"marketplace plugin entry without a name: {record!r}")
        if not isinstance(source, dict) or source.get("source") != "local":
            continue
        raw_path = source.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            raise SystemExit(f"local marketplace plugin without a path: {name}")
        plugin_root = expand_path(raw_path)
        if not plugin_root.is_absolute():
            plugin_root = repo_root / plugin_root
        plugin_root = plugin_root.resolve()
        if plugin_root != repo_root and not plugin_root.is_relative_to(repo_root):
            raise SystemExit(f"marketplace plugin path escapes the repository: {name}: {plugin_root}")
        plugins.append((name, plugin_root))
    if not plugins:
        raise SystemExit(f"marketplace file declares no local plugins: {marketplace_file}")
    return plugins


def marketplace_repo_root(marketplace_file: Path) -> Path:
    return marketplace_file.resolve().parents[2]


def load_skill_catalog(marketplace_file: Path = MARKETPLACE_FILE) -> SkillCatalog:
    repo_root = marketplace_repo_root(marketplace_file)
    sources: list[SkillSource] = []
    for plugin_name, plugin_root in load_marketplace_plugins(marketplace_file, repo_root=repo_root):
        skills_root = plugin_root / "skills"
        if not skills_root.is_dir():
            continue
        for skill_dir in sorted(skills_root.iterdir()):
            if not skill_dir.is_dir():
                continue
            if not (skill_dir / "SKILL.md").is_file():
                raise SystemExit(
                    f"malformed plugin skill directory (SKILL.md missing): {skill_dir}"
                )
            sources.append(SkillSource(plugin=plugin_name, name=skill_dir.name, path=skill_dir))

    by_name: dict[str, list[SkillSource]] = {}
    for source in sources:
        by_name.setdefault(source.name, []).append(source)
    collisions = {name: owners for name, owners in by_name.items() if len(owners) > 1}
    if collisions:
        details = "; ".join(
            f"{name}: {', '.join(owner.plugin for owner in owners)}"
            for name, owners in sorted(collisions.items())
        )
        raise SystemExit(f"skill name collisions across plugins: {details}")

    if not sources:
        raise SystemExit("no plugin skills found to expose")
    return SkillCatalog(sources=sources, plugins_root=repo_root / "plugins")


def managed_destination(link: Path, plugins_root: Path) -> Path | None:
    """Return the repository plugins path a managed symlink points at, if any."""

    if not link.is_symlink():
        return None
    destination = link.resolve()
    if destination.is_relative_to(plugins_root):
        return destination
    return None


def print_plan(action: str, target: Path, source: Path | None = None) -> None:
    suffix = f" -> {source}" if source is not None else ""
    print(f"{action}: {target}{suffix}")


def check_layer(
    catalog: SkillCatalog,
    *,
    target_root: Path,
    prune: bool,
) -> int:
    sources = catalog.sources
    expected = {source.name: source for source in sources}
    failures = 0

    for source in sources:
        target = target_root / source.name
        if target.is_symlink():
            destination = managed_destination(target, catalog.plugins_root)
            if destination is None:
                print_plan("unmanaged-link", target)
                failures += 1
            elif destination != source.path:
                if destination.is_dir():
                    print_plan("drift", target, destination)
                else:
                    print_plan("dangling", target, destination)
                failures += 1
            else:
                print_plan("ok", target, destination)
        elif target.exists():
            print_plan("unmanaged-entry", target)
            failures += 1
        else:
            print_plan("missing", target, source.path)
            failures += 1

    if prune and target_root.is_dir():
        for target in sorted(target_root.iterdir()):
            if target.name in expected or not target.is_symlink():
                continue
            destination = managed_destination(target, catalog.plugins_root)
            if destination is not None:
                print_plan("extra-managed", target, destination)
                failures += 1

    if failures:
        print(f"agents skills layer check failed with {failures} issue(s)")
        return 1
    print(f"agents skills layer check OK: {len(sources)} skill(s)")
    return 0


def sync_layer(
    catalog: SkillCatalog,
    *,
    target_root: Path,
    dry_run: bool,
    prune: bool,
    force: bool,
) -> int:
    sources = catalog.sources
    expected = {source.name: source for source in sources}

    if not dry_run:
        target_root.mkdir(parents=True, exist_ok=True)

    for source in sources:
        target = target_root / source.name
        if target.is_symlink():
            destination = managed_destination(target, catalog.plugins_root)
            if destination == source.path:
                print_plan("up-to-date", target, destination)
                continue
            if destination is None and not force:
                raise SystemExit(
                    f"refusing to replace unmanaged symlink: {target}; "
                    "use --force only after reviewing the link"
                )
            print_plan("would relink" if dry_run else "relink", target, source.path)
        elif target.exists():
            if target.is_dir():
                raise SystemExit(
                    f"refusing to replace real directory: {target}; "
                    "resolve the conflict manually and rerun"
                )
            if not force:
                raise SystemExit(
                    f"refusing to overwrite unmanaged target file: {target}; "
                    "use --force only after reviewing the file"
                )
            print_plan("would replace" if dry_run else "replace", target, source.path)
        else:
            print_plan("would link" if dry_run else "link", target, source.path)

        if not dry_run:
            if target.exists() or target.is_symlink():
                target.unlink()
            target.symlink_to(source.path)

    if prune and target_root.is_dir():
        for target in sorted(target_root.iterdir()):
            if target.name in expected or not target.is_symlink():
                continue
            destination = managed_destination(target, catalog.plugins_root)
            if destination is None:
                print_plan("keep unmanaged", target)
                continue
            print_plan("would prune" if dry_run else "prune", target, destination)
            if not dry_run:
                target.unlink()

    if dry_run:
        print("dry-run only; no agents skills links written")
    else:
        print(f"agents skills sync complete: {len(sources)} skill(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Expose my-codex plugin skills as symlinks under ~/.agents/skills."
    )
    parser.add_argument(
        "--marketplace-file",
        default=str(MARKETPLACE_FILE),
        help="Marketplace file listing the plugins whose skills are exposed.",
    )
    parser.add_argument(
        "--target-root",
        default=str(DEFAULT_TARGET_ROOT),
        help="User-level skills directory that harnesses scan (default: ~/.agents/skills).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned links without modifying the target.")
    parser.add_argument("--check", action="store_true", help="Fail if exposed skills are missing or out of sync.")
    parser.add_argument("--prune", action="store_true", help="Remove managed links for skills that no longer exist.")
    parser.add_argument("--force", action="store_true", help="Allow replacing unmanaged symlinks and files.")
    args = parser.parse_args()

    marketplace_file = expand_path(args.marketplace_file)
    target_root = expand_path(args.target_root)
    catalog = load_skill_catalog(marketplace_file)

    if args.check:
        return check_layer(catalog, target_root=target_root, prune=args.prune)
    return sync_layer(
        catalog,
        target_root=target_root,
        dry_run=args.dry_run,
        prune=args.prune,
        force=args.force,
    )


if __name__ == "__main__":
    raise SystemExit(main())
