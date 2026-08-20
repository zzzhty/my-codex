#!/usr/bin/env python3
"""Pure closure checks for mutually exclusive universal and plugin discovery."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from repo_skill_catalog import SkillCatalog, skill_frontmatter_name
from sync_agents_skills import managed_destination


@dataclass(frozen=True)
class PluginListRow:
    status: str
    version: str


def codex_plugin_rows(output: str) -> dict[tuple[str, str], PluginListRow]:
    """Parse the stable marketplace/plugin rows printed by `codex plugin list`."""

    rows: dict[tuple[str, str], PluginListRow] = {}
    marketplace_name: str | None = None
    for raw_line in output.splitlines():
        line = raw_line.strip()
        marketplace_match = re.fullmatch(r"Marketplace `([^`]+)`", line)
        if marketplace_match:
            marketplace_name = marketplace_match.group(1)
            continue
        if not line or line.startswith("PLUGIN") or marketplace_name is None:
            continue
        columns = re.split(r"\s{2,}", line, maxsplit=3)
        if len(columns) < 2:
            continue
        plugin_name, separator, listed_marketplace = columns[0].rpartition("@")
        if not separator or not plugin_name or listed_marketplace != marketplace_name:
            continue
        status = columns[1]
        version = columns[2] if len(columns) >= 4 else ""
        rows[(marketplace_name, plugin_name)] = PluginListRow(status=status, version=version)
    return rows


def enabled_plugin_names(
    rows: dict[tuple[str, str], PluginListRow],
    *,
    marketplace_name: str,
) -> set[str]:
    return {
        plugin_name
        for (marketplace, plugin_name), row in rows.items()
        if marketplace == marketplace_name and row.status == "installed, enabled"
    }


def _manifest_identity(manifest: Path, *, label: str) -> tuple[str, str]:
    if not manifest.is_file():
        raise ValueError(f"{label} manifest missing: {manifest}")
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} manifest is not valid readable JSON: {manifest}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} manifest must be an object: {manifest}")
    identity: list[str] = []
    for field in ("name", "version"):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} manifest {field} must be a non-empty string: {manifest}")
        identity.append(value.strip())
    return identity[0], identity[1]


def plugin_package_issues(
    catalog: SkillCatalog,
    *,
    plugin_sources: dict[str, Path],
) -> list[str]:
    """Validate that plugin packages are the packaging projection of catalog owners."""

    issues: list[str] = []
    expected_plugins = set(catalog.plugin_names)
    missing = sorted(expected_plugins - set(plugin_sources))
    extra = sorted(set(plugin_sources) - expected_plugins)
    if missing:
        issues.append("marketplace is missing skills-bearing plugin packages: " + ", ".join(missing))
    if extra:
        issues.append("marketplace has plugin packages outside the callable catalog: " + ", ".join(extra))

    for plugin_name in sorted(expected_plugins & set(plugin_sources)):
        source_root = plugin_sources[plugin_name]
        expected_root = catalog.plugins_root / plugin_name
        try:
            source_resolved = source_root.resolve(strict=True)
            expected_resolved = expected_root.resolve(strict=True)
        except OSError as exc:
            issues.append(f"{plugin_name}: plugin package path cannot be resolved: {exc}")
            continue
        if source_resolved != expected_resolved:
            issues.append(
                f"{plugin_name}: marketplace package is not the canonical catalog owner; "
                f"expected {expected_resolved}, found {source_resolved}"
            )
            continue
        try:
            manifest_name, _ = _manifest_identity(
                source_resolved / ".codex-plugin" / "plugin.json",
                label="source",
            )
        except ValueError as exc:
            issues.append(f"{plugin_name}: {exc}")
            continue
        if manifest_name != plugin_name:
            issues.append(
                f"{plugin_name}: source manifest name mismatch; found {manifest_name!r}"
            )
    return issues


def plugin_cache_preflight_issues(
    catalog: SkillCatalog,
    *,
    codex_home: Path,
    marketplace_name: str,
) -> list[str]:
    """Reject cache shapes that cannot be safely inspected after activation."""

    cache_root = codex_home / "plugins" / "cache" / marketplace_name
    if not cache_root.exists():
        return []
    if not cache_root.is_dir() or cache_root.is_symlink():
        return [f"plugin cache marketplace root is not an inspectable directory: {cache_root}"]
    try:
        resolved_cache_root = cache_root.resolve(strict=True)
    except OSError as exc:
        return [f"plugin cache marketplace root cannot be resolved: {cache_root}: {exc}"]

    issues: list[str] = []
    expected_plugins = set(catalog.plugin_names)
    for plugin_root in sorted(cache_root.iterdir(), key=lambda path: path.name):
        if not plugin_root.is_dir() or plugin_root.is_symlink():
            issues.append(f"plugin cache package entry is not an inspectable directory: {plugin_root}")
            continue
        try:
            resolved_plugin = plugin_root.resolve(strict=True)
            resolved_plugin.relative_to(resolved_cache_root)
        except (OSError, ValueError) as exc:
            issues.append(f"plugin cache package escapes marketplace root: {plugin_root}: {exc}")
            continue
        if plugin_root.name not in expected_plugins:
            issues.append(
                "cached my-codex plugin has no canonical repository skills: "
                + plugin_root.name
            )
            continue
        for version_root in sorted(plugin_root.iterdir(), key=lambda path: path.name):
            if not version_root.is_dir() or version_root.is_symlink():
                issues.append(
                    f"plugin cache version entry is not an inspectable directory: {version_root}"
                )
                continue
            try:
                version_root.resolve(strict=True).relative_to(resolved_plugin)
            except (OSError, ValueError) as exc:
                issues.append(f"plugin cache version escapes package root: {version_root}: {exc}")
    return issues


def _cached_skill_identities(version_root: Path) -> tuple[set[str], list[str]]:
    issues: list[str] = []
    skills_root = version_root / "skills"
    if not skills_root.is_dir() or skills_root.is_symlink():
        return set(), [f"cache skills directory missing or not inspectable: {skills_root}"]
    try:
        resolved_version = version_root.resolve(strict=True)
        resolved_skills = skills_root.resolve(strict=True)
        resolved_skills.relative_to(resolved_version)
    except (OSError, ValueError) as exc:
        return set(), [f"cache skills directory escapes version root: {skills_root}: {exc}"]

    identities: set[str] = set()
    for entry in sorted(skills_root.iterdir(), key=lambda path: path.name):
        if not entry.is_dir() or entry.is_symlink():
            issues.append(f"cache skill entry is not an inspectable directory: {entry}")
            continue
        skill_file = entry / "SKILL.md"
        try:
            resolved_entry = entry.resolve(strict=True)
            resolved_file = skill_file.resolve(strict=True)
            resolved_entry.relative_to(resolved_skills)
            resolved_file.relative_to(resolved_entry)
        except (OSError, ValueError) as exc:
            issues.append(f"cache skill path escapes version root: {entry}: {exc}")
            continue
        try:
            identity = skill_frontmatter_name(resolved_file)
        except SystemExit as exc:
            issues.append(str(exc))
            continue
        if identity in identities:
            issues.append(f"duplicate cached callable identity {identity!r} under {skills_root}")
            continue
        identities.add(identity)
    return identities, issues


def plugin_installation_issues(
    catalog: SkillCatalog,
    *,
    marketplace_name: str,
    target_root: Path,
    codex_home: Path,
    rows: dict[tuple[str, str], PluginListRow],
    plugin_sources: dict[str, Path],
) -> list[str]:
    """Validate the complete active plugin projection against canonical source."""

    issues = [
        *plugin_package_issues(catalog, plugin_sources=plugin_sources),
        *plugin_cache_preflight_issues(
            catalog,
            codex_home=codex_home,
            marketplace_name=marketplace_name,
        ),
    ]
    enabled = enabled_plugin_names(rows, marketplace_name=marketplace_name)
    issues.extend(
        plugin_profile_issues(
            catalog,
            target_root=target_root,
            enabled_plugin_names=enabled,
        )
    )

    expected_by_plugin: dict[str, set[str]] = {}
    for source in catalog.sources:
        expected_by_plugin.setdefault(source.plugin, set()).add(source.name)

    cache_marketplace_root = codex_home / "plugins" / "cache" / marketplace_name
    if cache_marketplace_root.is_dir():
        cached_packages = {path.name for path in cache_marketplace_root.iterdir() if path.is_dir()}
        extra_cached = sorted(cached_packages - set(catalog.plugin_names))
        if extra_cached:
            issues.append(
                "cached my-codex plugins have no canonical repository skills: "
                + ", ".join(extra_cached)
            )

    for plugin_name in catalog.plugin_names:
        source_root = plugin_sources.get(plugin_name)
        if source_root is None:
            continue
        try:
            source_name, source_version = _manifest_identity(
                source_root / ".codex-plugin" / "plugin.json",
                label="source",
            )
        except ValueError as exc:
            issues.append(f"{plugin_name}: {exc}")
            continue
        if source_name != plugin_name:
            issues.append(
                f"{plugin_name}: source manifest name mismatch; found {source_name!r}"
            )
            continue

        row = rows.get((marketplace_name, plugin_name))
        if row is None:
            issues.append(f"{plugin_name}@{marketplace_name}: missing from `codex plugin list`")
        else:
            if row.status != "installed, enabled":
                issues.append(
                    f"{plugin_name}@{marketplace_name}: expected status 'installed, enabled', "
                    f"found {row.status!r}"
                )
            if row.version != source_version:
                issues.append(
                    f"{plugin_name}@{marketplace_name}: installed version mismatch; "
                    f"expected {source_version!r}, found {row.version!r}"
                )

        plugin_cache_root = cache_marketplace_root / plugin_name
        versions = (
            sorted(path for path in plugin_cache_root.iterdir() if path.is_dir())
            if plugin_cache_root.is_dir()
            else []
        )
        if len(versions) != 1:
            found = ", ".join(path.name for path in versions) or "none"
            issues.append(
                f"{plugin_name}@{marketplace_name}: expected exactly one inspectable cache version "
                f"{source_version!r}; found {found}"
            )
            continue
        version_root = versions[0]
        if version_root.is_symlink() or version_root.name != source_version:
            issues.append(
                f"{plugin_name}@{marketplace_name}: cache version mismatch or symlink; "
                f"expected {source_version!r}, found {version_root.name!r}"
            )
            continue
        try:
            cache_name, cache_version = _manifest_identity(
                version_root / ".codex-plugin" / "plugin.json",
                label="cache",
            )
        except ValueError as exc:
            issues.append(f"{plugin_name}: {exc}")
            continue
        if (cache_name, cache_version) != (source_name, source_version):
            issues.append(
                f"{plugin_name}@{marketplace_name}: cache manifest identity mismatch; "
                f"expected {(source_name, source_version)!r}, found {(cache_name, cache_version)!r}"
            )

        cached_identities, cache_issues = _cached_skill_identities(version_root)
        issues.extend(f"{plugin_name}: {issue}" for issue in cache_issues)
        expected_identities = expected_by_plugin[plugin_name]
        missing_identities = sorted(expected_identities - cached_identities)
        extra_identities = sorted(cached_identities - expected_identities)
        if missing_identities or extra_identities:
            details: list[str] = []
            if missing_identities:
                details.append("missing " + ", ".join(missing_identities))
            if extra_identities:
                details.append("extra " + ", ".join(extra_identities))
            issues.append(
                f"{plugin_name}@{marketplace_name}: cached callable identities differ from "
                f"canonical source ({'; '.join(details)})"
            )
    return issues


def universal_profile_issues(
    catalog: SkillCatalog,
    *,
    target_root: Path,
    enabled_plugin_names: set[str],
) -> list[str]:
    issues: list[str] = []
    expected = catalog.by_name
    for name, source in expected.items():
        target = target_root / name
        if target.is_symlink():
            destination = managed_destination(target, catalog)
            if destination is None:
                issues.append(f"unmanaged universal symlink occupies callable identity {name}: {target}")
            elif destination != source.path:
                issues.append(
                    f"universal link drift for {name}: expected {source.path}, found {destination}"
                )
        elif target.exists():
            issues.append(f"unmanaged universal entry occupies callable identity {name}: {target}")
        else:
            issues.append(f"universal skill link missing for {name}: expected {target} -> {source.path}")

    if target_root.is_dir():
        for target in sorted(target_root.iterdir()):
            if target.name in expected or not target.is_symlink():
                continue
            destination = managed_destination(target, catalog)
            if destination is not None:
                issues.append(f"stale repository-owned universal link: {target} -> {destination}")

    active_conflicts = sorted(enabled_plugin_names & set(catalog.plugin_names))
    if active_conflicts:
        issues.append(
            "skills-bearing plugins remain enabled during universal discovery: "
            + ", ".join(active_conflicts)
        )
    return issues


def plugin_profile_issues(
    catalog: SkillCatalog,
    *,
    target_root: Path,
    enabled_plugin_names: set[str],
) -> list[str]:
    issues: list[str] = []
    expected_plugins = set(catalog.plugin_names)
    missing_plugins = sorted(expected_plugins - enabled_plugin_names)
    extra_plugins = sorted(enabled_plugin_names - expected_plugins)
    if missing_plugins:
        issues.append("skills-bearing plugins are not enabled: " + ", ".join(missing_plugins))
    if extra_plugins:
        issues.append(
            "enabled my-codex plugins have no canonical repository skills: "
            + ", ".join(extra_plugins)
        )

    if target_root.is_dir():
        for target in sorted(target_root.iterdir()):
            if target.name in catalog.by_name:
                issues.append(
                    f"universal callable identity remains active during plugin discovery: {target}"
                )
                continue
            if target.is_symlink():
                destination = managed_destination(target, catalog)
                if destination is not None:
                    issues.append(
                        f"stale repository-owned universal link remains during plugin discovery: "
                        f"{target} -> {destination}"
                    )
    return issues


def require_profile_closure(profile: str, issues: list[str]) -> None:
    if issues:
        raise SystemExit(
            f"{profile} discovery profile closure failed with {len(issues)} issue(s): "
            + "; ".join(issues)
        )
