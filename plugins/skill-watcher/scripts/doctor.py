#!/usr/bin/env python3
"""Run Skill Watcher V1 environment diagnostics."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from codex_hook_adapter import write_hook_event
from codex_hook_config import DEFAULT_TARGET, HOOK_EVENTS, PLUGIN_ROOT, default_python, is_skill_watcher_handler, load_config
from collect_event import DEFAULT_STATE_DIR, ensure_runtime_dirs


VALIDATOR = Path("/Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py")


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
        if not VALIDATOR.is_file():
            self.fail(f"plugin validator missing: {VALIDATOR}")
            return
        result = subprocess.run([str(python_path), str(VALIDATOR), str(PLUGIN_ROOT)], text=True, capture_output=True)
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
        hooks = config.get("hooks", {})
        if not isinstance(hooks, dict):
            self.fail(f"hook config field `hooks` is not an object: {DEFAULT_TARGET}")
            return
        matched_events = []
        stale_commands = []
        expected_python = str(default_python())
        for event in HOOK_EVENTS:
            for group in hooks.get(event, []):
                if not isinstance(group, dict):
                    continue
                matching_handlers = [handler for handler in group.get("hooks", []) if is_skill_watcher_handler(handler)]
                if matching_handlers:
                    matched_events.append(event)
                    for handler in matching_handlers:
                        command = str(handler.get("command") or "")
                        if expected_python not in command:
                            stale_commands.append(command)
                    break
        if set(matched_events) == set(HOOK_EVENTS):
            self.ok(f"Skill Watcher hook handlers installed: {DEFAULT_TARGET}")
        else:
            missing = sorted(set(HOOK_EVENTS) - set(matched_events))
            self.warn(f"Skill Watcher hook config incomplete at {DEFAULT_TARGET}; missing: {', '.join(missing)}")
        if stale_commands:
            self.fail(
                "Skill Watcher hook config uses a non-default Python interpreter; "
                f"expected {expected_python}; stale commands: {stale_commands}"
            )

    def check_sample_event(self) -> None:
        sample = {
            "hook_event_name": "UserPromptSubmit",
            "cwd": str(PLUGIN_ROOT),
            "session_id": "doctor-session",
            "turn_id": "doctor-turn",
            "model": "doctor-model",
            "prompt": "sample prompt containing token sk-doctorsecret1234567890",
        }
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            event = write_hook_event(sample, state_dir=state_dir)
            log_file = state_dir / "logs" / "events.jsonl"
            raw = log_file.read_text(encoding="utf-8")
        if "sk-doctorsecret" in raw:
            self.fail("sample event leaked a secret-like token")
            return
        if event.get("skill_name") != "unknown":
            self.fail("sample event did not default missing skill_name to unknown")
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
