# Demo Child B Goal

Overall status: Draft

Planning preflight marker: preflight:demo-child-b:20260713-b

Planning preflight status: Done

Preflight source: grill-with-docs

Resolved decisions: child-b owns one local demo outcome after child-a with no compatibility migration, external write, release/deploy, destructive, privacy, or cross-child scope.

Open decisions: None.

## M0 milestone

Implement the bounded child-b outcome.

## Milestone status table

| Milestone | Status | Review | Checkpoint |
|---|---|---|---|
| M0 | Not Started | Pending | Pending |
| Close | Not Started | Pending | Pending |

## Review gate

Review gate verifies the bounded child-b behavior.

## Checkpoint evidence

Checkpoint component: `components/checkpoint.md`

## Planning preflight

Planning preflight component: `components/planning-preflight.md`

## Loop Blueprint / Harness

Execution mode: Manual staged execution

Not applicable: manual staged execution because this child has no recurring trigger,
connector, subagent orchestration, worktree parallelism, or external side effect.

## Rollback path

Rollback restores the prior child-b revision.

## Close and archive procedure

Close after validation and preserve a durable archived child goal.

## Validation evidence

Child-b tests prove the bounded outcome.

## Failure handling

Report the failed command and exact child-b breakpoint.

## Continuation contract

Continue from the first incomplete child-b milestone.

## Pre-Approval / YOLO

Pre-approved YOLO local operations:

- Planned non-destructive local child-b edits, tests, and validation.

Pre-approved external reads/writes:

- Not applicable: this child does not access external systems.

Runtime hard stops:

- Stop only when repeated local diagnostics cannot progress, required inputs are unavailable,
  or the next action is unapproved and destructive or externally visible.

Non-stops:

- Continue through milestone boundaries, checkpoints, rebuilds, and recoverable validation.

## Runtime Hard Stops

Stop on permissions or destructive scope changes.

## Non-Stops

Continue through ordinary local validation.

## Reusable Prompt

Resume this bounded child-b goal.
