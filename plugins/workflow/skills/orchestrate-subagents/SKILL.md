---
name: orchestrate-subagents
description: Use only when the user invokes `$orchestrate-subagents` or explicitly asks Codex to use subagents or parallel agents for a complex task, including PR review, architecture review, debugging, failure triage, migration, refactor planning, impact analysis, test discovery, API/schema inspection, documentation alignment, and multi-file implementation planning.
---

# Orchestrate Subagents

Use this skill only when the user invokes `$orchestrate-subagents` or explicitly asks to use subagents. Do not use it to justify implicit delegation; otherwise follow the active environment's normal subagent policy.

## Core Contract

1. Spawn only when the task is genuinely parallelizable and materially useful.
2. Keep the parent agent responsible for planning, final decisions, integration, verification, and user-facing conclusions.
3. Give each subagent one task: one primary verb, one bounded scope, one expected output. Split mapping, review, implementation, validation, and docs checks when they are separate jobs.
4. Give every subagent explicit task-local instructions, ownership, expected output, stop condition, and file/write boundaries. Do not rely on inherited context or unstated requirements.
5. Use `worker` only for implementation with disjoint write ownership and clear authorization to edit; otherwise prefer read-only `explorer` or `default`.
6. Continue only non-overlapping parent work while subagents run.
7. Wait for selected subagents, or record exactly which one did not return and why.
8. Treat timeout, missing tools, incomplete findings, conflicting results, unsafe file overlap, and missing validation evidence as first-class failures.
9. Consolidate evidence before acting; subagent output does not replace parent review.

## Roles And Recipes

- `explorer`: read-only mapping, impact analysis, test discovery, schema inspection, evidence collection.
- `worker`: implementation slices with disjoint write scope and explicit edit authorization.
- `default`: review, triage, planning, validation, and evaluator work when no narrower role fits.

When using multiple subagents with the same role, add assignment labels such as `default as test-verifier` or `worker as api-adapter`. Do not request custom-agent names in recipes; encode behavior in the prompt, label, ownership block, expected output, and stop condition.

Read `references/subagent-recipes.md` for PR/branch review, debugging, implementation planning, bounded parallel implementation, API/schema inspection, and documentation alignment patterns.

## Parent Workflow

1. Restate task, success criteria, and non-goals briefly.
2. Identify parallel slices and shared files/artifacts that remain parent-owned.
3. Choose the minimum useful subagents. Do not delegate tiny tasks or tightly coupled sequential debugging.
4. Spawn each subagent with the prompt template below.
5. Qualify incomplete coverage: missing paths, commands, evidence, blockers, or stop-condition status means partial coverage.
6. Consolidate coverage, blocking issues, non-blocking risks, validation gaps, evidence, unresolved blockers, and next action.

## Subagent Prompt Template

```text
Task:
<specific assignment, not the whole parent task>

Assignment label:
<role plus purpose, such as default as test-verifier>

Single task:
<one primary verb, one bounded scope, one expected output>

Context:
<files, commands, branch/base, goal path, constraints, relevant facts>

Ownership:
<read-only scope or exact disjoint write scope>

Expected output:
- findings or implementation summary
- paths inspected or changed
- commands run and results
- evidence for each claim
- blockers and unknowns
- stop-condition status

Stop condition:
<when to stop, including max scope or exact completion signal>

Boundaries:
- Do not work outside <scope>.
- Do not revert edits made by others.
- Do not fabricate success if tools or evidence are missing.
```

For workers, also state that they are not alone in the codebase and must accommodate concurrent or parent edits.

## Consolidation And Failure

Parent summary fields:

1. Subagent coverage: role, assignment, status, paths, commands.
2. Blocking issues.
3. Non-blocking risks.
4. Missing tests or validation gaps.
5. Evidence: command output, files, diffs, screenshots, reports, logs.
6. Unresolved blockers and partial coverage.
7. Recommended next action.

If implementation happened, include changed files, behavior impact, validation results, rollback path, and remaining risk.

Stop or report partial coverage when tools are unavailable, policy blocks spawning, a subagent fails or cannot access required context, claims lack evidence, results conflict and cannot be reconciled, write scopes overlap, or required validation evidence is missing. The parent may run minimal diagnostics, but the original subagent failure must remain visible.
