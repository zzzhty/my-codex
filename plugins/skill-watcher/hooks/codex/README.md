# Codex Hook Integration

Skill Watcher V1 installs user-level Codex command hooks in `$CODEX_HOME/hooks.json`. It does not use plugin manifest hooks and does not modify `.codex-plugin/plugin.json`.

Install:

```bash
export MY_CODEX_ROOT="${MY_CODEX_ROOT:-$(git rev-parse --show-toplevel)}"
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export MY_CODEX_PYTHON="${MY_CODEX_PYTHON:-$CODEX_HOME/venvs/my-codex/bin/python}"

"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/install_codex_hook.py" --dry-run
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/install_codex_hook.py" --apply
```

Uninstall:

```bash
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/uninstall_codex_hook.py" --dry-run
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/uninstall_codex_hook.py" --apply
```

After install, open `/hooks` in Codex and review/trust the Skill Watcher command hook definitions. Codex skips non-managed command hooks until the exact hook definition is trusted.

## Handler

The installed command is:

```bash
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/codex_hook_adapter.py"
```

It observes these Codex lifecycle events:

- `SessionStart`
- `UserPromptSubmit`
- `PostToolUse`
- `Stop`

The adapter reads one Codex hook JSON object from stdin and appends a normalized, redacted Skill Watcher event to `$CODEX_HOME/skill-watcher/logs/events.jsonl`.

## Mapping

- `cwd` -> `workspace`
- `session_id` -> `session_id`
- `hook_event_name` -> normalized `event_type`
- `tool_name` -> `tools_used`
- `model`, `turn_id`, `permission_mode`, `transcript_path`, and `tool_use_id` -> `codex` metadata

For `PostToolUse`, responses with explicit non-zero exit status or error markers become `outcome: "failure"` and `failure_type: "tool_error"`. Empty or missing responses become `outcome: "unknown"`; other responses become `outcome: "success"`.

## Privacy Defaults

The adapter records summaries, lengths, hashes, tool names, outcomes, and redacted metadata. It does not persist full prompts, full assistant messages, full shell commands, full tool responses, file contents, secrets, or private business data.

Codex hook payloads do not include a stable native skill identifier. If `skill_name` is absent, Skill Watcher writes `skill_name: "unknown"` and does not parse transcripts to guess.

For `Stop`, the adapter prints minimal JSON output that lets Codex continue. Other observed events print nothing in hook mode, so they do not inject context or block the turn.
