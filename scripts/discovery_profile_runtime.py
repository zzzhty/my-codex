#!/usr/bin/env python3
"""Ordered, rollback-capable transitions between skill discovery profiles."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass


Step = Callable[[], None]
PluginStep = Callable[[str], None]


@dataclass(frozen=True)
class DiscoveryTransitionRuntime:
    preflight_universal: Step
    activate_universal: Step
    deactivate_universal: Step
    verify_universal: Step
    preflight_plugin: Step
    activate_plugin: PluginStep
    deactivate_plugin: PluginStep
    verify_plugin: Step
    verify_plugins_inactive: Step


def _transition_failure(
    *,
    direction: str,
    original: BaseException,
    rollback: BaseException,
) -> SystemExit:
    return SystemExit(
        f"discovery profile transition failed ({direction}): {original}; "
        f"rollback failed: {rollback}"
    )


def transition_plugin_to_universal(
    runtime: DiscoveryTransitionRuntime,
    plugin_selectors: Sequence[str],
) -> None:
    """Deactivate exact plugins before activating links; restore plugins on failure."""

    runtime.preflight_universal()
    removed: list[str] = []
    try:
        for selector in plugin_selectors:
            removed.append(selector)
            runtime.deactivate_plugin(selector)
        runtime.verify_plugins_inactive()
        runtime.activate_universal()
        runtime.verify_universal()
    except (Exception, SystemExit) as exc:
        try:
            runtime.deactivate_universal()
            for selector in removed:
                runtime.activate_plugin(selector)
            runtime.verify_plugin()
        except (Exception, SystemExit) as rollback_exc:
            raise _transition_failure(
                direction="plugin -> universal",
                original=exc,
                rollback=rollback_exc,
            ) from exc
        raise


def transition_universal_to_plugin(
    runtime: DiscoveryTransitionRuntime,
    plugin_selectors: Sequence[str],
) -> None:
    """Preflight packages, remove links, and restore universal links on failure."""

    runtime.preflight_plugin()
    installed: list[str] = []
    runtime.deactivate_universal()
    try:
        for selector in plugin_selectors:
            installed.append(selector)
            runtime.activate_plugin(selector)
        runtime.verify_plugin()
    except (Exception, SystemExit) as exc:
        try:
            for selector in reversed(installed):
                runtime.deactivate_plugin(selector)
            runtime.activate_universal()
            runtime.verify_universal()
        except (Exception, SystemExit) as rollback_exc:
            raise _transition_failure(
                direction="universal -> plugin",
                original=exc,
                rollback=rollback_exc,
            ) from exc
        raise
