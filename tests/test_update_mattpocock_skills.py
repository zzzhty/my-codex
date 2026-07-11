from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT_SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(ROOT_SCRIPTS))

import update_mattpocock_skills as updater  # noqa: E402


class MattPocockUpdaterTests(unittest.TestCase):
    def test_repo_owned_entrypoint_targets_existing_plugin(self) -> None:
        self.assertEqual(updater.repo_root(), REPO_ROOT)
        self.assertEqual(
            updater.target_plugin_root(),
            REPO_ROOT / "plugins" / "mattpocock-skills",
        )
        self.assertTrue(updater.target_plugin_root().is_dir())

    def test_sync_from_source_replaces_target_and_regenerates_owned_artifacts(self) -> None:
        upstream_phrase = (
            "The issue tracker and triage label vocabulary should have been provided to you — "
            "run `/setup-matt-pocock-skills` if not."
        )
        skill_text = (
            "---\n"
            "name: diagnosing-bugs\n"
            "description: Diagnose bugs.\n"
            "argument-hint: Describe the bug.\n"
            "disable-model-invocation: true\n"
            "---\n\n"
            f"{upstream_phrase}\n"
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repository = root / "repo"
            source = root / "upstream"
            plugin = repository / "plugins" / "mattpocock-skills"

            upstream_manifest = source / ".claude-plugin" / "plugin.json"
            upstream_manifest.parent.mkdir(parents=True)
            upstream_manifest.write_text(
                json.dumps(
                    {
                        "name": "mattpocock-skills",
                        "skills": [
                            "./skills/engineering/diagnosing-bugs",
                            "./skills/productivity/setup-matt-pocock-skills",
                            "./skills/productivity/teach",
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (source / "LICENSE").write_text("MIT\n", encoding="utf-8")

            diagnosing = source / "skills" / "engineering" / "diagnosing-bugs"
            diagnosing.mkdir(parents=True)
            (diagnosing / "SKILL.md").write_text(skill_text, encoding="utf-8")

            setup = source / "skills" / "productivity" / "setup-matt-pocock-skills"
            setup.mkdir(parents=True)
            (setup / "SKILL.md").write_text("# Claude setup\n", encoding="utf-8")

            teach = source / "skills" / "productivity" / "teach"
            teach.mkdir(parents=True)
            (teach / "SKILL.md").write_text(
                "---\nname: teach\ndescription: Teach the user.\n---\n\n# Teach\n",
                encoding="utf-8",
            )

            manifest = plugin / ".codex-plugin" / "plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                json.dumps(
                    {
                        "name": "mattpocock-skills",
                        "version": "1.0.1+codex.old-token",
                        "interface": {},
                    }
                ),
                encoding="utf-8",
            )
            stale_skill = plugin / "skills" / "removed-upstream-skill"
            stale_skill.mkdir(parents=True)
            (stale_skill / "SKILL.md").write_text("# stale\n", encoding="utf-8")

            with (
                mock.patch.object(updater, "repo_root", return_value=repository),
                mock.patch.object(updater, "target_plugin_root", return_value=plugin),
            ):
                skills, omitted = updater.sync_from_source(
                    source,
                    tag="v1.0.2",
                    commit="0123456789abcdef",
                    cachebuster=False,
                    run_validation=False,
                )

            self.assertEqual(skills, ["diagnosing-bugs", "teach"])
            self.assertEqual(omitted, ["setup-matt-pocock-skills"])
            self.assertEqual(
                {path.name for path in (plugin / "skills").iterdir()},
                {"diagnosing-bugs", "teach"},
            )

            copied_skill = (plugin / "skills" / "diagnosing-bugs" / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("argument-hint", copied_skill)
            self.assertNotIn("disable-model-invocation", copied_skill)
            self.assertNotIn("/setup-matt-pocock-skills", copied_skill)
            self.assertIn("current repo conventions", copied_skill)
            self.assertIn(upstream_phrase, (diagnosing / "SKILL.md").read_text(encoding="utf-8"))

            plugin_manifest = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(plugin_manifest["version"], "1.0.2+codex.old-token")

            metadata = json.loads(
                (plugin / ".codex-plugin" / "skill-watcher.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                metadata["legacy_names"]["mattpocock-skills:diagnose"],
                "mattpocock-skills:diagnosing-bugs",
            )
            teach_alias_values = [
                alias["value"]
                for alias in metadata["skills"]["mattpocock-skills:teach"]["aliases"]
            ]
            self.assertIn("teach me", teach_alias_values)
            self.assertNotIn("teach", teach_alias_values)

            readme = (plugin / "README.md").read_text(encoding="utf-8")
            self.assertIn("python scripts/update_mattpocock_skills.py", readme)
            self.assertIn("`v1.0.2` (`0123456789abcdef`)", readme)
            self.assertEqual((plugin / "LICENSE").read_text(encoding="utf-8"), "MIT\n")

    def test_sync_refuses_target_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repository = root / "repo"
            outside_plugin = root / "outside-plugin"
            outside_plugin.mkdir(parents=True)
            sentinel = outside_plugin / "keep.txt"
            sentinel.write_text("keep\n", encoding="utf-8")

            with (
                mock.patch.object(updater, "repo_root", return_value=repository),
                mock.patch.object(updater, "target_plugin_root", return_value=outside_plugin),
                self.assertRaises(SystemExit) as raised,
            ):
                updater.sync_from_source(
                    root / "unused-upstream",
                    tag="v1.0.2",
                    commit="unused",
                    cachebuster=False,
                    run_validation=False,
                )

            self.assertIn("outside expected parent", str(raised.exception))
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")

    def test_cachebuster_uses_configured_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / "custom-codex-home"
            helper = (
                codex_home
                / "skills"
                / ".system"
                / "plugin-creator"
                / "scripts"
                / "update_plugin_cachebuster.py"
            )
            helper.parent.mkdir(parents=True)
            helper.write_text("# test helper\n", encoding="utf-8")
            plugin = root / "plugin"

            with (
                mock.patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}, clear=False),
                mock.patch.object(updater, "run", return_value="") as run_command,
            ):
                updater.run_cachebuster(plugin)

            run_command.assert_called_once_with(
                [sys.executable, str(helper), str(plugin)]
            )


if __name__ == "__main__":
    unittest.main()
