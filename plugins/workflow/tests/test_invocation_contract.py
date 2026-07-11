from __future__ import annotations

import unittest
from pathlib import Path


WORKFLOW_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKFLOW_ROOT.parents[1]
ORCHESTRATE_ROOT = WORKFLOW_ROOT / "skills" / "orchestrate-subagents"


def skill_description(skill_file: Path) -> str:
    for line in skill_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError(f"description missing: {skill_file}")


class InvocationContractTests(unittest.TestCase):
    def test_orchestrate_trigger_is_scoped_to_user_requested_subagents(self) -> None:
        description = skill_description(ORCHESTRATE_ROOT / "SKILL.md")
        metadata = (ORCHESTRATE_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn("explicitly asks", description)
        self.assertIn("subagents", description)
        self.assertIn("parallel agents", description)
        self.assertIn("tool availability", description)
        self.assertNotIn("PR review", description)
        self.assertNotIn("architecture review", description)
        self.assertNotIn("debugging", description)
        self.assertNotIn("migration", description)
        self.assertNotIn("allow_implicit_invocation: false", metadata)
        self.assertIn("user-requested Codex subagents", metadata)

    def test_prompt_strategy_uses_authorized_evaluators_without_cross_invocation(self) -> None:
        prompt_strategy = (
            WORKFLOW_ROOT / "skills" / "prompt-strategy-loop" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("active environment or plan authorizes delegation", prompt_strategy)
        self.assertIn("does not invoke `orchestrate-subagents`", prompt_strategy)
        self.assertIn("stop at an unverified proposal", prompt_strategy)
        self.assertNotIn("current environment exposes subagent tools", prompt_strategy)

    def test_broad_review_delegation_does_not_cross_invoke_orchestrate(self) -> None:
        guidance_files = (
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "agents" / "operating-principles.md",
        )
        old_prompt = "Use $orchestrate-subagents for this read-only review"
        for path in guidance_files:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(old_prompt, text)
                self.assertIn("does not invoke `$orchestrate-subagents`", text)


if __name__ == "__main__":
    unittest.main()
