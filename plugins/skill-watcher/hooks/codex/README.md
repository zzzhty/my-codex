# Codex Hook Integration

Skill Watcher V1 installs user-level Codex command hooks in `$CODEX_HOME/hooks.json`. It does not use plugin manifest hooks and does not modify `.codex-plugin/plugin.json`.

Install:

Unix:

```bash
export MY_CODEX_ROOT="${MY_CODEX_ROOT:-$(git rev-parse --show-toplevel)}"
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export MY_CODEX_PYTHON="${MY_CODEX_PYTHON:-$CODEX_HOME/venvs/my-codex/bin/python}"

"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/install_codex_hook.py" --dry-run
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/install_codex_hook.py" --apply
```

Windows PowerShell:

```powershell
# Run from the my-codex checkout.
$env:CODEX_HOME = "$env:USERPROFILE\.codex"
$env:MY_CODEX_ROOT = (Get-Location).Path
$python = "$env:CODEX_HOME\venvs\my-codex\Scripts\python.exe"

uv venv "$env:CODEX_HOME\venvs\my-codex"
uv pip install --python $python -r "$env:MY_CODEX_ROOT\requirements.txt"

& $python "$env:MY_CODEX_ROOT\plugins\skill-watcher\scripts\install_codex_hook.py" --dry-run --python $python
& $python "$env:MY_CODEX_ROOT\plugins\skill-watcher\scripts\install_codex_hook.py" --apply --python $python
```

Uninstall:

```bash
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/uninstall_codex_hook.py" --dry-run
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/uninstall_codex_hook.py" --apply
```

After install, open `/hooks` in Codex and review/trust the Skill Watcher command hook definitions. Codex skips non-managed command hooks until the exact hook definition is trusted.

Plugin marketplace refreshes do not rewrite `$CODEX_HOME/hooks.json`. After changing hook logic, rerun the hook installer above or refresh the whole `my-codex` marketplace from the repository root:

```bash
python3 scripts/refresh_my_codex.py
```

Windows PowerShell:

```powershell
py scripts\refresh_my_codex.py
```

The repository-level helper refreshes the marketplace with Git first and local checkout fallback before reinstalling plugin cache entries and hooks.

## Handler

The installed command is:

```bash
"$MY_CODEX_PYTHON" -B "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/codex_hook_adapter.py"
```

On Windows, the installed command is rendered as a Windows command line with `Scripts\python.exe`; on Unix, it is rendered with POSIX shell quoting. Command hook handlers use `async: false` and `timeoutSec` to match the current Codex hook schema.

It observes these Codex lifecycle events by default:

- `SessionStart`
- `UserPromptSubmit`
- `PostToolUse`
- `Stop`

`SessionStart` refreshes `$CODEX_HOME/skill-watcher/monitored-skills.json` and is not persisted by default.

The adapter reads one Codex hook JSON object from stdin, infers monitored-skill attribution when possible, and appends only useful normalized events to `$CODEX_HOME/skill-watcher/logs/events.jsonl`.

## Mapping

- `cwd` -> `workspace`
- `session_id` -> `session_id`
- `hook_event_name` -> normalized `event_type`
- `tool_name` -> `tools_used`
- `model`, `turn_id`, `permission_mode`, `transcript_path`, and `tool_use_id` -> `codex` metadata

For `PostToolUse`, responses with explicit non-zero exit status or error markers become `outcome: "failure"` and `failure_type: "tool_error"`. Empty or missing responses become `outcome: "unknown"`; other responses become `outcome: "success"`.

By default, successful `PostToolUse` events are counted in transient turn state but are not persisted as individual log records. Failed `PostToolUse` events are persisted only when a monitored skill is active. `Stop` writes one monitored `turn_summary` event and clears transient state.

## Monitored Skill Attribution

Codex hook payloads do not include a stable native skill identifier. Skill Watcher therefore records only explainable monitored-skill attribution:

- `provided`: hook payload explicitly supplied a monitored `skill_name`
- `prompt_mention`: the user prompt explicitly mentioned a monitored skill name or alias
- `assistant_announcement`: the assistant message explicitly mentioned a monitored skill name or alias
- `unknown`: no reliable monitored-skill signal

The default monitored skill allowlist is every skill packaged by the `my-codex` marketplace. Override it with the comma-, semicolon-, or newline-separated `SKILL_WATCHER_MONITORED_SKILLS` environment variable when a narrower run is needed.

For monitored prompts, the adapter stores a redacted `user_skill_context` summary, length, hash, and matched alias. This captures the extra information users mention while invoking a skill as improvement evidence without storing raw prompts.

## Privacy Defaults

The adapter records summaries, lengths, hashes, tool names, outcomes, and redacted metadata. It does not persist full prompts, full assistant messages, full shell commands, full tool responses, file contents, secrets, or private business data.

For `Stop`, the adapter prints minimal JSON output that lets Codex continue. Other observed events print nothing in hook mode, so they do not inject context or block the turn.
