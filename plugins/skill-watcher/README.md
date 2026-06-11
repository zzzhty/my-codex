# Skill Watcher

Skill Watcher is a `my-codex` Codex plugin for maintaining skills from observed usage evidence. V1 installs user-level Codex hook handlers, records redacted JSONL events, writes report artifacts, generates bounded proposal drafts, and validates candidate `SKILL.md` files.

This plugin is installed from the `my-codex` marketplace. It observes and proposes maintenance updates, but it does not modify existing skills automatically.

## Layout

```text
.codex-plugin/plugin.json
skills/skill-maintainer/
hooks/codex/
scripts/
```

Runtime state is written under `$CODEX_HOME/skill-watcher/`:

```text
logs/events.jsonl
reports/
proposals/
snapshots/
rejected/
backups/
turns/
```

## Setup

Unix:

```bash
export MY_CODEX_ROOT="${MY_CODEX_ROOT:-$(git rev-parse --show-toplevel)}"
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export MY_CODEX_PYTHON="${MY_CODEX_PYTHON:-$CODEX_HOME/venvs/my-codex/bin/python}"
export PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py}"

cd "$MY_CODEX_ROOT"
python3 scripts/bootstrap_tooling_env.py
cd plugins/skill-watcher
```

Windows PowerShell:

```powershell
# Run from the my-codex checkout.
$env:MY_CODEX_ROOT = (Get-Location).Path
$env:CODEX_HOME = "$env:USERPROFILE\.codex"
$env:MY_CODEX_PYTHON = "$env:CODEX_HOME\venvs\my-codex\Scripts\python.exe"
$env:PLUGIN_VALIDATOR = "$env:CODEX_HOME\skills\.system\plugin-creator\scripts\validate_plugin.py"

uv venv "$env:CODEX_HOME\venvs\my-codex"
uv pip install --python $env:MY_CODEX_PYTHON -r requirements.txt
Set-Location plugins\skill-watcher
```

Skill Watcher uses the shared my-codex tooling interpreter:

```text
$MY_CODEX_PYTHON
```

## Smoke Test

```bash
printf '%s\n' '{"event_type":"skill_stop","skill_name":"demo","outcome":"failure","failure_type":"tool_error","notes":"token sk-1234567890 should redact","metadata":{"api_key":"secret"}}' \
  | "$MY_CODEX_PYTHON" scripts/collect_event.py

"$MY_CODEX_PYTHON" scripts/summarize_logs.py --skill demo --since 1d
"$MY_CODEX_PYTHON" scripts/propose_skill_patch.py --skill-dir skills/skill-maintainer --skill skill-maintainer --since 1d
"$MY_CODEX_PYTHON" scripts/validate_candidate.py --candidate-skill skills/skill-maintainer/SKILL.md
```

Validate the plugin:

```bash
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/skill-watcher"
```

## Codex Hook Install

Skill Watcher installs user-level hooks at `$CODEX_HOME/hooks.json` and preserves unrelated hook entries. The default generated handlers observe `SessionStart`, `UserPromptSubmit`, `PostToolUse`, and `Stop`. `SessionStart` refreshes the monitored-skill allowlist and is not persisted unless hook debugging is enabled.

The hook config uses the current Codex command-hook schema:

- command handlers include `type: "command"`, `async: false`, `command`, `timeoutSec`, and `statusMessage`
- Unix commands are shell-quoted with POSIX quoting
- Windows commands are rendered with Windows command-line quoting and use `Scripts\python.exe`
- non-managed command hooks remain `untrusted` until reviewed in Codex `/hooks`

```bash
"$MY_CODEX_PYTHON" scripts/install_codex_hook.py --dry-run
"$MY_CODEX_PYTHON" scripts/install_codex_hook.py --apply
```

On Windows, pass the Windows venv interpreter explicitly if neither `MY_CODEX_TOOLING_PYTHON` nor `MY_CODEX_PYTHON` is set:

```powershell
$python = "$env:USERPROFILE\.codex\venvs\my-codex\Scripts\python.exe"
& $python scripts\install_codex_hook.py --dry-run --python $python
& $python scripts\install_codex_hook.py --apply --python $python
```

After applying, open `/hooks` in Codex and review/trust the new command hook definitions. Codex requires this for non-managed command hooks before they run.

When refreshing the whole `my-codex` marketplace, use the repository-level helper from the checkout root:

```bash
python3 scripts/refresh_my_codex.py
```

Windows PowerShell:

```powershell
py scripts\refresh_my_codex.py
```

That helper uses the Git marketplace source only when the checkout is aligned and clean, otherwise falls back to the local checkout, reruns `codex plugin add` for every plugin selected by `.agents/plugins/install-manifest.json`, and then reruns this hook installer. This is required after hook schema changes because plugin marketplace refreshes do not rewrite `$CODEX_HOME/hooks.json`.

After refresh, run the repository-level closure check from the checkout root:

```bash
python3 scripts/check_my_codex.py
```

Windows PowerShell:

```powershell
py scripts\check_my_codex.py
```

Uninstall only Skill Watcher handlers:

```bash
"$MY_CODEX_PYTHON" scripts/uninstall_codex_hook.py --dry-run
"$MY_CODEX_PYTHON" scripts/uninstall_codex_hook.py --apply
```

## Runtime Reports

Generate report-only summaries:

```bash
"$MY_CODEX_PYTHON" scripts/generate_report.py --since 1d
"$MY_CODEX_PYTHON" scripts/generate_report.py --incremental --since 7d
"$MY_CODEX_PYTHON" scripts/generate_report.py --skill skill-maintainer --since 1d
```

The Codex automation named `Skill Watcher Weekly Report` runs this incremental report workflow weekly on Sunday at 20:00 Asia/Shanghai and returns the report path plus summary counts. It does not generate proposals or modify skills.
Incremental runs store their successful watermark in `$CODEX_HOME/skill-watcher/report-state.json`; the `--since 7d` window is only the first-run fallback. A small overlap with recent event hashes prevents late-arriving events from being dropped at the report boundary.

## Weekly Report Workflow Contract

- Trigger: the `Skill Watcher Weekly Report` Codex automation, or an explicit user request to run the same report workflow.
- Working directory: `plugins/skill-watcher`.
- Command: `"$MY_CODEX_PYTHON" scripts/generate_report.py --incremental --since 7d`, with optional `--skill <skill-name>` when the user narrows scope.
- Outputs: report path, event count, and outcome counts from the command output.
- Report location: `$CODEX_HOME/skill-watcher/reports/`.
- Incremental state location: `$CODEX_HOME/skill-watcher/report-state.json`.
- Memory location: `$CODEX_HOME/automations/skill-watcher-weekly-report/memory.md` when the scheduled automation needs run memory.
- Allowed actions: generate the report, summarize the requested counts, update the Skill Watcher report watermark after successful report writes, and update the automation memory file when running inside that automation workflow.
- Forbidden actions: do not generate proposals, update proposal status, modify any `SKILL.md`, or mutate skill source unless the user explicitly expands the scope.
- Validation: use the command output as the evidence source; do not assume success without a printed report path and counts.

## Hook Privacy and Attribution

The Codex hook adapter stores summaries, lengths, hashes, tool names, outcomes, and redacted metadata. It does not store full prompts, full assistant messages, full shell commands, or full tool responses.

Codex hook payloads do not provide a stable native skill identifier. Skill Watcher now monitors an allowlist of high-value skills and records only explainable attribution:

- `provided`: hook payload explicitly supplied a monitored `skill_name`
- `prompt_mention`: the user prompt explicitly mentioned a monitored skill name or alias
- `assistant_announcement`: the assistant message explicitly mentioned a monitored skill name or alias
- `unknown`: no reliable monitored-skill signal

On `SessionStart`, Skill Watcher scans the current `my-codex` marketplace source for `plugins/*/skills/*/SKILL.md`, derives monitored names as `<plugin-name>:<skill-name>`, and writes the current allowlist to `$CODEX_HOME/skill-watcher/monitored-skills.json`. Subsequent hook events read that file before falling back to the built-in bootstrap list, so adding or renaming packaged skills does not require editing the adapter's static allowlist.

Override the allowlist with a comma-, semicolon-, or newline-separated `SKILL_WATCHER_MONITORED_SKILLS` environment variable.

For monitored prompts, Skill Watcher records a redacted `user_skill_context` summary, length, and hash. This captures the extra information the user mentioned while invoking the skill as potential future improvement evidence, without storing the raw prompt.

Noise filtering:

- `SessionStart` refreshes `$CODEX_HOME/skill-watcher/monitored-skills.json` and is not persisted by default.
- `UserPromptSubmit` is persisted only when it identifies a monitored skill.
- `PostToolUse` updates per-turn tool counts for the active monitored skill, but successful tool calls are not persisted by default.
- failed `PostToolUse` events are persisted for the active monitored skill.
- `Stop` writes one `turn_summary` event for the active monitored skill, then clears transient turn state.
- set `SKILL_WATCHER_DEBUG_ALL_EVENTS=1` to persist all normalized events for hook debugging.

## Proposal Status

Generated proposal files include YAML frontmatter with `status: "draft"`. Update status explicitly:

```bash
"$MY_CODEX_PYTHON" scripts/update_proposal_status.py --proposal "$CODEX_HOME/skill-watcher/proposals/<proposal>.md" --status needs-validation
"$MY_CODEX_PYTHON" scripts/update_proposal_status.py --proposal "$CODEX_HOME/skill-watcher/proposals/<proposal>.md" --status rejected --reason "insufficient evidence"
```

Rejected proposals write a small buffer record under `$CODEX_HOME/skill-watcher/rejected/`.

## Diagnostics

```bash
"$MY_CODEX_PYTHON" scripts/doctor.py
"$MY_CODEX_PYTHON" -m py_compile scripts/*.py
"$MY_CODEX_PYTHON" -m unittest discover -s tests
```
