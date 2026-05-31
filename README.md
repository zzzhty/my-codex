# Codex Marketplace

Local Codex plugin marketplace for personal development plugins.

This repository is the development mainline for the plugins listed below. Edit the plugin copies under `plugins/`, then reinstall or refresh the Codex plugin cache when a change should be available to new Codex sessions.

## Plugins

- `skill-watcher`: observes Codex skill usage and produces report/proposal artifacts.
- `doc-watcher`: audits configured local repositories for documentation semantic drift.

## Local Install

```bash
codex plugin marketplace add /Users/max/Projects/codex-marketplace
codex plugin add skill-watcher@codex-marketplace
codex plugin add doc-watcher@codex-marketplace
```

## Validation

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
cd plugins/skill-watcher && .venv/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py "$PWD"
cd plugins/doc-watcher/backend && uv run python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/codex-marketplace/plugins/doc-watcher
```

## Layout

```text
.agents/plugins/marketplace.json
plugins/
  skill-watcher/
  doc-watcher/
```
