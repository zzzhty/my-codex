# Codex Agents

This directory is the source of truth for `my-codex` managed custom agents.

Managed target:

```text
$CODEX_HOME/agents/
```

Use `scripts/sync_codex_agents.py` to copy these files into the target. Do not hand-edit managed target files; edit the source TOML here and sync again.

The current managed roster includes read-only agents only:

- `code_mapper.toml`
- `reviewer.toml`
- `docs_researcher.toml`

Deferred write-capable agents such as `impl_worker` and `test_runner` need a separate plan before they are added.
