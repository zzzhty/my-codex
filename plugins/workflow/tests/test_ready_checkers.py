from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GOAL_CHECKER = ROOT / "skills" / "long-running-goal" / "scripts" / "check_goal_ready.py"
SOP_CHECKER = ROOT / "skills" / "sop" / "scripts" / "check_sop_ready.py"

CLOSE_EVIDENCE = """
## Close Gate

Close execution evidence:

Validation: all required checks passed.

Checkpoint evidence: close revision recorded.
"""

LOOP_HARNESS = """## Loop Blueprint / Harness

Execution mode: Loop-shaped execution

Trigger:
- Resume on an explicit user command.
Inputs:
- Read the goal file and validation logs.
Triage and orchestration:
- Convert findings into ordered milestone work.
Worktree and isolation:
- Serialize edits in the current checkout.
Skills and context:
- Read this skill and the project instructions.
Connector read/write boundaries:
- Not applicable: this loop has no connector access.
Independent verification:
- Run the owning checker and an independent review.
Runtime hard stops:
- Stop only after repeated technical failure with no in-plan next step.
Durable learning:
- Write validated results into the goal evidence.
"""


def replace_all(text: str, *pairs: tuple[str, str]) -> str:
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def remove_between(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[:start_index] + text[end_index:]


class ReadyCheckerTests(unittest.TestCase):
    def run_checker(
        self,
        checker: Path,
        document: Path,
        *extra_args: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(checker), str(document), *extra_args],
            capture_output=True,
            check=False,
            text=True,
        )

    def run_goal(self, text: str, *args: str, name: str = "goal.md") -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            document = Path(tmp) / name
            document.write_text(text, encoding="utf-8")
            return self.run_checker(GOAL_CHECKER, document, *args)

    def assert_goal_error(self, text: str, message: str, *args: str) -> None:
        completed = self.run_goal(text, *args)
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn(message, completed.stderr)

    def with_harness(self, text: str, harness: str) -> str:
        return (
            text[: text.index("## Loop Blueprint / Harness")]
            + harness.rstrip()
            + "\n\n"
            + text[text.index("## Rollback path") :]
        )

    @property
    def ready(self) -> str:
        return (FIXTURES / "ready_goal.md").read_text(encoding="utf-8")

    def assert_checker_contract(self, checker: Path, fixture: Path) -> None:
        completed = self.run_checker(checker, fixture)
        self.assertEqual(completed.returncode, 0, completed.stderr)

        incomplete = fixture.read_text(encoding="utf-8")
        incomplete += "\n```bash\nrun <unfinished-command>\n```\n"
        failed = self.run_goal(incomplete) if checker == GOAL_CHECKER else None
        if checker != GOAL_CHECKER:
            with tempfile.TemporaryDirectory() as tmp:
                document = Path(tmp) / fixture.name
                document.write_text(incomplete, encoding="utf-8")
                failed = self.run_checker(checker, document)

        assert failed is not None
        self.assertEqual(failed.returncode, 1)
        self.assertIn("unresolved placeholders: <unfinished-command>", failed.stderr)

    def test_long_running_goal_checker_validates_placeholders_inside_fences(self) -> None:
        self.assert_checker_contract(GOAL_CHECKER, FIXTURES / "ready_goal.md")

    def test_goal_lifecycle_rejection_matrix(self) -> None:
        ready = self.ready
        closed_incomplete = ready.replace("Overall status: Ready", "Overall status: Closed")
        done_without_evidence = ready.replace(
            "| M0 | Ready | Pending | Pending |",
            "| M0 | Done | Pending | Pending |",
        )
        out_of_order = replace_all(
            ready,
            (
                "## Milestone status table",
                "## M1 milestone\n\nFuture work.\n\n## Milestone status table",
            ),
            (
                "| Close | Not Started | Pending | Pending |",
                "| M1 | Done | Passed | Done |\n| Close | Not Started | Pending | Pending |",
            ),
        )
        current_after_not_started = replace_all(
            ready,
            ("Overall status: Ready", "Overall status: In Progress"),
            (
                "## Milestone status table",
                "## M1 milestone\n\nStatus: In Progress\n\nCurrent work.\n\n"
                "## Milestone status table",
            ),
            (
                "| M0 | Ready | Pending | Pending |",
                "| M0 | Not Started | Pending | Pending |\n"
                "| M1 | In Progress | Pending | Pending |",
            ),
        )
        multiple_current = replace_all(
            ready,
            (
                "## Milestone status table",
                "## M1 milestone\n\nStatus: In Progress\n\nCurrent work.\n\n"
                "## Milestone status table",
            ),
            (
                "| Close | Not Started | Pending | Pending |",
                "| M1 | In Progress | Pending | Pending |\n"
                "| Close | Not Started | Pending | Pending |",
            ),
        )
        non_contiguous = replace_all(
            ready,
            (
                "## Milestone status table",
                "## M2 milestone\n\nFuture work.\n\n## Milestone status table",
            ),
            (
                "| Close | Not Started | Pending | Pending |",
                "| M2 | Not Started | Pending | Pending |\n"
                "| Close | Not Started | Pending | Pending |",
            ),
        )
        close_done_not_closed = replace_all(
            ready,
            ("| M0 | Ready | Pending | Pending |", "| M0 | Done | Passed | Done |"),
            (
                "| Close | Not Started | Pending | Pending |",
                "| Close | Done | Passed | Done |",
            ),
        )
        closed_without_evidence = close_done_not_closed.replace(
            "Overall status: Ready", "Overall status: Closed"
        )
        blocked_without_evidence = replace_all(
            ready,
            ("Overall status: Ready", "Overall status: In Progress"),
            ("| M0 | Ready | Pending | Pending |", "| M0 | Blocked | Pending | Pending |"),
        )
        missing_section = ready.replace("## M0 milestone\n\nBaseline recorded.\n\n", "")
        extra_section = ready.replace(
            "## Milestone status table",
            "## M1 milestone\n\nFuture work.\n\n## Milestone status table",
        )
        duplicate_section = ready.replace(
            "## Milestone status table",
            "## M0 duplicate\n\nDuplicate work.\n\n## Milestone status table",
        )
        missing_m0_row = replace_all(
            ready,
            ("Overall status: Ready", "Overall status: Closed"),
            ("| M0 | Ready | Pending | Pending |\n", ""),
            (
                "| Close | Not Started | Pending | Pending |",
                "| Close | Done | Passed | Done |",
            ),
        ) + CLOSE_EVIDENCE

        cases = [
            ("draft", ready.replace("Overall status: Ready", "Overall status: Draft"), "overall goal status must be Ready", ()),
            ("missing_table", remove_between(ready, "## Milestone status table", "## Review gate"), "missing milestone status table", ()),
            ("closed_incomplete", closed_incomplete, "Closed goal requires every milestone", ()),
            ("done_without_evidence", done_without_evidence, "M0 status Done requires Review Passed", ()),
            ("done_after_incomplete", out_of_order, "Done milestone M1 follows incomplete M0", ()),
            ("current_after_not_started", current_after_not_started, "M1 In Progress requires M0 Done", ()),
            ("multiple_current", multiple_current, "multiple current milestones", ()),
            ("overall_current_mismatch", ready.replace("| M0 | Ready | Pending | Pending |", "| M0 | In Progress | Pending | Pending |"), "overall Ready requires current milestone Ready", ()),
            ("unknown_status", ready.replace("| M0 | Ready | Pending | Pending |", "| M0 | Waiting | Pending | Pending |"), "M0 has invalid milestone status Waiting", ()),
            ("premature_completion", ready.replace("| M0 | Ready | Pending | Pending |", "| M0 | Ready | Passed | Done |"), "Review/Checkpoint completion requires", ()),
            ("failed_review", ready.replace("| M0 | Ready | Pending | Pending |", "| M0 | Ready | Failed | Pending |"), "Review Failed requires milestone status", ()),
            ("non_contiguous", non_contiguous, "milestone sequence must be contiguous", ()),
            ("missing_close", ready.replace("| Close | Not Started | Pending | Pending |\n", ""), "exactly one Close row", ()),
            ("conflicting_draft", ready.replace("Overall status: Ready", "Overall status: Draft") + "\nGoal status: Ready\n", "overall goal statuses disagree", ("--allow-draft",)),
            ("section_status_mismatch", ready.replace("## M0 milestone\n\nBaseline recorded.", "### M0 - Baseline\n\nStatus: In Progress\n\nBaseline recorded."), "status disagrees between section and milestone table", ()),
            ("close_done_not_closed", close_done_not_closed, "Close is Done/Passed/Done but overall goal status is Ready", ()),
            ("closed_without_evidence", closed_without_evidence, "Closed goal requires Close execution evidence", ()),
            ("ready_without_current", ready.replace("| M0 | Ready | Pending | Pending |", "| M0 | Not Started | Pending | Pending |"), "overall Ready requires exactly one Ready milestone", ()),
            ("blocked_without_evidence", blocked_without_evidence, "Blocked requires section-local runtime hard-stop evidence", ()),
            ("missing_section", missing_section, "milestone table has no matching section: M0", ()),
            ("extra_section", extra_section, "milestone section has no matching table row: M1", ()),
            ("duplicate_section", duplicate_section, "duplicate milestone sections: M0", ()),
            ("missing_m0_row", missing_m0_row, "milestone status table must include M0", ()),
        ]
        for name, text, message, args in cases:
            with self.subTest(name=name):
                self.assert_goal_error(text, message, *args)

    def test_preflight_rejection_matrix(self) -> None:
        ready = self.ready
        skip_mismatch = ready.replace(
            "preflight:demo:20260710-ready",
            "preflight:demo:skip:20260710-ready",
        )
        missing_source = ready.replace("\nPreflight source: grill-with-docs\n", "\n")
        partial_draft = missing_source.replace("Overall status: Ready", "Overall status: Draft")
        cases = [
            ("skip_mismatch", skip_mismatch, "preflight skip marker requires status", ()),
            ("missing_source", missing_source, "missing planning preflight source field", ()),
            ("partial_draft", partial_draft, "missing planning preflight source field", ("--allow-draft",)),
        ]
        for name, text, message, args in cases:
            with self.subTest(name=name):
                self.assert_goal_error(text, message, *args)

    def test_harness_and_permission_rejection_matrix(self) -> None:
        ready = self.ready
        missing_harness = remove_between(ready, "## Loop Blueprint / Harness", "## Rollback path")
        no_reason = re.sub(
            r"Not applicable: manual staged execution because.*?external side effect\.",
            "Not applicable: manual staged execution",
            ready,
            flags=re.DOTALL,
        )
        incomplete_loop = ready.replace(
            "Execution mode: Manual staged execution", "Execution mode: Loop-shaped execution"
        )
        empty_loop = self.with_harness(
            ready,
            LOOP_HARNESS.replace(
                "Connector read/write boundaries:\n- Not applicable: this loop has no connector access.",
                "Connector read/write boundaries:",
            ),
        )
        unsafe_local = ready.replace(
            "Planned non-destructive local code and documentation edits, tests, and validation.",
            "Delete production data, publish a release, and send external messages.",
        )

        def hard_stop(value: str) -> str:
            return re.sub(
                r"Stop only when repeated local diagnostics.*?externally visible\.",
                value,
                ready,
                flags=re.DOTALL,
            )

        cases = [
            ("missing_harness", missing_harness, "missing Loop Blueprint / Harness section"),
            ("manual_without_reason", no_reason, "manual harness opt-out requires a reason"),
            ("incomplete_loop", incomplete_loop, "missing harness field: Connector read/write boundaries"),
            ("empty_loop", empty_loop, "empty harness field: Connector read/write boundaries"),
            ("unsafe_local", unsafe_local, "YOLO local operations must be non-destructive and local"),
            ("first_failure", hard_stop("Stop at the first validation failure, any milestone boundary, or checkpoint."), "runtime hard stop misclassifies recoverable work"),
            ("negation_semicolon", hard_stop("Do not stop at checkpoints; stop at the first validation failure."), "runtime hard stop misclassifies recoverable work"),
            ("negation_comma", hard_stop("Do not stop at checkpoints, but stop at the first validation failure."), "runtime hard stop misclassifies recoverable work"),
            ("pending_approval", ready.replace("Not applicable: this demo does not access external systems.", "GitHub release write: pending approval."), "unresolved external write approval keeps the goal Draft"),
            ("awaiting_approval", ready.replace("Not applicable: this demo does not access external systems.", "GitHub release write is awaiting user approval."), "unresolved external write approval keeps the goal Draft"),
            ("manual_connector", ready + "\nThis goal uses the GitHub connector to create release issues.\n", "goal declares connector use but Loop harness is Not applicable"),
            ("manual_parallel", ready + "\nThis goal uses parallel worktrees and multiple subagents.\n", "goal declares Loop-shaped orchestration but harness is Not applicable"),
        ]
        for name, text, message in cases:
            with self.subTest(name=name):
                self.assert_goal_error(text, message)

    def test_goal_checker_accepts_valid_contract_matrix(self) -> None:
        ready = self.ready
        draft = ready.replace("Overall status: Ready", "Overall status: Draft")
        draft_pending = draft + "\nGoal status: Draft\n"
        draft_pending = draft_pending.replace(
            "Not applicable: this demo does not access external systems.",
            "GitHub release write: pending approval.",
        )
        in_progress = replace_all(
            ready,
            ("Overall status: Ready", "Overall status: In Progress"),
            ("| M0 | Ready | Pending | Pending |", "| M0 | In Progress | Pending | Pending |"),
        )
        blocked = replace_all(
            in_progress,
            ("| M0 | In Progress | Pending | Pending |", "| M0 | Blocked | Pending | Pending |"),
            (
                "## M0 milestone\n\nBaseline recorded.",
                "### M0 - Baseline\n\nStatus: Blocked\n\n"
                "Runtime hard-stop evidence: required credentials are unavailable.\n\n"
                "Baseline recorded.",
            ),
        )
        closed = replace_all(
            ready,
            ("Overall status: Ready", "Overall status: Closed"),
            ("| M0 | Ready | Pending | Pending |", "| M0 | Done | Passed | Done |"),
            ("| Close | Not Started | Pending | Pending |", "| Close | Done | Passed | Done |"),
        ) + CLOSE_EVIDENCE
        skipped = replace_all(
            ready,
            ("preflight:demo:20260710-ready", "preflight:demo:skip:20260710-ready"),
            ("Planning preflight status: Done", "Planning preflight status: Skipped by explicit user instruction"),
            ("Preflight source: grill-with-docs", "Preflight source: user skip"),
        )
        loop_shaped = self.with_harness(ready, LOOP_HARNESS)
        close_in_progress = replace_all(
            ready,
            ("Overall status: Ready", "Overall status: In Progress"),
            ("| M0 | Ready | Pending | Pending |", "| M0 | Done | Passed | Done |"),
            ("| Close | Not Started | Pending | Pending |", "| Close | In Progress | Pending | Pending |"),
        )
        close_blocked = replace_all(
            close_in_progress,
            ("| Close | In Progress | Pending | Pending |", "| Close | Blocked | Pending | Pending |"),
        ) + "\n## Close Gate\n\nRuntime hard-stop evidence: required credentials are unavailable.\n"
        named_milestone = ready.replace(
            "| M0 | Ready | Pending | Pending |",
            "| M0 `Baseline` | Ready | Pending | Pending |",
        )
        safe_release = ready.replace(
            "Planned non-destructive local code and documentation edits, tests, and validation.",
            "Planned non-destructive local Release builds, tests, and validation.",
        )

        cases = {
            "ready": (ready, ()),
            "draft": (draft, ("--allow-draft",)),
            "draft_pending": (draft_pending, ("--allow-draft",)),
            "in_progress": (in_progress, ()),
            "blocked": (blocked, ()),
            "closed": (closed, ()),
            "skipped_preflight": (skipped, ()),
            "loop_shaped": (loop_shaped, ()),
            "close_in_progress": (close_in_progress, ()),
            "close_blocked": (close_blocked, ()),
            "named_milestone": (named_milestone, ()),
            "safe_release": (safe_release, ()),
        }
        for name, (text, args) in cases.items():
            with self.subTest(name=name):
                completed = self.run_goal(text, *args, name=f"{name}.md")
                self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_sop_checker_validates_placeholders_inside_fences(self) -> None:
        self.assert_checker_contract(SOP_CHECKER, FIXTURES / "ready_sop.md")

    def test_goal_template_marks_only_documentation_examples(self) -> None:
        template = (
            ROOT
            / "skills"
            / "long-running-goal"
            / "templates"
            / "long_running_goal_template.md"
        ).read_text(encoding="utf-8")

        self.assertIn("```bash placeholder-example\ncp <skill-folder>", template)
        self.assertIn(
            "```text placeholder-example\nCheckpoint component: <Pending / Done>",
            template,
        )
        self.assertEqual(template.count("placeholder-example"), 2)


if __name__ == "__main__":
    unittest.main()
