---
name: orchestrate-subagents
description: Use only when the user invokes `$orchestrate-subagents` or explicitly asks the harness to use subagents, parallel agents, or multi-agent delegation; tool availability, environment authorization, and task parallelizability alone are not triggers.
---

# Orchestrate Subagents

This skill defines the detailed workflow after a user-requested trigger. Tool availability, environment authorization, or task parallelizability alone do not trigger it, and invoking it does not expand the active environment's delegation authority.

## Core Contract

1. Spawn only when the task is genuinely parallelizable and materially useful.
2. Keep the parent agent responsible for planning, final decisions, integration, verification, and user-facing conclusions.
3. Give each subagent one task: one primary verb, one bounded scope, one expected output. Split mapping, review, implementation, validation, and docs checks when they are separate jobs.
4. Give every subagent explicit task-local instructions, ownership, expected output, stop condition, and file/write boundaries. Do not rely on inherited context or unstated requirements.
5. Use `worker` only for implementation with disjoint write ownership and clear authorization to edit; otherwise prefer read-only `explorer` or `default`.
6. Continue only non-overlapping parent work while subagents run.
7. Wait for selected subagents, or record exactly which one did not return and why.
8. Treat policy-blocked spawning, timeout, missing tools, inaccessible required context, incomplete findings, conflicting results, unsafe file overlap, and missing validation evidence as first-class failures.
9. Consolidate evidence before acting; subagent output does not replace parent review.

## Roles And Recipes

- `explorer`: read-only mapping, impact analysis, test discovery, schema inspection, evidence collection.
- `worker`: implementation slices with disjoint write scope and explicit edit authorization.
- `default`: review, triage, planning, validation, and evaluator work when no narrower role fits.

When using multiple subagents with the same role, add assignment labels such as `default as test-verifier` or `worker as api-adapter`. Do not request custom-agent names in recipes; encode behavior in the prompt, label, ownership block, expected output, and stop condition.

Read `references/subagent-recipes.md` for PR/branch review, debugging, implementation planning, bounded parallel implementation, API/schema inspection, and documentation alignment patterns.

## Parent Workflow

1. Restate the task, success criteria, non-goals, shared artifacts, and parent-owned integration.
2. Slice the work and spawn the minimum useful agents with the prompt template; do not delegate tiny tasks or tightly coupled sequential debugging, and continue only non-overlapping parent work.
3. Wait for selected results and mark coverage partial when paths, commands, evidence, blockers, or stop-condition status are missing.
4. Consolidate role/status/path/command evidence into blockers, risks, validation gaps, unknowns, and the next action.

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

For implementation, also report changed files, behavior impact, validation, rollback, and residual risk. Stop or report partial coverage on any Core Contract failure; parent diagnostics may narrow it but must not hide the original failure.
