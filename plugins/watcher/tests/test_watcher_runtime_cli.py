from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
DOC_SCRIPTS = SCRIPTS / "doc"
ROOT_SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(ROOT_SCRIPTS))
sys.path.insert(0, str(DOC_SCRIPTS))
sys.path.insert(0, str(SCRIPTS))

import audit_repo  # noqa: E402
import audit_runtime  # noqa: E402
import watcher_cli  # noqa: E402
from refresh_my_codex import cached_plugin_names, prune_stale_plugins  # noqa: E402


class WatcherRuntimeCliTests(unittest.TestCase):
    def test_cli_dispatches_skill_report_to_existing_script(self) -> None:
        calls: list[list[str]] = []

        def fake_run(command: list[str]) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            return subprocess.CompletedProcess(command, 0)

        with mock.patch("watcher_cli.subprocess.run", fake_run):
            exit_code = watcher_cli.main(["skill", "report", "--since", "7d"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(calls[0][0], sys.executable)
        self.assertEqual(Path(calls[0][1]).name, "generate_report.py")
        self.assertEqual(Path(calls[0][1]).parent.name, "skill")
        self.assertEqual(calls[0][2:], ["--since", "7d"])

    def test_cli_dispatches_doc_report_to_existing_script(self) -> None:
        calls: list[list[str]] = []

        def fake_run(command: list[str]) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            return subprocess.CompletedProcess(command, 0)

        with mock.patch("watcher_cli.subprocess.run", fake_run):
            exit_code = watcher_cli.main(["doc", "report", "--digest"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(Path(calls[0][1]).name, "generate_report.py")
        self.assertEqual(Path(calls[0][1]).parent.name, "doc")
        self.assertEqual(calls[0][2:], ["--digest"])

    def test_migrate_state_defaults_to_dry_run_without_moving(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp)
            source = codex_home / "skill-watcher"
            source.mkdir()
            (source / "logs").mkdir()

            exit_code = watcher_cli.run_migrate_state(["--domain", "skill", "--codex-home", str(codex_home)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(source.is_dir())
            self.assertFalse((codex_home / "watcher" / "skill").exists())

    def test_migrate_state_apply_moves_without_copy_or_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp)
            source = codex_home / "skill-watcher"
            source.mkdir()
            (source / "logs").mkdir()

            exit_code = watcher_cli.run_migrate_state(
                ["--domain", "skill", "--codex-home", str(codex_home), "--apply"]
            )

            self.assertEqual(exit_code, 0)
            self.assertFalse(source.exists())
            self.assertTrue((codex_home / "watcher" / "skill" / "logs").is_dir())

    def test_migrate_state_fails_when_target_already_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp)
            source = codex_home / "doc-watcher"
            target = codex_home / "watcher" / "doc"
            source.mkdir()
            target.mkdir(parents=True)

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = watcher_cli.run_migrate_state(
                    ["--domain", "doc", "--codex-home", str(codex_home), "--apply"]
                )

            self.assertEqual(exit_code, 1)
            self.assertTrue(source.is_dir())
            self.assertTrue(target.is_dir())
            self.assertIn("refusing to merge", stderr.getvalue())

    def test_migrate_state_rejects_dry_run_and_apply_together(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            watcher_cli.run_migrate_state(["--dry-run", "--apply"])

        self.assertIn("choose only one", str(raised.exception))

    def test_doc_runtime_uses_watcher_doc_env_and_ignores_old_doc_watcher_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / "current-doc-state"
            legacy = root / "legacy-doc-state"
            default = root / "default-doc-state"

            with mock.patch.dict(
                "os.environ",
                {
                    "WATCHER_DOC_STATE_DIR": str(current),
                    "DOC_WATCHER_STATE_DIR": str(legacy),
                },
                clear=True,
            ):
                self.assertEqual(audit_repo.resolve_state_dir(None), current)
                self.assertEqual(audit_runtime.resolve_audit_state_dir(), current)

            with mock.patch.dict("os.environ", {"DOC_WATCHER_STATE_DIR": str(legacy)}, clear=True):
                with mock.patch("audit_repo.DEFAULT_STATE_DIR", default):
                    self.assertEqual(audit_repo.resolve_state_dir(None), default)

    def test_prune_stale_plugins_removes_cache_only_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp)
            config = codex_home / "config.toml"
            config.write_text(
                "\n".join(
                    [
                        '[plugins."old-plugin@my-codex"]',
                        "enabled = true",
                        '[plugins."workflow@my-codex"]',
                        "enabled = true",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            cache_root = codex_home / "plugins" / "cache" / "my-codex"
            (cache_root / "cached-only" / "0.1.0").mkdir(parents=True)
            calls: list[list[str]] = []

            def fake_run(command, *, env, dry_run, check=True):  # type: ignore[no-untyped-def]
                calls.append(command)
                return 0

            with mock.patch("refresh_my_codex.run", fake_run):
                prune_stale_plugins(
                    "codex",
                    codex_home=codex_home,
                    marketplace_name="my-codex",
                    desired_plugin_names=["workflow"],
                    env={},
                    dry_run=False,
                )

            self.assertEqual(calls, [["codex", "plugin", "remove", "old-plugin@my-codex"]])
            self.assertEqual(cached_plugin_names(codex_home, "my-codex"), set())


if __name__ == "__main__":
    unittest.main()
