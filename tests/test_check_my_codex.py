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

import check_my_codex  # noqa: E402
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


class PluginValidationCheckRunner(RecordingCheckRunner):
    def __init__(self) -> None:
        super().__init__()
        self.commands: list[list[str]] = []

    def run_command(
        self,
        command: list[str],
        *,
        env: dict[str, str],
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        self.commands.append(command)
        return subprocess.CompletedProcess(command, 0, "validated\n", "")


class PluginValidationRoutingTests(unittest.TestCase):
    def test_matt_package_uses_repo_owned_native_validator(self) -> None:
        runner = PluginValidationCheckRunner()
        runner.check_plugin_validation(
            Path("/tooling/python"),
            ["mattpocock-skills@my-codex"],
            env={},
            validator=Path("/missing/bundled-validator.py"),
        )

        self.assertEqual(runner.failures, 0)
        self.assertEqual(
            runner.commands,
            [
                [
                    "/tooling/python",
                    str(REPO_ROOT / "scripts" / "update_mattpocock_skills.py"),
                    "--validate-only",
                ]
            ],
        )

    def test_other_plugins_keep_bundled_validator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            validator = Path(tmp) / "validate_plugin.py"
            validator.write_text("# fixture\n", encoding="utf-8")
            runner = PluginValidationCheckRunner()
            runner.check_plugin_validation(
                Path("/tooling/python"),
                ["watcher@my-codex", "mattpocock-skills@my-codex"],
                env={},
                validator=validator,
            )

        self.assertEqual(runner.failures, 0)
        self.assertEqual(
            runner.commands[0],
            [
                "/tooling/python",
                str(validator),
                str(REPO_ROOT / "plugins" / "watcher"),
            ],
        )
        self.assertEqual(
            runner.commands[1],
            [
                "/tooling/python",
                str(REPO_ROOT / "scripts" / "update_mattpocock_skills.py"),
                "--validate-only",
            ],
        )


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


class PluginSelectionScopeTests(unittest.TestCase):
    def test_filtered_checks_keep_full_manifest_scope_for_stale_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install_manifest = root / "install-manifest.json"
            marketplace = root / "marketplace.json"
            plugin_names = ("watcher", "workflow", "mattpocock-skills")
            install_manifest.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "marketplace": "my-codex",
                        "plugins": [
                            {"name": name, "install": True, "check": True}
                            for name in plugin_names
                        ],
                    }
                ),
                encoding="utf-8",
            )
            marketplace.write_text(
                json.dumps(
                    {
                        "name": "my-codex",
                        "plugins": [{"name": name} for name in plugin_names],
                    }
                ),
                encoding="utf-8",
            )

            plugins_to_check, desired_plugins = check_my_codex.plugin_check_scopes(
                ["watcher"],
                "my-codex",
                manifest_file=install_manifest,
                marketplace_file=marketplace,
            )

        self.assertEqual(plugins_to_check, ["watcher@my-codex"])
        self.assertEqual(
            desired_plugins,
            [
                "watcher@my-codex",
                "workflow@my-codex",
                "mattpocock-skills@my-codex",
            ],
        )


if __name__ == "__main__":
    unittest.main()
