---
name: long-running-goal
description: Use when creating, upgrading, executing, resuming, continuing, evolving, or closing a continuation-ready long-running goal plan or strict serial Long-Running Goal Sequence for a project, especially when work needs ordered milestones or child goals, validation/review gates, checkpoint evidence, Loop Blueprint/harness boundaries, frozen YOLO non-stops, runtime hard stops, current-doc synchronization, strategy/plan evolution, close/archive hygiene, or request-supersession decisions for an active goal context.
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

Use `templates/long_running_goal_template.md` for one goal and `templates/long_running_goal_sequence_template.md` for a `Sequence Child Goals` branch unless the repo has a stronger local convention. Copy it into the active goal directory, replace all `<...>` placeholders, and do not mark the goal `Ready` while placeholders remain. The readiness checker also scans fenced commands and evidence; only documentation-only examples whose opening fence contains the exact `placeholder-example` token are exempt.

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

## Branch Routing

- Before you create or upgrade a goal, or define a Loop-shaped execution harness, read `references/create-and-loop.md` and satisfy every matching completion criterion before marking the goal `Ready`.
- For `Sequence Child Goals` (formal artifact: `Long-Running Goal Sequence`; `umbrella` is only an alias), read `references/sequence-child-goals.md` before creation, authorization, promotion, resume, or close. The sequence parent and every child require a non-skip `Done` preflight from `grill-with-docs`.
- For a production cutover that compares a new implementation with an authoritative old path, read `references/production-cutover.md` before freezing modes or claiming speedup.
- Before you execute, resume, continue, advance, evolve, or close a goal, read `references/execute-and-close.md`; follow the goal file and finish its matching execution or close criterion.

Load every reference whose condition matches a combined task. These pointers disclose branch detail only; the inline supersession, `Ready`, pre-approval/YOLO, runtime hard-stop, and Codex goal-tool contracts always apply.

After creating, upgrading, or evolving a goal, update only the current docs that need concise pointers; keep detailed milestone plans in the goal file.

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

## Bundled Helpers

Use these scripts when they match the project surface:

```bash
python <skill-folder>/scripts/check_goal_ready.py <goal-file>
python <skill-folder>/scripts/check_goal_sequence.py <sequence-file> [--allow-draft]
python <skill-folder>/scripts/check_md_links.py <planning-root>
python <skill-folder>/scripts/check_todo_index.py [--mode active|closed|absent] [--archived-goal <archive-path>] <goal-file> <index-file> [<index-file> ...]
```

`check_goal_ready.py` validates one goal's written contract. `check_goal_sequence.py` composes that check with mandatory non-skip preflights and cross-child ordering, state, milestone, handoff, and close consistency; `--allow-draft` relaxes lifecycle only. `check_md_links.py` checks relative Markdown links. `check_todo_index.py` defaults to exact-link `active` validation; use `closed` with `--archived-goal` after archiving, or `absent` after deletion without an archive.

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
10. If a sequence, are every child boundary and required grill preflight frozen, one child current, handoffs consistent, and authorization no broader than the children?
