---
name: long-running-goal
description: Use when creating, upgrading, executing, resuming, continuing, evolving, or closing a continuation-ready long-running goal plan for a project, especially when work needs ordered milestones, validation/review gates, checkpoint evidence, Loop Blueprint/harness boundaries, frozen YOLO non-stops, runtime hard stops, current-doc synchronization, strategy/plan evolution, close/archive hygiene, or request-supersession decisions for an active goal context.
---

# Long Running Goal

Use this skill when a task should become an executable, continuation-ready goal plan in the project's planning area, or when an existing checklist/TODO needs to become a staged goal contract.

Do not use it for short one-off implementation plans. A long-running goal is appropriate when work needs ordered milestones, gates, evidence, a reusable continuation contract, and a close step that leaves active docs clean.

A `Ready` goal means the plan is complete enough for the same or another agent to continue without chat history: current state, next milestone, gates, evidence requirements, pre-approved execution scope, and runtime hard stops are all explicit.

## Request Supersession Guard

When an active or compacted goal context exists, classify the newest user request before doing goal work.

Continue the active goal only when the request asks to execute, resume, continue, close, or advance that goal, or asks for status/evidence/clarification/progress about the same goal. Answer or record same-goal context and continue unless the user explicitly says to pause, stop, redirect, or change scope.

Pause the old goal when the newest request is unrelated planning, explanation, alignment, skill editing, review-only analysis, git maintenance, or another bounded task. Do not run milestone commands, edit old goal evidence, or update goal-tool status for a paused goal.

If the request changes the goal plan itself, update the planning document and indexes only unless the user also asks for execution. If ambiguous, inspect or answer the bounded surface first instead of continuing stale implementation work.

## Goal File And Template

Use `templates/long_running_goal_template.md` for new goals unless the repo has a stronger local convention. Copy it into the active goal directory, replace all `<...>` placeholders, and do not mark the goal `Ready` while placeholders remain.

Find the planning area in this order: user-specified path, existing active goal/TODO directories such as `docs/todo/`, current-doc indexes that already reference active work, then `docs/todo/<goal_slug>_long_running_goal_plan.md` as a fallback. Do not create a parallel planning tree when a live one already exists, and do not append `/todo` to a directory that is already the goal directory.

If preserving a compact local goal style, the copied or handwritten goal must still include:

1. Current baseline and source-of-truth evidence.
2. Owner boundaries, default behavior, compatibility surface, non-goals.
3. Ordered milestones with scope, gates, validation, evidence, checkpoints.
4. Loop Blueprint / harness boundaries when recurring, automated, parallelized, connector-backed, or subagent-orchestrated.
5. Frozen YOLO non-stop boundary and runtime hard-stop boundary.
6. Failure breakpoints and rollback/disable path.
7. Current-doc/TODO sync requirements.
8. Close/archive procedure and reusable continuation prompt.

## Components

Use bundled components as internal workflow steps, not as standalone user-facing skills:

1. `components/planning-preflight.md`: before goal creation/conversion or first implementation without a completed marker, run `grill-with-docs`; skip only by explicit user instruction and record the skip marker.
2. `components/checkpoint.md`: before any milestone or close step is `Done`, record revision evidence without default empty commits.

## Create Or Upgrade

In this section, `upgrade` means converting or reshaping an existing TODO, PRD, issue, checklist, or rough plan into a long-running-goal contract. It does not mean ordinary runtime evolution during milestone execution.

1. Read current truth before drafting: root instructions, README/area overviews, active TODO or goal indexes, current guides, status/boundary registers, validation logs, runtime audits, architecture/contract docs, and existing goal/archive docs.
2. Apply `components/planning-preflight.md` before freezing the goal unless the user explicitly skips the grill.
3. Create or reshape the goal file as a continuation contract, preserve useful findings from existing TODOs, and record the planning-preflight marker or skip marker.
4. Freeze the contract before implementation:
   - product semantics, owner boundaries, compatibility surface, future/non-goals
   - sequential milestones, usually `M0 Contract Review / Design Freeze`, implementation milestones, docs/release closeout, then `Close`
   - milestone scope, review gate, validation commands, evidence slots, checkpoint expectations
   - execution shape: manual staged execution or Loop-shaped execution
   - pre-approved YOLO local operations, pre-approved external reads/writes, runtime hard stops
   - Loop harness fields when applicable: trigger, inputs, triage/orchestration, isolation, connector boundaries, independent verifier, durable learning
5. Keep foreseeable approval out of runtime execution. Human approval gates, external-write permission, destructive-action permission, connector permission, and unresolved design approval must be settled before `Ready`; otherwise keep the goal `Draft`.
6. Add close criteria and a reusable continuation prompt that names the exact goal path and repeats the sequential milestone, YOLO boundary, Loop harness, evidence, hard-stop, and close-gate rules.

## Loop Blueprint Harness

Do not force automation into small or one-off plans. For manual staged execution, say `Not applicable` with the reason.

When a goal uses recurring triggers, multiple agents, worktrees, connectors, external side effects, or automated triage, make the harness explicit before implementation starts. The plan must answer:

1. Trigger: what starts or resumes the loop.
2. Inputs: which source-of-truth artifacts are read.
3. Triage and orchestration: how findings become scoped tasks and who owns each step.
4. Worktree and isolation: shared checkout, separate worktrees/branches, or serialized edits.
5. Skills and context: mandatory skills, runbooks, docs, specs, or prior decisions.
6. Connector read/write boundaries: readable/mutable systems, pre-approved writes, and writes that keep the goal `Draft` until approved.
7. Independent verification: subagent, script, test, reviewer, or gate that checks producer work without trusting self-evaluation.
8. Runtime hard stops: exact technical breakpoints where execution stops and asks the user.
9. Durable learning: where results are written back, such as a skill, TODO, report, validation log, runbook, automation memory, or current doc.

If the goal claims automation, connector writes, subagent orchestration, worktree parallelism, or any future approval breakpoint but leaves the corresponding harness or pre-approval field unspecified, keep it `Draft`.

## Pre-Approval And YOLO Boundary

Long-running goals preserve momentum across milestones. A milestone boundary, review gate, checkpoint, routine uncertainty, rebuild, refresh, reinstall, validation command, docs sync, generated-artifact cleanup, or other planned non-destructive local operation is not a permission prompt.

Before marking a goal `Ready`, freeze:

1. Pre-approved YOLO local operations: non-destructive local actions needed by the plan, including code/docs/source-skill edits, rebuilds, refreshes, reinstalls, workspace dependency restores, tests, lint, formatting, link checks, plugin/cache refreshes, and generated-artifact cleanup.
2. Pre-approved external reads/writes: every connector, API, issue, PR, CI, automation, hook, or messaging surface that may be read or written. Foreseeable unapproved external writes keep the goal `Draft`.
3. Runtime hard stops: only the conditions that may stop execution after the goal is `Ready`.

During execution, use YOLO mode inside the frozen scope:

1. Continue after validations and review gates pass.
2. Run planned non-destructive local operations without asking.
3. Diagnose and fix ordinary failures when the next useful step is clear and in scope.
4. Retry or vary local diagnostics before stopping; a single failed command, stale cache, missing build artifact, failed rebuild, or failed validation with a clear local next step is not a stop condition.
5. Record assumptions, risk, validation evidence, checkpoint evidence, and YOLO actions in the goal document.
6. Ask the user only at a runtime hard stop:
   - technical progress is impossible after repeated local diagnostics or fixes, normally at least three attempts or three distinct approaches unless immediately decisive
   - required credentials, files, tools, or source-of-truth inputs are missing and cannot be obtained locally
   - the next step is destructive, irreversible, privacy-sensitive, externally visible, or an unapproved external write
   - evidence contradicts frozen goal semantics and continuing would change scope or product behavior
   - a required subagent, connector, worktree, or verifier failed and no meaningful local fallback exists inside the frozen plan

Runtime hard stops are true technical stop conditions, not status checkpoints. If the plan says report, record evidence, rebuild, refresh, validate, or sync docs, do that and continue unless a hard stop applies.

## Codex Goal Tool Boundary

Use Codex goal tools only when the user explicitly asks to create, execute, resume, or close a long-running goal in the active conversation. A planning document alone is not an active Codex goal.

When creating an active Codex goal, set the objective to the project outcome, set a token budget only if requested, avoid nested active goals, and do not mark it `complete` until no required work remains. Do not mark it `blocked` unless the same blocker has repeated for the required threshold and no meaningful progress is possible.

During ordinary milestone execution, update the goal document and project evidence. Do not use goal completion as a substitute for milestone status, gates, commits, validation logs, or final reporting.

## Production Cutover Gate

For cutovers that compare a new implementation against an authoritative old path, freeze default, full-shadow diagnostic, and production/shadow-reduced modes before implementation. Full-shadow keeps both paths running and records diffs. The old path remains rollback until a review gate records a default/full-shadow/production comparison matrix, correctness evidence, mode-specific timing evidence, and the decision to change defaults.

Do not claim production speedup by disabling shadow checks while still depending on old-path metadata, output contracts, or side effects. Production timing counts only after the new path owns the metadata/output contract it needs, old hot-path work is actually skipped, reuse/allocator assumptions are frozen when relevant, and correctness gates still pass.

## Execute, Checkpoint, And Evolve

When the user asks to execute a goal, follow the goal file rather than improvising. After context transition, interruption, or compaction, re-read the newest user request and active goal document before resuming.

Before the first implementation milestone, confirm the goal file records a completed planning-preflight marker from `components/planning-preflight.md` or an explicit user-skip marker. If not, run the preflight component before mutating implementation files.

For each milestone:

1. Mark it `In Progress`.
2. Implement only its scope.
3. If a gate, validation rule, rollback path, milestone boundary, Loop field, or skill strategy is too weak for observed risk, pause mutation only long enough to update the contract; do not ask for permission unless a runtime hard stop applies.
4. Run the milestone validation commands.
5. Record changed files, behavior impact, command results, doc sync, rollback path, remaining risk, and checkpoint evidence.
6. If the milestone exercises a Loop Blueprint, also record trigger/input path, orchestration or worktree isolation evidence, connector read/write evidence, independent verification, YOLO actions, and runtime hard-stop decisions.
7. Apply `components/checkpoint.md`.
8. Mark milestone `Done`, review `Passed`, and checkpoint `Done` only after evidence is recorded.

When a review gate passes, enter the next milestone automatically. When it fails, keep fixing and diagnosing in scope while the next useful step is clear; stop only at the runtime hard-stop boundary.

When execution exposes a weak gate, validation rule, rollback path, milestone boundary, Loop field, or skill strategy, state the gap and evidence, update the reusable strategy first when the rule belongs in this skill or template, update the active goal next, validate the edits, record changed strategy files and reason in goal evidence, then resume the original milestone. If the evolved rule invalidates completed work, reopen affected milestone evidence or mark the gate failed and fix the issue. Do not silently weaken acceptance criteria after implementation, bypass gates with fallback/alternate backends/fake success/hidden partial success/silent degradation, or repackage deprecated surfaces as current semantics unless the goal explicitly requires it and docs are updated.

Use a Git commit as checkpoint evidence only when the project already uses version control and the user or local workflow expects checkpoint commits. Otherwise record an equivalent revision, issue/task history, artifact path, review note, or `Not applicable: no VCS in this workspace`.

## Current Docs And Close

After creating, upgrading, or evolving a goal, update only the current docs that need concise pointers: active TODO/goal index, development/runtime/status docs, boundary registers, validation logs, or runtime test checklists. Keep detailed milestone plans in the goal file.

When all milestones are done:

1. Change goal status to `Closed` while preparing close evidence.
2. Fill close execution evidence before removing or archiving the active goal.
3. Sync durable outcomes into current docs, indexes, validation logs, and status/boundary registers.
4. Follow local archive conventions; do not invent dated archive trees or checked-in closed copies just to preserve history.
5. Remove closed goals from active navigation, or archive/delete the goal file according to local convention.
6. Run `git diff --check -- <changed-paths>` and `check_md_links.py` when Markdown links changed.
7. Record close checkpoint evidence. If version control is active and expected, use the local close commit/revision format, such as `<goal_slug> close: <summary>`.

## Bundled Helpers

Use these scripts when they match the project surface:

```bash
python <skill-folder>/scripts/check_goal_ready.py <goal-file>
python <skill-folder>/scripts/check_md_links.py <planning-root>
python <skill-folder>/scripts/check_todo_index.py <goal-file> <index-file> [<index-file> ...]
```

`check_goal_ready.py` catches unresolved placeholders and missing core sections. `check_md_links.py` checks relative Markdown links. `check_todo_index.py` verifies the active goal is discoverable from TODO or README indexes.

## Quality Bar

A useful long-running goal must answer:

1. What source of truth was read?
2. What semantics and owner boundaries are frozen?
3. What is explicitly out of scope?
4. What milestones must happen in order?
5. What commands prove each milestone?
6. What counts as blocked?
7. Which actions are frozen as YOLO non-stops, and which runtime hard stops actually require the user?
8. How does the work close and leave active docs clean?
9. If Loop-shaped, what harness constrains triggers, inputs, orchestration, worktrees, connectors, verification, runtime hard stops, and durable learning?
