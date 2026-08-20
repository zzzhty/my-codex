# My Codex

Local Codex marketplace for personal development plugins, reusable skills, and global Codex instructions.

This repository is the development mainline for the plugins and personal Codex configuration listed below. Edit the source copies here, then reinstall or refresh the Codex plugin cache when a change should be available to new Codex sessions.

`AGENTS.md` is also maintained here and linked into `$CODEX_HOME/AGENTS.md`.

## Plugins

- `watcher`: observes Codex skill usage, audits documentation drift, and packages `doc-alignment`, `housekeeping`, `skill-maintainer`, and `skill-compressor` workflows.
- `workflow`: packages reusable workflow skills, including continuation-ready long-running goal plans with frozen YOLO non-stops and runtime hard stops, SOP execution harnesses, prompt/strategy loops, explicit subagent orchestration, and standalone summaries.
- `mattpocock-skills`: packages the unchanged published skill tree and native Codex metadata from `mattpocock/skills`.

The old `plugins/doc-watcher` and `plugins/skill-watcher` source trees were removed after the Watcher migration. Git history remains the recovery path for those retired plugin sources.

## Skill Discovery Profiles

`plugins/*/skills/*/SKILL.md` is the canonical callable-skill catalog. The frontmatter `name` is the callable identity even when a physical directory has a different name; marketplace metadata and plugin caches are projections, not catalog authority.

Every refresh and closure check requires one explicit, mutually exclusive discovery profile:

- `universal` exposes repository skill directories as `~/.agents/skills/<callable-name>` symlinks and requires all skills-bearing `my-codex` plugins to be disabled.
- `plugin` installs and enables every skills-bearing package selected by `.agents/plugins/install-manifest.json` and requires the repository-owned universal links to be absent.

Profile transitions preflight the replacement before removing the old active path and roll back when activation or closure fails. The universal projection manages only symlinks proven to target direct skill directories in this checkout, prunes only repository-owned stale links, preserves unrelated user skills, and fails instead of overwriting an unmanaged same-name entry. The unchanged `plugins/mattpocock-skills/skills/` mirror remains source-identical because projection links never rewrite its content.

The optional plugin distribution has no copied build tree or separate skill catalog: each canonical `plugins/<name>` directory is the package input and build artifact. `.agents/plugins/install-manifest.json` schema v2 declares `discoveryProfile: "plugin"`; each source manifest must expose exactly `./skills/`, and its name, version, skill directories, and callable frontmatter identities are checked against the repository catalog before install. Marketplace packages remain `AVAILABLE`, not installed by default. Source-package validation is independent of the active runtime profile:

```bash
PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py}"
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" "$PLUGIN_VALIDATOR" plugins/watcher
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" "$PLUGIN_VALIDATOR" plugins/workflow
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" scripts/update_mattpocock_skills.py --validate-only
```

Installation uses `scripts/refresh_my_codex.py --discovery-profile plugin`; active-state verification uses `scripts/check_my_codex.py --discovery-profile plugin`. Both reject incomplete package selection, and the closure check fails while any repository-owned universal skill link is active. Universal refresh never installs a package and refreshes Watcher hooks directly from the repository with an explicit repo root.

`scripts/sync_agents_skills.py` is the low-level universal projection tool. Use its `--check --prune` mode to inspect an already selected universal profile; use the profile-aware refresh helper for activation so plugins are deactivated in the required order:

```bash
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" scripts/sync_agents_skills.py --check --prune
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" scripts/refresh_my_codex.py --discovery-profile universal
```

## Matt Pocock Upstream Sync

The repo-owned updater for the `mattpocock-skills` package lives outside the Watcher runtime. From the repository root, run:

```bash
python3 scripts/bootstrap_tooling_env.py
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" scripts/update_mattpocock_skills.py
```

By default it selects the latest upstream semantic-version tag, clones the source under `~/.codex/sources`, and copies every skill published by the upstream manifest without content rewrites or omissions. It then regenerates only the local plugin wrapper and Watcher metadata, updates the cachebuster, and validates byte parity plus upstream's native Codex invocation contract. Use `--source-dir <upstream-checkout> --tag <vX.Y.Z>` to sync from an existing checkout, or `--validate-only` to check the currently packaged plugin without fetching or changing files.

Never edit `plugins/mattpocock-skills/skills/` directly. Its updater-owned upstream lock makes local drift fail validation and blocks an upstream refresh before that drift can be overwritten; local adaptation belongs only in the plugin wrapper, Watcher metadata, and repository-owned tooling around the unchanged mirror.

After reviewing the source diff, refresh only the updated package when needed:

```bash
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" scripts/refresh_my_codex.py --discovery-profile plugin --plugin mattpocock-skills
```

## Orchestration Workflow

Use the `workflow` plugin's `$orchestrate-subagents` skill when the user invokes
it or explicitly asks for bounded Codex subagents or parallel agents. Ordinary
environment-authorized delegation does not invoke this skill by itself:

```text
Use $orchestrate-subagents to review this branch against main.
```

The same workflow can be requested in natural language, such as `Use parallel
subagents to review this branch against main.` The full workflow lives in
`plugins/workflow/skills/orchestrate-subagents/SKILL.md`. Keep root docs
limited to install, validation, and entry-point guidance.

The orchestration workflow uses Codex's built-in subagent roles, such as
`explorer`, `default`, and `worker`, with task-local assignment labels like
`code-mapper` and `test-verifier`. The managed support file lives in
`agents/operating-principles.md`; repo-facing notes live in
`docs/codex-agent-support.md`. Local custom-agent preset TOML is not maintained
in this repository.

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
codex plugin add watcher@my-codex
codex plugin add workflow@my-codex
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
codex plugin add watcher@my-codex
codex plugin add workflow@my-codex
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

Use this interpreter for Codex hooks, Watcher maintenance scripts, and skill/plugin validation that needs my-codex tooling dependencies.

## Windows/Unix Compatibility Notes

This repository is the Windows-oriented checkout of the original Unix-first `zzzhty/my-codex` workflow. The compatibility surface is intentionally narrow: it does not add separate plugins, skills, manifests, or top-level modules for Windows. Windows support lives in install documentation, shared tooling venv path selection, Watcher hook command generation, hook schema alignment, and Windows-aware error messages.

Key path differences:

- Unix venv Python: `$CODEX_HOME/venvs/my-codex/bin/python`
- Windows venv Python: `$env:CODEX_HOME\venvs\my-codex\Scripts\python.exe`
- Unix global instructions: symlink `AGENTS.md` into `$CODEX_HOME/AGENTS.md`
- Windows global instructions: copy `AGENTS.md` into `$env:CODEX_HOME\AGENTS.md`

On Windows, use `Copy-Item` for `AGENTS.md` instead of a symlink. File symlink behavior depends on local policy and privileges, so symlinks can fail even when the repository itself is valid.

`scripts/bootstrap_tooling_env.py` is cross-platform and selects the venv interpreter by platform:

- Windows: `Scripts\python.exe`
- Unix: `bin/python`

The bootstrap resolves the selected base Python to its real executable before creating the venv. This prevents PATH aliases or uv-managed Python symlinks from producing a `pyvenv.cfg` that cannot locate the standard library. If an existing tooling venv cannot start, reports the wrong prefix, or was created from a different base interpreter, bootstrap rebuilds it and restores the previous directory if creation or dependency validation fails. `--dry-run` performs the same read-only health preflight and prints whether a rebuild would occur.

If a Watcher script fails because `PyYAML` is missing, refresh the shared tooling venv from the repository root:

Unix:

```bash
python3 scripts/bootstrap_tooling_env.py
```

Windows PowerShell:

```powershell
py scripts\bootstrap_tooling_env.py
```

## Marketplace And Hook Debugging

Refresh the marketplace plugin cache and Watcher skill hooks with the platform wrapper:

Unix:

```bash
scripts/upgrade_my_codex.sh --discovery-profile universal
# or: scripts/upgrade_my_codex.sh --discovery-profile plugin
```

Windows PowerShell:

```powershell
.\scripts\upgrade_my_codex.ps1 -DiscoveryProfile universal
# or: .\scripts\upgrade_my_codex.ps1 -DiscoveryProfile plugin
```

The wrappers require and propagate the same profile to `scripts/refresh_my_codex.py` and `scripts/check_my_codex.py`, set the shared environment, and sync root `AGENTS.md` into `$CODEX_HOME/AGENTS.md` as the final step. They use the bootstrap Python only to create or refresh the shared tooling venv, then run refresh and check with that tooling Python so the catalog's PyYAML dependency is available. In the `plugin` profile, Codex CLI resolution uses one cross-platform precedence: an explicit `--codex`/`-CodexPath`, then `CODEX_BIN`, then `codex` from `PATH`, then the visible standalone install under `CODEX_INSTALL_DIR` (defaulting to `~/.local/bin` on Unix and `%LOCALAPPDATA%\Programs\OpenAI\Codex\bin` on Windows), then `$CODEX_HOME/packages/standalone/current`, and finally platform-managed fallbacks. On Windows those final fallbacks are the Desktop-managed CLI under `%LOCALAPPDATA%\OpenAI\Codex\bin` followed by VS Code or VS Code Insiders' bundled CLI; on Unix they are VS Code Server, VS Code Server Insiders, local VS Code, and local VS Code Insiders. Explicit paths and `CODEX_BIN` are strict when the CLI is needed. The universal profile does not resolve Codex when no configured skills-bearing plugin needs inspection or removal. Plugin activation requires `codex plugin marketplace add`, `codex plugin add`, and `codex plugin list`; a universal transition from active plugins and pruning also require `codex plugin remove`, while rollback requires `codex plugin add`.

`scripts/refresh_my_codex.py` runs the shared tooling bootstrap and applies the selected discovery profile. The `plugin` profile refreshes the marketplace source and exact manifest-selected packages; the `universal` profile never reads marketplace metadata or plugin cache and manages the repository-owned projection links. Both profiles then sync the subagent support file into `$CODEX_HOME/agents/`, refresh `$CODEX_HOME/hooks.json`, and run Watcher skill doctor. Use `--dry-run` to print commands without changing local state. `--skip-marketplace`, `--skip-plugins`, and `--skip-agents-skills` are rejected because they can weaken profile closure; `--skip-agents` remains available for the unrelated support-file sync.

Stale plugin pruning is off by default and valid only with the `plugin` profile. Pass `--prune-plugins` to `scripts/upgrade_my_codex.sh` or `-PrunePlugins` to `.\scripts\upgrade_my_codex.ps1` when you want the wrapper to ask for confirmation before removing installed or cached `my-codex` plugins that are no longer selected by `.agents/plugins/install-manifest.json`.

Plugin-profile install selection lives in the explicitly tagged `.agents/plugins/install-manifest.json` and must cover every package that owns canonical skills. Repeated `--plugin` arguments may refresh a narrower package set only when the complete plugin profile is already active; closure checks always validate the full selected profile.

Migrate legacy Watcher runtime roots explicitly before final checks:

```bash
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" plugins/watcher/scripts/watcher migrate-state --dry-run
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" plugins/watcher/scripts/watcher migrate-state --apply
```

This moves `$CODEX_HOME/skill-watcher/` to `$CODEX_HOME/watcher/skill/` and `$CODEX_HOME/doc-watcher/` to `$CODEX_HOME/watcher/doc/`. It refuses to merge when a target directory already exists.

Direct helper usage remains supported after `scripts/bootstrap_tooling_env.py` has created the shared tooling venv:

```bash
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" scripts/refresh_my_codex.py --discovery-profile universal
# or: "${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" scripts/refresh_my_codex.py --discovery-profile plugin
```

Windows PowerShell:

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$ToolingPython = Join-Path $CodexHome "venvs\my-codex\Scripts\python.exe"
& $ToolingPython scripts\refresh_my_codex.py --discovery-profile universal
# or: & $ToolingPython scripts\refresh_my_codex.py --discovery-profile plugin
```

Run the final closure check after refresh:

Unix:

```bash
"${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" scripts/check_my_codex.py --discovery-profile universal
# or: "${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python" scripts/check_my_codex.py --discovery-profile plugin
```

Windows PowerShell:

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$ToolingPython = Join-Path $CodexHome "venvs\my-codex\Scripts\python.exe"
& $ToolingPython scripts\check_my_codex.py --discovery-profile universal
# or: & $ToolingPython scripts\check_my_codex.py --discovery-profile plugin
```

The check script verifies the shared tooling Python, selected discovery closure, Watcher skill hook schema, subagent support-file sync state, source plugin validation, and Watcher skill doctor. Universal closure verifies every frontmatter-derived link and the absence of enabled skills-bearing plugins without reading marketplace or cache state. Plugin closure verifies the exact marketplace/source package set, manifest `./skills/` projection, source package tree and identities, enabled CLI status and source version, exactly one cache version per package, cached callable identities, and the absence of universal links. The script is read-only for plugin installs, hooks, and support files. Use `--skip-agents` to skip the unrelated support-file sync check.

After the helper refreshes hooks, open `/hooks` in Codex and trust the refreshed Watcher skill command hook definitions. Codex skips non-managed command hooks until the exact hook definition is trusted.

The platform wrappers sync global instructions after validation. Windows compares SHA256 hashes and copies `AGENTS.md` after confirmation when `$CODEX_HOME\AGENTS.md` differs or is missing. Unix checks whether `$CODEX_HOME/AGENTS.md` is already a symlink to this checkout's `AGENTS.md`; if it points elsewhere or is missing, it asks before replacing it with `ln -sfn`.

Manual Windows PowerShell marketplace reinstall checklist:

```powershell
$env:MY_CODEX_ROOT = (Get-Location).Path
$env:CODEX_HOME = "$env:USERPROFILE\.codex"
$env:MY_CODEX_PYTHON = "$env:CODEX_HOME\venvs\my-codex\Scripts\python.exe"
$env:PLUGIN_VALIDATOR = "$env:CODEX_HOME\skills\.system\plugin-creator\scripts\validate_plugin.py"

py scripts\bootstrap_tooling_env.py
codex plugin marketplace add $env:MY_CODEX_ROOT
codex plugin add watcher@my-codex
codex plugin add workflow@my-codex
codex plugin add mattpocock-skills@my-codex
```

Watcher installs user-level Codex command hooks in `$CODEX_HOME/hooks.json`. It does not use plugin manifest hooks and does not modify `.codex-plugin/plugin.json`.

The generated hook handlers observe:

- `SessionStart`
- `UserPromptSubmit`
- `PostToolUse`
- `Stop`

`SessionStart` refreshes `$CODEX_HOME/watcher/skill/skill-metadata-cache.json` and is not persisted by default. The callable inventory comes only from the repository catalog under the explicit `--repo-root`; marketplace metadata, plugin manifests, plugin cache, and the runtime cache are not callable authorities. Repository `.codex-plugin/skill-watcher.json` files are non-callable attribution overlays for namespaced identities, roles, aliases, supporting relationships, logical groups, and legacy mappings. Missing repository source, catalog failures, unknown overlay schemas, and invalid references fail visibly.

Expected command-hook schema:

```json
{
  "type": "command",
  "async": false,
  "command": "... watcher skill observe --repo-root <my-codex-root>",
  "timeoutSec": 10,
  "statusMessage": "Watcher skill: observe <event>"
}
```

Windows hook commands are rendered with Windows command-line quoting and should point at `Scripts\python.exe`. Unix hook commands use POSIX quoting and should point at `bin/python`.

Install or refresh Watcher skill hooks from the source checkout:

Unix:

```bash
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/watcher/scripts/watcher" skill install-hook --repo-root "$MY_CODEX_ROOT" --dry-run
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/plugins/watcher/scripts/watcher" skill install-hook --repo-root "$MY_CODEX_ROOT" --apply
```

Windows PowerShell:

```powershell
$python = "$env:USERPROFILE\.codex\venvs\my-codex\Scripts\python.exe"
& $python "$env:MY_CODEX_ROOT\plugins\watcher\scripts\watcher" skill install-hook --repo-root $env:MY_CODEX_ROOT --dry-run --python $python
& $python "$env:MY_CODEX_ROOT\plugins\watcher\scripts\watcher" skill install-hook --repo-root $env:MY_CODEX_ROOT --apply --python $python
```

After applying hooks, open `/hooks` in Codex and trust the Watcher skill command hook definitions. Codex skips non-managed command hooks until the exact hook definition is trusted.

Runtime Watcher skill state is written under `$CODEX_HOME/watcher/skill/`:

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

Watcher monitors the canonical repository skill set by default and can be narrowed with `WATCHER_SKILL_MONITORED_SKILLS`. Installed hooks embed the explicit repository root, so repository and universal-symlink execution share the same source runtime and do not depend on plugin cache or working-directory inference. Because Codex hook payloads do not provide a stable native skill id, attribution is recorded as `provided`, `prompt_mention`, `assistant_announcement`, or `unknown`. Successful tool calls are counted in transient turn state but are not persisted as individual records; failed tool calls and one `turn_summary` are persisted for active monitored skills.

When the user explicitly invokes a monitored skill, the adapter stores a redacted `user_skill_context` summary/hash for the extra information mentioned with that skill. This is intended as future skill-improvement evidence without retaining the raw prompt.

## Validation

Unix:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .agents/plugins/install-manifest.json >/dev/null
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/watcher"
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/workflow"
"$MY_CODEX_PYTHON" "$MY_CODEX_ROOT/scripts/update_mattpocock_skills.py" --validate-only
"$MY_CODEX_PYTHON" -m unittest discover -s tests -p 'test_*.py' -v
```

Windows PowerShell:

```powershell
& $env:MY_CODEX_PYTHON -m json.tool .agents\plugins\marketplace.json | Out-Null
& $env:MY_CODEX_PYTHON -m json.tool .agents\plugins\install-manifest.json | Out-Null
& $env:MY_CODEX_PYTHON $env:PLUGIN_VALIDATOR "$env:MY_CODEX_ROOT\plugins\watcher"
& $env:MY_CODEX_PYTHON $env:PLUGIN_VALIDATOR "$env:MY_CODEX_ROOT\plugins\workflow"
& $env:MY_CODEX_PYTHON "$env:MY_CODEX_ROOT\scripts\update_mattpocock_skills.py" --validate-only
& $env:MY_CODEX_PYTHON -m unittest discover -s tests -p 'test_*.py' -v
```

## Layout

```text
.agents/plugins/marketplace.json
.agents/plugins/install-manifest.json
plugins/
  watcher/
  workflow/
  mattpocock-skills/
requirements.txt
scripts/bootstrap_tooling_env.py
scripts/check_my_codex.py
scripts/refresh_my_codex.py
scripts/sync_agents_skills.py
scripts/sync_codex_agents.py
scripts/update_mattpocock_skills.py
scripts/upgrade_my_codex.ps1
scripts/upgrade_my_codex.sh
tests/
agents/
```
