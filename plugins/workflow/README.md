# Workflow

Reusable Codex workflow skills maintained from the my-codex repository.

## Skills

- `long-running-goal`: continuation-ready staged goal plans with milestones, validation gates, checkpoint evidence, a reusable Continuation contract, frozen YOLO non-stops, runtime hard stops, and close hygiene.
- `orchestrate-subagents`: explicit Codex subagent orchestration for complex tasks that need bounded delegation, evidence consolidation, failure handling, and parent-owned integration.
- `prompt-strategy-loop`: evidence-backed prompt and agent-strategy iteration with independent subagent evaluation and bounded writeback.
- `sop`: standard operating procedures for repeatable manual, agent-executed, or automated workflows with explicit trigger, inputs, execution harness, permissions, ordered steps, outputs, validation evidence, allowed/forbidden actions, stop conditions, escalation, failure handling, and durable writeback.
- `summary-in-html`: standalone HTML developer summaries for a project, directory, module, feature area, documentation chapter, or user-specified scope, with optional image assets when explicitly requested.

## Shared Vocabulary

- `Continuation contract`: the durable goal file contract that lets the same or another agent continue without chat history.
- `Workflow component`: an internal reusable step used by a skill, such as `long-running-goal` planning preflight or checkpoint evidence, without becoming a standalone user-invoked skill.
- `YOLO non-stops`: planned non-destructive local operations inside a `Ready` long-running goal, such as rebuild, refresh, reinstall, tests, lint, formatting, docs sync, code edits, source skill edits, plugin/cache refresh, and generated-artifact cleanup.
- `Runtime hard stops`: the only post-`Ready` long-running-goal conditions that should pause for the user, such as repeated technical impossibility, missing unavailable credentials or source facts, destructive/irreversible/privacy-sensitive/unapproved external writes, frozen semantic conflict, or required verifier/subagent/connector failure with no in-plan local next step.
