from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT_SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(ROOT_SCRIPTS))

from check_my_codex import CheckRunner  # noqa: E402


def write_manifest(path: Path, *, name: str, version: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"name": name, "version": version}) + "\n",
        encoding="utf-8",
    )


class RecordingCheckRunner(CheckRunner):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def ok(self, message: str) -> None:
        self.messages.append(f"OK {message}")

    def fail(self, message: str) -> None:
        self.failures += 1
        self.messages.append(f"FAIL {message}")


class PluginListCheckRunner(RecordingCheckRunner):
    def __init__(self, output: str) -> None:
        super().__init__()
        self.output = output

    def run_command(
        self,
        command: list[str],
        *,
        env: dict[str, str],
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, self.output, "")


class MarketplaceCatalogIdentityTests(unittest.TestCase):
    def test_marketplace_source_path_is_the_identity_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_root = Path(tmp)
            plugin_dir = source_root / "catalog-sources" / "renamed-package-dir"
            write_manifest(
                plugin_dir / ".codex-plugin" / "plugin.json",
                name="demo",
                version="1.2.3",
            )
            marketplace = source_root / ".agents" / "plugins" / "marketplace.json"
            marketplace.parent.mkdir(parents=True)
            marketplace.write_text(
                json.dumps(
                    {
                        "name": "my-codex",
                        "plugins": [
                            {
                                "name": "demo",
                                "source": {
                                    "source": "local",
                                    "path": "./catalog-sources/renamed-package-dir",
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            runner = RecordingCheckRunner()
            sources = runner.check_marketplace_file(["demo@my-codex"], source_root=source_root)

        self.assertEqual(runner.failures, 0)
        self.assertEqual(sources, {"demo": plugin_dir.resolve()})

    def test_marketplace_rejects_unknown_sources_and_duplicate_names(self) -> None:
        cases = (
            (
                "unknown-source",
                [
                    {
                        "name": "demo",
                        "source": {"source": "git", "path": "./catalog-sources/demo"},
                    }
                ],
                "unsupported marketplace source kind",
            ),
            (
                "duplicate-name",
                [
                    {
                        "name": "demo",
                        "source": {"source": "local", "path": "./catalog-sources/demo"},
                    },
                    {
                        "name": "demo",
                        "source": {"source": "local", "path": "./catalog-sources/demo"},
                    },
                ],
                "duplicate marketplace plugin name",
            ),
        )
        for label, plugins, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                source_root = Path(tmp)
                write_manifest(
                    source_root / "catalog-sources" / "demo" / ".codex-plugin" / "plugin.json",
                    name="demo",
                    version="1.2.3",
                )
                marketplace = source_root / ".agents" / "plugins" / "marketplace.json"
                marketplace.parent.mkdir(parents=True)
                marketplace.write_text(
                    json.dumps({"name": "my-codex", "plugins": plugins}),
                    encoding="utf-8",
                )

                runner = RecordingCheckRunner()
                sources = runner.check_marketplace_file(["demo@my-codex"], source_root=source_root)

            self.assertIsNone(sources)
            self.assertEqual(runner.failures, 1)
            self.assertIn(expected, "\n".join(runner.messages))


class PluginCacheIdentityTests(unittest.TestCase):
    def test_exact_source_cache_identity_allows_stale_sibling_versions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin_dir = root / "catalog-sources" / "demo-package"
            codex_home = root / "codex-home"
            current = "1.2.3+codex.current"
            source_manifest = plugin_dir / ".codex-plugin" / "plugin.json"
            current_cache = (
                codex_home
                / "plugins"
                / "cache"
                / "my-codex"
                / "demo"
                / current
                / ".codex-plugin"
                / "plugin.json"
            )
            stale_cache = (
                codex_home
                / "plugins"
                / "cache"
                / "my-codex"
                / "demo"
                / "1.2.2+codex.old"
                / ".codex-plugin"
                / "plugin.json"
            )
            write_manifest(source_manifest, name="demo", version=current)
            write_manifest(current_cache, name="demo", version=current)
            write_manifest(stale_cache, name="demo", version="1.2.2+codex.old")

            runner = RecordingCheckRunner()
            runner.check_plugin_cache(
                ["demo@my-codex"],
                codex_home=codex_home,
                plugin_sources={"demo": plugin_dir},
            )

        self.assertEqual(runner.failures, 0)
        self.assertTrue(any("source/cache manifest identity" in message for message in runner.messages))

    def test_old_cache_versions_do_not_satisfy_current_source_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin_dir = root / "catalog-sources" / "demo-package"
            codex_home = root / "codex-home"
            current = "1.2.3+codex.current"
            write_manifest(
                plugin_dir / ".codex-plugin" / "plugin.json",
                name="demo",
                version=current,
            )
            for version in ("1.2.1+codex.old", "1.2.2+codex.old"):
                write_manifest(
                    codex_home
                    / "plugins"
                    / "cache"
                    / "my-codex"
                    / "demo"
                    / version
                    / ".codex-plugin"
                    / "plugin.json",
                    name="demo",
                    version=version,
                )

            runner = RecordingCheckRunner()
            runner.check_plugin_cache(
                ["demo@my-codex"],
                codex_home=codex_home,
                plugin_sources={"demo": plugin_dir},
            )

        self.assertEqual(runner.failures, 1)
        self.assertIn(current, "\n".join(runner.messages))
        self.assertIn("exact cache manifest missing", "\n".join(runner.messages))

    def test_source_and_cache_manifest_errors_fail_with_exact_evidence(self) -> None:
        cases = (
            ("source-name", {"source_name": "other"}, "source manifest name mismatch"),
            ("source-json", {"invalid_source_json": True}, "source manifest is not valid JSON"),
            ("cache-name", {"cache_name": "other"}, "cache manifest name mismatch"),
            ("cache-version", {"cache_version": "9.9.9"}, "cache manifest version mismatch"),
            ("cache-json", {"invalid_cache_json": True}, "cache manifest is not valid JSON"),
        )
        for label, overrides, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plugin_dir = root / "catalog-sources" / "demo-package"
                codex_home = root / "codex-home"
                current = "1.2.3+codex.current"
                source_manifest = plugin_dir / ".codex-plugin" / "plugin.json"
                cache_manifest = (
                    codex_home
                    / "plugins"
                    / "cache"
                    / "my-codex"
                    / "demo"
                    / current
                    / ".codex-plugin"
                    / "plugin.json"
                )
                if overrides.get("invalid_source_json"):
                    source_manifest.parent.mkdir(parents=True, exist_ok=True)
                    source_manifest.write_text("{not-json\n", encoding="utf-8")
                else:
                    write_manifest(
                        source_manifest,
                        name=str(overrides.get("source_name", "demo")),
                        version=current,
                    )
                if overrides.get("invalid_cache_json"):
                    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
                    cache_manifest.write_text("{not-json\n", encoding="utf-8")
                else:
                    write_manifest(
                        cache_manifest,
                        name=str(overrides.get("cache_name", "demo")),
                        version=str(overrides.get("cache_version", current)),
                    )

                runner = RecordingCheckRunner()
                runner.check_plugin_cache(
                    ["demo@my-codex"],
                    codex_home=codex_home,
                    plugin_sources={"demo": plugin_dir},
                )

            self.assertEqual(runner.failures, 1)
            self.assertIn(expected, "\n".join(runner.messages))


class PluginInstalledIdentityTests(unittest.TestCase):
    def test_plugin_list_requires_exact_source_version_and_enabled_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_dir = Path(tmp) / "catalog-sources" / "demo-package"
            current = "1.2.3+codex.current"
            write_manifest(
                plugin_dir / ".codex-plugin" / "plugin.json",
                name="demo",
                version=current,
            )
            output = (
                "Marketplace `my-codex`\n"
                "C:\\source\\.agents\\plugins\\marketplace.json\n\n"
                "PLUGIN  STATUS              VERSION                    PATH\n"
                f"demo@my-codex  installed, enabled  {current}  C:\\cache\\demo\n"
            )

            runner = PluginListCheckRunner(output)
            runner.check_codex_plugin_list(
                "codex",
                ["demo@my-codex"],
                env={},
                plugin_sources={"demo": plugin_dir},
            )

        self.assertEqual(runner.failures, 0)
        self.assertTrue(any("source plugin name/version identities" in message for message in runner.messages))

    def test_plugin_list_rejects_installed_version_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_dir = Path(tmp) / "catalog-sources" / "demo-package"
            write_manifest(
                plugin_dir / ".codex-plugin" / "plugin.json",
                name="demo",
                version="1.2.3+codex.current",
            )
            output = (
                "Marketplace `my-codex`\n"
                "C:\\source\\.agents\\plugins\\marketplace.json\n\n"
                "PLUGIN  STATUS              VERSION                  PATH\n"
                "demo@my-codex  installed, enabled  1.2.2+codex.old  C:\\cache\\demo\n"
            )

            runner = PluginListCheckRunner(output)
            runner.check_codex_plugin_list(
                "codex",
                ["demo@my-codex"],
                env={},
                plugin_sources={"demo": plugin_dir},
            )

        self.assertEqual(runner.failures, 1)
        self.assertIn("installed version mismatch", "\n".join(runner.messages))

    def test_plugin_list_rejects_disabled_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_dir = Path(tmp) / "catalog-sources" / "demo-package"
            current = "1.2.3+codex.current"
            write_manifest(
                plugin_dir / ".codex-plugin" / "plugin.json",
                name="demo",
                version=current,
            )
            output = (
                "Marketplace `my-codex`\n"
                "C:\\source\\.agents\\plugins\\marketplace.json\n\n"
                "PLUGIN  STATUS     VERSION                    PATH\n"
                f"demo@my-codex  installed  {current}  C:\\cache\\demo\n"
            )

            runner = PluginListCheckRunner(output)
            runner.check_codex_plugin_list(
                "codex",
                ["demo@my-codex"],
                env={},
                plugin_sources={"demo": plugin_dir},
            )

        self.assertEqual(runner.failures, 1)
        self.assertIn("expected status 'installed, enabled'", "\n".join(runner.messages))


if __name__ == "__main__":
    unittest.main()
