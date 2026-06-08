# Subagent Roster

This document is the current source of truth for custom subagent names, model policy, fallback behavior, and deferred roles managed by `my-codex`.

## Current Scope

The current roster includes read-only custom agents only:

| Agent | Work mode | Model | Reasoning | Sandbox | Built-in fallback |
|---|---|---|---|---|---|
| `code_mapper` | read-only | `gpt-5.4-mini` | medium | read-only | `explorer as code-mapper` |
| `reviewer` | read-only | `gpt-5.5` | high | read-only | `default as implementation-reviewer` |
| `docs_researcher` | read-only | `gpt-5.4-mini` | medium | read-only | `default as docs-researcher` |

Source TOML lives in [codex-home/agents/](../../codex-home/agents/). Managed copies are synced into `$CODEX_HOME/agents/` by [scripts/sync_codex_agents.py](../../scripts/sync_codex_agents.py).

## Model Policy

The parent agent remains responsible for planning, delegation, write-scope decisions, integration, validation, and final user-facing conclusions.

Use `gpt-5.4-mini` for fast read-heavy mapping and documentation checks. Use `gpt-5.5` for high-judgment review work where correctness, regression, security, compatibility, and missing-test risks matter more than speed.

If a pinned model is unavailable in a runtime account, do not silently edit the TOML or route to a different model. Use the built-in fallback role named in the roster and report partial coverage.

## Safety Policy

Current agents must stay read-only:

- `sandbox_mode = "read-only"` is required.
- Agents must not edit files, run destructive commands, or claim success without paths, commands, and evidence.
- Parent runtime overrides can supersede spawned-session sandbox defaults, so read-only intent must also be repeated in orchestration prompts and verified from runtime metadata when it matters.
- Each spawned agent gets one task only. Mapping, review, docs verification, implementation, and validation stay separate assignments.

## Fallback Policy

Recipes should prefer the matching custom agent when it exists in the current Codex environment, then name the built-in fallback explicitly:

- Prefer `code_mapper`; fallback to `explorer as code-mapper`.
- Prefer `reviewer`; fallback to `default as implementation-reviewer`.
- Prefer `docs_researcher`; fallback to `default as docs-researcher`.

If neither the custom agent nor the fallback role is available, the parent must report partial coverage or stop if that coverage is required for the gate.

Runtime selector coverage has been verified for the current subagent tool surface: parent calls use `agent_type`, and local session metadata records the resulting `agent_role`. Child sessions do not expose a direct `AGENT_TYPE` environment variable, and `codex exec` does not expose a direct custom-agent selector flag. Do not treat assignment labels alone as proof that a custom-agent TOML was loaded; use selector calls and session metadata when exact proof matters.

## Deferred Roles

The following roles are intentionally not part of the current roster:

| Deferred agent | Reason |
|---|---|
| `impl_worker` | Needs disjoint write ownership, rollback policy, conflict handling, and parent integration gates. |
| `test_runner` | Test execution can write caches, snapshots, coverage, temp files, and generated artifacts. |

Write-capable custom agents require a separate plan with explicit ownership, rollback, conflict handling, validation, and final parent integration rules.

## Official Surface

Codex custom agents are standalone TOML files under personal `$CODEX_HOME/agents/` or project `.codex/agents/`. Every custom agent file must define `name`, `description`, and `developer_instructions`; optional settings include `model`, `model_reasoning_effort`, and `sandbox_mode`.

Reference: [Subagents - Codex | OpenAI Developers](https://developers.openai.com/codex/subagents).
