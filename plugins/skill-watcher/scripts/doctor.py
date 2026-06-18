#!/usr/bin/env python3
"""Run Skill Watcher V1 environment diagnostics."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from codex_hook_adapter import write_hook_event
from codex_hook_config import (
    CODEX_HOME,
    DEFAULT_TARGET,
    HOOK_EVENTS,
    PLUGIN_ROOT,
    adapter_path,
    default_python,
    desired_handler,
    expand_path,
    is_skill_watcher_handler,
    load_config,
    validate_hook_shape,
)
from collect_event import DEFAULT_STATE_DIR, ensure_runtime_dirs


def describe_handler_mismatch(handler: dict[str, object], expected: dict[str, object]) -> list[str]:
    mismatches = []
    for key, expected_value in expected.items():
        if handler.get(key) != expected_value:
            mismatches.append(f"{key} expected {expected_value!r}, found {handler.get(key)!r}")
    extra_keys = sorted(set(handler) - set(expected))
    if extra_keys:
        mismatches.append(f"unexpected keys: {', '.join(extra_keys)}")
    return mismatches


def find_managed_hook_issues(
    config: dict[str, object],
    *,
    python_path: Path,
    adapter: Path,
) -> tuple[set[str], list[str]]:
    hooks = config.get("hooks", {})
    if not isinstance(hooks, dict):
        return set(), ["hook config field `hooks` is not an object"]

    matched_events: set[str] = set()
    issues: list[str] = []
    expected_events = set(HOOK_EVENTS)
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            continue
        for group_index, group in enumerate(groups):
            if not isinstance(group, dict):
                continue
            handlers = group.get("hooks", [])
            if not isinstance(handlers, list):
                continue
            for handler_index, handler in enumerate(handlers):
                if not is_skill_watcher_handler(handler):
                    continue
                location = f"{event}[{group_index}].hooks[{handler_index}]"
                if event not in expected_events:
                    issues.append(f"{location} is a stale Skill Watcher event; default install no longer uses {event}")
                    continue
                matched_events.add(str(event))
                expected = desired_handler(str(event), python_path=python_path, adapter=adapter)
                mismatches = describe_handler_mismatch(handler, expected)
                if mismatches:
                    issues.append(f"{location} does not match desired handler schema: {'; '.join(mismatches)}")
    return matched_events, issues


def validator_path() -> Path:
    override = os.environ.get("PLUGIN_VALIDATOR") or os.environ.get("CODEX_PLUGIN_VALIDATOR")
    if override:
        return expand_path(override)
    return CODEX_HOME / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"


class Doctor:
    def __init__(self) -> None:
        self.failures = 0
        self.warnings = 0

    def ok(self, message: str) -> None:
        print(f"OK   {message}")

    def warn(self, message: str) -> None:
        self.warnings += 1
        print(f"WARN {message}")

    def fail(self, message: str) -> None:
        self.failures += 1
        print(f"FAIL {message}")

    def run(self) -> None:
        python_path = default_python()
        if python_path.is_file():
            self.ok(f"tooling python exists: {python_path}")
        else:
            self.fail(f"tooling python missing: {python_path}")
            return

        self.check_pyyaml(python_path)
        self.check_plugin_validation(python_path)
        self.check_state_dir()
        self.check_hook_config()
        self.check_sample_event()

        if self.failures:
            raise SystemExit(f"doctor failed with {self.failures} failure(s), {self.warnings} warning(s)")
        print(f"doctor passed with {self.warnings} warning(s)")

    def check_pyyaml(self, python_path: Path) -> None:
        result = subprocess.run(
            [str(python_path), "-c", "import yaml; print(yaml.__version__)"],
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            self.ok(f"PyYAML import works: {result.stdout.strip()}")
        else:
            self.fail(f"PyYAML import failed: {result.stderr.strip() or result.stdout.strip()}")

    def check_plugin_validation(self, python_path: Path) -> None:
        validator = validator_path()
        if not validator.is_file():
            self.fail(f"plugin validator missing: {validator}")
            return
        result = subprocess.run([str(python_path), str(validator), str(PLUGIN_ROOT)], text=True, capture_output=True)
        if result.returncode == 0:
            self.ok("plugin validation passed")
        else:
            output = (result.stderr or result.stdout).strip()
            self.fail(f"plugin validation failed: {output}")

    def check_state_dir(self) -> None:
        try:
            ensure_runtime_dirs(DEFAULT_STATE_DIR)
        except OSError as exc:
            self.fail(f"state directory is not writable: {DEFAULT_STATE_DIR}: {exc}")
            return
        self.ok(f"state directory writable: {DEFAULT_STATE_DIR}")

    def check_hook_config(self) -> None:
        if not DEFAULT_TARGET.exists():
            self.warn(f"hook config not installed yet: {DEFAULT_TARGET}")
            return
        try:
            config = load_config(DEFAULT_TARGET)
        except SystemExit as exc:
            self.fail(str(exc))
            return
        try:
            validate_hook_shape(config)
        except SystemExit as exc:
            self.fail(str(exc))
            return

        python_path = default_python()
        matched_events, issues = find_managed_hook_issues(config, python_path=python_path, adapter=adapter_path())
        if set(matched_events) == set(HOOK_EVENTS):
            self.ok(f"Skill Watcher hook handlers installed: {DEFAULT_TARGET}")
        else:
            missing = sorted(set(HOOK_EVENTS) - set(matched_events))
            self.warn(f"Skill Watcher hook config incomplete at {DEFAULT_TARGET}; missing: {', '.join(missing)}")

        if issues:
            self.fail(
                "Skill Watcher hook config has stale managed handlers at "
                f"{DEFAULT_TARGET}. Run install_codex_hook.py --apply to refresh. Issues: {issues}"
            )

    def check_sample_event(self) -> None:
        sample = {
            "hook_event_name": "UserPromptSubmit",
            "cwd": str(PLUGIN_ROOT),
            "session_id": "doctor-session",
            "turn_id": "doctor-turn",
            "model": "doctor-model",
            "prompt": "Use diagnose on this sample prompt containing token sk-doctorsecret1234567890",
        }
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            event = write_hook_event(sample, state_dir=state_dir)
            log_file = state_dir / "logs" / "events.jsonl"
            raw = log_file.read_text(encoding="utf-8")
        if "sk-doctorsecret" in raw:
            self.fail("sample event leaked a secret-like token")
            return
        if event.get("skill_name") != "mattpocock-skills:diagnosing-bugs":
            self.fail("sample event did not infer the monitored diagnosing-bugs skill")
            return
        parsed = json.loads(raw.strip())
        if parsed.get("codex", {}).get("prompt_summary"):
            self.ok("sample hook event appended and redacted")
        else:
            self.fail("sample hook event missing prompt summary")


def main() -> None:
    Doctor().run()


if __name__ == "__main__":
    main()
