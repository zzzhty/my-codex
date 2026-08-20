from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_my_codex  # noqa: E402
from check_skill_discovery import plugin_profile_issues, universal_profile_issues  # noqa: E402
from repo_skill_catalog import load_repo_skill_catalog  # noqa: E402
from sync_agents_skills import sync_layer  # noqa: E402


def write_skill(root: Path, plugin: str, name: str) -> Path:
    skill = root / "plugins" / plugin / "skills" / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: fixture\n---\n",
        encoding="utf-8",
    )
    return skill


class DiscoveryProfileClosureTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.repo = root / "repo"
        self.one = write_skill(self.repo, "alpha", "one")
        self.two = write_skill(self.repo, "beta", "two")
        self.catalog = load_repo_skill_catalog(self.repo)
        self.target = root / "agents" / "skills"
        self.addCleanup(self._tmp.cleanup)

    def test_universal_requires_exact_links_and_no_enabled_skill_plugins(self) -> None:
        sync_layer(self.catalog, target_root=self.target, dry_run=False, prune=True)
        self.assertEqual(
            universal_profile_issues(
                self.catalog,
                target_root=self.target,
                enabled_plugin_names=set(),
            ),
            [],
        )
        issues = universal_profile_issues(
            self.catalog,
            target_root=self.target,
            enabled_plugin_names={"alpha"},
        )
        self.assertTrue(any("remain enabled" in issue for issue in issues))

    def test_universal_rejects_missing_drift_unmanaged_and_stale_owned_links(self) -> None:
        self.target.mkdir(parents=True)
        (self.target / "one").symlink_to(self.two)
        (self.target / "two").mkdir()
        (self.target / "stale").symlink_to(self.one)
        issues = universal_profile_issues(
            self.catalog,
            target_root=self.target,
            enabled_plugin_names=set(),
        )
        report = "\n".join(issues)
        self.assertIn("link drift", report)
        self.assertIn("unmanaged universal entry", report)
        self.assertIn("stale repository-owned", report)

    def test_plugin_requires_exact_plugins_and_no_universal_entries(self) -> None:
        self.assertEqual(
            plugin_profile_issues(
                self.catalog,
                target_root=self.target,
                enabled_plugin_names={"alpha", "beta"},
            ),
            [],
        )
        sync_layer(self.catalog, target_root=self.target, dry_run=False, prune=True)
        issues = plugin_profile_issues(
            self.catalog,
            target_root=self.target,
            enabled_plugin_names={"alpha", "adapter"},
        )
        report = "\n".join(issues)
        self.assertIn("not enabled: beta", report)
        self.assertIn("no canonical repository skills: adapter", report)
        self.assertIn("universal callable identity remains active", report)


class CheckDiscoveryProfileCliTests(unittest.TestCase):
    def run_main(self, arguments: list[str]) -> None:
        with mock.patch.object(sys, "argv", ["check_my_codex.py", *arguments]):
            check_my_codex.main()

    def test_missing_profile_fails_before_catalog_or_runtime_checks(self) -> None:
        with mock.patch.object(check_my_codex, "load_repo_skill_catalog") as load_catalog:
            with self.assertRaises(SystemExit) as raised:
                self.run_main([])
        self.assertEqual(raised.exception.code, 2)
        load_catalog.assert_not_called()

    def test_universal_without_configured_plugins_does_not_resolve_codex_or_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            arguments = [
                "--discovery-profile",
                "universal",
                "--codex-home",
                str(root / "codex"),
                "--agents-skills-root",
                str(root / "agents" / "skills"),
                "--skip-hooks",
                "--skip-agents",
                "--skip-plugin-validation",
                "--skip-doctor",
            ]
            with (
                mock.patch.object(
                    check_my_codex,
                    "resolve_codex_executable",
                    side_effect=AssertionError("Codex must not be resolved"),
                ),
                mock.patch.object(
                    check_my_codex,
                    "marketplace_plugin_sources",
                    side_effect=AssertionError("marketplace must not be read"),
                ),
                mock.patch.object(check_my_codex.CheckRunner, "check_tooling_python"),
                mock.patch.object(check_my_codex.CheckRunner, "check_universal_discovery_profile"),
                mock.patch.object(check_my_codex.CheckRunner, "check_agents_skills_layer"),
                mock.patch.object(check_my_codex.CheckRunner, "check_watcher_runtime_cutover"),
            ):
                self.run_main(arguments)

    def test_legacy_bypass_fails_before_runtime_checks(self) -> None:
        with mock.patch.object(check_my_codex, "resolve_codex_executable") as resolve:
            with self.assertRaisesRegex(SystemExit, "legacy bypass"):
                self.run_main(
                    [
                        "--discovery-profile",
                        "universal",
                        "--skip-plugins",
                    ]
                )
        resolve.assert_not_called()


if __name__ == "__main__":
    unittest.main()
