from __future__ import annotations

import contextlib
import errno
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import sync_agents_skills  # noqa: E402


def write_skill(plugin_root: Path, name: str) -> Path:
    skill_dir = plugin_root / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test skill {name}\n---\n",
        encoding="utf-8",
    )
    return skill_dir


class Sandbox:
    """A temporary repository with two plugin directories and three skills."""

    def __init__(self, base: Path) -> None:
        self.repo_root = base / "repo"
        self.alpha_root = self.repo_root / "plugins" / "alpha"
        self.beta_root = self.repo_root / "plugins" / "beta"
        self.foo = write_skill(self.alpha_root, "foo")
        self.bar = write_skill(self.alpha_root, "bar")
        self.baz = write_skill(self.beta_root, "baz")
        self.target_root = base / "agents" / "skills"
        self.catalog = sync_agents_skills.load_repo_skill_catalog(self.repo_root)


class SyncLayerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.sandbox = Sandbox(Path(self._tmp.name))
        self.addCleanup(self._tmp.cleanup)

    def test_sync_creates_links_and_is_idempotent(self) -> None:
        status = sync_agents_skills.sync_layer(
            self.sandbox.catalog, target_root=self.sandbox.target_root,
            dry_run=False, prune=True,
        )
        self.assertEqual(status, 0)
        for source in self.sandbox.catalog.sources:
            link = self.sandbox.target_root / source.name
            self.assertTrue(link.is_symlink(), link)
            self.assertEqual(link.resolve(), source.path.resolve())

        again = sync_agents_skills.sync_layer(
            self.sandbox.catalog, target_root=self.sandbox.target_root,
            dry_run=False, prune=True,
        )
        self.assertEqual(again, 0)
        self.assertEqual(
            sorted(path.name for path in self.sandbox.target_root.iterdir()),
            ["bar", "baz", "foo"],
        )

    def test_sync_declares_directory_symlinks_for_cross_platform_projection(self) -> None:
        with mock.patch.object(Path, "symlink_to", autospec=True) as symlink_to:
            with contextlib.redirect_stdout(io.StringIO()):
                status = sync_agents_skills.sync_layer(
                    self.sandbox.catalog,
                    target_root=self.sandbox.target_root,
                    dry_run=False,
                    prune=False,
                )

        self.assertEqual(status, 0)
        self.assertEqual(symlink_to.call_count, len(self.sandbox.catalog.sources))
        for call in symlink_to.call_args_list:
            self.assertEqual(call.kwargs, {"target_is_directory": True})
            self.assertIn(call.args[0].name, {"foo", "bar", "baz"})
            self.assertTrue(call.args[1].is_dir())

    def test_check_detects_missing_drift_and_unmanaged_entries(self) -> None:
        self.assertEqual(
            sync_agents_skills.check_layer(
                self.sandbox.catalog, target_root=self.sandbox.target_root, prune=True
            ),
            1,
        )

        sync_agents_skills.sync_layer(
            self.sandbox.catalog, target_root=self.sandbox.target_root,
            dry_run=False, prune=False,
        )
        # Repoint one managed link at another skill: managed drift.
        (self.sandbox.target_root / "foo").unlink()
        (self.sandbox.target_root / "foo").symlink_to(self.sandbox.bar)
        # Replace one link with an unmanaged real directory.
        (self.sandbox.target_root / "bar").unlink()
        (self.sandbox.target_root / "bar").mkdir()
        report = io.StringIO()
        with contextlib.redirect_stdout(report):
            status = sync_agents_skills.check_layer(
                self.sandbox.catalog, target_root=self.sandbox.target_root, prune=True
            )
        self.assertEqual(status, 1)
        self.assertIn("drift:", report.getvalue())
        self.assertIn("unmanaged-entry:", report.getvalue())

    def test_check_flags_stale_managed_link_only_with_prune(self) -> None:
        sync_agents_skills.sync_layer(
            self.sandbox.catalog, target_root=self.sandbox.target_root,
            dry_run=False, prune=False,
        )
        ghost = self.sandbox.target_root / "ghost"
        ghost.symlink_to(self.sandbox.foo)
        without_prune = sync_agents_skills.check_layer(
            self.sandbox.catalog, target_root=self.sandbox.target_root, prune=False
        )
        self.assertEqual(without_prune, 0)
        with_prune = sync_agents_skills.check_layer(
            self.sandbox.catalog, target_root=self.sandbox.target_root, prune=True
        )
        self.assertEqual(with_prune, 1)

    def test_prune_removes_stale_managed_links_and_keeps_unmanaged_entries(self) -> None:
        target_root = self.sandbox.target_root
        target_root.mkdir(parents=True)
        ghost = target_root / "ghost"
        ghost.symlink_to(self.sandbox.foo)
        user_skill = target_root / "user-skill"
        user_skill.mkdir()
        (user_skill / "SKILL.md").write_text("---\nname: user-skill\n---\n", encoding="utf-8")

        status = sync_agents_skills.sync_layer(
            self.sandbox.catalog, target_root=target_root, dry_run=False, prune=True
        )
        self.assertEqual(status, 0)
        self.assertFalse(ghost.exists() or ghost.is_symlink())
        self.assertTrue(user_skill.is_dir())

    def test_sync_never_replaces_unmanaged_targets(self) -> None:
        target_root = self.sandbox.target_root
        target_root.mkdir(parents=True)
        (target_root / "foo").mkdir()
        (target_root / "bar").write_text("unmanaged file", encoding="utf-8")
        outside = target_root / "outside-note"
        outside.symlink_to(self.sandbox.repo_root / ".agents")

        with self.assertRaises(SystemExit):
            sync_agents_skills.sync_layer(
                self.sandbox.catalog, target_root=target_root, dry_run=False, prune=False
            )

        (target_root / "foo").rmdir()
        with self.assertRaises(SystemExit):
            sync_agents_skills.sync_layer(
                self.sandbox.catalog, target_root=target_root, dry_run=False, prune=False
            )

        (target_root / "bar").unlink()
        status = sync_agents_skills.sync_layer(
            self.sandbox.catalog, target_root=target_root, dry_run=False, prune=False
        )
        self.assertEqual(status, 0)
        self.assertEqual((target_root / "foo").resolve(), self.sandbox.foo.resolve())
        self.assertEqual((target_root / "bar").resolve(), self.sandbox.bar.resolve())
        self.assertEqual((target_root / "baz").resolve(), self.sandbox.baz.resolve())
        self.assertEqual(outside.resolve(), (self.sandbox.repo_root / ".agents").resolve())

    def test_duplicate_skill_names_across_plugins_are_rejected(self) -> None:
        write_skill(self.sandbox.beta_root, "foo")
        with self.assertRaises(SystemExit):
            sync_agents_skills.load_repo_skill_catalog(self.sandbox.repo_root)

    def test_skill_directory_without_skill_file_is_rejected(self) -> None:
        malformed = self.sandbox.alpha_root / "skills" / "malformed"
        malformed.mkdir()
        with self.assertRaises(SystemExit):
            sync_agents_skills.load_repo_skill_catalog(self.sandbox.repo_root)


class RepositoryCatalogTests(unittest.TestCase):
    def test_live_repository_enumerates_the_three_skill_plugins(self) -> None:
        catalog = sync_agents_skills.load_repo_skill_catalog()
        plugins = {source.plugin for source in catalog.sources}
        self.assertEqual(plugins, {"watcher", "workflow", "mattpocock-skills"})
        self.assertGreaterEqual(len(catalog.sources), 30)
        for source in catalog.sources:
            self.assertEqual(source.name, source.path.name)
            self.assertTrue((source.path / "SKILL.md").is_file())

    def test_live_projection_exposes_every_tracked_skill_tree_entry(self) -> None:
        catalog = sync_agents_skills.load_repo_skill_catalog()
        tracked = subprocess.run(
            ["git", "-C", str(catalog.repo_root), "ls-files", "-z", "--", "plugins"],
            check=True,
            capture_output=True,
        ).stdout
        tracked_paths = tuple(
            catalog.repo_root / raw.decode("utf-8")
            for raw in tracked.split(b"\0")
            if raw and b"/skills/" in raw
        )
        with tempfile.TemporaryDirectory() as tmp:
            temporary_root = Path(tmp)
            probe_target = temporary_root / "directory-target"
            probe_link = temporary_root / "directory-link"
            probe_target.mkdir()
            try:
                probe_link.symlink_to(probe_target, target_is_directory=True)
            except NotImplementedError as exc:  # pragma: no cover - unsupported platform boundary
                self.skipTest(f"directory symlinks unavailable: {exc}")
            except OSError as exc:  # pragma: no cover - platform/filesystem capability boundary
                unsupported_errnos = {
                    code
                    for code in (
                        getattr(errno, "ENOSYS", None),
                        getattr(errno, "ENOTSUP", None),
                        getattr(errno, "EOPNOTSUPP", None),
                    )
                    if code is not None
                }
                if getattr(exc, "winerror", None) in {1, 50, 1314} or exc.errno in unsupported_errnos:
                    self.skipTest(f"directory symlinks unavailable: {exc}")
                raise
            probe_link.unlink()

            target_root = temporary_root / "agents" / "skills"
            with contextlib.redirect_stdout(io.StringIO()):
                status = sync_agents_skills.sync_layer(
                    catalog,
                    target_root=target_root,
                    dry_run=False,
                    prune=True,
                )
            self.assertEqual(status, 0)

            checked_entries = 0
            for source in catalog.sources:
                projected_root = target_root / source.name
                self.assertTrue(projected_root.is_symlink(), projected_root)
                self.assertEqual(projected_root.resolve(strict=True), source.path)
                source_entries = tuple(
                    path for path in tracked_paths if path.is_relative_to(source.path)
                )
                self.assertTrue(source_entries, source.path)
                for source_entry in source_entries:
                    relative = source_entry.relative_to(source.path)
                    projected_entry = projected_root / relative
                    resolved_source = source_entry.resolve(strict=True)
                    resolved_source.relative_to(catalog.repo_root)
                    self.assertEqual(projected_entry.resolve(strict=True), resolved_source)
                    checked_entries += 1

        self.assertEqual(checked_entries, len(tracked_paths))
        self.assertGreater(checked_entries, len(catalog.sources))


if __name__ == "__main__":
    unittest.main()
