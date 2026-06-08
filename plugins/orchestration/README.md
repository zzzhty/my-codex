# Orchestration

Orchestration is a thin Codex plugin for explicit subagent delegation workflows.
It packages reusable skills that help a parent agent split complex work into
bounded subagent assignments, wait for results, and consolidate evidence,
blockers, risks, validation gaps, and next actions.

Current MVP scope:

- plugin manifest and marketplace integration
- `$orchestrate-subagents` skill
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

The current runtime surface is the explicit `$orchestrate-subagents` workflow.
It does not provide implicit auto-delegation, hooks, MCP servers, custom-agent
sync, or a control-plane runtime.

When repo-managed custom agents are synced by `my-codex`, the orchestration
recipes prefer read-only `code_mapper`, `reviewer`, and `docs_researcher`
assignments with built-in fallbacks. This plugin still does not own the sync
process or write to `$CODEX_HOME/agents/`.

In the current runtime, exact custom-agent selection is available through the
subagent tool's `agent_type` field and is recorded in local session metadata as
`agent_role`. Prompt assignment labels are useful context, but they are not
proof that a custom-agent TOML was loaded.

## Usage

Invoke the skill explicitly when a task is complex enough to benefit from
bounded subagents:

```text
Use $orchestrate-subagents to review this branch against main.
```

The parent agent remains responsible for planning, spawning selected subagents,
waiting for results, rejecting incomplete reports, and consolidating:

1. subagent coverage
2. blocking issues
3. non-blocking risks
4. missing tests
5. evidence
6. unresolved blockers
7. recommended next action

Subagent failure is reported as a first-class failure. The workflow must not
claim success when a subagent times out, lacks tools, returns incomplete
evidence, or cannot cover its assigned scope.

## Install

Install from the local `my-codex` marketplace after adding this checkout as a
marketplace source:

```bash
codex plugin add orchestration@my-codex
```

## Validation

```bash
python3 -m json.tool plugins/orchestration/.codex-plugin/plugin.json >/dev/null
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/orchestration"
python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo --plugin orchestration
```
