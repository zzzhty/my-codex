# Orchestration

Orchestration is a thin Codex plugin for explicit subagent delegation workflows.
It packages reusable skills that help a parent agent split complex work into
bounded subagent assignments, wait for results, and consolidate evidence,
blockers, risks, validation gaps, and next actions.

Current MVP scope:

- plugin manifest and marketplace integration
- `$orchestrate-subagents` skill in the next milestone
- explicit subagent orchestration only

Out of scope:

- control-plane runtime
- worker registry or durable assignment state
- Codex hooks
- MCP server
- automatic edits to `$CODEX_HOME/config.toml`
- default writes to `$CODEX_HOME/agents/`

## Plugin Layout

```text
.codex-plugin/plugin.json
skills/orchestrate-subagents/SKILL.md
skills/orchestrate-subagents/agents/openai.yaml
skills/orchestrate-subagents/references/subagent-recipes.md
```

The skill files are added in M2 of the active long-running goal. Until then,
this plugin skeleton is installable metadata only and does not claim runtime
skill behavior.

## Install

Install from the local `my-codex` marketplace after adding this checkout as a
marketplace source:

```bash
codex plugin add orchestration@my-codex
```

## Validation

```bash
python3 -m json.tool plugins/orchestration/.codex-plugin/plugin.json >/dev/null
python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo --plugin orchestration
```

Full plugin validation is expected after M2 adds the `orchestrate-subagents`
skill.
