from __future__ import annotations

import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "long-running-goal"
SKILL = SKILL_DIR / "SKILL.md"
REFERENCES = {
    "create": SKILL_DIR / "references" / "create-and-loop.md",
    "cutover": SKILL_DIR / "references" / "production-cutover.md",
    "execute": SKILL_DIR / "references" / "execute-and-close.md",
}


class LongRunningGoalDisclosureTests(unittest.TestCase):
    def test_high_risk_contracts_remain_inline(self) -> None:
        text = SKILL.read_text(encoding="utf-8")

        for heading in (
            "## Request Supersession Guard",
            "## Goal File And Template",
            "## Components",
            "## Pre-Approval And YOLO Boundary",
            "## Codex Goal Tool Boundary",
            "## Quality Bar",
        ):
            self.assertIn(heading, text)
        self.assertIn("only at a runtime hard stop", text)
        self.assertIn("Use Codex goal tools only when the user explicitly asks", text)
        self.assertIn("do not mark the goal `Ready` while placeholders remain", text)
        self.assertIn("After creating, upgrading, or evolving a goal, update only the current docs", text)
        self.assertLessEqual(len(text.splitlines()), 125)

    def test_each_conditional_branch_has_a_strong_pointer_and_completion_criterion(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")

        for relative_path in (
            "references/create-and-loop.md",
            "references/production-cutover.md",
            "references/execute-and-close.md",
        ):
            self.assertIn(relative_path, skill)
        for trigger in ("create or upgrade", "Loop-shaped", "production cutover", "execute, resume, continue, advance, evolve, or close"):
            self.assertIn(trigger, skill)
        for moved_heading in (
            "## Create Or Upgrade",
            "## Loop Blueprint Harness",
            "## Production Cutover Gate",
            "## Execute, Checkpoint, And Evolve",
            "## Current Docs And Close",
        ):
            self.assertNotIn(moved_heading, skill)

        for reference in REFERENCES.values():
            text = reference.read_text(encoding="utf-8")
            self.assertIn("Completion criterion:", text)

        create = REFERENCES["create"].read_text(encoding="utf-8")
        self.assertIn("Trigger:", create)
        self.assertIn("Connector read/write boundaries:", create)
        execute = REFERENCES["execute"].read_text(encoding="utf-8")
        self.assertIn("Apply `../components/checkpoint.md`", execute)
        self.assertIn("Remove closed goals from active navigation", execute)
        cutover = REFERENCES["cutover"].read_text(encoding="utf-8")
        self.assertIn("default/full-shadow/production comparison matrix", cutover)


if __name__ == "__main__":
    unittest.main()
