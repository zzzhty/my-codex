from __future__ import annotations

import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "doc-alignment"
SKILL = SKILL_DIR / "SKILL.md"
REFERENCE = SKILL_DIR / "references" / "alignment-reference.md"


class DocAlignmentDisclosureTests(unittest.TestCase):
    def test_common_and_safety_contracts_remain_inline(self) -> None:
        text = SKILL.read_text(encoding="utf-8")

        for heading in (
            "## Core Contract",
            "## Mode Selection",
            "## Watcher Doc Audit Workflow",
            "## Review Workflow",
            "## Finding Severity",
            "## Final Report",
        ):
            self.assertIn(heading, text)
        self.assertIn("Scheduled Watcher doc audits must keep target repositories read-only", text)
        self.assertIn("Use implementation mode when the user asks", text)
        self.assertIn("Fix root causes before claiming alignment", text)
        self.assertLessEqual(len(text.splitlines()), 120)

    def test_branch_reference_is_explicit_and_complete(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        reference = REFERENCE.read_text(encoding="utf-8")

        self.assertIn("references/alignment-reference.md", skill)
        for trigger in ("script or entry-point", "documentation tree", "planning/TODO", "agent skill", "validation"):
            self.assertIn(trigger, skill)
        for moved_heading in (
            "## Script And Entry-Point Naming",
            "## Documentation Tree Alignment",
            "## Planning/TODO Tree Alignment",
            "## Skill Alignment",
            "## Validation",
        ):
            self.assertNotIn(moved_heading, skill)
            self.assertIn(moved_heading, reference)
        self.assertGreaterEqual(reference.count("Completion criterion:"), 5)
        self.assertIn("python3 -m compileall -q scripts/watcher_runtime", reference)


if __name__ == "__main__":
    unittest.main()
