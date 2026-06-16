#!/usr/bin/env python3
"""Normalize Codex hook payloads into Skill Watcher JSONL events."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from collect_event import append_event, ensure_runtime_dirs, expand_path, normalize_event, state_dir_from_env_or_arg
from redact_event import redact_event, redact_string


SUPPORTED_HOOK_EVENTS = {"SessionStart", "UserPromptSubmit", "PostToolUse", "Stop"}
SUMMARY_LIMIT = 160
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST_FILE = "monitored-skills.json"
DEFAULT_MONITORED_SKILLS = (
    "skill-watcher:skill-maintainer",
    "skill-watcher:skill-compressor",
    "doc-watcher:doc-alignment",
    "doc-watcher:housekeeping",
    "workflow:long-running-goal",
    "workflow:orchestrate-subagents",
    "workflow:prompt-strategy-loop",
    "workflow:sop",
    "workflow:summary-in-html",
    "mattpocock-skills:caveman",
    "mattpocock-skills:diagnose",
    "mattpocock-skills:grill-me",
    "mattpocock-skills:grill-with-docs",
    "mattpocock-skills:handoff",
    "mattpocock-skills:improve-codebase-architecture",
    "mattpocock-skills:prototype",
    "mattpocock-skills:setup-matt-pocock-skills",
    "mattpocock-skills:tdd",
    "mattpocock-skills:to-issues",
    "mattpocock-skills:to-prd",
    "mattpocock-skills:triage",
    "mattpocock-skills:write-a-skill",
    "mattpocock-skills:zoom-out",
)
DEFAULT_SKILL_ALIASES = {
    "skill-watcher:skill-maintainer": ("skill-maintainer", "skill maintainer", "skill watcher"),
    "skill-watcher:skill-compressor": ("skill-compressor", "skill compressor", "skill compression"),
    "doc-watcher:doc-alignment": ("doc-alignment", "doc watcher", "documentation alignment"),
    "doc-watcher:housekeeping": ("housekeeping", "cleanup", "clean up", "repo cleanup"),
    "workflow:long-running-goal": ("long-running-goal", "long running goal", "long-running goal"),
    "workflow:orchestrate-subagents": ("orchestrate-subagents", "orchestrate subagents"),
    "workflow:prompt-strategy-loop": (
        "prompt-strategy-loop",
        "prompt strategy loop",
        "prompt loop",
        "strategy loop",
    ),
    "workflow:summary-in-html": ("summary-in-html", "summary in html", "html summary", "developer summary"),
    "workflow:sop": (
        "sop",
        "standard operating procedure",
        "standard procedure",
        "标准流程",
        "标准处理流程",
    ),
    "mattpocock-skills:caveman": ("caveman", "caveman mode"),
    "mattpocock-skills:diagnose": ("diagnose", "diagnose this", "debug this"),
    "mattpocock-skills:grill-me": ("grill-me", "grill me"),
    "mattpocock-skills:grill-with-docs": ("grill-with-docs", "grill with docs"),
    "mattpocock-skills:handoff": ("handoff", "handoff document"),
    "mattpocock-skills:improve-codebase-architecture": (
        "improve-codebase-architecture",
        "improve codebase architecture",
        "improve architecture",
        "architecture review",
    ),
    "mattpocock-skills:prototype": ("prototype", "prototype this"),
    "mattpocock-skills:setup-matt-pocock-skills": ("setup-matt-pocock-skills", "setup matt pocock skills"),
    "mattpocock-skills:tdd": ("tdd", "test-driven", "red-green-refactor"),
    "mattpocock-skills:to-issues": ("to-issues", "to issues"),
    "mattpocock-skills:to-prd": ("to-prd", "to prd"),
    "mattpocock-skills:triage": ("triage", "triage issues"),
    "mattpocock-skills:write-a-skill": ("write-a-skill", "write a skill"),
    "mattpocock-skills:zoom-out": ("zoom-out", "zoom out"),
}
FAILURE_TEXT_RE = re.compile(
    r"(?:exit(?:ed)?\s+(?:with\s+)?(?:code|status)\s+[1-9]\d*|"
    r"non[- ]zero\s+exit|traceback|exception|error)",
    re.IGNORECASE,
)


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        raise SystemExit("no Codex hook JSON provided on stdin")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid Codex hook JSON: line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("Codex hook payload must be a JSON object")
    return payload


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def compact_text(value: str, *, limit: int = SUMMARY_LIMIT) -> str:
    redacted = redact_string(value)
    compacted = " ".join(redacted.split())
    if not compacted:
        return ""
    if len(compacted) <= 12:
        return "[omitted]"
    if len(compacted) <= limit:
        prefix_length = min(len(compacted) - 1, max(12, len(compacted) // 2))
        return compacted[:prefix_length] + "..."
    return compacted[: limit - 3] + "..."


def summarize_text(value: str, *, limit: int = SUMMARY_LIMIT) -> dict[str, Any]:
    return {
        "type": "text",
        "length": len(value),
        "sha256": sha256_text(value),
        "summary": compact_text(value, limit=limit),
    }


def json_fingerprint(value: Any) -> str:
    try:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    except TypeError:
        raw = repr(value)
    return raw


def summarize_json_value(value: Any, *, limit: int = SUMMARY_LIMIT) -> dict[str, Any]:
    if isinstance(value, str):
        return summarize_text(value, limit=limit)

    redacted = redact_event(value)
    raw = json_fingerprint(redacted)
    summary: dict[str, Any] = {
        "type": type(value).__name__,
        "length": len(raw),
        "sha256": sha256_text(raw),
        "summary": compact_text(raw, limit=limit),
    }
    if isinstance(value, dict):
        summary["keys"] = sorted(str(key) for key in value.keys())[:20]
    elif isinstance(value, list):
        summary["items"] = len(value)
    return summary


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_env_list(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return ()
    values = re.split(r"[,\n;]+", raw)
    return tuple(value.strip() for value in values if value.strip())


def marketplace_root_from_adapter() -> Path:
    override = os.environ.get("MY_CODEX_ROOT")
    if override:
        return expand_path(override)
    for parent in Path(__file__).resolve().parents:
        if (parent / ".agents" / "plugins" / "marketplace.json").is_file():
            return parent
    for parent in Path(__file__).resolve().parents:
        if parent.name == "plugins":
            return parent.parent
    return PLUGIN_ROOT


def plugin_name_from_manifest(plugin_dir: Path) -> str:
    manifest = plugin_dir / ".codex-plugin" / "plugin.json"
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        if isinstance(data, dict) and isinstance(data.get("name"), str) and data["name"].strip():
            return data["name"].strip()
    return plugin_dir.name


def skill_name_from_frontmatter(skill_file: Path) -> str:
    try:
        lines = skill_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return skill_file.parent.name
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == "---":
                break
            if stripped.startswith("name:"):
                name = stripped.split(":", 1)[1].strip().strip("\"'")
                return name or skill_file.parent.name
    return skill_file.parent.name


def marketplace_plugin_dirs(marketplace_root: Path) -> list[Path]:
    marketplace = marketplace_root / ".agents" / "plugins" / "marketplace.json"
    if not marketplace.is_file():
        return sorted((marketplace_root / "plugins").glob("*"))
    try:
        data = json.loads(marketplace.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return sorted((marketplace_root / "plugins").glob("*"))
    plugins = data.get("plugins") if isinstance(data, dict) else None
    if not isinstance(plugins, list):
        return sorted((marketplace_root / "plugins").glob("*"))

    plugin_dirs: list[Path] = []
    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue
        source = plugin.get("source")
        if not isinstance(source, dict) or source.get("source") != "local":
            continue
        raw_path = source.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            continue
        path = expand_path(raw_path)
        if not path.is_absolute():
            path = marketplace_root / path
        plugin_dirs.append(path)
    return sorted(plugin_dirs)


def discover_packaged_skills(marketplace_root: Path | None = None) -> tuple[str, ...]:
    root = marketplace_root or marketplace_root_from_adapter()
    skills: set[str] = set()
    for plugin_dir in marketplace_plugin_dirs(root):
        skills_dir = plugin_dir / "skills"
        if not skills_dir.is_dir():
            continue
        plugin_name = plugin_name_from_manifest(plugin_dir)
        for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
            skills.add(f"{plugin_name}:{skill_name_from_frontmatter(skill_file)}")
    return tuple(sorted(skills))


def allowlist_path(state_dir: Path) -> Path:
    return state_dir / ALLOWLIST_FILE


def load_dynamic_monitored_skills(state_dir: Path | None = None) -> tuple[str, ...]:
    target_state_dir = state_dir or state_dir_from_env_or_arg(None)
    path = allowlist_path(target_state_dir)
    if not path.is_file():
        return ()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ()
    skills = data.get("skills") if isinstance(data, dict) else None
    if not isinstance(skills, list):
        return ()
    return tuple(str(skill).strip() for skill in skills if str(skill).strip())


def refresh_dynamic_monitored_skills(state_dir: Path) -> dict[str, Any]:
    source_root = marketplace_root_from_adapter()
    skills = discover_packaged_skills(source_root)
    if skills:
        path = allowlist_path(state_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "generated_at": utc_now(),
                    "source_root": str(source_root),
                    "skills": list(skills),
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    return {
        "path": str(allowlist_path(state_dir)),
        "skill_count": len(skills),
        "source_root": str(source_root),
        "updated": bool(skills),
    }


def monitored_skills(state_dir: Path | None = None) -> tuple[str, ...]:
    configured = parse_env_list(os.environ.get("SKILL_WATCHER_MONITORED_SKILLS"))
    if configured:
        return configured
    dynamic = load_dynamic_monitored_skills(state_dir)
    return dynamic or DEFAULT_MONITORED_SKILLS


def aliases_for_skill(skill_name: str) -> tuple[str, ...]:
    aliases = [skill_name]
    if ":" in skill_name:
        aliases.append(skill_name.rsplit(":", 1)[-1])
    aliases.extend(DEFAULT_SKILL_ALIASES.get(skill_name, ()))
    deduped: list[str] = []
    for alias in aliases:
        normalized = alias.strip().lower()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return tuple(deduped)


def alias_matches(text: str, alias: str) -> bool:
    escaped = re.escape(alias)
    if len(alias) <= 4 and re.fullmatch(r"[a-z0-9_-]+", alias):
        return re.search(rf"(?<![a-z0-9_-]){escaped}(?![a-z0-9_-])", text) is not None
    return alias in text


def text_for_matching(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json_fingerprint(value)


def match_monitored_skill(value: Any, *, state_dir: Path | None = None) -> dict[str, str] | None:
    text = text_for_matching(value).lower()
    if not text:
        return None
    for skill_name in monitored_skills(state_dir):
        for alias in aliases_for_skill(skill_name):
            if alias_matches(text, alias):
                return {"skill_name": skill_name, "matched_alias": alias}
    return None


def context_from_match(match: dict[str, str], *, attribution: str, confidence: str) -> dict[str, str]:
    return {
        "skill_name": match["skill_name"],
        "skill_attribution": attribution,
        "skill_confidence": confidence,
        "matched_alias": match["matched_alias"],
    }


def infer_skill_context(payload: dict[str, Any], *, state_dir: Path | None = None) -> dict[str, str] | None:
    provided = payload.get("skill_name") or payload.get("skill")
    provided_match = match_monitored_skill(provided, state_dir=state_dir)
    if provided_match:
        return context_from_match(provided_match, attribution="provided", confidence="high")

    if "prompt" in payload:
        prompt_match = match_monitored_skill(payload.get("prompt"), state_dir=state_dir)
        if prompt_match:
            return context_from_match(prompt_match, attribution="prompt_mention", confidence="high")

    if "last_assistant_message" in payload:
        assistant_match = match_monitored_skill(payload.get("last_assistant_message"), state_dir=state_dir)
        if assistant_match:
            return context_from_match(assistant_match, attribution="assistant_announcement", confidence="medium")

    return None


def user_skill_context(payload: dict[str, Any], context: dict[str, str] | None) -> dict[str, Any] | None:
    if not context or context.get("skill_attribution") != "prompt_mention" or "prompt" not in payload:
        return None
    summary = summarize_json_value(payload.get("prompt"), limit=240)
    summary["matched_alias"] = context.get("matched_alias", "")
    summary["source"] = "prompt"
    return summary


def safe_slug(value: str) -> str:
    slug = "".join(char if char.isalnum() or char in "-_." else "-" for char in value).strip("-")
    return slug or "unknown"


def turn_state_path(state_dir: Path, payload: dict[str, Any]) -> Path | None:
    session_id = str(payload.get("session_id") or "").strip()
    if not session_id:
        return None
    return state_dir / "turns" / f"{safe_slug(session_id)}.json"


def load_turn_state(state_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path = turn_state_path(state_dir, payload)
    if path is None or not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_turn_state(state_dir: Path, payload: dict[str, Any], state: dict[str, Any]) -> None:
    path = turn_state_path(state_dir, payload)
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clear_turn_state(state_dir: Path, payload: dict[str, Any]) -> None:
    path = turn_state_path(state_dir, payload)
    if path is None or not path.exists():
        return
    try:
        path.unlink()
    except OSError:
        return


def state_skill_context(state: dict[str, Any]) -> dict[str, str] | None:
    skill_name = str(state.get("skill_name") or "")
    if not skill_name:
        return None
    return {
        "skill_name": skill_name,
        "skill_attribution": str(state.get("skill_attribution") or "unknown"),
        "skill_confidence": str(state.get("skill_confidence") or "unknown"),
        "matched_alias": str(state.get("matched_alias") or ""),
    }


def initial_turn_state(payload: dict[str, Any], context: dict[str, str], usage_context: dict[str, Any] | None) -> dict[str, Any]:
    state: dict[str, Any] = {
        "schema_version": 1,
        "session_id": str(payload.get("session_id") or ""),
        "turn_id": str(payload.get("turn_id") or ""),
        "skill_name": context["skill_name"],
        "skill_attribution": context["skill_attribution"],
        "skill_confidence": context["skill_confidence"],
        "matched_alias": context.get("matched_alias", ""),
        "tool_count": 0,
        "tool_failures": 0,
        "tools_used": {},
        "started_at": utc_now(),
        "updated_at": utc_now(),
    }
    if usage_context is not None:
        state["user_skill_context"] = usage_context
    return state


def update_tool_stats(state: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    state["tool_count"] = int(state.get("tool_count") or 0) + 1
    if event.get("outcome") == "failure":
        state["tool_failures"] = int(state.get("tool_failures") or 0) + 1
    tools = state.get("tools_used")
    if not isinstance(tools, dict):
        tools = {}
    for tool in event.get("tools_used", []):
        name = str(tool)
        tools[name] = int(tools.get(name) or 0) + 1
    state["tools_used"] = tools
    state["updated_at"] = utc_now()
    return state


def camel_to_snake(value: str) -> str:
    first = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", first).lower()


def truthy_error_value(value: Any) -> bool:
    if value in (None, False, "", [], {}):
        return False
    if isinstance(value, str):
        lowered = value.strip().lower()
        return lowered not in {"0", "false", "none", "null", "ok", "success"}
    return True


def has_failure_marker(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered in {"exit_code", "exitcode", "return_code", "returncode", "status_code"}:
                try:
                    if int(item) != 0:
                        return True
                except (TypeError, ValueError):
                    if truthy_error_value(item):
                        return True
            if lowered in {"error", "errors", "exception", "failure", "failed", "is_error"} and truthy_error_value(item):
                return True
            if has_failure_marker(item):
                return True
        return False
    if isinstance(value, list):
        return any(has_failure_marker(item) for item in value)
    if isinstance(value, str):
        return FAILURE_TEXT_RE.search(value) is not None
    return False


def detect_post_tool_outcome(tool_response: Any) -> tuple[str, str]:
    if tool_response in (None, "", [], {}):
        return "unknown", ""
    if has_failure_marker(tool_response):
        return "failure", "tool_error"
    return "success", ""


def normalize_hook_payload(
    payload: dict[str, Any],
    *,
    skill_context: dict[str, str] | None = None,
    state_dir: Path | None = None,
) -> dict[str, Any]:
    hook_event_name = str(payload.get("hook_event_name") or payload.get("event") or "unknown")
    event_type = camel_to_snake(hook_event_name)
    context = skill_context or infer_skill_context(payload, state_dir=state_dir)
    skill_name = context["skill_name"] if context else "unknown"
    skill_attribution = context["skill_attribution"] if context else "unknown"
    skill_confidence = context["skill_confidence"] if context else "unknown"
    tool_name = payload.get("tool_name")

    outcome = "unknown"
    failure_type = ""
    if hook_event_name == "PostToolUse":
        outcome, failure_type = detect_post_tool_outcome(payload.get("tool_response"))
    elif hook_event_name == "UserPromptSubmit" and context:
        outcome = "success"

    event: dict[str, Any] = {
        "agent": "codex",
        "event_type": event_type,
        "workspace": str(payload.get("cwd") or ""),
        "session_id": str(payload.get("session_id") or ""),
        "skill_name": skill_name,
        "skill_version": str(payload.get("skill_version") or ""),
        "trigger_reason": f"Codex hook {hook_event_name}",
        "tools_used": [str(tool_name)] if tool_name else [],
        "outcome": outcome,
        "failure_type": failure_type,
        "notes": f"Observed Codex {hook_event_name} event.",
        "codex": {
            "hook_event_name": hook_event_name,
            "model": payload.get("model"),
            "turn_id": payload.get("turn_id"),
            "permission_mode": payload.get("permission_mode"),
            "transcript_path": payload.get("transcript_path"),
            "tool_use_id": payload.get("tool_use_id"),
            "skill_attribution": skill_attribution,
            "skill_confidence": skill_confidence,
            "matched_alias": context.get("matched_alias", "") if context else "",
            "monitored_skill": context is not None,
        },
    }

    usage_context = user_skill_context(payload, context)
    if usage_context is not None:
        event["codex"]["user_skill_context"] = usage_context

    if hook_event_name not in SUPPORTED_HOOK_EVENTS:
        event["notes"] = f"Observed unsupported Codex hook event {hook_event_name}."

    if "prompt" in payload:
        event["codex"]["prompt_summary"] = summarize_json_value(payload.get("prompt"))
    if "last_assistant_message" in payload:
        event["codex"]["last_assistant_message_summary"] = summarize_json_value(payload.get("last_assistant_message"))
    if "tool_input" in payload:
        event["codex"]["tool_input_summary"] = summarize_json_value(payload.get("tool_input"))
    if "tool_response" in payload:
        event["codex"]["tool_response_summary"] = summarize_json_value(payload.get("tool_response"))

    args = argparse.Namespace(
        agent=None,
        event_type=None,
        workspace=None,
        session_id=None,
        skill=None,
        skill_version=None,
        trigger_reason=None,
        outcome=None,
        failure_type=None,
        user_feedback=None,
        notes=None,
        tool=None,
        file_touched=None,
        check=None,
    )
    return normalize_event(redact_event(event), args)


def should_persist_event(event: dict[str, Any]) -> bool:
    if os.environ.get("SKILL_WATCHER_DEBUG_ALL_EVENTS", "").strip().lower() in {"1", "true", "yes", "on"}:
        return True

    codex = event.get("codex") if isinstance(event.get("codex"), dict) else {}
    if not codex.get("monitored_skill"):
        return False

    event_type = event.get("event_type")
    if event_type == "user_prompt_submit":
        return True
    if event_type == "post_tool_use":
        return event.get("outcome") == "failure"
    if event_type == "turn_summary":
        return True
    return False


def apply_turn_summary(event: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    tool_count = int(state.get("tool_count") or 0)
    tool_failures = int(state.get("tool_failures") or 0)
    tools_used = state.get("tools_used") if isinstance(state.get("tools_used"), dict) else {}

    event["event_type"] = "turn_summary"
    event["outcome"] = "failure" if tool_failures else "success"
    event["failure_type"] = "tool_error" if tool_failures else ""
    event["notes"] = "Observed monitored Codex turn summary."
    event["tools_used"] = sorted(str(tool) for tool in tools_used.keys())
    event["codex"]["turn_summary"] = {
        "tool_count": tool_count,
        "tool_failures": tool_failures,
        "tools_used": tools_used,
    }
    if isinstance(state.get("user_skill_context"), dict):
        event["codex"]["turn_summary"]["user_skill_context"] = state["user_skill_context"]
    return event


def write_hook_event(payload: dict[str, Any], *, state_dir: Path | None = None, log_file: Path | None = None) -> dict[str, Any]:
    target_state_dir = state_dir or state_dir_from_env_or_arg(None)
    target_log_file = log_file or target_state_dir / "logs" / "events.jsonl"
    ensure_runtime_dirs(target_state_dir)

    hook_event_name = str(payload.get("hook_event_name") or payload.get("event") or "unknown")
    allowlist_update = refresh_dynamic_monitored_skills(target_state_dir) if hook_event_name == "SessionStart" else None
    direct_context = infer_skill_context(payload, state_dir=target_state_dir)
    state = load_turn_state(target_state_dir, payload)
    context = direct_context or state_skill_context(state)
    event = normalize_hook_payload(payload, skill_context=context, state_dir=target_state_dir)
    if allowlist_update is not None:
        event["codex"]["allowlist_update"] = allowlist_update

    if hook_event_name == "UserPromptSubmit":
        if direct_context:
            usage_context = event.get("codex", {}).get("user_skill_context")
            write_turn_state(target_state_dir, payload, initial_turn_state(payload, direct_context, usage_context))
        else:
            clear_turn_state(target_state_dir, payload)
    elif hook_event_name == "PostToolUse" and context:
        if not state:
            state = initial_turn_state(payload, context, None)
        state = update_tool_stats(state, event)
        write_turn_state(target_state_dir, payload, state)
    elif hook_event_name == "Stop" and context:
        event = apply_turn_summary(event, state)

    persisted = should_persist_event(event)
    event["codex"]["persisted"] = persisted
    if persisted:
        append_event(event, target_log_file)
    if hook_event_name == "Stop":
        clear_turn_state(target_state_dir, payload)
    return event


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect a Codex hook event for Skill Watcher.")
    parser.add_argument("--state-dir", help="Runtime state directory. Defaults to $CODEX_HOME/skill-watcher.")
    parser.add_argument("--log-file", help="Explicit JSONL log path. Overrides --state-dir logs/events.jsonl.")
    parser.add_argument("--dry-run", action="store_true", help="Normalize and print the event without appending.")
    parser.add_argument("--print-event", action="store_true", help="Print the normalized event JSON. Not for hook config use.")
    args = parser.parse_args()

    payload = read_payload()
    state_dir = state_dir_from_env_or_arg(args.state_dir)
    log_file = expand_path(args.log_file) if args.log_file else state_dir / "logs" / "events.jsonl"
    if args.dry_run:
        state = load_turn_state(state_dir, payload)
        context = infer_skill_context(payload, state_dir=state_dir) or state_skill_context(state)
        event = normalize_hook_payload(payload, skill_context=context, state_dir=state_dir)
        if str(payload.get("hook_event_name") or payload.get("event") or "unknown") == "Stop" and context:
            event = apply_turn_summary(event, state)
        event["codex"]["persisted"] = should_persist_event(event)
        json.dump(event, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return

    event = write_hook_event(payload, state_dir=state_dir, log_file=log_file)

    if args.print_event:
        json.dump(event, sys.stdout, ensure_ascii=False, sort_keys=True)
        sys.stdout.write("\n")
    elif payload.get("hook_event_name") == "Stop":
        json.dump({"continue": True, "suppressOutput": True}, sys.stdout, separators=(",", ":"))
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
