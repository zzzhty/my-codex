# My Codex

Local Codex marketplace for personal development plugins, reusable skills, and global Codex instructions.

This repository is the development mainline for the plugins and personal Codex configuration listed below. Edit the source copies here, then reinstall or refresh the Codex plugin cache when a change should be available to new Codex sessions.

`AGENTS.md` is also maintained here and linked into `$CODEX_HOME/AGENTS.md`.

## Plugins

- `skill-watcher`: observes Codex skill usage and produces report/proposal artifacts.
- `doc-watcher`: audits configured local repositories for documentation semantic drift.
- `workflow`: packages reusable workflow skills, including long-running goal management.
- `mattpocock-skills`: packages the local Codex-adapted copy of `mattpocock/skills`.
- `orchestration`: packages explicit Codex subagent orchestration workflows.

## Orchestration Workflow

Use the `orchestration` plugin when a task explicitly needs bounded Codex
subagents. Invoke the workflow directly instead of relying on implicit
auto-delegation:

```text
Use $orchestrate-subagents to review this branch against main.
```

The full workflow lives in
`plugins/orchestration/skills/orchestrate-subagents/SKILL.md`. Keep root docs
limited to install, validation, and entry-point guidance.

Custom-agent source TOML lives in `codex-home/agents/` and is synced into
`$CODEX_HOME/agents/` by `scripts/sync_codex_agents.py`. The M1 roster is
read-only only: `code_mapper`, `reviewer`, and `docs_researcher`. Write-capable
custom agents such as `impl_worker` and `test_runner` remain deferred until a
separate plan defines write ownership, rollback, conflict handling, and
validation gates.

Current roster policy lives in `docs/agents/subagent-roster.md`. The current
runtime exposes custom-agent selection through the subagent tool's `agent_type`
field, while `codex exec` does not expose a direct custom-agent selector flag.
The closed v1 plan and validation evidence lives in
`docs/todo/archive/subagent-model-routing-v1.md`; exact selector evidence lives
in `docs/todo/archive/subagent-runtime-selection-validation.md`.

## Local Install

For routine install or refresh, prefer the platform wrapper in
[Marketplace And Hook Debugging](#marketplace-and-hook-debugging). The manual
commands below are a fallback and should mirror
`.agents/plugins/install-manifest.json`.

Unix:

```bash
export MY_CODEX_ROOT="${MY_CODEX_ROOT:-$PWD}"
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export MY_CODEX_PYTHON="${MY_CODEX_PYTHON:-$CODEX_HOME/venvs/my-codex/bin/python}"
export PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py}"

codex plugin marketplace add "$MY_CODEX_ROOT"
codex plugin add skill-watcher@my-codex
codex plugin add doc-watcher@my-codex
codex plugin add workflow@my-codex
codex plugin add mattpocock-skills@my-codex
codex plugin add orchestration@my-codex
```

Windows PowerShell:

```powershell
$env:MY_CODEX_ROOT = (Get-Location).Path
$env:CODEX_HOME = "$env:USERPROFILE\.codex"
$env:MY_CODEX_PYTHON = "$env:CODEX_HOME\venvs\my-codex\Scripts\python.exe"
$env:PLUGIN_VALIDATOR = "$env:CODEX_HOME\skills\.system\plugin-creator\scripts\validate_plugin.py"

Set-Location $env:MY_CODEX_ROOT
codex plugin marketplace add $env:MY_CODEX_ROOT
codex plugin add skill-watcher@my-codex
codex plugin add doc-watcher@my-codex
codex plugin add workflow@my-codex
codex plugin add mattpocock-skills@my-codex
codex plugin add orchestration@my-codex
```

Install directly from this repository checkout. Do not clone or copy the repo to an extra local path just to install the marketplace.

Global instructions are linked or copied from this repository checkout.

Unix:

```bash
ln -sfn "$MY_CODEX_ROOT/AGENTS.md" "$CODEX_HOME/AGENTS.md"
```

Windows PowerShell:

```powershell
Copy-Item -LiteralPath "$env:MY_CODEX_ROOT\AGENTS.md" -Destination "$env:CODEX_HOME\AGENTS.md" -Force
```

On Windows, prefer copying `AGENTS.md` instead of creating a symlink; file symlink behavior depends on local policy and privileges.

## Tooling Runtime

Shared my-codex Python tooling uses a runtime venv outside plugin source trees:

Unix:

```bash
python3 scripts/bootstrap_tooling_env.py
```

Windows PowerShell:

```powershell
py scripts\bootstrap_tooling_env.py
```

The shared interpreter is:

```text
$MY_CODEX_PYTHON
```

Use this interpreter for Codex hooks, Skill Watcher maintenance scripts, and skill/plugin validation that needs my-codex tooling dependencies.

## Windows/Unix Compatibility Notes

This repository is the Windows-oriented checkout of the original Unix-first `zzzhty/my-codex` workflow. The compatibility surface is intentionally narrow: it does not add separate plugins, skills, manifests, or top-level modules for Windows. Windows support lives in install documentation, shared tooling venv path selection, Skill Watcher hook command generation, hook schema alignment, and Windows-aware error messages.

Key path differences:

- Unix venv Python: `$CODEX_HOME/venvs/my-codex/bin/python`
- Windows venv Python: `$env:CODEX_HOME\venvs\my-codex\Scripts\python.exe`
- Unix global instructions: symlink `AGENTS.md` into `$CODEX_HOME/AGENTS.md`
- Windows global instructions: copy `AGENTS.md` into `$env:CODEX_HOME\AGENTS.md`

On Windows, use `Copy-Item` for `AGENTS.md` instead of a symlink. File symlink behavior depends on local policy and privileges, so symlinks can fail even when the repository itself is valid.

`scripts/bootstrap_tooling_env.py` is cross-platform and selects the venv interpreter by platform:

- Windows: `Scripts\python.exe`
- Unix: `bin/python`

If a Skill Watcher script fails because `PyYAML` is missing, refresh the shared tooling venv from the repository root:

Unix:

```bash
python3 scripts/bootstrap_tooling_env.py
```

Windows PowerShell:

```powershell
py scripts\bootstrap_tooling_env.py
```

## Marketplace And Hook Debugging

Refresh the marketplace plugin cache and Skill Watcher hooks with the platform wrapper:

Unix:

```bash
scripts/upgrade_my_codex.sh
```

Windows PowerShell:

```powershell
.\scripts\upgrade_my_codex.ps1
```

The wrappers only resolve platform-specific Python/Codex paths, set the shared environment, call `scripts/refresh_my_codex.py`, run `scripts/check_my_codex.py`, and sync root `AGENTS.md` into `$CODEX_HOME/AGENTS.md` as the final step. The Unix wrapper fails before refresh when the Codex CLI does not expose `codex plugin add` and `codex plugin list`; non-interactive plugin installs require Codex CLI 0.131.0 or newer. The Python helper is the reusable cross-platform marketplace source of truth.

`scripts/refresh_my_codex.py` runs the shared tooling bootstrap, uses the checkout's `remote.origin.url` as the Git marketplace source only when local `HEAD` matches the requested `origin/git-ref` and the worktree is clean, falls back to the current checkout as a local marketplace source when the Git source is stale, dirty, unavailable, or fails, runs `codex plugin add` for every plugin selected by the install manifest, syncs custom agents into `$CODEX_HOME/agents/`, refreshes `$CODEX_HOME/hooks.json`, and runs Skill Watcher doctor. Use `--dry-run` to print commands and the custom-agent sync plan without changing local Codex state. Use `--skip-agents` to skip custom-agent sync.

Default plugin install and final-check selection lives in `.agents/plugins/install-manifest.json`. Edit that manifest to choose which `my-codex` plugins are installed and checked by default; use repeated `--plugin` arguments only for a one-off narrower run.

Direct helper usage remains supported:

```bash
python3 scripts/refresh_my_codex.py
```

Windows PowerShell:

```powershell
py scripts\refresh_my_codex.py
```

Run the final closure check after refresh:

Unix:

```bash
python3 scripts/check_my_codex.py
```

Windows PowerShell:

```powershell
py scripts\check_my_codex.py
```

The check script verifies the local marketplace file, shared tooling Python, `codex plugin list` installation status, plugin cache manifests, Skill Watcher hook schema, custom-agent sync state, plugin validation, and Skill Watcher doctor. It does not modify plugin installs, `$CODEX_HOME/hooks.json`, or `$CODEX_HOME/agents/`. Use `--skip-agents` to skip custom-agent sync checks.

After the helper refreshes hooks, open `/hooks` in Codex and trust the refreshed Skill Watcher command hook definitions. Codex skips non-managed command hooks until the exact hook definition is trusted.

The platform wrappers sync global instructions after validation. Windows compares SHA256 hashes and copies `AGENTS.md` after confirmation when `$CODEX_HOME\AGENTS.md` differs or is missing. Unix checks whether `$CODEX_HOME/AGENTS.md` is already a symlink to this checkout's `AGENTS.md`; if it points elsewhere or is missing, it asks before replacing it with `ln -sfn`.

Manual Windows PowerShell marketplace reinstall checklist:

```powershell
$env:MY_CODEX_ROOT = (Get-Location).Path
$env:CODEX_HOME = "$env:USERPROFILE\.codex"
$env:MY_CODEX_PYTHON = "$env:CODEX_HOME\venvs\my-codex\Scripts\python.exe"
$env:PLUGIN_VALIDATOR = "$env:CODEX_HOME\skills\.system\plugin-creator\scripts\validate_plugin.py"

py scripts\bootstrap_tooling_env.py
codex plugin marketplace add $env:MY_CODEX_ROOT
codex plugin add skill-watcher@my-codex
codex plugin add doc-watcher@my-codex
codex plugin add workflow@my-codex
codex plugin add mattpocock-skills@my-codex
codex plugin add orchestration@my-codex
```

Skill Watcher installs user-level Codex command hooks in `$CODEX_HOME/hooks.json`. It does not use plugin manifest hooks and does not modify `.codex-plugin/plugin.json`.

The generated hook handlers observe:

- `UserPromptSubmit`
- `PostToolUse`
- `Stop`

`SessionStart` is not installed by default because it does not provide useful skill attribution.

Expected command-hook schema:

```json
{
  "type": "command",
  "async": false,
  "command": "...",
  "timeoutSec": 10,
  "statusMessage": "Skill Watcher: observe <event>"
}
```

Windows hook commands are rendered with Windows command-line quoting and should point at `Scripts\python.exe`. Unix hook commands use POSIX quoting and should point at `bin/python`.

Install or refresh Skill Watcher hooks from the source checkout:

Unix:

```bash
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/install_codex_hook.py" --dry-run
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/skill-watcher/scripts/install_codex_hook.py" --apply
```

Windows PowerShell:

```powershell
$python = "$env:USERPROFILE\.codex\venvs\my-codex\Scripts\python.exe"
& $python "$env:MY_CODEX_ROOT\plugins\skill-watcher\scripts\install_codex_hook.py" --dry-run --python $python
& $python "$env:MY_CODEX_ROOT\plugins\skill-watcher\scripts\install_codex_hook.py" --apply --python $python
```

After applying hooks, open `/hooks` in Codex and trust the Skill Watcher command hook definitions. Codex skips non-managed command hooks until the exact hook definition is trusted.

Runtime Skill Watcher state is written under `$CODEX_HOME/skill-watcher/`:

```text
logs/events.jsonl
reports/
proposals/
snapshots/
rejected/
backups/
turns/
```

The hook adapter records summaries, lengths, hashes, tool names, outcomes, and redacted metadata. It does not store full prompts, full assistant messages, full shell commands, full tool responses, file contents, secrets, or private business data.

Skill Watcher monitors the skills packaged by the `my-codex` marketplace by default and can be narrowed with `SKILL_WATCHER_MONITORED_SKILLS`. Because Codex hook payloads do not provide a stable native skill id, attribution is recorded as `provided`, `prompt_mention`, `assistant_announcement`, or `unknown`. Successful tool calls are counted in transient turn state but are not persisted as individual records; failed tool calls and one `turn_summary` are persisted for active monitored skills.

When the user explicitly invokes a monitored skill, the adapter stores a redacted `user_skill_context` summary/hash for the extra information mentioned with that skill. This is intended as future skill-improvement evidence without retaining the raw prompt.

## Validation

Unix:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .agents/plugins/install-manifest.json >/dev/null
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/skill-watcher"
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/doc-watcher"
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/workflow"
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/mattpocock-skills"
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/orchestration"
```

Windows PowerShell:

```powershell
& $env:MY_CODEX_PYTHON -m json.tool .agents\plugins\marketplace.json | Out-Null
& $env:MY_CODEX_PYTHON -m json.tool .agents\plugins\install-manifest.json | Out-Null
& $env:MY_CODEX_PYTHON $env:PLUGIN_VALIDATOR "$env:MY_CODEX_ROOT\plugins\skill-watcher"
& $env:MY_CODEX_PYTHON $env:PLUGIN_VALIDATOR "$env:MY_CODEX_ROOT\plugins\doc-watcher"
& $env:MY_CODEX_PYTHON $env:PLUGIN_VALIDATOR "$env:MY_CODEX_ROOT\plugins\workflow"
& $env:MY_CODEX_PYTHON $env:PLUGIN_VALIDATOR "$env:MY_CODEX_ROOT\plugins\mattpocock-skills"
& $env:MY_CODEX_PYTHON $env:PLUGIN_VALIDATOR "$env:MY_CODEX_ROOT\plugins\orchestration"
```

## Layout

```text
.agents/plugins/marketplace.json
.agents/plugins/install-manifest.json
plugins/
  skill-watcher/
  doc-watcher/
  workflow/
  mattpocock-skills/
  orchestration/
requirements-tools.txt
scripts/bootstrap_tooling_env.py
scripts/check_my_codex.py
scripts/refresh_my_codex.py
scripts/sync_codex_agents.py
scripts/upgrade_my_codex.ps1
scripts/upgrade_my_codex.sh
codex-home/agents/
```
