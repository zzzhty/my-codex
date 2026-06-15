---
name: long-running-goal
description: Use when creating, upgrading, executing, resuming, evolving, or closing a long-running goal plan for a project, especially when work needs ordered milestones, review gates, checkpoint evidence, validation evidence, explicit Loop Blueprint/harness boundaries for triggers, inputs, orchestration, worktrees, connectors, independent verification, human escalation, current-doc synchronization, failure breakpoints, plan/gate evolution, close/archive hygiene, or a decision about whether the newest user request supersedes an active goal context.
---

# Long Running Goal

Use this skill when a task should become an executable long-running goal in the project's planning area, or when an existing checklist/TODO needs to be upgraded into a staged goal contract.

Do not use it for a short one-off implementation plan. A long-running goal is appropriate when the work needs ordered milestones, milestone gates, validation evidence, checkpoint evidence, and a close step that leaves active docs clean.

## Request Supersession Guard

When this skill is loaded while an active or recently compacted goal context exists, classify the newest user request before doing any goal work.

Continue the active goal only when the newest request explicitly asks to execute, resume, continue, close, or advance that goal or one of its milestones. If the newest request asks for planning, explanation, alignment, skill editing, review-only analysis, git maintenance, or another bounded task, treat the active goal as paused and do not run milestone commands, edit goal evidence, or update goal-tool status for the old goal.

If the newest request asks to change the goal plan itself, update the planning document and indexes only; do not implement milestone code unless the user also asks for execution. If the request is ambiguous, answer or inspect the bounded surface first instead of continuing stale implementation work.

## Bundled Template

The reusable template is bundled in this skill at:

```text
templates/long_running_goal_template.md
```

Resolve that path relative to the skill folder. Copy the template into the project's active planning area, then replace all placeholders before marking the goal `Ready`.

## Template Flexibility

Use the bundled template for a new goal when the project has no stronger local convention. When the repository already uses a compact goal/TODO style, preserve that local style instead of forcing the full template, but the copied or handwritten goal must still include:

1. Current baseline and source-of-truth evidence.
2. Explicit owner boundaries, default behavior, compatibility surface, and non-goals.
3. Ordered milestones with scope, gates, validation, and checkpoint expectations.
4. Loop Blueprint / harness boundaries when the goal is recurring, automated, parallelized, connector-backed, or subagent-orchestrated.
5. Failure breakpoints and rollback/disable path.
6. Current-doc/TODO sync requirements.
7. Close/archive procedure and reusable execution prompt.

Do not mark a goal `Ready` while unresolved `<...>` placeholders remain.

## Planning Area Discovery

Before creating or upgrading a goal, identify where the project already keeps active plans and current guidance.

Prefer existing conventions in this order:

1. User-specified goal path, goal directory, or planning root.
2. Existing active goal/TODO directories, such as `docs/todo/`, `planning/todo/`, `goals/`, or `.codex/goals/`.
3. Existing current-doc indexes, development guides, validation logs, runbooks, or architecture/status registers that already reference active work.
4. If no convention exists and the user wants a new file, use goal directory `docs/todo/` and goal path `docs/todo/<goal_slug>_long_running_goal_plan.md` unless the repository clearly favors another docs root.

Do not create a new planning tree when the repository already has a live one under another name.

Use `<goal-dir>` for the directory that directly contains active goal plan files. Use `<planning-root>` only for the broader docs/planning tree when the project has one. Do not append `/todo` to a directory that is already the goal directory.

## Creation Workflow

1. Read current truth before drafting:
   - root instructions such as `AGENTS.md`
   - root `README.md` and area overview docs
   - current TODO/checklist/goal index
   - current development, usage, or runtime guide
   - status/boundary registers when present
   - relevant validation logs, runtime audits, architecture docs, contract docs, and existing goal/archive docs

2. Create or upgrade the goal file:
   - New goal path: `<goal-dir>/<goal_slug>_long_running_goal_plan.md` unless local conventions differ.
   - Copy from `templates/long_running_goal_template.md`.
   - Replace every `<...>` placeholder before marking the goal `Ready`.
   - If upgrading an existing TODO, preserve useful findings but reshape them into the template sections.

3. Freeze the contract before implementation:
   - State owner boundaries and product semantics.
   - Split current owner, compatibility surface, and future/non-goal boundaries.
   - Define ordered milestones: usually `M0 Contract Review / Design Freeze`, implementation milestones, docs/release closeout, then `Close`.
   - Give every milestone clear scope, review gate, recommended validation, evidence slots, and checkpoint evidence expectations.
   - Classify the execution shape as manual staged execution or Loop-shaped execution before implementation starts.
   - For Loop-shaped goals, freeze the trigger, input sources, triage/orchestration rule, worktree/isolation strategy, connector permissions, independent verifier, human escalation breakpoint, and durable learning target.

4. Add the execution contract:
   - Milestones must run sequentially.
   - Set each milestone `In Progress` before work starts.
   - Do not enter the next milestone until review gates pass, but continue automatically after a passed gate unless the gate explicitly requires human approval.
   - Record code, behavior, test, doc, rollback, and risk evidence per milestone.
   - If a Loop Blueprint exists, record harness evidence when the milestone changes triggers, inputs, orchestration, worktrees, connectors, subagents, or escalation behavior.
   - Diagnose and fix ordinary failures inside the milestone scope; stop only at the permission boundary below, and record root cause, failing command/path, exact breakpoint when known, and next diagnostic step.
   - Do not use fallback, compatibility fake-success, alternate backend, hidden partial success, or silent degradation to bypass gates.

5. Add close criteria:
   - All milestones `Done`.
   - All review gates `Passed`.
   - All checkpoint evidence recorded.
   - Current docs, validation logs, runtime/test checklists, and TODO/goal indexes synchronized.
   - `git diff --check` and relevant link checks pass.
   - Future/residual risks explicitly listed.
   - Close checkpoint evidence recorded. If the project uses Git or another version-control workflow, prefer the local close commit/revision format, such as `<goal_slug> close: <summary>`.

6. Add a reusable prompt:
   - Include the exact goal path.
   - Repeat the sequential milestone, Loop Blueprint, evidence, checkpoint, failure-handling, and close-gate rules.

## Loop Blueprint Harness

A long-running goal may be manually executed. Do not force automation into small or one-off plans.

When the goal is intended to run as a loop, or when it uses recurring triggers, multiple agents, worktrees, connectors, external side effects, or automated triage, make the harness explicit before implementation starts. Do not rely on the Strategy Evolution Loop or the model's judgment to discover these boundaries late.

The goal plan must answer:

1. Trigger: what starts or resumes the loop, and whether it is manual, scheduled, hook-driven, CI-driven, issue-driven, or goal-tool-driven.
2. Inputs: which source-of-truth artifacts are read, such as TODO indexes, issues, CI logs, reports, runtime state, user prompts, or prior checkpoint evidence.
3. Triage and orchestration: how findings become tasks, which tasks are in scope, how priority is assigned, and which role owns each step.
4. Worktree and isolation strategy: whether agents share the current checkout, use separate worktrees/branches, or must serialize edits to avoid file races.
5. Skills and context: which skills, runbooks, or project docs are mandatory inputs for each role.
6. Connectors and permissions: which external systems may be read or mutated, and which writes require human approval.
7. Independent verification: which subagent, script, test, reviewer, or gate checks the producer's work without trusting self-evaluation.
8. Human escalation: the exact breakpoint where the loop stops and reports to the user instead of continuing.
9. Durable learning: which result should be written back to a skill, TODO, report, validation log, runbook, or automation memory.

If any item is not applicable, say so explicitly with the reason. If the goal claims automation, connector writes, subagent orchestration, or worktree parallelism but leaves the corresponding harness field unspecified, keep the goal in `Draft`.

## Continuation And Permission Boundary

Long-running goals are meant to preserve momentum across milestones. Do not pause to ask for permission merely because a milestone boundary, review gate, checkpoint, or routine uncertainty exists.

Default behavior during execution:

1. Continue through sequential milestones after required validations and review gates pass.
2. Diagnose and fix ordinary failures when the next useful step is clear and inside the goal scope.
3. Record assumptions, risk, validation evidence, and checkpoint evidence in the goal document instead of interrupting for confirmation.
4. Ask the user only at a true stop condition:
   - the goal or user explicitly names a human approval gate
   - the next step is destructive, irreversible, privacy-sensitive, externally visible, or writes to an external connector without pre-approved permission
   - required credentials, files, tools, or source-of-truth inputs are missing and cannot be obtained locally
   - evidence contradicts the goal semantics and continuing would change scope or product behavior
   - the same blocker has repeated and no meaningful local diagnostic or implementation step remains

Human escalation is a stop condition, not a routine status checkpoint. If the plan says "report" or "record evidence", do that in the goal evidence and continue unless one of the stop conditions above applies.

## Codex Goal Tool Boundary

Use Codex goal tools only when the user explicitly asks to create, execute, resume, or close a long-running goal in the active conversation. A planning document by itself is not the same thing as an active Codex goal.

When creating an active Codex goal:

1. Set the objective to the concrete project outcome, not to a single milestone unless the user scoped it that way.
2. Set a token budget only when the user explicitly requested one.
3. If an active goal already exists, continue or clarify the existing goal instead of creating a nested goal.
4. Do not mark the goal `complete` until the objective is actually achieved and no required work remains.
5. Do not mark the goal `blocked` unless the same blocker has repeated for the required blocked-threshold turns and no meaningful progress is possible.

During ordinary milestone execution, update the goal document and project evidence. Do not use goal completion as a substitute for milestone status updates, review gates, commits, validation logs, or final user reporting.

Do not mark an active Codex goal complete or blocked because the user redirected the turn to another task. A redirected request pauses the goal unless the user explicitly closes, cancels, or resumes it.

## Common Pattern: Production Cutover With Shadow

For cutover work where a new implementation is compared against an existing authoritative path, freeze these modes before implementation:

1. Existing default mode remains the rollback path.
2. Full-shadow diagnostic mode keeps both paths running and records diffs.
3. Production or shadow-reduced mode is explicit and opt-in until measured.

The production path must own the metadata and output contract it depends on before old hot-path work is skipped. Do not claim a speedup by disabling shadow checks while still relying on side effects from the old implementation.

Before any default flip, require a matrix that compares default, full-shadow, and production modes with correctness evidence and timing evidence. Record the default decision as a review gate, not as an implementation accident.

Keep timing evidence mode-specific. Full-shadow timing includes diagnostic and comparison overhead and must not be reported as production speed. Production timing is only meaningful after the new path owns the metadata/output contract it needs, old hot-path work is actually skipped, allocator/workspace reuse is frozen where relevant, and correctness gates still pass.

## Bundled Helpers

Use these scripts when they match the project surface. They are intentionally lightweight and use only Python standard library modules.

```bash
python <skill-folder>/scripts/check_goal_ready.py <goal-file>
python <skill-folder>/scripts/check_md_links.py <planning-root>
python <skill-folder>/scripts/check_todo_index.py <goal-file> <index-file> [<index-file> ...]
```

`check_goal_ready.py` catches unresolved placeholders and missing core sections. `check_md_links.py` checks relative Markdown links. `check_todo_index.py` verifies the active goal is discoverable from the project's TODO or README indexes.

## Current Docs Sync

After creating or upgrading a goal:

1. Update the active TODO/goal index if one exists, such as `<goal-dir>/README.md` or a current checklist.
2. Update current development, usage, runtime, or status docs only with concise current-state pointers.
3. Update boundary/status registers when the goal changes owner boundaries, compatibility surfaces, conditional work, future scope, or no-longer-reopened decisions.
4. Keep detailed milestone plans in the goal doc; do not duplicate full milestone content into current docs.
5. If the goal changes validation scope, update the relevant validation log or runtime test checklist with planned/actual gates.

## Strategy Evolution Loop

During execution, improve the plan before continuing if evidence shows that a gate, validation rule, rollback path, milestone boundary, Loop Blueprint field, or skill strategy is not rigorous enough for the actual risk.

Use this loop only for contract quality, not to avoid a hard implementation problem or bypass a failing gate:

1. Pause implementation at the current breakpoint.
2. State the gap precisely: which gate, rule, milestone boundary, or harness boundary is too weak and what evidence exposed it.
3. Update the reusable strategy first when the gap belongs in this skill or its bundled template.
4. Update the active goal plan next, including Loop Blueprint fields, milestone scope, review gate, validation commands, rollback path, and checkpoint evidence expectations affected by the new rule.
5. Validate the skill or plan edits with the relevant helper scripts and lightweight diff checks.
6. Record in the goal evidence that the plan evolved before implementation continued, including changed strategy files and the reason.
7. Resume the original milestone from the paused breakpoint and follow the stronger gate.

Do not silently change acceptance criteria after implementation just to make current work pass. If the evolved rule invalidates completed work, reopen the affected milestone evidence or mark the gate failed and fix the underlying issue.

## Execution And Checkpoints

When the user explicitly asks to execute a goal, follow the goal file rather than improvising.

Before resuming after a context transition, interruption, or automatic compaction:

1. Re-read the newest user request and the active goal document.
2. Confirm which milestone is currently requested and which milestone is merely next in the document.
3. Do not continue an older implementation thread if the newest request changed to planning, explanation, alignment, skill editing, or another bounded task.
4. If the user asks only for a plan or explanation, do not edit code unless they explicitly convert the request into execution.
5. If the user redirects to a different task, leave the goal document untouched unless the redirect explicitly asks to update goal state or planning docs.

For each milestone:

1. Mark the milestone `In Progress`.
2. Implement only the milestone scope.
3. If execution exposes an insufficient gate or strategy, run the Strategy Evolution Loop before continuing.
4. Run the milestone's validation commands.
5. Fill the evidence section with actual commands and results.
6. Record checkpoint evidence for the milestone.
7. Mark milestone `Done`, review `Passed`, checkpoint `Done`.

If the project uses a compact goal document without prewritten evidence slots, add a short execution evidence block for the milestone before marking it `Done`. It must include changed files, behavior impact, validation commands/results, rollback path, and remaining risk.

If the milestone exercises a Loop Blueprint, the evidence block must also include the trigger/input path used, orchestration or worktree isolation evidence, connector read/write evidence, independent verification result, and any human escalation decision.

Keep each checkpoint scoped. Do not wait until the end to record evidence.

Use a Git commit as checkpoint evidence only when the project already uses Git/version control and the user or local workflow expects checkpoint commits. Do not initialize Git, create artificial commits, or fabricate checkpoint success just to satisfy the template. In non-VCS contexts, record an equivalent checkpoint such as issue/task history, document revision, saved artifact path, signed-off review note, or `Not applicable: no VCS in this workspace`.

When a milestone has a review gate, record evidence and the exact pass/fail state. If the gate passes, enter the next milestone automatically unless the gate explicitly says human approval is required. If the gate fails, continue with in-scope fixes and diagnostics when the next useful step is clear; stop only at the permission boundary above.

## Close Workflow

When all milestones are done:

1. Change overall status and target status to `Closed` while preparing close checkpoint evidence.
2. Fill close execution evidence before removing or archiving the active goal.
3. Sync durable outcomes into current docs, status/boundary registers, validation logs, runtime/test checklists, and the active TODO/goal index.
4. If the goal changes a legacy boundary, update the relevant archive or legacy summary when one exists.
5. Follow local archive conventions. If no convention exists, do not create dated archive directories or checked-in closed plan copies just to preserve history.
6. Remove the closed goal from active TODO/goal navigation; if it is no longer needed as an active execution contract, delete or archive the goal file according to local convention.
7. Run validation scoped to the changed paths:

```bash
git diff --check -- <changed-paths>
```

If Markdown links changed, run a relative-link check scoped to the changed docs/planning tree:

```bash
python - <<'PY'
from pathlib import Path
import re
root = Path("<docs-or-planning-root>")
pat = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
missing = []
for f in root.rglob("*.md"):
    text = f.read_text(encoding="utf-8")
    for m in pat.finditer(text):
        target = m.group(1).strip()
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        p = (f.parent / target).resolve()
        ok = p.is_dir() if target.endswith("/") else p.exists()
        if not ok:
            line = text[:m.start()].count("\n") + 1
            missing.append((str(f), line, m.group(1)))
if missing:
    for f, line, target in missing:
        print(f"{f}:{line} missing {target}")
    raise SystemExit(1)
print("all markdown relative links resolve")
PY
```

8. Record close checkpoint evidence. If Git/version control is active and expected, commit close with the recorded close message.

## Quality Bar

A useful long-running goal is not a vague roadmap. It must answer:

1. What source of truth was read?
2. What exact semantics and owner boundaries are being frozen?
3. What is explicitly not in scope?
4. What milestones must happen in order?
5. What commands prove each milestone?
6. What counts as blocked?
7. Which actions require human permission, and which passed gates may continue automatically?
8. How does the work close and leave active docs clean?
9. If the work is Loop-shaped, what harness constrains triggers, inputs, orchestration, worktrees, connectors, verification, escalation, and durable learning?
