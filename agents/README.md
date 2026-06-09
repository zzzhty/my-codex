# Codex Agents

This directory is the source of truth for `my-codex` managed custom agents and subagent support notes.

Managed target:

```text
$CODEX_HOME/agents/
```

Use `scripts/sync_codex_agents.py` to copy these files into the target. Do not hand-edit managed target files; edit the source files here and sync again.

The sync script validates `*.toml` custom-agent definitions and copies the other UTF-8 support files in this directory into the target.

The current managed roster includes read-only agents only:

- `code_mapper.toml`
- `reviewer.toml`
- `docs_researcher.toml`

Subagent support notes:

- `agent-operating-model.md`
- `subagent-roster.md`

Deferred write-capable agents such as `impl_worker` and `test_runner` need a separate plan before they are added.
