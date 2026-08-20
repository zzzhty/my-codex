#!/usr/bin/env python3
"""Shared policy for the two mutually exclusive skill discovery profiles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from repo_skill_catalog import SkillCatalog


class DiscoveryProfile(str, Enum):
    UNIVERSAL = "universal"
    PLUGIN = "plugin"


DISCOVERY_PROFILE_CHOICES = tuple(profile.value for profile in DiscoveryProfile)


@dataclass(frozen=True)
class RefreshProfileOptions:
    profile: DiscoveryProfile
    skip_marketplace: bool = False
    skip_plugins: bool = False
    skip_agents_skills: bool = False
    prune_plugins: bool = False
    selected_plugins: tuple[str, ...] = ()


@dataclass(frozen=True)
class CheckProfileOptions:
    profile: DiscoveryProfile
    skip_plugins: bool = False
    skip_agents_skills: bool = False
    selected_plugins: tuple[str, ...] = ()


def parse_discovery_profile(raw: str) -> DiscoveryProfile:
    try:
        return DiscoveryProfile(raw)
    except ValueError as exc:
        choices = ", ".join(DISCOVERY_PROFILE_CHOICES)
        raise SystemExit(f"invalid discovery profile {raw!r}; expected one of: {choices}") from exc


def _reject_legacy_bypasses(flags: dict[str, bool]) -> None:
    active = sorted(name for name, enabled in flags.items() if enabled)
    if active:
        raise SystemExit(
            "legacy bypass flags cannot weaken an explicit discovery profile: "
            + ", ".join(active)
        )


def validate_refresh_profile(options: RefreshProfileOptions) -> None:
    _reject_legacy_bypasses(
        {
            "--skip-marketplace": options.skip_marketplace,
            "--skip-plugins": options.skip_plugins,
            "--skip-agents-skills": options.skip_agents_skills,
        }
    )
    if options.profile is DiscoveryProfile.UNIVERSAL:
        if options.prune_plugins:
            raise SystemExit("--prune-plugins is incompatible with discovery profile universal")
        if options.selected_plugins:
            raise SystemExit("--plugin is valid only with discovery profile plugin")


def validate_check_profile(options: CheckProfileOptions) -> None:
    _reject_legacy_bypasses(
        {
            "--skip-plugins": options.skip_plugins,
            "--skip-agents-skills": options.skip_agents_skills,
        }
    )
    if options.selected_plugins:
        raise SystemExit(
            "--plugin cannot narrow a discovery-profile closure check; validate the complete selected profile"
        )


def ensure_plugin_profile_covers_catalog(
    catalog: SkillCatalog,
    selectors: list[str] | tuple[str, ...],
    *,
    marketplace_name: str,
) -> None:
    selected_names: set[str] = set()
    for selector in selectors:
        name, separator, marketplace = selector.partition("@")
        if not separator or not name or marketplace != marketplace_name:
            raise SystemExit(
                f"plugin profile selector must target {marketplace_name!r}: {selector!r}"
            )
        selected_names.add(name)
    expected_names = set(catalog.plugin_names)
    missing = sorted(expected_names - selected_names)
    extra = sorted(selected_names - expected_names)
    if missing or extra:
        details = []
        if missing:
            details.append("missing skills-bearing plugins: " + ", ".join(missing))
        if extra:
            details.append("selected plugins without canonical skills: " + ", ".join(extra))
        raise SystemExit("plugin discovery profile does not match repository catalog: " + "; ".join(details))
