from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
SCRIPTS = ROOT / "scripts"
ROOT_SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(ROOT_SCRIPTS))
sys.path.insert(0, str(SCRIPTS))

from codex_hook_adapter import DEFAULT_MONITORED_SKILLS, normalize_hook_payload, write_hook_event  # noqa: E402
from codex_hook_config import (  # noqa: E402
    default_python,
    install_skill_watcher_hooks,
    remove_skill_watcher_hooks,
    skill_watcher_command,
)
from doctor import find_managed_hook_issues  # noqa: E402
from propose_skill_patch import build_proposal  # noqa: E402
from redact_event import REDACTION, redact_event  # noqa: E402
from refresh_my_codex import marketplace_source_arg  # noqa: E402
from update_proposal_status import update_status  # noqa: E402


class SkillWatcherV1Tests(unittest.TestCase):
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

    def test_codex_hook_lifecycle_filters_summarizes_and_guards_skill_list(self) -> None:
        packaged = sorted(
            f"{skill_file.parents[2].name}:{skill_file.parent.name}"
            for skill_file in (REPO_ROOT / "plugins").glob("*/skills/*/SKILL.md")
        )
        self.assertEqual(sorted(DEFAULT_MONITORED_SKILLS), packaged)

        normalized = normalize_hook_payload(
            {
                "hook_event_name": "PostToolUse",
                "cwd": "/tmp/workspace",
                "session_id": "session-1",
                "turn_id": "turn-1",
                "tool_name": "Bash",
                "tool_input": {"command": "printf sk-testsecret123456789"},
                "tool_response": {"exit_code": 1, "stderr": "error token sk-testsecret123456789"},
            }
        )
        serialized = json.dumps(normalized, sort_keys=True)
        self.assertEqual(normalized["event_type"], "post_tool_use")
        self.assertEqual(normalized["skill_name"], "unknown")
        self.assertEqual(normalized["outcome"], "failure")
        self.assertEqual(normalized["failure_type"], "tool_error")
        self.assertIn("tool_input_summary", normalized["codex"])
        self.assertNotIn("printf sk-testsecret123456789", serialized)
        self.assertNotIn("sk-testsecret123456789", serialized)

        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            unknown = write_hook_event(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "cwd": "/tmp/workspace",
                    "session_id": "session-unknown",
                    "turn_id": "turn-unknown",
                    "prompt": "ordinary task without a monitored skill",
                },
                state_dir=state_dir,
            )
            base = {
                "cwd": "/tmp/workspace",
                "session_id": "session-2",
                "turn_id": "turn-2",
            }
            prompt = write_hook_event(
                {
                    **base,
                    "hook_event_name": "UserPromptSubmit",
                    "prompt": "Use diagnose on flaky tests with sk-testsecret123456789",
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
            lines = (state_dir / "logs" / "events.jsonl").read_text(encoding="utf-8").splitlines()

        self.assertFalse(unknown["codex"]["persisted"])
        self.assertEqual(prompt["skill_name"], "mattpocock-skills:diagnose")
        self.assertEqual(prompt["codex"]["skill_attribution"], "prompt_mention")
        self.assertTrue(prompt["codex"]["persisted"])
        self.assertIn("user_skill_context", prompt["codex"])
        self.assertFalse(success["codex"]["persisted"])
        self.assertTrue(failure["codex"]["persisted"])
        self.assertEqual(summary["event_type"], "turn_summary")
        self.assertEqual(summary["codex"]["turn_summary"]["tool_count"], 2)
        self.assertEqual(summary["codex"]["turn_summary"]["tool_failures"], 1)
        self.assertIn("user_skill_context", summary["codex"]["turn_summary"])
        self.assertEqual(len(lines), 3)
        self.assertNotIn("sk-testsecret123456789", "\n".join(lines))

    def test_hook_config_runtime_helpers_and_stale_schema_detection(self) -> None:
        with mock.patch.dict("os.environ", {"MY_CODEX_PYTHON": "/tmp/shared-python"}, clear=True):
            self.assertEqual(default_python(), Path("/tmp/shared-python"))
        with mock.patch.dict(
            "os.environ",
            {
                "MY_CODEX_PYTHON": "/tmp/shared-python",
                "MY_CODEX_TOOLING_PYTHON": "/tmp/tooling-python",
            },
            clear=True,
        ):
            self.assertEqual(default_python(), Path("/tmp/tooling-python"))

        python = Path(r"C:\Users\Max Smith\.codex\venvs\my-codex\Scripts\python.exe")
        adapter = Path(r"C:\Users\Max Smith\Projects\my-codex\plugins\skill-watcher\scripts\codex_hook_adapter.py")
        with mock.patch("codex_hook_config.os.name", "nt"):
            self.assertEqual(
                skill_watcher_command(python, adapter),
                r'"C:\Users\Max Smith\.codex\venvs\my-codex\Scripts\python.exe" '
                r'"C:\Users\Max Smith\Projects\my-codex\plugins\skill-watcher\scripts\codex_hook_adapter.py"',
            )

        self.assertEqual(marketplace_source_arg("https://github.com/example/my-codex"), "https://github.com/example/my-codex")
        self.assertEqual(marketplace_source_arg("example/my-codex"), "example/my-codex")

        existing = {
            "hooks": {
                "PostToolUse": [
                    {"matcher": "Bash", "hooks": [{"type": "command", "command": "/usr/bin/true"}]}
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
        uninstalled, removed_on_uninstall = remove_skill_watcher_hooks(installed)

        self.assertEqual(installed, installed_again)
        self.assertEqual(removed, 3)
        self.assertEqual(removed_on_uninstall, 3)
        self.assertEqual(installed["hooks"]["PostToolUse"][0]["hooks"][0]["command"], "/usr/bin/true")
        self.assertNotIn("SessionStart", installed["hooks"])
        self.assertEqual(uninstalled["hooks"], {"PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "/usr/bin/true"}]}]})
        for event in ("UserPromptSubmit", "PostToolUse", "Stop"):
            handlers = [handler for group in installed["hooks"][event] for handler in group["hooks"]]
            managed = [handler for handler in handlers if "codex_hook_adapter.py" in handler["command"]]
            self.assertTrue(managed)
            for handler in managed:
                self.assertIs(handler["async"], False)
                self.assertEqual(handler["timeoutSec"], 10)
                self.assertNotIn("timeout", handler)

        old_handler = {
            "type": "command",
            "command": "/tmp/python /tmp/skill-watcher/scripts/codex_hook_adapter.py",
            "timeout": 10,
            "statusMessage": "Skill Watcher: observe UserPromptSubmit",
        }
        matched_events, issues = find_managed_hook_issues(
            {
                "hooks": {
                    "UserPromptSubmit": [{"hooks": [old_handler]}],
                    "SessionStart": [{"hooks": [{**old_handler, "statusMessage": "Skill Watcher: observe SessionStart"}]}],
                }
            },
            python_path=Path("/tmp/python"),
            adapter=Path("/tmp/skill-watcher/scripts/codex_hook_adapter.py"),
        )

        self.assertEqual(matched_events, {"UserPromptSubmit"})
        self.assertTrue(any("timeoutSec" in issue for issue in issues))
        self.assertTrue(any("unexpected keys: timeout" in issue for issue in issues))
        self.assertTrue(any("SessionStart" in issue for issue in issues))

    def test_proposal_frontmatter_and_status_transitions(self) -> None:
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

            previous, _ = update_status(
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
