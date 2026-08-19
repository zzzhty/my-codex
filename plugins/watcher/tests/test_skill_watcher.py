from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


TEST_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TEST_ROOT.parents[1]
ROOT = REPO_ROOT / "plugins" / "watcher"
SCRIPTS = ROOT / "scripts"
ROOT_SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(ROOT_SCRIPTS))
sys.path.insert(0, str(SCRIPTS))

import refresh_my_codex  # noqa: E402
from watcher_runtime.skill.codex_hook_adapter import (  # noqa: E402
    HookRuntimePaths,
    discover_packaged_skills,
    discover_skill_metadata,
    load_dynamic_monitored_skills,
    normalize_hook_payload,
    process_hook,
    write_hook_event,
)
from watcher_runtime.skill.codex_hook_config import (  # noqa: E402
    default_python,
    install_skill_watcher_hooks,
    remove_skill_watcher_hooks,
    skill_watcher_command,
)
from check_my_codex import CheckRunner, decode_subprocess_output  # noqa: E402
from watcher_runtime.skill.doctor import find_managed_hook_issues  # noqa: E402
from watcher_runtime.skill.report_pipeline import (  # noqa: E402
    event_hash,
    load_report_state,
    report_state_key,
    save_report_state,
    state_since,
    update_report_state,
)
from watcher_runtime.skill.propose_skill_patch import build_proposal  # noqa: E402
from watcher_runtime.skill.redact_event import REDACTION, redact_event  # noqa: E402
from refresh_my_codex import (  # noqa: E402
    cached_plugin_names,
    configured_plugin_names,
    default_plugin_names,
    marketplace_source_arg,
    resolve_codex_executable,
    selected_plugins,
    stale_plugin_names,
)
from watcher_runtime.skill.runtime_paths import (  # noqa: E402
    ensure_runtime_dirs as runtime_ensure_runtime_dirs,
    hook_backup_dir,
    log_file_path,
    report_state_path as runtime_report_state_path,
    reports_dir,
    safe_slug as runtime_safe_slug,
    state_dir_from_env_or_arg as runtime_state_dir_from_env_or_arg,
    turns_dir,
)
from watcher_runtime.skill.report_pipeline import (  # noqa: E402
    ReportOutputPolicy,
    ReportQuery,
    generate_report as run_report_pipeline,
)
from sync_codex_agents import load_sources  # noqa: E402
from watcher_runtime.skill.report_pipeline import parse_since, read_events_since  # noqa: E402
from watcher_runtime.skill.proposal_artifact import update_status  # noqa: E402


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

    def test_check_runner_reports_permission_error_without_traceback(self) -> None:
        runner = CheckRunner()

        def denied_run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
            raise PermissionError("denied")

        with mock.patch("check_my_codex.subprocess.run", denied_run):
            result = runner.run_command(["codex", "plugin", "list"], env={})

        self.assertEqual(result.returncode, 126)
        self.assertIn("command not executable: codex", result.stderr)

    def test_windows_codex_resolution_uses_path_then_managed_fallbacks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            user_home = root / "UserProfile"
            local_app_data = root / "LocalAppData"
            codex_home = user_home / ".codex"
            visible_cli = local_app_data / "Programs" / "OpenAI" / "Codex" / "bin" / "codex.exe"
            standalone_cli = codex_home / "packages" / "standalone" / "current" / "bin" / "codex.exe"
            legacy_standalone_cli = codex_home / "packages" / "standalone" / "current" / "codex.exe"
            desktop_cli = local_app_data / "OpenAI" / "Codex" / "bin" / "abc123" / "codex.exe"
            extension_cli = (
                user_home
                / ".vscode"
                / "extensions"
                / "openai.chatgpt-1.2.3"
                / "bin"
                / "windows-x86_64"
                / "codex.exe"
            )
            for candidate in (visible_cli, standalone_cli, legacy_standalone_cli, desktop_cli, extension_cli):
                candidate.parent.mkdir(parents=True, exist_ok=True)
                candidate.write_text("", encoding="utf-8")
            path_cli = root / "WindowsApps" / "OpenAI.Codex" / "codex.exe"

            with mock.patch.object(refresh_my_codex.sys, "platform", "win32"):
                with mock.patch("refresh_my_codex.platform.machine", return_value="AMD64"):
                    with mock.patch.dict(
                        os.environ,
                        {
                            "HOME": str(user_home),
                            "LOCALAPPDATA": str(local_app_data),
                            "USERPROFILE": str(user_home),
                        },
                        clear=True,
                    ):
                        with mock.patch("refresh_my_codex.shutil.which", return_value=str(path_cli)):
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(path_cli),
                            )

                        with mock.patch("refresh_my_codex.shutil.which", return_value=None):
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(visible_cli),
                            )
                            visible_cli.unlink()
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(standalone_cli),
                            )
                            standalone_cli.unlink()
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(legacy_standalone_cli),
                            )
                            legacy_standalone_cli.unlink()
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(desktop_cli),
                            )
                            desktop_cli.unlink()
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(extension_cli),
                            )

    def test_unix_codex_resolution_uses_path_then_standalone_then_vscode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            user_home = root / "home"
            codex_home = user_home / ".codex"
            custom_visible_cli = root / "custom-install" / "codex"
            visible_cli = user_home / ".local" / "bin" / "codex"
            standalone_cli = codex_home / "packages" / "standalone" / "current" / "bin" / "codex"
            legacy_standalone_cli = codex_home / "packages" / "standalone" / "current" / "codex"
            extension_cli = (
                user_home
                / ".vscode-server"
                / "extensions"
                / "openai.chatgpt-1.2.3"
                / "bin"
                / "linux-x86_64"
                / "codex"
            )
            for candidate in (custom_visible_cli, visible_cli, standalone_cli, legacy_standalone_cli, extension_cli):
                candidate.parent.mkdir(parents=True, exist_ok=True)
                candidate.write_text("", encoding="utf-8")
            path_cli = root / "path" / "codex"

            with mock.patch.object(refresh_my_codex.sys, "platform", "linux"):
                with mock.patch("refresh_my_codex.platform.machine", return_value="x86_64"):
                    with mock.patch.dict(
                        os.environ,
                        {
                            "CODEX_INSTALL_DIR": str(custom_visible_cli.parent),
                            "HOME": str(user_home),
                        },
                        clear=True,
                    ):
                        with mock.patch("refresh_my_codex.shutil.which", return_value=str(path_cli)):
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(path_cli),
                            )

                        with mock.patch("refresh_my_codex.shutil.which", return_value=None):
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(custom_visible_cli),
                            )
                            custom_visible_cli.unlink()
                            os.environ.pop("CODEX_INSTALL_DIR")
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(visible_cli),
                            )
                            visible_cli.unlink()
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(standalone_cli),
                            )
                            standalone_cli.unlink()
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(legacy_standalone_cli),
                            )
                            legacy_standalone_cli.unlink()
                            self.assertEqual(
                                resolve_codex_executable(None, codex_home=codex_home),
                                str(extension_cli),
                            )

    def test_codex_resolution_treats_explicit_sources_as_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            configured_cli = root / "configured" / "codex"
            configured_cli.parent.mkdir(parents=True)
            configured_cli.write_text("", encoding="utf-8")
            explicit_cli = root / "explicit" / "codex"
            explicit_cli.parent.mkdir(parents=True)
            explicit_cli.write_text("", encoding="utf-8")

            with mock.patch.dict(os.environ, {"CODEX_BIN": str(configured_cli)}, clear=True):
                self.assertEqual(
                    resolve_codex_executable(str(explicit_cli), codex_home=codex_home),
                    str(explicit_cli),
                )

                with self.assertRaisesRegex(SystemExit, "missing-explicit"):
                    resolve_codex_executable(str(root / "missing-explicit" / "codex"), codex_home=codex_home)

            with mock.patch.dict(
                os.environ,
                {"CODEX_BIN": str(root / "missing-configured" / "codex")},
                clear=True,
            ):
                with self.assertRaisesRegex(SystemExit, "missing-configured"):
                    resolve_codex_executable(None, codex_home=codex_home)

    def test_watcher_plugin_validation_uses_tooling_python(self) -> None:
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
            ["watcher@my-codex"],
            env={},
            validator=validator,
        )

        self.assertEqual(calls[0][0][0], str(tooling_python))
        self.assertEqual(calls[0][0][1], str(validator))
        self.assertIsNone(calls[0][1])

    def test_check_runner_uses_canonical_watcher_doctor_entrypoint(self) -> None:
        runner = CheckRunner()
        calls: list[list[str]] = []

        def fake_run_command(command, *, env, cwd=None):  # type: ignore[no-untyped-def]
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, "ok", "")

        runner.run_command = fake_run_command  # type: ignore[method-assign]
        tooling_python = Path("C:/tooling/python.exe")

        runner.check_doctor(tooling_python, env={})

        self.assertEqual(
            calls,
            [
                [
                    str(tooling_python),
                    str(ROOT / "scripts" / "watcher"),
                    "skill",
                    "doctor",
                ]
            ],
        )

    def test_install_manifest_drives_default_plugin_selection(self) -> None:
        expected = [
            "watcher",
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
            selected_plugins(["watcher"], "my-codex", action="install"),
            ["watcher@my-codex"],
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

    def test_agent_sync_ignores_legacy_custom_agent_toml_presets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_root = Path(tmp)
            (source_root / "operating-principles.md").write_text("support note\n", encoding="utf-8")
            (source_root / "reviewer.toml").write_text('name = "reviewer"\n', encoding="utf-8")

            sources = load_sources(source_root)

        self.assertEqual([source.target_name for source in sources], ["operating-principles.md"])

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

    def test_mattpocock_v123_metadata_preserves_native_and_historical_attribution(self) -> None:
        metadata = discover_skill_metadata(REPO_ROOT)
        packaged = set(metadata["skills"])
        for skill_name in (
            "code-review",
            "implement",
            "research",
            "resolving-merge-conflicts",
            "setup-matt-pocock-skills",
            "to-questionnaire",
            "to-spec",
            "to-tickets",
            "wait-what",
            "wayfinder",
            "wizard",
            "writing-for-agents",
        ):
            full_name = f"mattpocock-skills:{skill_name}"
            self.assertIn(full_name, packaged)
            aliases = metadata["skills"][full_name]["aliases"]
            self.assertIn(
                {"value": full_name, "kind": "skill_name", "match": "phrase"},
                aliases,
            )
            self.assertIn(
                {"value": skill_name, "kind": "slug", "match": "token"},
                aliases,
            )

        explicit_workflows = {
            "ask-matt",
            "grill-me",
            "grill-with-docs",
            "handoff",
            "implement",
            "improve-codebase-architecture",
            "setup-matt-pocock-skills",
            "teach",
            "to-questionnaire",
            "to-spec",
            "to-tickets",
            "triage",
            "wait-what",
            "wayfinder",
        }
        for full_name, values in metadata["skills"].items():
            if not full_name.startswith("mattpocock-skills:"):
                continue
            skill_name = full_name.split(":", 1)[1]
            expected_group = (
                "explicit-workflows"
                if skill_name in explicit_workflows
                else "implicit-primitives"
            )
            self.assertEqual(values["logical_group"], expected_group)

        self.assertNotIn("mattpocock-skills:to-prd", packaged)
        self.assertNotIn("mattpocock-skills:to-issues", packaged)
        self.assertNotIn("mattpocock-skills:writing-great-skills", packaged)
        self.assertIn("mattpocock-skills:setup-matt-pocock-skills", packaged)
        self.assertEqual(
            set(metadata["skills"]["mattpocock-skills:implement"]["supporting_skills"]),
            {
                "mattpocock-skills:code-review",
                "mattpocock-skills:tdd",
            },
        )
        self.assertEqual(
            set(metadata["skills"]["mattpocock-skills:wayfinder"]["supporting_skills"]),
            {
                "mattpocock-skills:domain-modeling",
                "mattpocock-skills:grilling",
                "mattpocock-skills:prototype",
                "mattpocock-skills:research",
            },
        )

        renamed = (
            ("mattpocock-skills:to-prd", "to-prd", "mattpocock-skills:to-spec"),
            ("mattpocock-skills:to-issues", "to-issues", "mattpocock-skills:to-tickets"),
            (
                "mattpocock-skills:write-a-skill",
                "write-a-skill",
                "mattpocock-skills:writing-for-agents",
            ),
            (
                "mattpocock-skills:writing-great-skills",
                "writing-great-skills",
                "mattpocock-skills:writing-for-agents",
            ),
        )
        for legacy_full_name, legacy_slug, current_name in renamed:
            with self.subTest(legacy_full_name=legacy_full_name, source="provided"):
                provided = normalize_hook_payload(
                    {
                        "hook_event_name": "UserPromptSubmit",
                        "skill_name": legacy_full_name,
                    }
                )
                self.assertEqual(provided["skill_attribution"]["primary"]["name"], current_name)
                self.assertEqual(provided["skill_attribution"]["primary"]["source"], "provided")

            for prompt_alias in (legacy_full_name, legacy_slug):
                with self.subTest(prompt_alias=prompt_alias, source="prompt_mention"):
                    prompt = normalize_hook_payload(
                        {
                            "hook_event_name": "UserPromptSubmit",
                            "prompt": f"Use ${prompt_alias} for this work",
                        }
                    )
                    primary = prompt["skill_attribution"]["primary"]
                    self.assertEqual(primary["name"], current_name)
                    self.assertEqual(primary["source"], "prompt_mention")
                    self.assertEqual(primary["alias_kind"], "legacy")

    def test_codex_hook_lifecycle_filters_summarizes_and_guards_skill_list(self) -> None:
        packaged = sorted(
            f"{plugin_name}:{skill_file.parent.name}"
            for plugin_name in default_plugin_names("install", marketplace_name="my-codex")
            for skill_file in (REPO_ROOT / "plugins" / plugin_name / "skills").glob("*/SKILL.md")
        )
        self.assertIn("mattpocock-skills:setup-matt-pocock-skills", packaged)
        self.assertEqual(discover_packaged_skills(REPO_ROOT), tuple(packaged))
        metadata = discover_skill_metadata(REPO_ROOT)
        self.assertEqual(set(metadata["skills"]), set(packaged))
        self.assertEqual(
            metadata["legacy_names"]["mattpocock-skills:diagnose"],
            "mattpocock-skills:diagnosing-bugs",
        )
        self.assertEqual(
            metadata["skills"]["mattpocock-skills:grill-with-docs"]["supporting_skills"],
            ["mattpocock-skills:domain-modeling", "mattpocock-skills:grilling"],
        )

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
        self.assertNotIn("skill_name", normalized)
        self.assertIsNone(normalized["skill_attribution"]["primary"])
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
            lines = log_file_path(state_dir).read_text(encoding="utf-8").splitlines()
            dynamic_skills = load_dynamic_monitored_skills(state_dir)

        self.assertFalse(session_start["codex"]["persisted"])
        self.assertEqual(session_start["codex"]["metadata_update"]["skill_count"], len(packaged))
        self.assertEqual(dynamic_skills, tuple(packaged))
        self.assertFalse(unknown["codex"]["persisted"])
        self.assertEqual(prompt["skill_attribution"]["primary"]["name"], "mattpocock-skills:diagnosing-bugs")
        self.assertEqual(prompt["skill_attribution"]["primary"]["source"], "prompt_mention")
        self.assertTrue(prompt["codex"]["persisted"])
        self.assertIn("user_skill_context", prompt["codex"])
        self.assertFalse(success["codex"]["persisted"])
        self.assertTrue(failure["codex"]["persisted"])
        self.assertEqual(summary["event_type"], "turn_summary")
        self.assertEqual(summary["codex"]["turn_summary"]["tool_count"], 2)
        self.assertEqual(summary["codex"]["turn_summary"]["tool_failure_count"], 1)
        self.assertEqual(summary["codex"]["turn_summary"]["task_outcome"], "unknown")
        self.assertEqual(summary["outcome"], "unknown")
        self.assertIn("user_skill_context", summary["codex"]["turn_summary"])
        self.assertEqual(len(lines), 3)
        self.assertNotIn("sk-testsecret123456789", "\n".join(lines))

        sop_prompt = normalize_hook_payload(
            {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "请使用标准流程整理这次重复任务。",
            }
        )
        self.assertEqual(sop_prompt["skill_attribution"]["primary"]["name"], "workflow:sop")
        self.assertEqual(sop_prompt["skill_attribution"]["primary"]["source"], "prompt_mention")
        self.assertEqual(sop_prompt["skill_attribution"]["primary"]["matched_alias"], "标准流程")

        sop_assistant = normalize_hook_payload(
            {
                "hook_event_name": "Stop",
                "last_assistant_message": "I will use $sop for this recurring procedure.",
            }
        )
        self.assertEqual(sop_assistant["skill_attribution"]["primary"]["name"], "workflow:sop")
        self.assertEqual(sop_assistant["skill_attribution"]["primary"]["source"], "assistant_announcement")
        self.assertEqual(sop_assistant["skill_attribution"]["primary"]["matched_alias"], "sop")

    def test_metadata_discovery_rejects_invalid_marketplace_contracts(self) -> None:
        cases = (
            ("missing", None, "marketplace file missing"),
            ("invalid-json", "{not-json\n", "invalid marketplace JSON"),
            ("invalid-plugins", json.dumps({"plugins": {}}), "plugins must be a list"),
            ("invalid-entry", json.dumps({"plugins": ["bad"]}), "entry #1 must be an object"),
            (
                "missing-name",
                json.dumps({"plugins": [{"source": {"source": "local", "path": "./plugins/demo"}}]}),
                "entry #1 name missing",
            ),
            (
                "unknown-source-kind",
                json.dumps({"plugins": [{"name": "demo", "source": {"source": "git"}}]}),
                "unsupported marketplace source kind",
            ),
            (
                "missing-local-plugin",
                json.dumps(
                    {
                        "plugins": [
                            {
                                "name": "missing",
                                "source": {"source": "local", "path": "./plugins/missing"},
                            }
                        ]
                    }
                ),
                "local plugin path missing",
            ),
        )
        for label, marketplace_text, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                marketplace = root / ".agents" / "plugins" / "marketplace.json"
                if marketplace_text is not None:
                    marketplace.parent.mkdir(parents=True)
                    marketplace.write_text(marketplace_text, encoding="utf-8")

                with self.assertRaises(SystemExit) as raised:
                    discover_skill_metadata(root)

                self.assertIn(expected, str(raised.exception))

    def test_metadata_discovery_rejects_invalid_plugin_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins" / "demo"
            marketplace = root / ".agents" / "plugins" / "marketplace.json"
            marketplace.parent.mkdir(parents=True)
            marketplace.write_text(
                json.dumps(
                    {
                        "plugins": [
                            {
                                "name": "demo",
                                "source": {"source": "local", "path": "./plugins/demo"},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            skill = plugin / "skills" / "foo" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: foo\ndescription: Test.\n---\n", encoding="utf-8")
            manifest = plugin / ".codex-plugin" / "plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("{not-json\n", encoding="utf-8")

            with self.assertRaises(SystemExit) as raised:
                discover_skill_metadata(root)

        self.assertIn("invalid plugin manifest JSON", str(raised.exception))

    def test_metadata_discovery_rejects_catalog_manifest_name_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins" / "demo"
            marketplace = root / ".agents" / "plugins" / "marketplace.json"
            marketplace.parent.mkdir(parents=True)
            marketplace.write_text(
                json.dumps(
                    {
                        "plugins": [
                            {
                                "name": "catalog-name",
                                "source": {"source": "local", "path": "./plugins/demo"},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            manifest = plugin / ".codex-plugin" / "plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                json.dumps({"name": "manifest-name", "version": "1.0.0"}),
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit) as raised:
                discover_skill_metadata(root)

        self.assertIn("marketplace/plugin manifest name mismatch", str(raised.exception))

    def test_metadata_discovery_requires_known_manifest_schema(self) -> None:
        for schema_version in (None, 999):
            with self.subTest(schema_version=schema_version), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plugin = root / "plugins" / "demo"
                marketplace = root / ".agents" / "plugins" / "marketplace.json"
                marketplace.parent.mkdir(parents=True)
                marketplace.write_text(
                    json.dumps(
                        {
                            "plugins": [
                                {
                                    "name": "demo",
                                    "source": {"source": "local", "path": "./plugins/demo"},
                                }
                            ]
                        }
                    ),
                    encoding="utf-8",
                )
                plugin_manifest = plugin / ".codex-plugin" / "plugin.json"
                plugin_manifest.parent.mkdir(parents=True)
                plugin_manifest.write_text(
                    json.dumps({"name": "demo", "version": "1.0.0"}),
                    encoding="utf-8",
                )
                skill = plugin / "skills" / "foo" / "SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_text("---\nname: foo\ndescription: Test.\n---\n", encoding="utf-8")
                metadata = {"skills": {}, "legacy_names": {}}
                if schema_version is not None:
                    metadata["schema_version"] = schema_version
                (plugin / ".codex-plugin" / "skill-watcher.json").write_text(
                    json.dumps(metadata),
                    encoding="utf-8",
                )

                with self.assertRaises(SystemExit) as raised:
                    discover_skill_metadata(root)

                self.assertIn("unsupported skill metadata schema_version", str(raised.exception))

    def test_metadata_discovery_rejects_duplicate_legacy_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = []
            for plugin_name in ("alpha", "beta"):
                plugin = root / "plugins" / plugin_name
                entries.append(
                    {
                        "name": plugin_name,
                        "source": {"source": "local", "path": f"./plugins/{plugin_name}"},
                    }
                )
                plugin_manifest = plugin / ".codex-plugin" / "plugin.json"
                plugin_manifest.parent.mkdir(parents=True)
                plugin_manifest.write_text(
                    json.dumps({"name": plugin_name, "version": "1.0.0"}),
                    encoding="utf-8",
                )
                skill_name = f"{plugin_name}:entry"
                skill = plugin / "skills" / "entry" / "SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_text("---\nname: entry\ndescription: Test.\n---\n", encoding="utf-8")
                (plugin / ".codex-plugin" / "skill-watcher.json").write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "skills": {},
                            "legacy_names": {"legacy:shared": skill_name},
                        }
                    ),
                    encoding="utf-8",
                )
            marketplace = root / ".agents" / "plugins" / "marketplace.json"
            marketplace.parent.mkdir(parents=True)
            marketplace.write_text(json.dumps({"plugins": entries}), encoding="utf-8")

            with self.assertRaises(SystemExit) as raised:
                discover_skill_metadata(root)

        self.assertIn("duplicate legacy skill metadata entries", str(raised.exception))

    def test_metadata_discovery_rejects_invalid_logical_group(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins" / "demo"
            marketplace = root / ".agents" / "plugins" / "marketplace.json"
            marketplace.parent.mkdir(parents=True)
            marketplace.write_text(
                json.dumps(
                    {
                        "plugins": [
                            {
                                "name": "demo",
                                "source": {"source": "local", "path": "./plugins/demo"},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            plugin_manifest = plugin / ".codex-plugin" / "plugin.json"
            plugin_manifest.parent.mkdir(parents=True)
            plugin_manifest.write_text(
                json.dumps({"name": "demo", "version": "1.0.0"}),
                encoding="utf-8",
            )
            skill = plugin / "skills" / "entry" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: entry\ndescription: Test.\n---\n", encoding="utf-8")
            (plugin / ".codex-plugin" / "skill-watcher.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "skills": {"demo:entry": {"logical_group": "Not Valid"}},
                        "legacy_names": {},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit) as raised:
                discover_skill_metadata(root)

        self.assertIn("invalid logical_group", str(raised.exception))

    def test_session_start_surfaces_metadata_discovery_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            state_dir = Path(tmp) / "state"
            marketplace = root / ".agents" / "plugins" / "marketplace.json"
            marketplace.parent.mkdir(parents=True)
            marketplace.write_text("{not-json\n", encoding="utf-8")

            with mock.patch.dict("os.environ", {"MY_CODEX_ROOT": str(root)}, clear=False):
                with self.assertRaises(SystemExit) as raised:
                    process_hook(
                        {
                            "hook_event_name": "SessionStart",
                            "session_id": "metadata-failure",
                        },
                        HookRuntimePaths(state_dir=state_dir, log_file=log_file_path(state_dir)),
                    )

            self.assertFalse((state_dir / "skill-metadata-cache.json").exists())

        self.assertIn("invalid marketplace JSON", str(raised.exception))

    def test_hook_runtime_dry_run_normalizes_without_writing_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            result = process_hook(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "cwd": "/tmp/workspace",
                    "session_id": "session-dry-run",
                    "turn_id": "turn-dry-run",
                    "prompt": "Use diagnose on flaky tests",
                },
                HookRuntimePaths(state_dir=state_dir, log_file=log_file_path(state_dir)),
                persist=False,
            )

            self.assertFalse(log_file_path(state_dir).exists())
            self.assertEqual(list((state_dir / "turns").glob("*.json")), [])

        self.assertTrue(result.persisted)
        self.assertEqual(result.hook_event_name, "UserPromptSubmit")
        self.assertEqual(result.event["skill_attribution"]["primary"]["name"], "mattpocock-skills:diagnosing-bugs")

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
        adapter = Path(r"C:\Users\Max Smith\Projects\my-codex\plugins\watcher\scripts\watcher")
        with mock.patch("watcher_runtime.skill.codex_hook_config.os.name", "nt"):
            self.assertEqual(
                skill_watcher_command(python, adapter),
                r'"C:\Users\Max Smith\.codex\venvs\my-codex\Scripts\python.exe" -B '
                r'"C:\Users\Max Smith\Projects\my-codex\plugins\watcher\scripts\watcher" skill observe',
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
            adapter=Path("/tmp/watcher/scripts/watcher"),
        )
        installed_again, removed = install_skill_watcher_hooks(
            installed,
            python_path=Path("/tmp/python"),
            adapter=Path("/tmp/watcher/scripts/watcher"),
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
            managed = [handler for handler in handlers if "skill observe" in handler["command"]]
            self.assertTrue(managed)
            for handler in managed:
                self.assertIs(handler["async"], False)
                self.assertEqual(handler["timeoutSec"], 10)
                self.assertNotIn("timeout", handler)

        old_handler = {
            "type": "command",
            "command": "/tmp/python /tmp/watcher/scripts/skill/codex_hook_adapter.py",
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
            adapter=Path("/tmp/watcher/scripts/watcher"),
        )

        self.assertEqual(matched_events, {"SessionStart", "UserPromptSubmit"})
        self.assertTrue(any("timeoutSec" in issue for issue in issues))
        self.assertTrue(any("unexpected keys: timeout" in issue for issue in issues))
        self.assertTrue(any("SessionStart" in issue for issue in issues))

    def test_runtime_paths_centralize_state_layout_and_env_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "state"
            custom_log = Path(tmp) / "custom-events.jsonl"

            runtime_ensure_runtime_dirs(state_dir)

            self.assertEqual(log_file_path(state_dir), state_dir / "logs" / "events.jsonl")
            self.assertEqual(log_file_path(state_dir, str(custom_log)), custom_log)
            self.assertEqual(runtime_report_state_path(state_dir), state_dir / "report-state.json")
            self.assertEqual(reports_dir(state_dir), state_dir / "reports")
            self.assertEqual(hook_backup_dir(state_dir), state_dir / "backups" / "hooks-json")
            self.assertEqual(turns_dir(state_dir), state_dir / "turns")
            for dirname in ("logs", "reports", "proposals", "snapshots", "rejected", "backups", "turns"):
                self.assertTrue((state_dir / dirname).is_dir())

            with mock.patch.dict("os.environ", {"WATCHER_SKILL_STATE_DIR": str(state_dir)}, clear=False):
                self.assertEqual(runtime_state_dir_from_env_or_arg(None), state_dir)
            self.assertEqual(runtime_state_dir_from_env_or_arg(str(state_dir / "explicit")), state_dir / "explicit")
            self.assertEqual(runtime_safe_slug("skill watcher:demo", fallback="x"), "skill-watcher-demo")
            self.assertEqual(runtime_safe_slug("!!!", fallback="x"), "x")

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

    def test_report_pipeline_writes_report_state_and_counts_outcomes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            log_file = log_file_path(state_dir)
            log_file.parent.mkdir(parents=True)
            events = [
                {
                    "timestamp": "2026-06-05T00:00:00Z",
                    "event_type": "turn_summary",
                    "session_id": "s1",
                    "outcome": "unknown",
                    "task_outcome": "failure",
                    "skill_attribution": {
                        "primary": {"name": "demo", "role": "entrypoint"},
                        "supporting": [{"name": "support", "role": "discipline"}],
                        "effective": ["demo", "support"],
                        "mentioned": [],
                    },
                    "codex": {
                        "turn_id": "t1",
                        "turn_summary": {"task_outcome": "failure", "tool_failure_count": 2},
                    },
                },
                {
                    "timestamp": "2026-06-06T00:00:00Z",
                    "event_type": "turn_summary",
                    "session_id": "s2",
                    "outcome": "unknown",
                    "task_outcome": "success",
                    "skill_attribution": {
                        "primary": {"name": "demo", "role": "entrypoint"},
                        "supporting": [],
                        "effective": ["demo"],
                        "mentioned": [],
                    },
                    "codex": {
                        "turn_id": "t2",
                        "turn_summary": {"task_outcome": "success", "tool_failure_count": 0},
                    },
                },
            ]
            log_file.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
            (state_dir / "skill-metadata-cache.json").write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "skills": {
                            "demo": {"logical_group": "explicit-workflows"},
                            "support": {"logical_group": "implicit-primitives"},
                        },
                        "legacy_names": {},
                    }
                ),
                encoding="utf-8",
            )

            result = run_report_pipeline(
                ReportQuery(
                    state_dir=state_dir,
                    log_file=log_file,
                    skill="demo",
                    since_raw="2026-06-05T00:00:00Z",
                    incremental=True,
                ),
                ReportOutputPolicy(write_output=True),
            )
            loaded = load_report_state(state_dir)
            output_exists = result.output.is_file() if result.output is not None else False

        self.assertEqual(result.event_count, 2)
        self.assertEqual(result.outcome_counts["failure"], 1)
        self.assertEqual(result.outcome_counts["success"], 1)
        self.assertIn("supporting-only", result.report)
        self.assertIn("`support`", result.report)
        self.assertIn("## Usage By Logical Group", result.report)
        self.assertIn("| explicit-workflows | 2 | 2 | 0 | `demo` |", result.report)
        self.assertIn("| implicit-primitives | 1 | 0 | 1 | `support` |", result.report)
        self.assertIn("| `demo` | entrypoint | explicit-workflows |", result.report)
        self.assertIsNotNone(result.output)
        self.assertTrue(output_exists)
        self.assertEqual(result.state_path, state_dir / "report-state.json")
        self.assertEqual(loaded["reports"]["demo"]["last_event_count"], 2)


if __name__ == "__main__":
    unittest.main()
