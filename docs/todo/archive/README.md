# Closed TODO Plans

Archive files are closed historical records. Current unresolved plans and design
notes belong in [../README.md](../README.md), not in this directory.

## Closed Long-Running Goals

- [Subagent Runtime Selection Validation](subagent-runtime-selection-validation.md): closed after verifying current-session custom-agent selection through `multi_agent_v1.spawn_agent.agent_type` plus local session metadata `agent_role`, documenting CLI and child-session self-identity limits, and syncing orchestration guidance.
- [Subagent Model Routing V1](subagent-model-routing-v1.md): closed after adding M1 read-only custom agents, managed `$CODEX_HOME/agents/` sync, refresh/check integration, custom-agent-first orchestration fallbacks, and runtime validation evidence.
- [Refactor `personal-skills` into `workflow`](refactor-personal-skills.md): closed after renaming the plugin, adding `workflow:sop`, moving default plugin install/check selection into `.agents/plugins/install-manifest.json`, refreshing `workflow@my-codex`, and removing the old `personal-skills@my-codex` install/cache surface.

## Historical Design Notes

- [Subagent model routing notes](subagent-model-routing-notes.md): background design note for the closed v1 plan, including external reference analysis and earlier custom-agent options.
