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

Global instructions are linked with:

```bash
ln -sfn "$MY_CODEX_ROOT/AGENTS.md" "$CODEX_HOME/AGENTS.md"
```

## Tooling Runtime

Shared my-codex Python tooling uses a runtime venv outside plugin source trees:

```bash
python3 scripts/bootstrap_tooling_env.py
```

The shared interpreter is:

```text
$MY_CODEX_PYTHON
```

Use this interpreter for Codex hooks, Skill Watcher maintenance scripts, and skill/plugin validation that needs my-codex tooling dependencies.

## Validation

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/skill-watcher"
(cd plugins/doc-watcher/backend && uv run python "$PLUGIN_VALIDATOR" ..)
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/personal-skills"
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/mattpocock-skills"
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
