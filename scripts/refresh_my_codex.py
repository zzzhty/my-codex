#!/usr/bin/env python3
"""Refresh the local my-codex marketplace plugins and Skill Watcher hooks."""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_FILE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
DEFAULT_VENV = CODEX_HOME / "venvs" / "my-codex"
PLUGIN_NAMES = (
    "skill-watcher",
    "doc-watcher",
    "personal-skills",
    "mattpocock-skills",
)


def expand_path(raw: str | Path) -> Path:
    return Path(os.path.expandvars(str(raw))).expanduser()


def venv_python(venv_path: Path) -> Path:
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def command_text(command: list[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def resolve_executable(raw: str) -> str:
    expanded = os.path.expandvars(os.path.expanduser(raw))
    if any(separator in expanded for separator in (os.sep, os.altsep) if separator):
        path = Path(expanded)
        if path.is_file():
            return str(path)
        raise SystemExit(f"executable does not exist: {path}")
    resolved = shutil.which(expanded)
    if resolved is None:
        raise SystemExit(f"executable not found on PATH: {raw}")
    return resolved


def marketplace_source_arg(raw: str) -> str:
    if "://" in raw or raw.startswith("git@"):
        return raw
    expanded = os.path.expandvars(os.path.expanduser(raw))
    path_like = (
        raw.startswith((".", "~", "/", "\\"))
        or (len(raw) >= 3 and raw[1] == ":" and raw[2] in {"\\", "/"})
        or Path(expanded).exists()
    )
    if path_like:
        return str(Path(expanded))
    return raw


def run(command: list[str], *, env: dict[str, str], dry_run: bool) -> None:
    print("+ " + command_text(command), flush=True)
    if dry_run:
        return
    try:
        subprocess.run(command, check=True, env=env)
    except FileNotFoundError as exc:
        raise SystemExit(f"command not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"command failed with exit code {exc.returncode}: {command_text(command)}") from exc


def selected_plugins(raw_plugins: list[str] | None, marketplace_name: str) -> list[str]:
    plugins = raw_plugins or list(PLUGIN_NAMES)
    return [plugin if "@" in plugin else f"{plugin}@{marketplace_name}" for plugin in plugins]


def tooling_python_from_args(args: argparse.Namespace, venv_path: Path) -> Path:
    override = args.python or os.environ.get("MY_CODEX_TOOLING_PYTHON") or os.environ.get("MY_CODEX_PYTHON")
    if override:
        return expand_path(override)
    return venv_python(venv_path)


def build_env(*, codex_home: Path, tooling_python: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    env["MY_CODEX_ROOT"] = str(REPO_ROOT)
    env["MY_CODEX_PYTHON"] = str(tooling_python)
    env["MY_CODEX_TOOLING_PYTHON"] = str(tooling_python)
    env.setdefault(
        "PLUGIN_VALIDATOR",
        str(codex_home / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"),
    )
    return env


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refresh my-codex plugin installs and user-level Skill Watcher hooks."
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them.")
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"), help="Codex CLI executable.")
    parser.add_argument("--codex-home", default=str(CODEX_HOME), help="Codex home directory.")
    parser.add_argument("--venv", default=str(DEFAULT_VENV), help="Shared my-codex tooling venv path.")
    parser.add_argument("--python", help="Explicit tooling Python for hooks and diagnostics.")
    parser.add_argument("--marketplace-name", default="my-codex", help="Configured marketplace name.")
    parser.add_argument(
        "--marketplace-source",
        default=str(REPO_ROOT),
        help="Marketplace source for `codex plugin marketplace add`.",
    )
    parser.add_argument(
        "--marketplace-upgrade",
        action="store_true",
        help="Run `codex plugin marketplace upgrade <name>` instead of adding the local checkout source.",
    )
    parser.add_argument(
        "--plugin",
        action="append",
        help="Plugin name or PLUGIN@MARKETPLACE selector to refresh. May be repeated.",
    )
    parser.add_argument("--skip-bootstrap", action="store_true", help="Do not refresh the shared tooling venv.")
    parser.add_argument("--skip-marketplace", action="store_true", help="Do not refresh marketplace config/snapshot.")
    parser.add_argument("--skip-plugins", action="store_true", help="Do not run `codex plugin add`.")
    parser.add_argument("--skip-hooks", action="store_true", help="Do not refresh Skill Watcher hooks.")
    parser.add_argument("--skip-doctor", action="store_true", help="Do not run Skill Watcher doctor after refresh.")
    args = parser.parse_args()

    if not MARKETPLACE_FILE.is_file():
        raise SystemExit(f"marketplace file does not exist: {MARKETPLACE_FILE}")

    codex_home = expand_path(args.codex_home)
    venv_path = expand_path(args.venv)
    tooling_python = tooling_python_from_args(args, venv_path)
    env = build_env(codex_home=codex_home, tooling_python=tooling_python)
    codex = resolve_executable(args.codex)

    if not args.skip_bootstrap:
        run(
            [sys.executable, str(REPO_ROOT / "scripts" / "bootstrap_tooling_env.py"), "--venv", str(venv_path)],
            env=env,
            dry_run=args.dry_run,
        )

    if not args.skip_marketplace:
        if args.marketplace_upgrade:
            run([codex, "plugin", "marketplace", "upgrade", args.marketplace_name], env=env, dry_run=args.dry_run)
        else:
            run(
                [codex, "plugin", "marketplace", "add", marketplace_source_arg(args.marketplace_source)],
                env=env,
                dry_run=args.dry_run,
            )

    if not args.skip_plugins:
        for plugin in selected_plugins(args.plugin, args.marketplace_name):
            run([codex, "plugin", "add", plugin], env=env, dry_run=args.dry_run)

    hook_installer = REPO_ROOT / "plugins" / "skill-watcher" / "scripts" / "install_codex_hook.py"
    if not args.skip_hooks:
        if not args.dry_run and not tooling_python.is_file():
            raise SystemExit(f"tooling Python does not exist: {tooling_python}")
        if not hook_installer.is_file():
            raise SystemExit(f"Skill Watcher hook installer does not exist: {hook_installer}")
        run(
            [str(tooling_python), str(hook_installer), "--apply", "--python", str(tooling_python)],
            env=env,
            dry_run=args.dry_run,
        )

    doctor = REPO_ROOT / "plugins" / "skill-watcher" / "scripts" / "doctor.py"
    if not args.skip_doctor:
        if not args.dry_run and not tooling_python.is_file():
            raise SystemExit(f"tooling Python does not exist: {tooling_python}")
        run([str(tooling_python), str(doctor)], env=env, dry_run=args.dry_run)

    if args.dry_run:
        print("dry-run only; no changes written")
    else:
        print("refresh complete")
        if not args.skip_hooks:
            print("open /hooks in Codex to review and trust refreshed Skill Watcher command hooks")


if __name__ == "__main__":
    main()
