from __future__ import annotations

import unittest
from pathlib import Path


WORKFLOW_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKFLOW_ROOT.parents[1]
AGENTS = REPO_ROOT / "AGENTS.md"
SUPPORT = REPO_ROOT / "agents" / "operating-principles.md"
ORCHESTRATE = WORKFLOW_ROOT / "skills" / "orchestrate-subagents" / "SKILL.md"
RECIPES = (
    WORKFLOW_ROOT
    / "skills"
    / "orchestrate-subagents"
    / "references"
    / "subagent-recipes.md"
)


class InstructionOwnershipTests(unittest.TestCase):
    def test_root_owns_global_policy_and_support_note_maps_repository_surfaces(self) -> None:
        root = AGENTS.read_text(encoding="utf-8")
        support = SUPPORT.read_text(encoding="utf-8")

        for semantic in (
            "Surface failures directly",
            "Keep tests focused on behavioral red lines",
            "Use subagents only when",
            "Treat subagent failures as first-class failures",
        ):
            self.assertIn(semantic, root)

        self.assertIn("Root `AGENTS.md` owns global authority", support)
        self.assertIn("Repository-specific support paths and role-label mapping", support)
        self.assertIn("does not invoke `$orchestrate-subagents` by itself", support)
        self.assertIn("scripts/sync_codex_agents.py", support)
        self.assertIn("preserve the user-visible local time", support)
        self.assertIn("verify the written automation state", support)
        self.assertIn("Do not write secrets, full private prompts, full tool responses", support)
        self.assertIn("Memory updates must remain reviewable", support)

    def test_orchestrate_skill_is_a_deep_interface_with_one_level_disclosure(self) -> None:
        skill = ORCHESTRATE.read_text(encoding="utf-8")
        recipes = RECIPES.read_text(encoding="utf-8")

        self.assertIn("name: orchestrate-subagents", skill)
        self.assertIn("references/subagent-recipes.md", skill)
        self.assertIn("## Assignment Contract", recipes)

        for required_entry_semantic in (
            "minimum useful set",
            "parent agent responsible",
            "disjoint",
            "partial",
            "parent independently reviewed",
        ):
            self.assertIn(required_entry_semantic, skill)

        for assignment_field in (
            "Task:",
            "Assignment label:",
            "Single task:",
            "Context:",
            "Ownership:",
            "Expected output:",
            "Stop condition:",
            "Boundaries:",
        ):
            self.assertIn(assignment_field, recipes)

    def test_global_authority_and_local_workflow_delta_are_both_reachable(self) -> None:
        root = AGENTS.read_text(encoding="utf-8")
        skill = ORCHESTRATE.read_text(encoding="utf-8")
        recipes = RECIPES.read_text(encoding="utf-8")

        self.assertIn("Use subagents only when", root)
        self.assertIn("explicitly asks", skill)
        self.assertIn("one primary verb", recipes)
        self.assertIn("exact disjoint write scope", recipes)
        self.assertIn("Do not hide timeouts", recipes)


if __name__ == "__main__":
    unittest.main()
