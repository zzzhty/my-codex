#!/usr/bin/env python3
"""Run final closure checks for the local my-codex installation."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from refresh_my_codex import (
    CODEX_HOME,
    DEFAULT_VENV,
    MARKETPLACE_FILE,
    REPO_ROOT,
    build_env,
    command_text,
    expand_path,
    resolve_executable,
    selected_plugins,
    tooling_python_from_args,
)


SKILL_WATCHER_SCRIPTS = REPO_ROOT / "plugins" / "skill-watcher" / "scripts"
sys.path.insert(0, str(SKILL_WATCHER_SCRIPTS))

from codex_hook_config import adapter_path, load_config  # noqa: E402
from doctor import find_managed_hook_issues  # noqa: E402


def configure_output_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")


def decode_subprocess_output(raw: bytes | str | None) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    return raw.decode("utf-8", errors="replace")


def print_text(message: str) -> None:
    try:
        print(message)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        safe = message.encode(encoding, errors="backslashreplace").decode(encoding, errors="replace")
        print(safe)


class CheckRunner:
    def __init__(self) -> None:
        self.failures = 0
        self.warnings = 0

    def ok(self, message: str) -> None:
        print_text(f"OK   {message}")

    def warn(self, message: str) -> None:
        self.warnings += 1
        print_text(f"WARN {message}")

    def fail(self, message: str) -> None:
        self.failures += 1
        print_text(f"FAIL {message}")

    def run_command(self, command: list[str], *, env: dict[str, str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        print("+ " + command_text(command), flush=True)
        try:
            result = subprocess.run(command, cwd=str(cwd) if cwd else None, env=env, capture_output=True)
            return subprocess.CompletedProcess(
                command,
                result.returncode,
                decode_subprocess_output(result.stdout),
                decode_subprocess_output(result.stderr),
            )
        except FileNotFoundError as exc:
            return subprocess.CompletedProcess(command, 127, "", f"command not found: {exc.filename}")

    def check_marketplace_file(self, expected_plugins: list[str]) -> None:
        if not MARKETPLACE_FILE.is_file():
            self.fail(f"marketplace file missing: {MARKETPLACE_FILE}")
            return
        try:
            data = json.loads(MARKETPLACE_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.fail(f"marketplace file is not valid JSON: {MARKETPLACE_FILE}: {exc}")
            return
        if data.get("name") != "my-codex":
            self.fail(f"marketplace name mismatch in {MARKETPLACE_FILE}: {data.get('name')!r}")
            return
        marketplace_plugins = data.get("plugins")
        if not isinstance(marketplace_plugins, list):
            self.fail(f"marketplace plugins field is not a list: {MARKETPLACE_FILE}")
            return
        present = {str(plugin.get("name")) for plugin in marketplace_plugins if isinstance(plugin, dict)}
        expected = {selector.split("@", 1)[0] for selector in expected_plugins}
        missing = sorted(expected - present)
        if missing:
            self.fail(f"marketplace is missing plugins: {', '.join(missing)}")
            return
        self.ok(f"marketplace file includes expected plugins: {MARKETPLACE_FILE}")

    def check_tooling_python(self, tooling_python: Path, *, env: dict[str, str]) -> None:
        if not tooling_python.is_file():
            self.fail(f"tooling Python missing: {tooling_python}")
            return
        result = self.run_command([str(tooling_python), "-c", "import yaml; print(yaml.__version__)"], env=env)
        if result.returncode == 0:
            self.ok(f"tooling Python imports PyYAML: {tooling_python} ({result.stdout.strip()})")
        else:
            output = (result.stderr or result.stdout).strip()
            self.fail(f"tooling Python cannot import PyYAML: {tooling_python}: {output}")

    def check_codex_plugin_list(self, codex: str, plugins: list[str], *, env: dict[str, str]) -> None:
        result = self.run_command([codex, "plugin", "list"], env=env)
        if result.returncode != 0:
            output = (result.stderr or result.stdout).strip()
            self.fail(f"`codex plugin list` failed: {output}")
            return
        output = result.stdout
        if "Marketplace `my-codex`" not in output:
            self.fail("`codex plugin list` does not include Marketplace `my-codex`")
            return
        failures = []
        for plugin in plugins:
            if plugin not in output:
                failures.append(f"{plugin} missing from plugin list")
            elif "installed, enabled" not in next((line for line in output.splitlines() if plugin in line), ""):
                failures.append(f"{plugin} is not installed, enabled")
        if failures:
            self.fail("; ".join(failures))
            return
        self.ok("codex plugin list shows expected my-codex plugins installed and enabled")

    def check_plugin_cache(self, plugins: list[str], *, codex_home: Path) -> None:
        missing = []
        cache_root = codex_home / "plugins" / "cache"
        for selector in plugins:
            plugin_name, _, marketplace_name = selector.partition("@")
            plugin_root = cache_root / marketplace_name / plugin_name
            manifests = sorted(plugin_root.glob("*/.codex-plugin/plugin.json"))
            if not manifests:
                missing.append(str(plugin_root))
        if missing:
            self.fail("plugin cache missing installed manifests: " + "; ".join(missing))
            return
        self.ok(f"plugin cache contains installed manifests under {cache_root}")

    def check_hook_config(self, tooling_python: Path, *, hook_config: Path) -> None:
        if not hook_config.is_file():
            self.fail(f"Skill Watcher hook config missing: {hook_config}")
            return
        try:
            config = load_config(hook_config)
        except SystemExit as exc:
            self.fail(str(exc))
            return
        matched_events, issues = find_managed_hook_issues(
            config,
            python_path=tooling_python,
            adapter=adapter_path(),
        )
        if issues:
            self.fail(
                "Skill Watcher hook config has stale managed handlers. "
                f"Run scripts/refresh_my_codex.py. Issues: {issues}"
            )
            return
        expected = {"UserPromptSubmit", "PostToolUse", "Stop"}
        if matched_events != expected:
            self.fail(
                "Skill Watcher hook config event coverage mismatch: "
                f"expected {sorted(expected)}, found {sorted(matched_events)}"
            )
            return
        self.ok(f"Skill Watcher hooks match current schema: {hook_config}")

    def check_plugin_validation(
        self,
        tooling_python: Path,
        plugins: list[str],
        *,
        env: dict[str, str],
        validator: Path,
    ) -> None:
        if not validator.is_file():
            self.fail(f"plugin validator missing: {validator}")
            return
        for selector in plugins:
            plugin_name = selector.split("@", 1)[0]
            plugin_dir = REPO_ROOT / "plugins" / plugin_name
            result = self.run_command([str(tooling_python), str(validator), str(plugin_dir)], env=env)
            if result.returncode == 0:
                self.ok(f"plugin validation passed: {plugin_name}")
            else:
                output = (result.stderr or result.stdout).strip()
                self.fail(f"plugin validation failed for {plugin_name}: {output}")

    def check_doctor(self, tooling_python: Path, *, env: dict[str, str]) -> None:
        doctor = REPO_ROOT / "plugins" / "skill-watcher" / "scripts" / "doctor.py"
        result = self.run_command([str(tooling_python), str(doctor)], env=env)
        if result.returncode == 0:
            self.ok("Skill Watcher doctor passed")
        else:
            output = (result.stderr or result.stdout).strip()
            self.fail(f"Skill Watcher doctor failed: {output}")

    def check_agent_sync(self, *, codex_home: Path, env: dict[str, str]) -> None:
        sync_script = REPO_ROOT / "scripts" / "sync_codex_agents.py"
        if not sync_script.is_file():
            self.fail(f"agent sync script missing: {sync_script}")
            return
        result = self.run_command(
            [sys.executable, str(sync_script), "--check", "--prune", "--codex-home", str(codex_home)],
            env=env,
        )
        if result.returncode == 0:
            self.ok(f"custom agents are synced: {codex_home / 'agents'}")
        else:
            output = (result.stderr or result.stdout).strip()
            self.fail(f"custom agents are not synced: {output}")

    def finish(self, *, strict_warnings: bool) -> None:
        if strict_warnings and self.warnings:
            self.failures += self.warnings
        if self.failures:
            raise SystemExit(f"check failed with {self.failures} failure(s), {self.warnings} warning(s)")
        print(f"check passed with {self.warnings} warning(s)")


def main() -> None:
    configure_output_streams()

    parser = argparse.ArgumentParser(description="Final checks for my-codex plugin and hook state.")
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"), help="Codex CLI executable.")
    parser.add_argument("--codex-home", default=str(CODEX_HOME), help="Codex home directory.")
    parser.add_argument("--venv", default=str(DEFAULT_VENV), help="Shared my-codex tooling venv path.")
    parser.add_argument("--python", help="Explicit tooling Python expected in hooks and diagnostics.")
    parser.add_argument("--marketplace-name", default="my-codex", help="Configured marketplace name.")
    parser.add_argument("--plugin", action="append", help="Plugin name or selector to check. May be repeated.")
    parser.add_argument("--skip-plugins", action="store_true", help="Skip `codex plugin list` and plugin cache checks.")
    parser.add_argument("--skip-hooks", action="store_true", help="Skip Skill Watcher hook config checks.")
    parser.add_argument("--skip-agents", action="store_true", help="Skip custom-agent sync checks.")
    parser.add_argument("--skip-plugin-validation", action="store_true", help="Skip plugin validator checks.")
    parser.add_argument("--skip-doctor", action="store_true", help="Skip Skill Watcher doctor.")
    parser.add_argument(
        "--skip-skill-watcher-doctor",
        action="store_true",
        help="Alias for --skip-doctor.",
    )
    parser.add_argument("--strict-warnings", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args()

    codex_home = expand_path(args.codex_home)
    venv_path = expand_path(args.venv)
    tooling_python = tooling_python_from_args(args, venv_path)
    env = build_env(codex_home=codex_home, tooling_python=tooling_python)
    codex = resolve_executable(args.codex)
    plugins = selected_plugins(args.plugin, args.marketplace_name, action="check")
    validator = Path(env["PLUGIN_VALIDATOR"])

    runner = CheckRunner()
    runner.check_marketplace_file(plugins)
    runner.check_tooling_python(tooling_python, env=env)
    if not args.skip_plugins:
        runner.check_codex_plugin_list(codex, plugins, env=env)
        runner.check_plugin_cache(plugins, codex_home=codex_home)
    if not args.skip_hooks:
        runner.check_hook_config(tooling_python, hook_config=codex_home / "hooks.json")
    if not args.skip_agents:
        runner.check_agent_sync(codex_home=codex_home, env=env)
    if not args.skip_plugin_validation:
        runner.check_plugin_validation(tooling_python, plugins, env=env, validator=validator)
    if not args.skip_doctor and not args.skip_skill_watcher_doctor:
        runner.check_doctor(tooling_python, env=env)
    runner.finish(strict_warnings=args.strict_warnings)


if __name__ == "__main__":
    main()
