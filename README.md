# My Codex

Local Codex marketplace for personal development plugins, reusable skills, and global Codex instructions.

This repository is the development mainline for the plugins and personal Codex configuration listed below. Edit the source copies here, then reinstall or refresh the Codex plugin cache when a change should be available to new Codex sessions.

`AGENTS.md` is also maintained here and linked into `$CODEX_HOME/AGENTS.md`.

## Plugins

- `skill-watcher`: observes Codex skill usage and produces report/proposal artifacts.
- `doc-watcher`: audits configured local repositories for documentation semantic drift.
- `personal-skills`: packages original personal skills maintained in this repository.
- `mattpocock-skills`: packages the local Codex-adapted copy of `mattpocock/skills`.

## Local Install

Unix:

```bash
export MY_CODEX_ROOT="${MY_CODEX_ROOT:-$PWD}"
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export MY_CODEX_PYTHON="${MY_CODEX_PYTHON:-$CODEX_HOME/venvs/my-codex/bin/python}"
export PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py}"

codex plugin marketplace add "$MY_CODEX_ROOT"
codex plugin add skill-watcher@my-codex
codex plugin add doc-watcher@my-codex
codex plugin add personal-skills@my-codex
codex plugin add mattpocock-skills@my-codex
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
codex plugin add personal-skills@my-codex
codex plugin add mattpocock-skills@my-codex
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

Use the current checkout directly as the marketplace source. Do not clone or copy this repository to a second path just to install the local marketplace; doing that makes cache and source-path debugging harder.

Windows PowerShell marketplace reinstall checklist:

```powershell
$env:MY_CODEX_ROOT = (Get-Location).Path
$env:CODEX_HOME = "$env:USERPROFILE\.codex"
$env:MY_CODEX_PYTHON = "$env:CODEX_HOME\venvs\my-codex\Scripts\python.exe"
$env:PLUGIN_VALIDATOR = "$env:CODEX_HOME\skills\.system\plugin-creator\scripts\validate_plugin.py"

py scripts\bootstrap_tooling_env.py
codex plugin marketplace add $env:MY_CODEX_ROOT
codex plugin add skill-watcher@my-codex
codex plugin add doc-watcher@my-codex
codex plugin add personal-skills@my-codex
codex plugin add mattpocock-skills@my-codex
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
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/skill-watcher"
(cd plugins/doc-watcher/backend && uv run python "$PLUGIN_VALIDATOR" ..)
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/personal-skills"
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/mattpocock-skills"
```

Windows PowerShell:

```powershell
& $env:MY_CODEX_PYTHON -m json.tool .agents\plugins\marketplace.json | Out-Null
& $env:MY_CODEX_PYTHON $env:PLUGIN_VALIDATOR "$env:MY_CODEX_ROOT\plugins\skill-watcher"
Push-Location plugins\doc-watcher\backend; uv run python $env:PLUGIN_VALIDATOR ..; Pop-Location
& $env:MY_CODEX_PYTHON $env:PLUGIN_VALIDATOR "$env:MY_CODEX_ROOT\plugins\personal-skills"
& $env:MY_CODEX_PYTHON $env:PLUGIN_VALIDATOR "$env:MY_CODEX_ROOT\plugins\mattpocock-skills"
```

## Layout

```text
.agents/plugins/marketplace.json
plugins/
  skill-watcher/
  doc-watcher/
  personal-skills/
  mattpocock-skills/
requirements-tools.txt
scripts/bootstrap_tooling_env.py
```
