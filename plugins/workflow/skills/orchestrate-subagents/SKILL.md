---
name: orchestrate-subagents
description: Use when the user explicitly asks for `$orchestrate-subagents`, subagents, parallel agents, or multi-agent delegation; tool availability and task parallelism alone are not triggers.
---

# Orchestrate Subagents

Use this skill only after the user-requested trigger. Delegation and mutation authority come from root instructions or an approved plan; this skill does not expand them.

## Contract

1. Spawn the minimum useful set only when independent work can proceed in parallel.
2. Keep the parent agent responsible for planning, final decisions, integration, cross-slice validation, and the user-facing conclusion.
3. Give each subagent one primary verb, one bounded scope, one expected output, one ownership block, and one stop condition.
4. Use `explorer` or `default` for read-only work. Use `worker` only when implementation is authorized and write ownership is exact and disjoint.
5. Keep shared files, generated artifacts, conflicts and final integration parent-owned. Continue only non-overlapping parent work while subagents run.
6. Wait for the selected agents. Preserve policy-blocked spawning, timeout, missing tools or required context, unsafe overlap, conflicting, incomplete, or missing-evidence results as `partial` or `blocked`; do not silently replace them with assumptions.
7. Treat subagent output as evidence for parent review, not as the final decision or validation result.

## Workflow

1. Freeze the parent task, success criteria, non-goals, shared artifacts, and parent-owned integration.
2. Read `references/subagent-recipes.md`, choose the narrowest recipe, and write complete assignment prompts from its Assignment Contract.
3. Spawn only materially useful assignments with non-overlapping ownership.
4. Wait for selected results and record each assignment's status, evidence, blockers, unknowns, and stop-condition outcome.
5. Consolidate findings into decisions, risks, validation gaps, conflicts, residual unknowns, and the next parent-owned action.

## Completion

Report assignment labels and statuses, paths inspected or changed, commands and results, evidence-backed findings, blockers, unknowns, partial coverage, and parent validation. For implementation, also report behavior impact, rollback, and residual risk.

Completion requires that every selected assignment is accounted for, write scopes remained disjoint, failures stayed visible, and the parent independently reviewed and integrated the result.
