# My Codex

Local Codex marketplace for personal development plugins, reusable skills, and global Codex instructions.

This repository is the development mainline for the plugins and personal Codex configuration listed below. Edit the source copies here, then reinstall or refresh the Codex plugin cache when a change should be available to new Codex sessions.

`AGENTS.md` is also maintained here and linked into `~/.codex/AGENTS.md`.

The old standalone project checkouts at `/Users/max/Projects/skill-watcher` and `/Users/max/Projects/doc-watcher` have been retired. The canonical source for both plugins is now under `plugins/` in this repository.

## Plugins

- `skill-watcher`: observes Codex skill usage and produces report/proposal artifacts.
- `doc-watcher`: audits configured local repositories for documentation semantic drift.
- `personal-skills`: packages original personal skills maintained in this repository.
- `mattpocock-skills`: packages the local Codex-adapted copy of `mattpocock/skills`.

## Local Install

```bash
codex plugin marketplace add /Users/max/Projects/my-codex
codex plugin add skill-watcher@my-codex
codex plugin add doc-watcher@my-codex
codex plugin add personal-skills@my-codex
codex plugin add mattpocock-skills@my-codex
```

Global instructions are linked with:

```bash
ln -sfn /Users/max/Projects/my-codex/AGENTS.md /Users/max/.codex/AGENTS.md
```

## Tooling Runtime

Shared my-codex Python tooling uses a runtime venv outside plugin source trees:

```bash
python3 scripts/bootstrap_tooling_env.py
```

The shared interpreter is:

```text
/Users/max/.codex/venvs/my-codex/bin/python
```

Use this interpreter for Codex hooks, Skill Watcher maintenance scripts, and skill/plugin validation that needs my-codex tooling dependencies.

## Validation

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
/Users/max/.codex/venvs/my-codex/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/skill-watcher
cd plugins/doc-watcher/backend && uv run python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/doc-watcher
/Users/max/.codex/venvs/my-codex/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/personal-skills
/Users/max/.codex/venvs/my-codex/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/mattpocock-skills
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
