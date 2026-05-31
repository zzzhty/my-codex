#!/usr/bin/env python3
"""Normalize Codex hook payloads into Skill Watcher JSONL events."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from collect_event import append_event, ensure_runtime_dirs, expand_path, normalize_event, state_dir_from_env_or_arg
from redact_event import redact_event, redact_string


SUPPORTED_HOOK_EVENTS = {"SessionStart", "UserPromptSubmit", "PostToolUse", "Stop"}
SUMMARY_LIMIT = 160
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


def normalize_hook_payload(payload: dict[str, Any]) -> dict[str, Any]:
    hook_event_name = str(payload.get("hook_event_name") or payload.get("event") or "unknown")
    event_type = camel_to_snake(hook_event_name)
    skill_name = str(payload.get("skill_name") or payload.get("skill") or "unknown")
    skill_attribution = "provided" if skill_name != "unknown" else "unknown"
    tool_name = payload.get("tool_name")

    outcome = "unknown"
    failure_type = ""
    if hook_event_name == "PostToolUse":
        outcome, failure_type = detect_post_tool_outcome(payload.get("tool_response"))

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
        },
    }

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


def write_hook_event(payload: dict[str, Any], *, state_dir: Path | None = None, log_file: Path | None = None) -> dict[str, Any]:
    target_state_dir = state_dir or state_dir_from_env_or_arg(None)
    target_log_file = log_file or target_state_dir / "logs" / "events.jsonl"
    event = normalize_hook_payload(payload)
    ensure_runtime_dirs(target_state_dir)
    append_event(event, target_log_file)
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
    event = normalize_hook_payload(payload)

    if args.dry_run:
        json.dump(event, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return

    ensure_runtime_dirs(state_dir)
    append_event(event, log_file)

    if args.print_event:
        json.dump(event, sys.stdout, ensure_ascii=False, sort_keys=True)
        sys.stdout.write("\n")
    elif payload.get("hook_event_name") == "Stop":
        json.dump({"continue": True, "suppressOutput": True}, sys.stdout, separators=(",", ":"))
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
