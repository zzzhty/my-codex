#!/usr/bin/env python3
"""Shared Codex hooks.json merge helpers for Skill Watcher."""

from __future__ import annotations

import copy
import difflib
import json
import os
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def expand_path(raw: str | Path) -> Path:
    return Path(os.path.expandvars(str(raw))).expanduser()


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CODEX_HOME = expand_path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
DEFAULT_TOOLING_VENV = CODEX_HOME / "venvs" / "my-codex"
DEFAULT_TARGET = CODEX_HOME / "hooks.json"
DEFAULT_STATE_DIR = CODEX_HOME / "skill-watcher"
HOOK_EVENTS = ("UserPromptSubmit", "PostToolUse", "Stop")
STATUS_PREFIX = "Skill Watcher:"
ADAPTER_NAME = "codex_hook_adapter.py"


def default_python() -> Path:
    override = os.environ.get("MY_CODEX_TOOLING_PYTHON")
    if override:
        return expand_path(override)
    windows_python = DEFAULT_TOOLING_VENV / "Scripts" / "python.exe"
    if os.name == "nt" and windows_python.is_file():
        return windows_python
    return DEFAULT_TOOLING_VENV / "bin" / "python"


def adapter_path() -> Path:
    return PLUGIN_ROOT / "scripts" / ADAPTER_NAME


def skill_watcher_command(python_path: Path | None = None, adapter: Path | None = None) -> str:
    args = [str(python_path or default_python()), str(adapter or adapter_path())]
    if os.name == "nt":
        return subprocess.list2cmdline(args)
    return " ".join(shlex.quote(arg) for arg in args)


def desired_handler(event: str, *, python_path: Path | None = None, adapter: Path | None = None) -> dict[str, Any]:
    return {
        "type": "command",
        "async": False,
        "command": skill_watcher_command(python_path, adapter),
        "timeoutSec": 10,
        "statusMessage": f"{STATUS_PREFIX} observe {event}",
    }


def desired_group(event: str, *, python_path: Path | None = None, adapter: Path | None = None) -> dict[str, Any]:
    return {"hooks": [desired_handler(event, python_path=python_path, adapter=adapter)]}


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to read hook config {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid hook config JSON {path}: line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"hook config {path} must contain a JSON object")
    return data


def dump_config(config: dict[str, Any]) -> str:
    return json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def validate_hook_shape(config: dict[str, Any]) -> None:
    hooks = config.get("hooks")
    if hooks is None:
        return
    if not isinstance(hooks, dict):
        raise SystemExit("hook config field `hooks` must be an object")
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            raise SystemExit(f"hook config event {event!r} must be a list")
        for index, group in enumerate(groups):
            if not isinstance(group, dict):
                raise SystemExit(f"hook config event {event!r} group {index} must be an object")
            handlers = group.get("hooks")
            if handlers is not None and not isinstance(handlers, list):
                raise SystemExit(f"hook config event {event!r} group {index} field `hooks` must be a list")


def is_skill_watcher_handler(handler: Any) -> bool:
    if not isinstance(handler, dict):
        return False
    command = str(handler.get("command") or "")
    status = str(handler.get("statusMessage") or "")
    return status.startswith(STATUS_PREFIX) or (ADAPTER_NAME in command and "skill-watcher" in command)


def remove_skill_watcher_hooks(config: dict[str, Any]) -> tuple[dict[str, Any], int]:
    updated = copy.deepcopy(config)
    validate_hook_shape(updated)
    hooks = updated.get("hooks")
    if not isinstance(hooks, dict):
        return updated, 0

    removed = 0
    for event in list(hooks.keys()):
        groups = hooks[event]
        if not isinstance(groups, list):
            continue
        retained_groups: list[dict[str, Any]] = []
        for group in groups:
            if not isinstance(group, dict):
                retained_groups.append(group)
                continue
            handlers = group.get("hooks", [])
            if not isinstance(handlers, list):
                retained_groups.append(group)
                continue
            retained_handlers = [handler for handler in handlers if not is_skill_watcher_handler(handler)]
            removed += len(handlers) - len(retained_handlers)
            if retained_handlers:
                new_group = copy.deepcopy(group)
                new_group["hooks"] = retained_handlers
                retained_groups.append(new_group)
        if retained_groups:
            hooks[event] = retained_groups
        else:
            del hooks[event]

    if not hooks:
        updated.pop("hooks", None)
    return updated, removed


def install_skill_watcher_hooks(
    config: dict[str, Any],
    *,
    python_path: Path | None = None,
    adapter: Path | None = None,
) -> tuple[dict[str, Any], int]:
    updated, removed = remove_skill_watcher_hooks(config)
    hooks = updated.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SystemExit("hook config field `hooks` must be an object")
    for event in HOOK_EVENTS:
        groups = hooks.setdefault(event, [])
        if not isinstance(groups, list):
            raise SystemExit(f"hook config event {event!r} must be a list")
        groups.append(desired_group(event, python_path=python_path, adapter=adapter))
    return updated, removed


def render_diff(before: dict[str, Any] | None, after: dict[str, Any], path: Path) -> str:
    before_text = "" if before is None else dump_config(before)
    after_text = dump_config(after)
    diff = difflib.unified_diff(
        before_text.splitlines(keepends=True),
        after_text.splitlines(keepends=True),
        fromfile=f"{path} (before)",
        tofile=f"{path} (after)",
    )
    return "".join(diff) or "no changes\n"


def backup_existing_file(path: Path, *, state_dir: Path = DEFAULT_STATE_DIR) -> Path | None:
    if not path.exists():
        return None
    backup_dir = state_dir / "backups" / "hooks-json"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = backup_dir / f"{timestamp}-hooks.json"
    try:
        shutil.copyfile(path, backup_path)
    except OSError as exc:
        raise SystemExit(f"failed to back up hook config {path} to {backup_path}: {exc}") from exc
    return backup_path


def write_config(path: Path, config: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(dump_config(config), encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to write hook config {path}: {exc}") from exc
