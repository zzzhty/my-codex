from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import refresh_my_codex as refresh  # noqa: E402
from check_skill_discovery import PluginListRow  # noqa: E402


class RefreshDiscoveryProfileCliTests(unittest.TestCase):
    def run_main(self, arguments: list[str]) -> None:
        with mock.patch.object(sys, "argv", ["refresh_my_codex.py", *arguments]):
            refresh.main()

    def test_missing_profile_fails_before_any_refresh_work(self) -> None:
        with mock.patch.object(refresh, "load_repo_skill_catalog") as load_catalog:
            with self.assertRaises(SystemExit) as raised:
                self.run_main(["--dry-run"])
        self.assertEqual(raised.exception.code, 2)
        load_catalog.assert_not_called()

    def test_invalid_profile_fails_closed(self) -> None:
        with mock.patch.object(refresh, "load_repo_skill_catalog") as load_catalog:
            with self.assertRaises(SystemExit) as raised:
                self.run_main(["--discovery-profile", "mixed", "--dry-run"])
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
                "--dry-run",
                "--skip-bootstrap",
                "--skip-agents",
                "--skip-hooks",
                "--skip-doctor",
            ]
            with (
                mock.patch.object(
                    refresh,
                    "resolve_codex_executable",
                    side_effect=AssertionError("Codex must not be resolved"),
                ),
                mock.patch.object(
                    refresh,
                    "marketplace_plugin_sources",
                    side_effect=AssertionError("marketplace must not be read"),
                ),
            ):
                self.run_main(arguments)

    def test_universal_with_configured_plugins_inspects_exact_enabled_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / "codex"
            codex_home.mkdir()
            codex_home.joinpath("config.toml").write_text(
                '\n'.join(
                    [
                        '[plugins."watcher@my-codex"]',
                        '[plugins."workflow@my-codex"]',
                        '[plugins."mattpocock-skills@my-codex"]',
                    ]
                ),
                encoding="utf-8",
            )
            rows = {
                ("my-codex", name): PluginListRow("installed, enabled", "fixture")
                for name in ("watcher", "workflow", "mattpocock-skills")
            }
            arguments = [
                "--discovery-profile",
                "universal",
                "--codex-home",
                str(codex_home),
                "--agents-skills-root",
                str(root / "agents" / "skills"),
                "--dry-run",
                "--skip-bootstrap",
                "--skip-agents",
                "--skip-hooks",
                "--skip-doctor",
            ]
            with (
                mock.patch.object(refresh, "resolve_codex_executable", return_value="/fake/codex") as resolve,
                mock.patch.object(refresh, "require_codex_plugin_commands") as require_commands,
                mock.patch.object(refresh, "read_codex_plugin_rows", return_value=rows) as inspect,
            ):
                self.run_main(arguments)

        resolve.assert_called_once()
        inspect.assert_called_once()
        self.assertTrue(require_commands.call_args.kwargs["require_remove"])
        self.assertFalse(require_commands.call_args.kwargs["require_marketplace"])

    def test_legacy_bypass_fails_before_bootstrap(self) -> None:
        with mock.patch.object(refresh, "run_tooling_bootstrap") as bootstrap:
            with self.assertRaisesRegex(SystemExit, "legacy bypass"):
                self.run_main(
                    [
                        "--discovery-profile",
                        "universal",
                        "--skip-agents-skills",
                        "--dry-run",
                    ]
                )
        bootstrap.assert_not_called()


if __name__ == "__main__":
    unittest.main()
