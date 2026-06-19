# Planning Preflight Component

Use this component before creating or converting a long-running goal, or before first implementation when the goal lacks a completed planning-preflight marker.

Default to `grill-with-docs` before the goal becomes executable. Skip only by explicit user instruction such as `skip grill`, `no grill`, or an equivalent direct instruction.

## Entry Conditions

Apply this component when:

1. A new long-running goal is being created from an idea, TODO, PRD, bug, migration, or broad implementation request.
2. An existing TODO, PRD, issue, or rough plan is being converted into a long-running goal contract.
3. A goal is about to enter implementation but its goal file does not record a completed planning-preflight marker.

Do not rerun it when the goal records a completed preflight marker or explicit user-skip marker. Ordinary runtime evolution updates the active goal and resumes; rerun preflight only when product semantics, scope, owner boundaries, or milestone order changed enough to obsolete the old marker.

## Idempotency Marker

Before asking grill questions, inspect the goal file for a non-placeholder marker:

```text
Planning preflight marker: preflight:<goal_slug>:<yyyymmdd>-<short-id>
Planning preflight status: Done / Skipped by explicit user instruction
```

If marker and status are complete, do not grill again. The marker is the plan contract's idempotency key; regenerate it only after grill completion, explicit user skip, or scope-changing evolution that invalidates the old marker. Record any supersession reason in `Resolved decisions` or `Open decisions`.

## Required Flow

1. Inspect code/docs for answers before asking the user.
2. Run `grill-with-docs`: `grilling` using `domain-modeling`.
3. Ask one unresolved design question at a time, with a recommended answer.
4. Write glossary or ADR docs only when `domain-modeling` requires it.
5. Stop when scope, owner boundaries, non-goals, compatibility, validation gates, rollback, and milestone order are concrete enough for the goal file.
6. Record the marker before marking the goal `Ready` or starting implementation.

## Skip Rules

If the user explicitly skips the grill, record the skip in the goal file:

```text
Planning preflight marker: preflight:<goal_slug>:skip:<yyyymmdd>-<short-id>
Planning preflight status: Skipped by explicit user instruction
Preflight source: user skip (<date or turn context>)
```

Do not infer skip from urgency, brevity, or direct implementation wording.

## Output Evidence

The goal file must record:

```text
Planning preflight marker: preflight:<goal_slug>:<yyyymmdd>-<short-id>
Planning preflight status: Done / Skipped by explicit user instruction
Preflight source: grill-with-docs / user skip
Resolved decisions: <summary or doc paths>
Open decisions: <none or explicit runtime hard stops>
Docs written: <CONTEXT.md / ADR paths / Not applicable>
```
