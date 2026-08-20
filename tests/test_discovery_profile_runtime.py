from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from discovery_profile_runtime import (  # noqa: E402
    DiscoveryTransitionRuntime,
    transition_plugin_to_universal,
    transition_universal_to_plugin,
)


class RecordingRuntime:
    def __init__(self, *, fail_at: str | None = None, rollback_fail_at: str | None = None) -> None:
        self.events: list[str] = []
        self.fail_at = fail_at
        self.rollback_fail_at = rollback_fail_at
        self.failed_once = False

    def step(self, label: str) -> None:
        self.events.append(label)
        if label == self.fail_at and not self.failed_once:
            self.failed_once = True
            raise SystemExit(f"failed at {label}")
        if self.failed_once and label == self.rollback_fail_at:
            raise SystemExit(f"rollback failed at {label}")

    def runtime(self) -> DiscoveryTransitionRuntime:
        return DiscoveryTransitionRuntime(
            preflight_universal=lambda: self.step("preflight-universal"),
            activate_universal=lambda: self.step("activate-universal"),
            deactivate_universal=lambda: self.step("deactivate-universal"),
            verify_universal=lambda: self.step("verify-universal"),
            preflight_plugin=lambda: self.step("preflight-plugin"),
            activate_plugin=lambda selector: self.step(f"activate-plugin:{selector}"),
            deactivate_plugin=lambda selector: self.step(f"deactivate-plugin:{selector}"),
            verify_plugin=lambda: self.step("verify-plugin"),
            verify_plugins_inactive=lambda: self.step("verify-plugins-inactive"),
        )


class DiscoveryProfileRuntimeTests(unittest.TestCase):
    def test_plugin_to_universal_orders_preflight_deactivation_and_activation(self) -> None:
        recording = RecordingRuntime()
        transition_plugin_to_universal(recording.runtime(), ["alpha@test", "beta@test"])
        self.assertEqual(
            recording.events,
            [
                "preflight-universal",
                "deactivate-plugin:alpha@test",
                "deactivate-plugin:beta@test",
                "verify-plugins-inactive",
                "activate-universal",
                "verify-universal",
            ],
        )

    def test_plugin_to_universal_failure_removes_partial_links_before_restoring_plugins(self) -> None:
        recording = RecordingRuntime(fail_at="verify-universal")
        with self.assertRaisesRegex(SystemExit, "failed at verify-universal"):
            transition_plugin_to_universal(recording.runtime(), ["alpha@test", "beta@test"])
        self.assertEqual(
            recording.events[-4:],
            [
                "deactivate-universal",
                "activate-plugin:alpha@test",
                "activate-plugin:beta@test",
                "verify-plugin",
            ],
        )

    def test_universal_to_plugin_preflights_before_removing_links(self) -> None:
        recording = RecordingRuntime()
        transition_universal_to_plugin(recording.runtime(), ["alpha@test", "beta@test"])
        self.assertEqual(
            recording.events,
            [
                "preflight-plugin",
                "deactivate-universal",
                "activate-plugin:alpha@test",
                "activate-plugin:beta@test",
                "verify-plugin",
            ],
        )

    def test_universal_to_plugin_failure_removes_partial_plugins_before_restoring_links(self) -> None:
        recording = RecordingRuntime(fail_at="activate-plugin:beta@test")
        with self.assertRaisesRegex(SystemExit, "failed at activate-plugin:beta@test"):
            transition_universal_to_plugin(recording.runtime(), ["alpha@test", "beta@test"])
        self.assertEqual(
            recording.events[-4:],
            [
                "deactivate-plugin:beta@test",
                "deactivate-plugin:alpha@test",
                "activate-universal",
                "verify-universal",
            ],
        )

    def test_rollback_failure_reports_both_breakpoints(self) -> None:
        recording = RecordingRuntime(
            fail_at="verify-universal",
            rollback_fail_at="activate-plugin:alpha@test",
        )
        with self.assertRaisesRegex(
            SystemExit,
            "failed at verify-universal.*rollback failed at activate-plugin:alpha@test",
        ):
            transition_plugin_to_universal(recording.runtime(), ["alpha@test"])


if __name__ == "__main__":
    unittest.main()
