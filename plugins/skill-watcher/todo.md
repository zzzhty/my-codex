# Skill Watcher Open Items

This document tracks what is still unclosed after the MVP and V1 implementation.

## Closed

- MVP plugin scaffold and local JSONL workflow are implemented.
- V1 source implementation has been migrated into `my-codex/plugins/skill-watcher`.
- User-level Codex hook path is confirmed as `$CODEX_HOME/hooks.json`.
- Skill Watcher hook handlers are installed by default for `UserPromptSubmit`, `PostToolUse`, and `Stop`; `SessionStart` remains available for debugging but is not part of the default noise-reduced install.
- Daily report automation is configured as `Skill Watcher Daily Report`.
- Plugin validation, unit tests, py_compile, doctor, local adapter smoke test, report generation, proposal generation, and candidate validation pass.
- Installed command hooks were trusted and captured real Codex events.
- Real hook payloads were observed for `SessionStart`, `UserPromptSubmit`, `PostToolUse`, and `Stop`.
- Noise-reduced monitored-skill attribution is implemented with default coverage for the skills packaged by the `my-codex` marketplace.
- The first scheduled `Skill Watcher Daily Report` wrote a report and did not generate proposals.

## Still Open

### V1 Operational Closure

- Decide retention rules for `$CODEX_HOME/skill-watcher/`, especially `logs/`, `snapshots/`, `reports/`, `proposals/`, `rejected/`, `backups/`, and transient `turns/`.

### V2 Build Scope

- Add a local service or CLI API for append-event, query-events, summarize, create-proposal, and mark-proposal-status.
- Add SQLite as the primary query store while preserving JSONL import/export.
- Add query indexes for timestamp, agent, workspace, session_id, skill_name, event_type, outcome, and failure_type.
- Add multi-agent adapters or templates for Claude Code and GitHub Copilot.
- Add a review surface for recent failures, reports, proposals, rejected edits, and snapshots.
- Track skill path, content hash, version metadata, snapshot path, proposal status, validation result, and proposal status history.
- Add rollback support that restores an explicit snapshot only after showing the current diff.
- Add PR-ready export with evidence summary, proposed diff, validation output, and rollback notes.

## Decisions Before V2

- Whether the local interface should be CLI-first, daemon-first, or MCP-first.
- Whether the review surface should be terminal-first or browser-based.
- Retention defaults for event logs, reports, snapshots, proposals, rejected proposal records, and hook config backups.
- Whether SQLite should be introduced as a strict replacement for JSONL reads or as a sidecar index with JSONL remaining the append-only source.
- Which non-Codex adapter should be implemented first.
