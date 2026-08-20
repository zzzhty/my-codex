from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_my_codex  # noqa: E402
from check_skill_discovery import (  # noqa: E402
    PluginListRow,
    codex_plugin_rows,
    plugin_installation_issues,
    plugin_package_issues,
    plugin_profile_issues,
    universal_profile_issues,
)
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


class PluginListParserTests(unittest.TestCase):
    def test_parses_installed_and_uninstalled_rows(self) -> None:
        output = (
            "Marketplace `my-codex`\n"
            "/repo/.agents/plugins/marketplace.json\n\n"
            "PLUGIN  STATUS              VERSION  PATH\n"
            "alpha@my-codex  installed, enabled  1.2.3  /cache/alpha\n"
            "beta@my-codex  not installed          /repo/plugins/beta\n"
        )
        self.assertEqual(
            codex_plugin_rows(output),
            {
                ("my-codex", "alpha"): PluginListRow("installed, enabled", "1.2.3"),
                ("my-codex", "beta"): PluginListRow("not installed", ""),
            },
        )

    def test_malformed_candidate_row_fails_closed(self) -> None:
        output = (
            "Marketplace `my-codex`\n"
            "/repo/.agents/plugins/marketplace.json\n\n"
            "PLUGIN  STATUS              VERSION  PATH\n"
            "alpha@my-codex installed, enabled 1.2.3 /cache/alpha\n"
        )
        with self.assertRaisesRegex(ValueError, "malformed plugin list row"):
            codex_plugin_rows(output)


class PluginInstallationClosureTests(unittest.TestCase):
    def test_cli_and_cache_version_drift_are_reported_by_shared_closure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            source = write_skill(repo, "alpha", "one")
            source_manifest = source.parents[1] / ".codex-plugin" / "plugin.json"
            source_manifest.parent.mkdir(parents=True, exist_ok=True)
            source_manifest.write_text(
                '{"name": "alpha", "version": "2.0.0", "skills": "./skills/"}\n',
                encoding="utf-8",
            )
            catalog = load_repo_skill_catalog(repo)
            codex_home = root / "codex"
            for version in ("1.0.0", "2.0.0"):
                (codex_home / "plugins" / "cache" / "test" / "alpha" / version).mkdir(
                    parents=True
                )

            issues = plugin_installation_issues(
                catalog,
                marketplace_name="test",
                target_root=root / "agents" / "skills",
                codex_home=codex_home,
                rows={
                    ("test", "alpha"): PluginListRow(
                        "installed, enabled",
                        "1.0.0",
                    )
                },
                plugin_sources={"alpha": source.parents[1]},
            )

        report = "\n".join(issues)
        self.assertIn("installed version mismatch", report)
        self.assertIn("expected exactly one inspectable cache version", report)

    def test_manifest_schema_and_identity_failures_are_reported_by_shared_closure(self) -> None:
        cases = (
            (
                "source-json",
                {"source_text": "{not-json\n"},
                "source manifest is not valid readable JSON",
            ),
            (
                "source-name",
                {"source_name": "other"},
                "source manifest name mismatch",
            ),
            (
                "cache-json",
                {"cache_text": "{not-json\n"},
                "cache manifest is not valid readable JSON",
            ),
            (
                "cache-name",
                {"cache_name": "other"},
                "found ('other', '2.0.0')",
            ),
            (
                "cache-version",
                {"cache_version": "9.9.9"},
                "found ('alpha', '9.9.9')",
            ),
        )
        for label, overrides, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                repo = root / "repo"
                source = write_skill(repo, "alpha", "one")
                source_manifest = source.parents[1] / ".codex-plugin" / "plugin.json"
                source_manifest.parent.mkdir(parents=True, exist_ok=True)
                source_manifest.write_text(
                    str(overrides.get("source_text"))
                    if "source_text" in overrides
                    else json.dumps(
                        {
                            "name": overrides.get("source_name", "alpha"),
                            "version": "2.0.0",
                            "skills": "./skills/",
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )
                catalog = load_repo_skill_catalog(repo)
                version_root = (
                    root / "codex" / "plugins" / "cache" / "test" / "alpha" / "2.0.0"
                )
                cache_manifest = version_root / ".codex-plugin" / "plugin.json"
                cache_manifest.parent.mkdir(parents=True, exist_ok=True)
                cache_manifest.write_text(
                    str(overrides.get("cache_text"))
                    if "cache_text" in overrides
                    else json.dumps(
                        {
                            "name": overrides.get("cache_name", "alpha"),
                            "version": overrides.get("cache_version", "2.0.0"),
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )
                cached_skill = version_root / "skills" / "one"
                cached_skill.mkdir(parents=True)
                cached_skill.joinpath("SKILL.md").write_text(
                    "---\nname: one\ndescription: fixture\n---\n",
                    encoding="utf-8",
                )

                issues = plugin_installation_issues(
                    catalog,
                    marketplace_name="test",
                    target_root=root / "agents" / "skills",
                    codex_home=root / "codex",
                    rows={
                        ("test", "alpha"): PluginListRow(
                            "installed, enabled",
                            "2.0.0",
                        )
                    },
                    plugin_sources={"alpha": source.parents[1]},
                )

            self.assertIn(expected, "\n".join(issues))

    def test_source_package_contract_locks_manifest_and_loaded_skill_tree(self) -> None:
        cases = (
            (
                "manifest-skills",
                "manifest",
                "source manifest skills must be exactly './skills/'",
            ),
            ("extra-directory", "extra", "outside the loaded catalog"),
            ("identity-drift", "identity", "callable identity changed after catalog load"),
            (
                "symlink-escape",
                "symlink",
                "source skill directory escapes package authority",
            ),
            (
                "nested-file-symlink-escape",
                "nested-file-symlink",
                "source package entry escapes package authority",
            ),
            (
                "nested-directory-symlink-escape",
                "nested-directory-symlink",
                "source package entry escapes package authority",
            ),
        )
        for label, mutation, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                repo = root / "repo"
                source = write_skill(repo, "alpha", "one")
                source_root = source.parents[1]
                manifest = source_root / ".codex-plugin" / "plugin.json"
                manifest.parent.mkdir(parents=True, exist_ok=True)
                manifest.write_text(
                    '{"name": "alpha", "version": "2.0.0", "skills": "./skills/"}\n',
                    encoding="utf-8",
                )
                catalog = load_repo_skill_catalog(repo)
                if mutation == "manifest":
                    manifest.write_text(
                        '{"name": "alpha", "version": "2.0.0", "skills": "./other/"}\n',
                        encoding="utf-8",
                    )
                elif mutation == "extra":
                    write_skill(repo, "alpha", "late-added")
                elif mutation == "symlink":
                    external = root / "external-skill"
                    external.mkdir()
                    external.joinpath("SKILL.md").write_text(
                        "---\nname: one\ndescription: external fixture\n---\n",
                        encoding="utf-8",
                    )
                    source.joinpath("SKILL.md").unlink()
                    source.rmdir()
                    source.symlink_to(external, target_is_directory=True)
                elif mutation == "nested-file-symlink":
                    external = root / "external-tool.py"
                    external.write_text("print('external')\n", encoding="utf-8")
                    scripts = source / "scripts"
                    scripts.mkdir()
                    scripts.joinpath("tool.py").symlink_to(external)
                elif mutation == "nested-directory-symlink":
                    external = root / "external-resources"
                    external.mkdir()
                    external.joinpath("data.txt").write_text("external\n", encoding="utf-8")
                    source.joinpath("references").symlink_to(
                        external,
                        target_is_directory=True,
                    )
                else:
                    source.joinpath("SKILL.md").write_text(
                        "---\nname: changed\ndescription: fixture\n---\n",
                        encoding="utf-8",
                    )

                issues = plugin_package_issues(
                    catalog,
                    plugin_sources={"alpha": source_root},
                )

            self.assertIn(expected, "\n".join(issues))

    def test_plugin_installation_closure_rejects_universal_links_with_valid_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            source = write_skill(repo, "alpha", "one")
            source_root = source.parents[1]
            source_manifest = source_root / ".codex-plugin" / "plugin.json"
            source_manifest.parent.mkdir(parents=True, exist_ok=True)
            source_manifest.write_text(
                '{"name": "alpha", "version": "2.0.0", "skills": "./skills/"}\n',
                encoding="utf-8",
            )
            catalog = load_repo_skill_catalog(repo)
            target = root / "agents" / "skills"
            sync_layer(catalog, target_root=target, dry_run=False, prune=True)
            version_root = root / "codex" / "plugins" / "cache" / "test" / "alpha" / "2.0.0"
            cache_manifest = version_root / ".codex-plugin" / "plugin.json"
            cache_manifest.parent.mkdir(parents=True, exist_ok=True)
            cache_manifest.write_text(
                '{"name": "alpha", "version": "2.0.0"}\n',
                encoding="utf-8",
            )
            cached_skill = version_root / "skills" / "one"
            cached_skill.mkdir(parents=True)
            cached_skill.joinpath("SKILL.md").write_text(
                "---\nname: one\ndescription: cached fixture\n---\n",
                encoding="utf-8",
            )

            issues = plugin_installation_issues(
                catalog,
                marketplace_name="test",
                target_root=target,
                codex_home=root / "codex",
                rows={
                    ("test", "alpha"): PluginListRow(
                        "installed, enabled",
                        "2.0.0",
                    )
                },
                plugin_sources={"alpha": source_root},
            )

        self.assertIn("universal callable identity remains active", "\n".join(issues))


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
