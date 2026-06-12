from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
SCRIPTS = ROOT / "scripts"
ROOT_SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(ROOT_SCRIPTS))
sys.path.insert(0, str(SCRIPTS))

from codex_hook_adapter import (  # noqa: E402
    DEFAULT_MONITORED_SKILLS,
    discover_packaged_skills,
    load_dynamic_monitored_skills,
    normalize_hook_payload,
    write_hook_event,
)
from codex_hook_config import (  # noqa: E402
    default_python,
    install_skill_watcher_hooks,
    remove_skill_watcher_hooks,
    skill_watcher_command,
)
from check_my_codex import CheckRunner, decode_subprocess_output  # noqa: E402
from doctor import find_managed_hook_issues  # noqa: E402
from generate_report import (  # noqa: E402
    event_hash,
    load_report_state,
    report_state_key,
    save_report_state,
    state_since,
    update_report_state,
)
from propose_skill_patch import build_proposal  # noqa: E402
from redact_event import REDACTION, redact_event  # noqa: E402
from refresh_my_codex import (  # noqa: E402
    cached_plugin_names,
    configured_plugin_names,
    default_plugin_names,
    marketplace_source_arg,
    selected_plugins,
    stale_plugin_names,
)
from summarize_logs import parse_since, read_events_since  # noqa: E402
from update_proposal_status import update_status  # noqa: E402


WINDOWS_PWSH_ENCODING_TEST = unittest.skipUnless(
    sys.platform == "win32",
    "Windows PowerShell encoding regression",
)


class SkillWatcherTests(unittest.TestCase):
    class StrictAsciiStdout:
        encoding = "ascii"

        def __init__(self) -> None:
            self.writes: list[str] = []

        def write(self, text: str) -> int:
            text.encode("ascii")
            self.writes.append(text)
            return len(text)

        def flush(self) -> None:
            return None

    @WINDOWS_PWSH_ENCODING_TEST
    def test_check_runner_tolerates_non_utf8_subprocess_output(self) -> None:
        runner = CheckRunner()

        result = runner.run_command(
            [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'\\x82')"],
            env={},
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout)

    @WINDOWS_PWSH_ENCODING_TEST
    def test_subprocess_output_prefers_utf8_with_replacement(self) -> None:
        raw = "▶ 系统找不到指定的文件。".encode("utf-8") + b"\x82"

        decoded = decode_subprocess_output(raw)

        self.assertIn("▶ 系统找不到指定的文件。", decoded)
        self.assertIn("\ufffd", decoded)

    @WINDOWS_PWSH_ENCODING_TEST
    def test_check_runner_prints_unencodable_failures_safely(self) -> None:
        runner = CheckRunner()
        stdout = self.StrictAsciiStdout()

        with mock.patch("sys.stdout", stdout):
            runner.fail("plugin output contains ▶")

        self.assertIn(r"\u25b6", "".join(stdout.writes))

    def test_doc_watcher_plugin_validation_uses_tooling_python(self) -> None:
        runner = CheckRunner()
        calls = []

        def fake_run_command(command, *, env, cwd=None):  # type: ignore[no-untyped-def]
            calls.append((command, cwd))
            return subprocess.CompletedProcess(command, 0, "ok", "")

        runner.run_command = fake_run_command  # type: ignore[method-assign]
        tooling_python = Path("C:/tooling/python.exe")
        validator = Path(__file__)

        runner.check_plugin_validation(
            tooling_python,
            ["doc-watcher@my-codex"],
            env={},
            validator=validator,
        )

        self.assertEqual(calls[0][0][0], str(tooling_python))
        self.assertEqual(calls[0][0][1], str(validator))
        self.assertIsNone(calls[0][1])

    def test_install_manifest_drives_default_plugin_selection(self) -> None:
        expected = [
            "skill-watcher",
            "doc-watcher",
            "workflow",
            "mattpocock-skills",
        ]

        self.assertEqual(
            default_plugin_names("install", marketplace_name="my-codex"),
            expected,
        )
        self.assertEqual(
            selected_plugins(None, "my-codex", action="install"),
            [f"{plugin}@my-codex" for plugin in expected],
        )
        self.assertEqual(
            selected_plugins(["doc-watcher"], "my-codex", action="install"),
            ["doc-watcher@my-codex"],
        )
        self.assertEqual(
            selected_plugins(["external@other-market"], "my-codex", action="install"),
            ["external@other-market"],
        )

    def test_install_manifest_fails_when_selected_plugin_is_missing_from_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest = tmp_path / "install-manifest.json"
            marketplace = tmp_path / "marketplace.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "marketplace": "my-codex",
                        "plugins": [
                            {"name": "missing-plugin", "install": True, "check": True},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            marketplace.write_text(
                json.dumps({"name": "my-codex", "plugins": [{"name": "skill-watcher"}]}),
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit) as raised:
                selected_plugins(
                    None,
                    "my-codex",
                    action="install",
                    manifest_file=manifest,
                    marketplace_file=marketplace,
                )

        self.assertIn("missing-plugin", str(raised.exception))

    def test_stale_plugin_detection_includes_config_and_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp)
            config = codex_home / "config.toml"
            config.write_text(
                "\n".join(
                    [
                        '[plugins."workflow@my-codex"]',
                        "enabled = true",
                        '[plugins."old-plugin@my-codex"]',
                        "enabled = true",
                        '[plugins."github@openai-curated"]',
                        "enabled = true",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            cache_root = codex_home / "plugins" / "cache" / "my-codex"
            (cache_root / "workflow" / "0.1.0").mkdir(parents=True)
            (cache_root / "cached-old" / "0.1.0").mkdir(parents=True)

            self.assertEqual(configured_plugin_names(codex_home, "my-codex"), {"workflow", "old-plugin"})
            self.assertEqual(cached_plugin_names(codex_home, "my-codex"), {"workflow", "cached-old"})
            self.assertEqual(
                stale_plugin_names(
                    codex_home=codex_home,
                    marketplace_name="my-codex",
                    desired_plugin_names=["workflow"],
                ),
                ["cached-old", "old-plugin"],
            )

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
        self.assertTrue(DEFAULT_MONITORED_SKILLS)
        self.assertLessEqual(set(DEFAULT_MONITORED_SKILLS), set(packaged))
        self.assertIn("doc-watcher:housekeeping", DEFAULT_MONITORED_SKILLS)
        self.assertEqual(discover_packaged_skills(REPO_ROOT), tuple(packaged))

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
            session_start = write_hook_event(
                {
                    "hook_event_name": "SessionStart",
                    "cwd": "/tmp/workspace",
                    "session_id": "session-start",
                    "turn_id": "turn-start",
                },
                state_dir=state_dir,
            )
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
            dynamic_skills = load_dynamic_monitored_skills(state_dir)

        self.assertFalse(session_start["codex"]["persisted"])
        self.assertEqual(session_start["codex"]["allowlist_update"]["skill_count"], len(packaged))
        self.assertEqual(dynamic_skills, tuple(packaged))
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

        sop_prompt = normalize_hook_payload(
            {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "请使用标准流程整理这次重复任务。",
            }
        )
        self.assertEqual(sop_prompt["skill_name"], "workflow:sop")
        self.assertEqual(sop_prompt["codex"]["skill_attribution"], "prompt_mention")
        self.assertEqual(sop_prompt["codex"]["matched_alias"], "标准流程")

        sop_assistant = normalize_hook_payload(
            {
                "hook_event_name": "Stop",
                "last_assistant_message": "I will use $sop for this recurring procedure.",
            }
        )
        self.assertEqual(sop_assistant["skill_name"], "workflow:sop")
        self.assertEqual(sop_assistant["codex"]["skill_attribution"], "assistant_announcement")
        self.assertEqual(sop_assistant["codex"]["matched_alias"], "sop")

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
                r'"C:\Users\Max Smith\.codex\venvs\my-codex\Scripts\python.exe" -B '
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
        self.assertEqual(removed, 4)
        self.assertEqual(removed_on_uninstall, 4)
        self.assertEqual(installed["hooks"]["PostToolUse"][0]["hooks"][0]["command"], "/usr/bin/true")
        self.assertIn("SessionStart", installed["hooks"])
        self.assertEqual(uninstalled["hooks"], {"PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "/usr/bin/true"}]}]})
        for event in ("SessionStart", "UserPromptSubmit", "PostToolUse", "Stop"):
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

        self.assertEqual(matched_events, {"SessionStart", "UserPromptSubmit"})
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

    def test_report_reader_and_state_support_incremental_windows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            log_file = state_dir / "logs" / "events.jsonl"
            log_file.parent.mkdir(parents=True)
            events = [
                {"timestamp": "2026-06-01T00:00:00Z", "skill_name": "demo", "outcome": "success"},
                {"timestamp": "2026-06-05T00:00:00Z", "skill_name": "demo", "outcome": "failure"},
                {"timestamp": "2026-06-06T00:00:00Z", "skill_name": "demo", "outcome": "success"},
            ]
            log_file.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")

            recent = read_events_since(log_file, parse_since("2026-06-05T00:00:00Z"), block_size=48)
            state = load_report_state(state_dir)
            key = report_state_key("demo")
            update_report_state(
                state,
                key=key,
                since=parse_since("2026-06-05T00:00:00Z"),
                until=datetime(2026, 6, 6, tzinfo=timezone.utc),
                event_count=len(recent),
                output=state_dir / "reports" / "demo.md",
                recent_hashes=[event_hash(event) for event in recent],
            )
            save_report_state(state_dir, state)
            loaded = load_report_state(state_dir)

        self.assertEqual([event["timestamp"] for event in recent], ["2026-06-05T00:00:00Z", "2026-06-06T00:00:00Z"])
        self.assertEqual(state_since(loaded, key), datetime(2026, 6, 6, tzinfo=timezone.utc))
        self.assertEqual(loaded["reports"][key]["last_event_count"], 2)
        self.assertEqual(len(loaded["reports"][key]["recent_event_hashes"]), 2)


if __name__ == "__main__":
    unittest.main()
