# Planning Preflight Component

Use this component before creating or converting a long-running goal, or before first implementation when the goal lacks a completed planning-preflight marker.

Default to `grill-with-docs` before the goal becomes executable. Skip only by explicit user instruction such as `skip grill`, `no grill`, or an equivalent direct instruction.

## Entry Conditions

Apply this component when:

1. A new long-running goal is being created from an idea, TODO, PRD, bug, migration, or broad implementation request.
2. An existing TODO, PRD, issue, or rough plan is being converted into a long-running goal contract.
3. A goal is about to enter implementation but its goal file does not record a completed planning-preflight marker.

Do not rerun it when the goal records a completed preflight marker or explicit user-skip marker. Ordinary runtime evolution updates the active goal and resumes; rerun preflight only when product semantics, scope, owner boundaries, or milestone order changed enough to obsolete the old marker. Refreshing only the time assessment is an evidence rebaseline and does not replace the marker.

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
3. Follow the rounds/frontier cadence owned by `grilling`: in each round, ask the whole currently unblocked frontier, number every question, and include a recommended answer for each. Wait for the user's batch answers, then recompute the frontier; questions that depend on unresolved answers belong to a later round.
4. Write glossary or ADR docs only when `domain-modeling` requires it.
5. Timebox, record, and report the preflight time assessment below.
6. Ask the user whether Close should use `watcher:housekeeping` for this goal's task-owned temporary cache roots, unless the same request already states the choice explicitly.
7. Stop when scope, owner boundaries, non-goals, compatibility, validation gates, rollback, milestone order, time assessment, and the temporary-cache housekeeping choice are concrete enough for the goal file.
8. Record the marker, time assessment, and housekeeping decision before marking the goal `Ready` or starting implementation.

## Preflight Time Assessment

Timebox the assessment to planning evidence already gathered plus at most one bounded inspection. Do not run a full build, test suite, benchmark, dependency install, CI wait, or new external read solely to estimate time.

Assess remaining wall-clock elapsed time from `Ready` to `Closed`; when resuming, use `current-milestone-to-Closed`. State dated evidence and assumptions, including whether external waits and serial or parallel execution are included. Record the section as visible plain Markdown; fenced, commented, indented-code, or HTML-wrapped content does not satisfy the contract. Record exactly one branch:

1. `Rough range`: record a low-high range in seconds, minutes, hours, days, business/working days, weeks, months, or years, use `Assessment mode: Rough range`, and set the distribution field to `Not required: rough range recorded.` Do not use a single-point ETA or present the range as an SLA.
2. `Distribution only`: use `Assessment mode: Distribution only`, set the estimate to the exact sentinel `Not quickly estimable`, explain the concrete blocker, and record at least two semantically distinct critical-path driver rows shaped `- <driver> — <Dominant / Material / Minor / Unknown> — <reason>`. Drivers and reasons must contain concrete text after Markdown decoration is removed.

Use relative bands rather than unmeasured percentages in the band position; a reason may cite a measured percentage as evidence. `Not quickly estimable` is a complete fallback, not an `Open decisions` entry, `Blocked` state, or runtime hard stop. An overrun is also a non-stop: update the dated evidence and continue unless an independent hard stop applies.

For a `Long-Running Goal Sequence`, apply the branch-specific timing roll-up in `../references/sequence-child-goals.md`; the field schema and two assessment modes above remain authoritative.

Completion criterion: the assessment is recorded in the goal and reported to the user, names the target, and selects exactly one valid branch. Its dated basis or blocker states external-wait and serial/parallel assumptions; `Rough range` has a low-high unit range, while `Distribution only` has at least two concrete, semantically distinct banded drivers.

## Task Temporary Cache Decision

Treat task temporary cache handling as a material preflight choice, not a derived implementation detail. Record exactly one user-confirmed policy:

1. `Enabled`: when concrete roots were created, Close invokes `watcher:housekeeping` for bounded inventory and cleanup of recorded, owner-specific disposable cache candidates.
2. `Disabled`: when concrete roots were created, Close does not clean them and instead records retained paths and sizes.
3. `Not applicable`: the user confirms that this goal will not create a task temporary cache root.

Skipping `grill-with-docs` does not skip this choice. It also does not skip the time assessment. If the user explicitly skips the grill without choosing a policy, ask only this material question before the preflight can complete. A legacy goal with no recorded policy remains valid but has no cleanup authorization; do not infer `Enabled` at Close.

For `Enabled` or `Disabled`, before a producer writes temporary data, use the host platform or runtime's standard temporary-directory resolver, then allocate an owner-specific goal/sequence namespace beneath the resolved root. Do not prescribe `/tmp`, a fixed Windows path, an environment-variable expression, the shared system/user temporary root itself, a generic `tmp` / `temp` / `cache` root, or another owner's directory. Record each fully resolved absolute owner root with a `goal-owned:` or `sequence-owned:` label and bind subsequent task-temporary writes to that recorded namespace. Reuse the recorded value at Close rather than resolving the platform root again. For `Not applicable`, record directly that no task temporary cache root will be created; do not resolve or allocate one.

`Enabled` authorizes the housekeeping workflow, not unconditional recursive deletion. Inventory first; preserve dependencies, runtime state, logs, reports, durable evidence, unknown producers, locked files, permission boundaries, and symlink/junction/reparse-point escapes. Keep durable Close evidence outside the temporary cache root. If `watcher:housekeeping` is unavailable, do not substitute a raw delete command: keep Close and the overall goal `In Progress`, or mark Close `Blocked` only when the normal runtime hard-stop contract is met. Only a new explicit user decision recorded as a preflight-policy evolution may switch the policy to `Disabled`.

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
## Preflight Time Assessment
Assessment target: <Ready-to-Closed / current-milestone-to-Closed>
Assessment mode: <Rough range / Distribution only>
Rough elapsed-time estimate: <low-high with unit / Not quickly estimable>
Basis or blocker: <YYYY-MM-DD evidence or blocker, external-wait scope, and serial/parallel assumptions>
Critical-path time-cost distribution: <Not required: rough range recorded. / at least two banded driver rows>
## Task Temporary Cache / Housekeeping
Close housekeeping policy: <Enabled / Disabled / Not applicable>
Housekeeping decision source: <explicit user confirmation with date or turn context>
Task temporary cache root strategy: <Enabled/Disabled: platform/runtime-resolved goal/sequence-owned namespace beneath the resolved root and owner-bound producers; Not applicable: explicit no-root strategy>
Recorded task temporary cache roots: <one fully resolved owner-labeled absolute path entry per root / Resolve and record before first use / None created / Not applicable>
Housekeeping boundary: <policy-specific watcher dependency or no-cleanup outcome, disposable scope, preservation rules>
```
