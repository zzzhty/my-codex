from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "doc-alignment"
SKILL = SKILL_DIR / "SKILL.md"
ALIGNMENT = SKILL_DIR / "references" / "alignment-reference.md"
WATCHER_AUDIT = SKILL_DIR / "references" / "watcher-audit.md"
WATCHER = SKILL_DIR.parents[1] / ".codex-plugin" / "skill-watcher.json"


class DocAlignmentDisclosureTests(unittest.TestCase):
    def test_entry_interface_keeps_mode_safety_and_one_level_pointers(self) -> None:
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn(
            "Scheduled Watcher doc audits must keep target repositories read-only",
            text,
        )
        self.assertIn("Use implementation mode when the user asks", text)
        self.assertIn("Fix root causes before claiming alignment", text)
        self.assertIn("references/watcher-audit.md", text)
        self.assertIn("references/alignment-reference.md", text)
        self.assertIn("report-only work must leave target repositories unchanged", text)
        self.assertIn("every triggered reference completion criterion", text)

    def test_watcher_audit_reference_is_complete_for_operations_branch(self) -> None:
        text = WATCHER_AUDIT.read_text(encoding="utf-8")

        self.assertIn("Trigger:", text)
        self.assertIn("scripts/watcher doc doctor", text)
        self.assertIn("scripts/watcher doc commit-counter", text)
        self.assertIn("scripts/watcher doc report", text)
        self.assertIn("scripts/watcher doc audit", text)
        self.assertIn("owner-command", text)
        self.assertIn("authority_paths", text)
        self.assertIn("commit-dependent", text)
        self.assertIn("Completion criterion:", text)

    def test_alignment_reference_owns_classification_surfaces_and_validation(self) -> None:
        text = ALIGNMENT.read_text(encoding="utf-8")

        for role in (
            "**Overview**",
            "**Guide**",
            "**Architecture / Contract**",
            "**Archive**",
            "**Script / Runner**",
            "**Skill**",
        ):
            self.assertIn(role, text)
        for severity in ("`High`", "`Medium`", "`Low`"):
            self.assertIn(severity, text)
        for semantic in (
            "runtime checks: `check_<target>`",
            "Root docs are current overview and execution entry points only",
            "Active index files are navigation and execution posture",
            "Keep `SKILL.md` frontmatter to `name` and `description`",
            "Match validation to the changed surface",
        ):
            self.assertIn(semantic, text)
        self.assertIn("python3 -m compileall -q scripts/watcher_runtime", text)
        self.assertGreaterEqual(text.count("Completion criterion:"), 6)

    def test_callable_and_watcher_identities_remain_unchanged(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        watcher = json.loads(WATCHER.read_text(encoding="utf-8"))

        self.assertIn("name: doc-alignment", skill)
        self.assertIn("watcher:doc-alignment", watcher["skills"])
        aliases = {
            item["value"]
            for item in watcher["skills"]["watcher:doc-alignment"]["aliases"]
        }
        self.assertIn("doc-alignment", aliases)
        self.assertIn("documentation alignment", aliases)


if __name__ == "__main__":
    unittest.main()
