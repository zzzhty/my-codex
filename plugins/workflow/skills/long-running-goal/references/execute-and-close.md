# Execute, Checkpoint, Evolve, And Close

Use the matching sections after `../SKILL.md` routes an execute, resume, continue, advance, evolve, or close branch here. The inline supersession, pre-approval/YOLO, runtime hard-stop, and goal-tool boundaries remain authoritative.

## Execute, Checkpoint, And Evolve

Follow the goal file rather than improvising. After context transition, interruption, or compaction, re-read the newest user request and active goal document before resuming.

Before the first implementation milestone, confirm the goal file records a completed planning-preflight marker from `../components/planning-preflight.md` or an explicit user-skip marker. If not, run the preflight component before mutating implementation files.

For each milestone:

1. Mark it `In Progress`.
2. Implement only its scope.
3. If a gate, validation rule, rollback path, milestone boundary, Loop field, or skill strategy is too weak for observed risk, pause mutation only long enough to update the contract; do not ask for permission unless a runtime hard stop applies.
4. Run the milestone validation commands.
5. Record changed files, behavior impact, command results, doc sync, rollback path, remaining risk, and checkpoint evidence.
6. If the milestone exercises a Loop Blueprint, also record trigger/input path, orchestration or worktree isolation evidence, connector read/write evidence, independent verification, YOLO actions, and runtime-hard-stop decisions.
7. Apply `../components/checkpoint.md`.
8. Mark milestone `Done`, review `Passed`, and checkpoint `Done` only after evidence is recorded.

When a review gate passes, enter the next milestone automatically. When it fails, keep fixing and diagnosing in scope while the next useful step is clear; stop only at the runtime hard-stop boundary.

When execution exposes a weak gate, validation rule, rollback path, milestone boundary, Loop field, or skill strategy, state the gap and evidence, update the reusable strategy first when the rule belongs in this skill or template, update the active goal next, validate the edits, record changed strategy files and reason in goal evidence, then resume the original milestone. If the evolved rule invalidates completed work, reopen affected milestone evidence or mark the gate failed and fix the issue. Do not silently weaken acceptance criteria after implementation, bypass gates with fallback/alternate backends/fake success/hidden partial success/silent degradation, or repackage deprecated surfaces as current semantics unless the goal explicitly requires it and docs are updated.

Use a Git commit as checkpoint evidence only when the project already uses version control and the user or local workflow expects checkpoint commits. Otherwise record an equivalent revision, issue/task history, artifact path, review note, or `Not applicable: no VCS in this workspace`.

Completion criterion: the current milestone has passing validation and recorded behavior, docs, rollback, risk, Loop evidence when applicable, review status, and checkpoint evidence before it is marked `Done` or execution advances.

## Current Docs And Close

After creating, upgrading, or evolving a goal, update only the current docs that need concise pointers: active TODO/goal index, development/runtime/status docs, boundary registers, validation logs, or runtime test checklists. Keep detailed milestone plans in the goal file.

When all milestones are done:

1. Mark the Close row `In Progress` and keep the overall goal `In Progress` while preparing close evidence.
2. Fill close execution evidence before removing or archiving the active goal.
3. Sync durable outcomes into current docs, indexes, validation logs, and status/boundary registers.
4. Follow local archive conventions; do not invent dated archive trees or checked-in closed copies just to preserve history.
5. Remove closed goals from active navigation, or archive/delete the goal file according to local convention.
6. Validate index topology with `check_todo_index.py --mode closed --archived-goal <archive-path> <old-active-path> <index>...` after archiving, or `--mode absent <old-active-path> <index>...` after deletion without an archive.
7. Run `git diff --check -- <changed-paths>` and `check_md_links.py` when Markdown links changed.
8. Record close checkpoint evidence. If version control is active and expected, use the local close commit/revision format, such as `<goal_slug> close: <summary>`.
9. Only after every close gate and evidence check passes, set the Close row to `Done/Passed/Done` and the overall goal status to `Closed`.

Completion criterion: every milestone is `Done`, close evidence and validation are recorded, durable current docs are synchronized, active navigation no longer points to closed work, and archive/delete handling follows local convention.
