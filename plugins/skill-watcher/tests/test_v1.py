from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from codex_hook_adapter import normalize_hook_payload, write_hook_event  # noqa: E402
from codex_hook_config import install_skill_watcher_hooks, remove_skill_watcher_hooks  # noqa: E402
from propose_skill_patch import build_proposal  # noqa: E402
from redact_event import REDACTION, redact_event  # noqa: E402
from update_proposal_status import update_status  # noqa: E402


class RedactionTests(unittest.TestCase):
    def test_redacts_secret_keys_and_values(self) -> None:
        payload = {
            "api_key": "plain-secret",
            "notes": "Bearer abcdefghijklmnop and sk-testsecret123",
            "nested": {"refresh_token": "another-secret"},
        }

        redacted = redact_event(payload)

        self.assertEqual(redacted["api_key"], REDACTION)
        self.assertEqual(redacted["nested"]["refresh_token"], REDACTION)
        self.assertNotIn("sk-testsecret123", json.dumps(redacted))
        self.assertNotIn("abcdefghijklmnop", json.dumps(redacted))


class CodexHookAdapterTests(unittest.TestCase):
    def test_normalizes_post_tool_use_failure_without_raw_prompt_or_command(self) -> None:
        payload = {
            "hook_event_name": "PostToolUse",
            "cwd": "/tmp/workspace",
            "session_id": "session-1",
            "turn_id": "turn-1",
            "model": "gpt-test",
            "permission_mode": "default",
            "tool_name": "Bash",
            "tool_input": {"command": "printf sk-testsecret123456789"},
            "tool_response": {"exit_code": 1, "stderr": "error token sk-testsecret123456789"},
        }

        event = normalize_hook_payload(payload)
        serialized = json.dumps(event, sort_keys=True)

        self.assertEqual(event["event_type"], "post_tool_use")
        self.assertEqual(event["skill_name"], "unknown")
        self.assertEqual(event["tools_used"], ["Bash"])
        self.assertEqual(event["outcome"], "failure")
        self.assertEqual(event["failure_type"], "tool_error")
        self.assertEqual(event["codex"]["skill_attribution"], "unknown")
        self.assertIn("tool_input_summary", event["codex"])
        self.assertIn("tool_response_summary", event["codex"])
        self.assertNotIn("printf sk-testsecret123456789", serialized)
        self.assertNotIn("sk-testsecret123456789", serialized)

    def test_writes_hook_event_to_state_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            event = write_hook_event(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "cwd": "/tmp/workspace",
                    "session_id": "session-2",
                    "turn_id": "turn-2",
                    "prompt": "Use diagnose on this short prompt with sk-testsecret123456789",
                },
                state_dir=state_dir,
            )

            log_file = state_dir / "logs" / "events.jsonl"
            lines = log_file.read_text(encoding="utf-8").splitlines()

        self.assertEqual(len(lines), 1)
        self.assertEqual(event["event_type"], "user_prompt_submit")
        self.assertEqual(event["skill_name"], "mattpocock-skills:diagnose")
        self.assertEqual(event["codex"]["skill_attribution"], "prompt_mention")
        self.assertTrue(event["codex"]["persisted"])
        self.assertIn("user_skill_context", event["codex"])
        self.assertNotIn("sk-testsecret123456789", lines[0])

    def test_suppresses_unmonitored_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            event = write_hook_event(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "cwd": "/tmp/workspace",
                    "session_id": "session-unknown",
                    "turn_id": "turn-unknown",
                    "prompt": "ordinary task without a monitored skill",
                },
                state_dir=state_dir,
            )

            log_file = state_dir / "logs" / "events.jsonl"
            lines = log_file.read_text(encoding="utf-8").splitlines() if log_file.exists() else []

        self.assertEqual(lines, [])
        self.assertEqual(event["skill_name"], "unknown")
        self.assertFalse(event["codex"]["persisted"])

    def test_filters_success_tools_and_writes_turn_summary_for_monitored_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            base = {
                "cwd": "/tmp/workspace",
                "session_id": "session-3",
                "turn_id": "turn-3",
            }
            write_hook_event(
                {
                    **base,
                    "hook_event_name": "UserPromptSubmit",
                    "prompt": "Use diagnose on the flaky pytest failure path",
                },
                state_dir=state_dir,
            )
            success = write_hook_event(
                {
                    **base,
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Bash",
                    "tool_response": {"exit_code": 0, "stdout": "ok"},
                },
                state_dir=state_dir,
            )
            failure = write_hook_event(
                {
                    **base,
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Bash",
                    "tool_response": {"exit_code": 1, "stderr": "error"},
                },
                state_dir=state_dir,
            )
            summary = write_hook_event({**base, "hook_event_name": "Stop"}, state_dir=state_dir)

            log_file = state_dir / "logs" / "events.jsonl"
            lines = log_file.read_text(encoding="utf-8").splitlines()

        self.assertFalse(success["codex"]["persisted"])
        self.assertTrue(failure["codex"]["persisted"])
        self.assertEqual(summary["event_type"], "turn_summary")
        self.assertEqual(summary["codex"]["turn_summary"]["tool_count"], 2)
        self.assertEqual(summary["codex"]["turn_summary"]["tool_failures"], 1)
        self.assertIn("user_skill_context", summary["codex"]["turn_summary"])
        self.assertEqual(len(lines), 3)


class HookConfigTests(unittest.TestCase):
    def test_install_is_idempotent_and_preserves_unrelated_hooks(self) -> None:
        existing = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Bash",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "/usr/bin/true",
                                "statusMessage": "Unrelated",
                            }
                        ],
                    }
                ]
            }
        }

        installed, _ = install_skill_watcher_hooks(
            existing,
            python_path=Path("/tmp/python"),
            adapter=Path("/tmp/skill-watcher/scripts/codex_hook_adapter.py"),
        )
        installed_again, removed = install_skill_watcher_hooks(
            installed,
            python_path=Path("/tmp/python"),
            adapter=Path("/tmp/skill-watcher/scripts/codex_hook_adapter.py"),
        )

        self.assertEqual(installed, installed_again)
        self.assertEqual(removed, 3)
        self.assertEqual(installed["hooks"]["PostToolUse"][0]["hooks"][0]["command"], "/usr/bin/true")
        self.assertNotIn("SessionStart", installed["hooks"])
        for event in ("UserPromptSubmit", "PostToolUse", "Stop"):
            handlers = [handler for group in installed["hooks"][event] for handler in group["hooks"]]
            skill_watcher_handlers = [
                handler for handler in handlers if "codex_hook_adapter.py" in handler["command"]
            ]
            self.assertTrue(skill_watcher_handlers)
            for handler in skill_watcher_handlers:
                self.assertIs(handler["async"], False)
                self.assertEqual(handler["timeoutSec"], 10)
                self.assertNotIn("timeout", handler)

    def test_uninstall_removes_only_skill_watcher_handlers(self) -> None:
        installed, _ = install_skill_watcher_hooks(
            {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "/usr/bin/true"}]}]}},
            python_path=Path("/tmp/python"),
            adapter=Path("/tmp/skill-watcher/scripts/codex_hook_adapter.py"),
        )

        uninstalled, removed = remove_skill_watcher_hooks(installed)

        self.assertEqual(removed, 3)
        self.assertEqual(uninstalled["hooks"], {"Stop": [{"hooks": [{"type": "command", "command": "/usr/bin/true"}]}]})


class ProposalStatusTests(unittest.TestCase):
    def test_generated_proposal_has_draft_frontmatter(self) -> None:
        proposal = build_proposal(
            proposal_id="proposal-1",
            skill_name="demo",
            skill_dir=Path("/tmp/demo"),
            skill_contents="line\n",
            report="# Report\n",
            snapshot_path=Path("/tmp/demo/SKILL.md"),
            timestamp="20260528T000000Z",
        )

        self.assertTrue(proposal.startswith("---\n"))
        self.assertIn('status: "draft"', proposal)
        self.assertIn('skill_name: "demo"', proposal)

    def test_status_transitions_and_rejected_buffer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "state"
            proposal_path = Path(tmp) / "proposal.md"
            proposal_path.write_text(
                "---\n"
                "proposal_id: proposal-1\n"
                "status: draft\n"
                "skill_name: demo\n"
                "---\n"
                "# Proposal\n",
                encoding="utf-8",
            )

            previous, rejected_path = update_status(
                proposal_path,
                "needs-validation",
                state_dir=state_dir,
                reason="needs checks",
            )
            previous_rejected, rejected_path = update_status(
                proposal_path,
                "rejected",
                state_dir=state_dir,
                reason="bad evidence",
            )

            updated = proposal_path.read_text(encoding="utf-8")
            rejected_text = rejected_path.read_text(encoding="utf-8") if rejected_path is not None else ""
            rejected_exists = rejected_path.is_file() if rejected_path is not None else False

        self.assertEqual(previous, "draft")
        self.assertEqual(previous_rejected, "needs-validation")
        self.assertIsNotNone(rejected_path)
        self.assertTrue(rejected_exists)
        self.assertIn("status: rejected", updated)
        self.assertIn("bad evidence", rejected_text)


if __name__ == "__main__":
    unittest.main()
