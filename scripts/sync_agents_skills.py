#!/usr/bin/env python3
"""Manage the universal user-level projection of repository-authoritative skills."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from repo_skill_catalog import REPO_ROOT, SkillCatalog, SkillSource, load_repo_skill_catalog

DEFAULT_TARGET_ROOT = Path.home() / ".agents" / "skills"


def expand_path(raw: str | Path) -> Path:
    return Path(os.path.expandvars(str(raw))).expanduser()


def managed_destination(link: Path, catalog: SkillCatalog) -> Path | None:
    """Return a direct repository skill path targeted by an owned projection link."""

    if not link.is_symlink():
        return None
    destination = link.resolve(strict=False)
    try:
        relative = destination.relative_to(catalog.plugins_root)
    except ValueError:
        return None
    if len(relative.parts) != 3 or relative.parts[1] != "skills":
        return None
    return destination


def preflight_layer(catalog: SkillCatalog, *, target_root: Path) -> None:
    """Fail before mutation when a canonical destination is owned by another source."""

    for source in catalog.sources:
        target = target_root / source.name
        if target.is_symlink():
            destination = managed_destination(target, catalog)
            if destination is None:
                raise SystemExit(f"refusing unmanaged universal skill symlink: {target}")
        elif target.exists():
            raise SystemExit(f"refusing unmanaged universal skill entry: {target}")


def preflight_profile_layer(catalog: SkillCatalog, *, target_root: Path) -> None:
    """Freeze a profile transition to the exact canonical projection names."""

    preflight_layer(catalog, target_root=target_root)
    for source in catalog.sources:
        target = target_root / source.name
        if not target.is_symlink():
            continue
        destination = managed_destination(target, catalog)
        if destination != source.path:
            raise SystemExit(
                "refusing universal skill link outside exact canonical mapping: "
                f"expected {target} -> {source.path}, found {destination}"
            )
    if not target_root.is_dir():
        return
    expected = catalog.by_name
    for target in sorted(target_root.iterdir()):
        if target.name in expected or not target.is_symlink():
            continue
        destination = managed_destination(target, catalog)
        if destination is not None:
            raise SystemExit(
                "refusing repository-target universal skill symlink outside exact "
                f"canonical set: {target} -> {destination}"
            )


def remove_managed_layer(
    catalog: SkillCatalog,
    *,
    target_root: Path,
    dry_run: bool,
) -> int:
    """Remove only canonical repository-owned links and preserve every other entry."""

    preflight_layer(catalog, target_root=target_root)
    if not target_root.is_dir():
        print("universal skills layer already inactive")
        return 0
    for source in catalog.sources:
        target = target_root / source.name
        destination = managed_destination(target, catalog)
        if destination is None:
            continue
        print_plan("would unlink" if dry_run else "unlink", target, destination)
        if not dry_run:
            target.unlink()
    return 0


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
            destination = managed_destination(target, catalog)
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
            destination = managed_destination(target, catalog)
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
) -> int:
    sources = catalog.sources
    expected = {source.name: source for source in sources}

    preflight_layer(catalog, target_root=target_root)

    if not dry_run:
        target_root.mkdir(parents=True, exist_ok=True)

    for source in sources:
        target = target_root / source.name
        if target.is_symlink():
            destination = managed_destination(target, catalog)
            if destination == source.path:
                print_plan("up-to-date", target, destination)
                continue
            if destination is None:
                raise SystemExit(f"refusing to replace unmanaged symlink: {target}")
            print_plan("would relink" if dry_run else "relink", target, source.path)
        elif target.exists():
            raise SystemExit(f"refusing to replace unmanaged target: {target}")
        else:
            print_plan("would link" if dry_run else "link", target, source.path)

        if not dry_run:
            if target.exists() or target.is_symlink():
                target.unlink()
            target.symlink_to(source.path, target_is_directory=True)

    if prune and target_root.is_dir():
        for target in sorted(target_root.iterdir()):
            if target.name in expected or not target.is_symlink():
                continue
            destination = managed_destination(target, catalog)
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
        description="Manage repository-authoritative skill symlinks under ~/.agents/skills."
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root containing plugins/*/skills source.",
    )
    parser.add_argument(
        "--target-root",
        default=str(DEFAULT_TARGET_ROOT),
        help="User-level skills directory that harnesses scan (default: ~/.agents/skills).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned links without modifying the target.")
    parser.add_argument("--check", action="store_true", help="Fail if exposed skills are missing or out of sync.")
    parser.add_argument("--prune", action="store_true", help="Remove managed links for skills that no longer exist.")
    args = parser.parse_args()

    repo_root = expand_path(args.repo_root)
    target_root = expand_path(args.target_root)
    catalog = load_repo_skill_catalog(repo_root)

    if args.check:
        return check_layer(catalog, target_root=target_root, prune=args.prune)
    return sync_layer(
        catalog,
        target_root=target_root,
        dry_run=args.dry_run,
        prune=args.prune,
    )


if __name__ == "__main__":
    raise SystemExit(main())
