# Demo Goal

Overall status: Ready

Planning preflight marker: preflight:demo:20260710-ready

Planning preflight status: Done

Preflight source: grill-with-docs

## M0 milestone

Baseline recorded.

## Milestone status table

| Milestone | Status | Review | Checkpoint |
|---|---|---|---|
| M0 | Ready | Pending | Pending |
| Close | Not Started | Pending | Pending |

## Review gate

Review gate accepted.

## Checkpoint evidence

Checkpoint component: `components/checkpoint.md`

## Planning preflight

Planning preflight component: `components/planning-preflight.md`

## Loop Blueprint / Harness

Execution mode: Manual staged execution

Not applicable: manual staged execution because this demo has no recurring trigger,
connector, subagent orchestration, worktree parallelism, or external side effect.

## Rollback path

Rollback restores the prior revision.

## Close and archive procedure

Close after validation and archive the plan.

## Validation evidence

Tests passed.

## Failure handling

Report the failed command and breakpoint.

## Continuation contract

Continue from the first incomplete milestone.

## Pre-Approval / YOLO

Pre-approved YOLO local operations:

- Planned non-destructive local code and documentation edits, tests, and validation.

Pre-approved external reads/writes:

- Not applicable: this demo does not access external systems.

Runtime hard stops:

- Stop only when repeated local diagnostics cannot make progress, required inputs are
  unavailable, or the next action is unapproved and destructive or externally visible.

Non-stops:

- Continue through milestone boundaries, checkpoints, rebuilds, and recoverable validation.

## Runtime Hard Stops

Stop on permissions or destructive scope changes.

## Non-Stops

Continue through ordinary local validation.

## Reusable Prompt

Resume this demo goal.

## Documented placeholder example

```text placeholder-example
Template syntax uses <goal-path> here.
```
