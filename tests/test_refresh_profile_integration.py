from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import refresh_my_codex as refresh  # noqa: E402
from check_skill_discovery import PluginListRow  # noqa: E402
from repo_skill_catalog import load_repo_skill_catalog  # noqa: E402


def write_skill(root: Path, plugin: str, name: str) -> None:
    skill_root = root / "plugins" / plugin / "skills" / name
    skill_root.mkdir(parents=True)
    skill_root.joinpath("SKILL.md").write_text(
        f"---\nname: {name}\ndescription: fixture\n---\n",
        encoding="utf-8",
    )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


class ProfileFixture:
    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.codex_home = root / "codex"
        self.target = root / "agents" / "skills"
        self.enabled: set[str] = set()
        self.events: list[str] = []
        self.bad_cached_identity: str | None = None
        for plugin, skill in (("alpha", "one"), ("beta", "two")):
            write_skill(self.repo, plugin, skill)
            write_json(
                self.repo / "plugins" / plugin / ".codex-plugin" / "plugin.json",
                {"name": plugin, "version": "1.0.0", "skills": "./skills/"},
            )
        write_json(
            self.repo / ".agents" / "plugins" / "marketplace.json",
            {
                "name": "test",
                "plugins": [
                    {
                        "name": plugin,
                        "source": {"source": "local", "path": f"./plugins/{plugin}"},
                        "policy": {
                            "installation": "AVAILABLE",
                            "authentication": "ON_INSTALL",
                        },
                    }
                    for plugin in ("alpha", "beta")
                ],
            },
        )
        write_json(
            self.repo / ".agents" / "plugins" / "install-manifest.json",
            {
                "schemaVersion": 2,
                "discoveryProfile": "plugin",
                "marketplace": "test",
                "plugins": [
                    {"name": plugin, "install": True, "check": True}
                    for plugin in ("alpha", "beta")
                ],
            },
        )
        self.catalog = load_repo_skill_catalog(self.repo)

    def configure_plugins(self) -> None:
        self.codex_home.mkdir(parents=True, exist_ok=True)
        self.codex_home.joinpath("config.toml").write_text(
            '\n'.join(
                f'[plugins."{name}@test"]\nenabled = true'
                for name in sorted(self.enabled)
            ),
            encoding="utf-8",
        )

    def rows(self, _codex: str, *, env: dict[str, str]) -> dict[tuple[str, str], PluginListRow]:
        del env
        return {
            ("test", name): PluginListRow("installed, enabled", "1.0.0")
            for name in self.enabled
        }

    def _write_cache(self, plugin: str) -> None:
        version_root = self.codex_home / "plugins" / "cache" / "test" / plugin / "1.0.0"
        write_json(
            version_root / ".codex-plugin" / "plugin.json",
            {"name": plugin, "version": "1.0.0"},
        )
        canonical = next(source for source in self.catalog.sources if source.plugin == plugin)
        cached_name = "wrong-identity" if self.bad_cached_identity == plugin else canonical.name
        cached_skill = version_root / "skills" / canonical.directory_name
        cached_skill.mkdir(parents=True, exist_ok=True)
        cached_skill.joinpath("SKILL.md").write_text(
            f"---\nname: {cached_name}\ndescription: cached fixture\n---\n",
            encoding="utf-8",
        )

    def run(self, command: list[str], *, env: dict[str, str], dry_run: bool, check: bool = True) -> int:
        del env, check
        selector = command[-1]
        plugin = selector.split("@", 1)[0]
        action = command[2]
        self.events.append(f"{action}:{plugin}")
        if dry_run:
            return 0
        if action == "add":
            self.enabled.add(plugin)
            self._write_cache(plugin)
        elif action == "remove":
            self.enabled.discard(plugin)
        else:  # pragma: no cover - fixture contract
            raise AssertionError(command)
        return 0


class RefreshProfileIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.fixture = ProfileFixture(Path(self._tmp.name))
        self.addCleanup(self._tmp.cleanup)

    def patches(self):
        return (
            mock.patch.object(refresh, "read_codex_plugin_rows", side_effect=self.fixture.rows),
            mock.patch.object(refresh, "run", side_effect=self.fixture.run),
        )

    def run_pruning_main(self) -> None:
        arguments = [
            "refresh_my_codex.py",
            "--discovery-profile",
            "plugin",
            "--marketplace-name",
            "test",
            "--marketplace-source",
            str(self.fixture.repo),
            "--codex-home",
            str(self.fixture.codex_home),
            "--agents-skills-root",
            str(self.fixture.target),
            "--dry-run",
            "--prune-plugins",
            "--skip-bootstrap",
            "--skip-agents",
            "--skip-hooks",
            "--skip-doctor",
        ]
        rows_patch, run_patch = self.patches()
        with (
            mock.patch.object(sys, "argv", arguments),
            mock.patch.object(refresh, "load_repo_skill_catalog", return_value=self.fixture.catalog),
            mock.patch.object(refresh, "resolve_codex_executable", return_value="codex"),
            mock.patch.object(refresh, "require_codex_plugin_commands"),
            mock.patch.object(
                refresh,
                "ensure_marketplace_source",
                return_value=refresh.MarketplaceSourceBinding(
                    "local",
                    str(self.fixture.repo),
                ),
            ),
            rows_patch,
            run_patch,
        ):
            refresh.main()

    def test_install_manifest_is_explicitly_owned_by_plugin_profile(self) -> None:
        manifest = self.fixture.repo / ".agents" / "plugins" / "install-manifest.json"
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload.pop("discoveryProfile")
        write_json(manifest, payload)

        with self.assertRaisesRegex(SystemExit, "discoveryProfile must be 'plugin'"):
            refresh.load_install_manifest(manifest)

        payload["schemaVersion"] = 1
        payload["discoveryProfile"] = "plugin"
        write_json(manifest, payload)
        with self.assertRaisesRegex(SystemExit, "schemaVersion must be 2"):
            refresh.load_install_manifest(manifest)

    def test_plugin_apply_rejects_a_marketplace_source_other_than_the_validated_checkout(self) -> None:
        with self.assertRaisesRegex(
            SystemExit,
            "local marketplace source is not the validated canonical checkout",
        ):
            refresh.apply_plugin_discovery_profile(
                self.fixture.catalog,
                codex="codex",
                codex_home=self.fixture.codex_home,
                marketplace_name="test",
                target_root=self.fixture.target,
                requested_plugins=None,
                marketplace_source_binding=refresh.MarketplaceSourceBinding(
                    "local",
                    str(self.fixture.repo.parent / "alternate"),
                ),
                env={},
                dry_run=False,
            )

    def test_git_marketplace_binding_requires_canonical_remote_and_exact_revision(self) -> None:
        with (
            mock.patch.object(refresh, "git_remote_source", return_value="git@example/repo.git"),
            mock.patch.object(refresh, "git_worktree_clean", return_value=(True, "clean")),
            mock.patch.object(refresh, "git_head_revision", return_value="abc123"),
        ):
            self.assertEqual(
                refresh.marketplace_source_binding_issues(
                    self.fixture.catalog,
                    refresh.MarketplaceSourceBinding(
                        "git",
                        "git@example/repo.git",
                        "abc123",
                    ),
                ),
                [],
            )
            wrong_source = refresh.marketplace_source_binding_issues(
                self.fixture.catalog,
                refresh.MarketplaceSourceBinding(
                    "git",
                    "git@example/other.git",
                    "abc123",
                ),
            )
            wrong_revision = refresh.marketplace_source_binding_issues(
                self.fixture.catalog,
                refresh.MarketplaceSourceBinding(
                    "git",
                    "git@example/repo.git",
                    "different",
                ),
            )

        self.assertIn("not the canonical checkout remote", "\n".join(wrong_source))
        self.assertIn("not pinned to the validated checkout revision", "\n".join(wrong_revision))

    def test_round_trip_preserves_exactly_one_active_discovery_profile(self) -> None:
        self.fixture.enabled.update({"alpha", "beta"})
        self.fixture.configure_plugins()
        rows_patch, run_patch = self.patches()
        with rows_patch, run_patch:
            refresh.apply_universal_discovery_profile(
                self.fixture.catalog,
                codex="codex",
                codex_home=self.fixture.codex_home,
                marketplace_name="test",
                target_root=self.fixture.target,
                env={},
                dry_run=False,
            )
            self.assertEqual(self.fixture.enabled, set())
            self.assertEqual(
                {path.name for path in self.fixture.target.iterdir()},
                {"one", "two"},
            )

            refresh.apply_plugin_discovery_profile(
                self.fixture.catalog,
                codex="codex",
                codex_home=self.fixture.codex_home,
                marketplace_name="test",
                target_root=self.fixture.target,
                requested_plugins=None,
                marketplace_source_binding=refresh.MarketplaceSourceBinding(
                    "local",
                    str(self.fixture.repo),
                ),
                env={},
                dry_run=False,
            )

        self.assertEqual(self.fixture.enabled, {"alpha", "beta"})
        self.assertFalse(self.fixture.target.exists() and any(self.fixture.target.iterdir()))
        self.assertEqual(
            self.fixture.events,
            ["remove:alpha", "remove:beta", "add:alpha", "add:beta"],
        )

    def test_plugin_closure_failure_restores_universal_links_and_removes_partial_plugins(self) -> None:
        refresh.sync_layer(
            self.fixture.catalog,
            target_root=self.fixture.target,
            dry_run=False,
            prune=True,
        )
        self.fixture.bad_cached_identity = "beta"
        rows_patch, run_patch = self.patches()
        with rows_patch, run_patch:
            with self.assertRaisesRegex(SystemExit, "cached callable identities differ"):
                refresh.apply_plugin_discovery_profile(
                    self.fixture.catalog,
                    codex="codex",
                    codex_home=self.fixture.codex_home,
                    marketplace_name="test",
                    target_root=self.fixture.target,
                    requested_plugins=None,
                    marketplace_source_binding=refresh.MarketplaceSourceBinding(
                        "local",
                        str(self.fixture.repo),
                    ),
                    env={},
                    dry_run=False,
                )

        self.assertEqual(self.fixture.enabled, set())
        self.assertEqual(
            {path.name for path in self.fixture.target.iterdir()},
            {"one", "two"},
        )
        self.assertEqual(
            self.fixture.events,
            ["add:alpha", "add:beta", "remove:beta", "remove:alpha"],
        )

    def test_plugin_selector_cannot_escape_the_selected_marketplace_or_catalog(self) -> None:
        rows_patch, run_patch = self.patches()
        with rows_patch, run_patch:
            with self.assertRaisesRegex(SystemExit, "canonical skills-bearing packages"):
                refresh.apply_plugin_discovery_profile(
                    self.fixture.catalog,
                    codex="codex",
                    codex_home=self.fixture.codex_home,
                    marketplace_name="test",
                    target_root=self.fixture.target,
                    requested_plugins=["alpha@other"],
                    marketplace_source_binding=refresh.MarketplaceSourceBinding(
                        "local",
                        str(self.fixture.repo),
                    ),
                    env={},
                    dry_run=False,
                )
        self.assertEqual(self.fixture.events, [])

    def test_prune_dry_run_reaches_cache_only_stale_plugin_before_full_closure(self) -> None:
        stale_cache = (
            self.fixture.codex_home
            / "plugins"
            / "cache"
            / "test"
            / "retired"
            / "0.9.0"
        )
        stale_cache.mkdir(parents=True)

        with self.assertRaisesRegex(
            SystemExit,
            "cached my-codex plugins have no canonical repository skills: retired",
        ):
            refresh.preflight_plugin_distribution(
                self.fixture.catalog,
                codex_home=self.fixture.codex_home,
                marketplace_name="test",
            )

        self.run_pruning_main()

        self.assertTrue(stale_cache.is_dir())
        self.assertEqual(self.fixture.events, ["add:alpha", "add:beta"])

    def test_prune_dry_run_reaches_enabled_stale_plugin_before_full_closure(self) -> None:
        self.fixture.enabled.add("retired")
        self.fixture.configure_plugins()

        self.run_pruning_main()

        self.assertEqual(
            self.fixture.events,
            ["remove:retired", "add:alpha", "add:beta"],
        )

    def test_prune_never_ignores_cli_only_uninventoried_plugin(self) -> None:
        self.fixture.enabled.add("retired")

        with self.assertRaisesRegex(
            SystemExit,
            "unclassified enabled my-codex plugins.*retired",
        ):
            self.run_pruning_main()

        self.assertEqual(self.fixture.events, [])


if __name__ == "__main__":
    unittest.main()
