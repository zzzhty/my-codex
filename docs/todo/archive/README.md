# Closed TODO Plans

Archive is a compact history index only. Current unresolved plans and design
notes belong in [../README.md](../README.md), not here.

## Closed Work

- Subagent model routing: added read-only custom agents (`code_mapper`, `reviewer`, `docs_researcher`), managed `$CODEX_HOME/agents/` sync, refresh/check integration, custom-agent-first orchestration fallbacks, and runtime selector validation through `agent_type` plus `agent_role` metadata. Future write-capable agents, advisor skills, and project-scoped `.codex/agents/` dogfood require separate active plans.
- Workflow plugin refactor: renamed `personal-skills` to `workflow`, added `workflow:sop`, moved default install/check selection into `.agents/plugins/install-manifest.json`, refreshed `workflow@my-codex`, and removed the old `personal-skills@my-codex` install/cache surface.
