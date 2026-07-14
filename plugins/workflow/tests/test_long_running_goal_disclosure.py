from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "long-running-goal"
SKILL = SKILL_DIR / "SKILL.md"
REFERENCES = {
    "create": SKILL_DIR / "references" / "create-and-loop.md",
    "sequence": SKILL_DIR / "references" / "sequence-child-goals.md",
    "cutover": SKILL_DIR / "references" / "production-cutover.md",
    "execute": SKILL_DIR / "references" / "execute-and-close.md",
}
SEQUENCE_TEMPLATE = SKILL_DIR / "templates" / "long_running_goal_sequence_template.md"
WATCHER = SKILL_DIR.parents[1] / ".codex-plugin" / "skill-watcher.json"


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
            "references/sequence-child-goals.md",
            "references/production-cutover.md",
            "references/execute-and-close.md",
        ):
            self.assertIn(relative_path, skill)
        for trigger in ("create or upgrade", "Loop-shaped", "Sequence Child Goals", "production cutover", "execute, resume, continue, advance, evolve, or close"):
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

    def test_sequence_branch_discloses_canonical_contract_and_aliases(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        reference = REFERENCES["sequence"].read_text(encoding="utf-8")
        template = SEQUENCE_TEMPLATE.read_text(encoding="utf-8")
        watcher = json.loads(WATCHER.read_text(encoding="utf-8"))

        self.assertIn(
            "scripts/check_goal_sequence.py <sequence-file> [--allow-draft]",
            skill,
        )
        self.assertIn("Long-Running Goal Sequence", reference)
        self.assertIn("one active Codex system goal", reference)
        self.assertIn("Completion criterion:", reference)
        self.assertIn("Done / grill-with-docs", reference)
        self.assertIn("never returns to `Ready` for a per-child authorization", reference)

        self.assertIn("Promotion policy: `automatic-after-close`", template)
        self.assertIn("## Child Preflight Register", template)
        self.assertIn("| Child ID | Marker | Status | Source |", template)
        self.assertIn("## Child Execution Register", template)
        self.assertIn(
            "| Order | Child ID | Parent milestone | Live goal | Closeout evidence | Depends on | State | Current milestone | Close revision |",
            template,
        )
        self.assertIn("sole current-state authority", template)
        self.assertIn("transition evidence historical", template)
        resume = template.split("## Reusable Resume Prompt", 1)[1].split(
            "## Related Documents", 1
        )[0]
        self.assertIn("Child Execution Register", resume)
        self.assertNotIn("<child-a>", resume)
        self.assertNotIn("<child-b>", resume)

        aliases = {
            item["value"]
            for item in watcher["skills"]["workflow:long-running-goal"]["aliases"]
        }
        self.assertIn("long-running goal sequence", aliases)
        self.assertIn("umbrella long-running goal", aliases)


if __name__ == "__main__":
    unittest.main()
