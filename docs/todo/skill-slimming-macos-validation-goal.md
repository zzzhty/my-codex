# Skill Slimming macOS Validation Long-Running Goal

Overall status: `Ready`

Updated: 2026-08-21

This goal owns the complete macOS validation and PR-ready handoff for PR #13. It is subordinate to `docs/todo/skill-slimming-plan.md`: that parent plan remains the design and semantic authority for S0-S4, while this goal owns only checkout isolation, validation, bounded repair, review, behavior sampling, evidence writeback, and the Draft-to-Ready transition.

## Goal Summary

Goal Name: `Skill Slimming macOS Validation`

Goal Description:

1. Validate the complete S0-S4 PR #13 candidate in a real macOS checkout with focused, root, Workflow, and Watcher tests plus current deterministic validators.
2. Prove the frozen routing, read-only, identity, delegation, long-running-goal, universal-resource, and installed-state boundaries with independent review and behavioral sampling.
3. Fix only proven PR #13 regressions, push validated evidence to the same branch, and mark PR #13 Ready when every gate passes; merge remains outside this goal.

Goal Status: `Ready`

Goal Owner: `my-codex repository maintainer / executing local Codex agent`

Goal Path: `docs/todo/skill-slimming-macos-validation-goal.md`

Planning root: `docs/todo`

Goal directory: `docs/todo`

Continuation contract: Read the newest user request, root `AGENTS.md`, `docs/todo/skill-slimming-plan.md`, this goal, current PR #13 metadata, and the live local checkout before acting. Resume only the first non-Done milestone. Preserve unrelated dirty work, all frozen S0-S4 semantics, PR #3 skill bodies, universal discovery state, and installed runtime state. The goal may update the PR #13 branch and PR metadata but may not merge PR #13.

Planning preflight marker: `preflight:skill-slimming-macos-validation:20260821-mac1`

Planning preflight status: `Done`

Preflight source: `grill-with-docs-equivalent review of PR #13, the current slimming parent plan, root instructions, current tests/validators, universal discovery architecture, and the previously prepared macOS validation prompt`

Resolved decisions: `Validation runs on macOS from the PR #13 candidate; dirty user work is isolated with a temporary worktree; source regressions and installed-state drift are separate evidence classes; bounded fixes stay on the same PR branch; independent read-only review is required for Ready; PR merge is not authorized.`

Open decisions: `None before execution. A runtime hard stop is required if an independent reviewer cannot be obtained, required credentials/source facts are unavailable, or a safe fix would violate the frozen scope.`

Docs written: `docs/todo/skill-slimming-plan.md; docs/todo/skill-slimming-macos-validation-goal.md; docs/todo/README.md`

## Preflight Time Assessment

Assessment target: `Ready-to-Closed`

Assessment mode: `Rough range`

Rough elapsed-time estimate: `1-4 hours`

Basis or blocker: `2026-08-21 estimate for one local checkout/worktree, four focused test modules, three full unittest suites, deterministic validation, read-only installed/universal inspection, one independent Contract review, five bounded behavior scenarios, and at most a small repair/retest loop. Network or dependency bootstrap delays are included only when locally recoverable; prolonged GitHub/auth/tool outages are excluded.`

Critical-path time-cost distribution: `Not required: rough range recorded.`

## Task Temporary Cache / Housekeeping

Close housekeeping policy: `Disabled`

Housekeeping decision source: `2026-08-21 validation-plan conversion: the user authorized validation and PR-branch writes but did not authorize deletion of temporary worktrees or logs, so the safe frozen policy is preserve-and-report.`

Task temporary cache root strategy: `Disabled cleanup: macOS validation may allocate goal-owned directories beneath the host-resolved temporary root for an isolated worktree, logs, support-sync targets, and fixtures. Record every resolved owner root before first use. Close preserves them and reports their exact paths unless a later explicit user request authorizes cleanup.`

Recorded task temporary cache roots: `Resolve and record before first use.`

Housekeeping boundary: `No Close cleanup. Never delete the shared temporary root. Never infer cleanup authorization from test completion, YOLO scope, or generic cleanup wording.`

## M0 Execution Baseline

M0 design-freeze baseline:

1. Parent semantic authority is `docs/todo/skill-slimming-plan.md`; S0-S4 source implementation is complete there, with validation/merge/archive still pending.
2. PR #13 is `Complete skill interface slimming plan (S0-S4)`, head branch `agent/skill-slimming-s0-s1`, targeting `main`; the branch head must be re-read at execution start because this goal commit itself advances the PR.
3. The pre-goal S0-S4 implementation head was `ff2474249470ad2787bbc08c0b178d87efc671d0`; this SHA is historical orientation only, not the execution authority.
4. The expected PR file scope is the existing 19-file S0-S4 candidate plus this goal file. `docs/todo/README.md` was already inside the PR scope before this goal was added.
5. Root `AGENTS.md`, PR #3 skill bodies, Matt Pocock mirror content, Watcher attribution overlays, universal discovery state, hooks, plugin cache, and installed copies are frozen unless a failing gate proves a narrowly scoped source correction is necessary and still within this goal.
6. PR #13 must remain Draft until full-checkout validation, independent Contract review, behavioral sampling, and any repair/retest loop pass.

Current source-of-truth evidence to read:

1. `AGENTS.md`, `docs/todo/README.md`, `docs/todo/skill-slimming-plan.md`, and this goal.
2. PR #13 metadata/diff and `origin/main...origin/agent/skill-slimming-s0-s1`.
3. `plugins/workflow/skills/orchestrate-subagents/**`, `plugins/watcher/skills/doc-alignment/**`, `plugins/workflow/skills/long-running-goal/**`, and their changed tests.
4. `scripts/sync_codex_agents.py`, Watcher CLI/README, ADR-0004, repository skill catalog/discovery tooling, and current installed/universal read-only state.

## Loop Blueprint / Harness Boundary

Execution mode: `Manual staged execution`

1. Trigger / heartbeat:
   - Start or resume only from an explicit user instruction to execute/continue this validation goal.
   - Re-read the newest request before each resume; same-goal evidence/status requests do not change scope.
2. Inputs / sources:
   - This goal, the parent slimming plan, root instructions, live Git state, PR #13 metadata/diff, test output, validator output, installed-state read-only inventory, and review/behavior evidence.
3. Triage and orchestration:
   - Execute milestones serially. A failing gate becomes a bounded diagnosis/fix task inside the current milestone or M5. Do not broaden slimming design during validation.
4. Worktree and isolation:
   - Use the current checkout only when clean. If user work is dirty, create a detached temporary worktree at the PR head; do not stash, reset, clean, or overwrite user work.
5. Skills and context:
   - Use `long-running-goal` for lifecycle execution, `diagnosing-bugs` for failing commands/tests, and `code-review` for the final Contract review. Do not invoke `$orchestrate-subagents` unless the user explicitly requests that workflow; broad read-only review may use a read-only reviewer under root `AGENTS.md` authority.
6. Connector read/write boundaries:
   - Pre-approved GitHub reads: PR, branch, diff, comments, reviews, and checks.
   - Pre-approved GitHub writes: commits/pushes to `agent/skill-slimming-s0-s1`, PR #13 body/comments, and Draft-to-Ready transition after all gates pass.
   - Not authorized: merging PR #13, writing to `main`, deleting branches, changing unrelated issues/PRs, or modifying installed runtime state.
7. Independent verification:
   - Final Ready requires a read-only reviewer independent from the implementation pass: a read-only subagent or a separate fresh Codex review session. A same-agent second pass may aid diagnosis but does not satisfy the final independence gate.
8. Runtime hard stops:
   - Required GitHub/auth/source access is unavailable and cannot be restored locally.
   - Three distinct in-scope diagnostic/fix approaches fail with no safe next step.
   - Independent review cannot be obtained.
   - The next fix would modify frozen installed/runtime state, identity semantics, universalization architecture, PR #3 skill bodies, or unrelated user work.
   - Evidence contradicts the S0-S4 frozen semantic oracle and continuing would require redesign rather than validation.
   - The next requested action is PR merge or another unapproved external/destructive write.
9. Durable learning:
   - Write milestone state, exact commands, pass/fail evidence, fixes, review verdict, behavior sampling, installed-state classification, and residual risk into this goal. Update the parent plan only when final validation changes its status/evidence, not to duplicate milestone detail.

## Pre-Approval / YOLO Boundary

1. Pre-approved YOLO local operations:
   - Git inspection/fetch; clean branch switch or detached temporary worktree creation; read-only source/runtime inventories; local dependency/tooling bootstrap through repository-owned tooling; focused/full tests; Python compilation; link/static checks; temporary fixtures; temporary support-sync targets; current validators; read-only Watcher doctor; bounded source/test/doc fixes inside PR #13; local commits; and revalidation.
2. Pre-approved external reads/writes:
   - GitHub reads for repository/PR/check/review state; pushes to the PR #13 branch; PR #13 comments/body updates; mark PR #13 Ready after every gate passes.
3. Runtime hard stops:
   - The hard stops listed in the Loop Blueprint, including merge, installed-state mutation, missing independent review, scope-changing semantic conflict, and repeated technical impossibility.
4. Non-stops:
   - Milestone transitions, expected test failures with an in-scope diagnosis, local dependency bootstrap, a temporary worktree, source-only fixes, repeated affected tests, timing rebaseline, documentation evidence updates, and PR comments that record validation progress.

## Goal Execution Contract

1. Execute strictly `M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> Close`.
2. Set the active milestone `In Progress` before doing its work and update the status table after each gate.
3. Record exact commands and evidence; distinguish source regression, test-oracle drift, environment dependency, installed-state drift, and runtime behavior evidence.
4. Use the smallest falsifying check first; after a fix, rerun affected focused checks before full suites.
5. Never hide a failed command with fallback success. If an alternate command is used because the documented CLI changed, record the original failure and why the replacement is semantically equivalent.
6. Stage only confirmed paths with `git add -- path...`; never use broad staging.
7. No milestone boundary or ordinary failing test is a permission prompt when a safe in-scope next step exists.
8. Only the frozen runtime hard stops may pause execution for the user.
9. Do not refresh or mutate `~/.agents/skills`, `$CODEX_HOME/agents`, Codex config, hooks, plugin cache, marketplace state, or Watcher runtime state during this goal.
10. A read-only installed-state check may fail because PR #13 is not activated; classify that separately from source validation.
11. M5 may be `Done / not needed` when no source repair is required, but it still needs review/checkpoint evidence stating that result.
12. Close archives this validation goal only after M0-M6 are Done. The parent slimming plan remains active until PR #13 is later merged and its own archive gate is satisfied.

## Status Definitions

| Status | Meaning |
| --- | --- |
| `Not Started` | Milestone contract is frozen but no execution evidence exists. |
| `In Progress` | This is the current validation milestone. |
| `Blocked` | A frozen runtime hard stop prevents safe progress. |
| `Done` | Scope, validation/review evidence, and checkpoint are complete. |

## Milestone Status

| Milestone | Status | Review | Checkpoint |
| --- | --- | --- | --- |
| M0 Live State and Isolation | Not Started | Pending | Pending |
| M1 Diff Scope and Frozen Surface Audit | Not Started | Pending | Pending |
| M2 Test Matrix and Source Validation | Not Started | Pending | Pending |
| M3 Deterministic, Installed-State, and Resource Audit | Not Started | Pending | Pending |
| M4 Independent Contract Review and Behavioral Sampling | Not Started | Pending | Pending |
| M5 Bounded Repair and Revalidation | Not Started | Pending | Pending |
| M6 PR Ready Handoff | Not Started | Pending | Pending |
| Close Validation Goal Archive | Not Started | Pending | Pending |

## M0 Live State and Isolation

Status: `Not Started`

Objective: Establish the exact macOS checkout, PR head, dirty-work boundary, Python/tooling baseline, and task-owned temporary roots before validation.

Commands:

```bash
REPO="${MY_CODEX_ROOT:-$HOME/.codex/my-codex}"
cd "$REPO"
pwd -P
python3 - <<'PY'
from pathlib import Path
print(Path('.').resolve())
PY
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short
git status --branch --short
git remote -v
git log --oneline --decorate -12
git fetch origin
git rev-parse origin/main
git rev-parse origin/agent/skill-slimming-s0-s1
```

Isolation rule:

- If the worktree is clean, switch/fast-forward to `agent/skill-slimming-s0-s1`.
- If any user work is dirty, create a detached `mktemp` worktree at `origin/agent/skill-slimming-s0-s1`; record the resolved worktree root before use and leave the original checkout untouched.
- Record any log/support/fixture temporary roots before first use; Close preserves them.

Select Python:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
TOOL_PY="$CODEX_HOME/venvs/my-codex/bin/python"
if [ -x "$TOOL_PY" ]; then PY="$TOOL_PY"; else PY="$(command -v python3)"; fi
"$PY" --version
```

Review gate: exact validation root, branch/HEAD, upstream refs, dirty-state isolation, Python, and temporary-root policy are recorded without mutating user work.

Checkpoint evidence: `Goal update containing the resolved checkout/worktree, HEAD, Python version, and recorded task-temporary roots; no empty commit required.`

Rollback: `Remove no user work. If a temporary worktree is unusable, create a new one and preserve/report the old root under the Disabled cleanup policy.`

Hard stop: `Required repo/auth access cannot be restored locally or safe worktree isolation is impossible.`

## M1 Diff Scope and Frozen Surface Audit

Status: `Not Started`

Objective: Prove PR #13 contains only the S0-S4 candidate plus this validation goal, and prove frozen surfaces remain unchanged.

Expected PR paths after this goal commit: 20 unique changed files. Confirm with Git/GitHub rather than trusting the count.

Commands:

```bash
git log --oneline origin/main..HEAD
git diff --stat origin/main...HEAD
git diff --name-status origin/main...HEAD
git diff --check origin/main...HEAD
```

Expected path set:

```text
agents/operating-principles.md
docs/todo/README.md
docs/todo/archive/README.md
docs/todo/archive/skill-slimming-batch-1-validation.md
docs/todo/archive/skill-slimming-v2-review.md
docs/todo/skill-slimming-macos-validation-goal.md
docs/todo/skill-slimming-plan.md
docs/todo/subagent-orchestration-follow-up.md
plugins/workflow/README.md
plugins/workflow/skills/long-running-goal/SKILL.md
plugins/workflow/skills/long-running-goal/agents/openai.yaml
plugins/workflow/skills/orchestrate-subagents/SKILL.md
plugins/workflow/skills/orchestrate-subagents/references/subagent-recipes.md
plugins/workflow/tests/test_instruction_ownership.py
plugins/workflow/tests/test_invocation_contract.py
plugins/workflow/tests/test_long_running_goal_disclosure.py
plugins/watcher/skills/doc-alignment/SKILL.md
plugins/watcher/skills/doc-alignment/references/alignment-reference.md
plugins/watcher/skills/doc-alignment/references/watcher-audit.md
plugins/watcher/tests/test_doc_alignment_disclosure.py
```

Frozen-surface check:

```bash
git diff --exit-code origin/main...HEAD -- \
  AGENTS.md \
  plugins/workflow/.codex-plugin/skill-watcher.json \
  plugins/watcher/.codex-plugin/skill-watcher.json \
  plugins/workflow/skills/summary-in-html/SKILL.md \
  plugins/workflow/skills/sop/SKILL.md \
  plugins/workflow/skills/prompt-strategy-loop/SKILL.md \
  plugins/watcher/skills/housekeeping/SKILL.md \
  plugins/watcher/skills/skill-compressor/SKILL.md \
  plugins/watcher/skills/skill-maintainer/SKILL.md \
  plugins/mattpocock-skills/skills
```

Review gate: exact diff scope is classified, frozen surfaces have no PR diff, and no unexpected file is silently accepted.

Checkpoint evidence: `Recorded path-set comparison, frozen-surface diff result, and any classified discrepancy.`

Rollback: `No mutation required. Unexpected PR paths remain a blocker until removed or explicitly re-scoped by the user.`

Hard stop: `A changed path requires identity/runtime/universalization/PR #3 redesign rather than validation.`

## M2 Test Matrix and Source Validation

Status: `Not Started`

Objective: Run the smallest semantic falsifiers first, then all current repository suites, without skipping a suite after another fails.

Focused tests:

```bash
"$PY" -m unittest -v \
  plugins.workflow.tests.test_invocation_contract \
  plugins.workflow.tests.test_instruction_ownership \
  plugins.workflow.tests.test_long_running_goal_disclosure \
  plugins.watcher.tests.test_doc_alignment_disclosure
```

Full suites:

```bash
LOG_ROOT="$(mktemp -d "${TMPDIR%/}/my-codex-pr13-logs.XXXXXX")"
printf '%s\n' "$LOG_ROOT"

"$PY" -m unittest discover -s tests -p 'test_*.py' -v \
  2>&1 | tee "$LOG_ROOT/root-tests.log"
"$PY" -m unittest discover -s plugins/workflow/tests -p 'test_*.py' -v \
  2>&1 | tee "$LOG_ROOT/workflow-tests.log"
"$PY" -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v \
  2>&1 | tee "$LOG_ROOT/watcher-tests.log"
```

Compile changed tests and run static diff validation:

```bash
"$PY" -m py_compile \
  plugins/workflow/tests/test_instruction_ownership.py \
  plugins/workflow/tests/test_invocation_contract.py \
  plugins/workflow/tests/test_long_running_goal_disclosure.py \
  plugins/watcher/tests/test_doc_alignment_disclosure.py

git diff --check origin/main...HEAD
```

Failure classification for every failure: `source regression`, `test oracle drift`, `environment/dependency failure`, or `unknown pending diagnosis`.

Review gate: all focused and full suites either pass or have a proven in-scope repair queued for M5; no suite was skipped because another failed.

Checkpoint evidence: `Exact test counts/results, log root, failures with classifications, and Python/tool versions.`

Rollback: `Tests are non-mutating outside recorded temporary artifacts. Dependency/tooling bootstrap must use repository-owned tooling and remain outside installed skill/runtime activation.`

Hard stop: `A required suite cannot run after three distinct local environment/diagnostic approaches, or fixing it would require scope expansion.`

## M3 Deterministic, Installed-State, and Resource Audit

Status: `Not Started`

Objective: Validate deterministic owners and universal resource resolution while keeping installed/runtime state read-only.

Markdown/link checks:

```bash
"$PY" plugins/workflow/skills/long-running-goal/scripts/check_md_links.py docs/todo
"$PY" plugins/workflow/skills/long-running-goal/scripts/check_md_links.py plugins/workflow/skills
"$PY" plugins/workflow/skills/long-running-goal/scripts/check_md_links.py plugins/watcher/skills
```

If the current CLI differs, inspect `--help`/source, record the original failure, and run the semantically equivalent scoped check.

Support-note source contract using a temporary target:

```bash
SUPPORT_TARGET="$(mktemp -d "${TMPDIR%/}/my-codex-agent-support.XXXXXX")"
printf '%s\n' "$SUPPORT_TARGET"
"$PY" scripts/sync_codex_agents.py --target-root "$SUPPORT_TARGET" --dry-run --prune
"$PY" scripts/sync_codex_agents.py --target-root "$SUPPORT_TARGET" --prune
"$PY" scripts/sync_codex_agents.py --target-root "$SUPPORT_TARGET" --check --prune
```

Read-only installed check is allowed:

```bash
"$PY" scripts/sync_codex_agents.py --check --prune
```

Classify expected installed drift separately; do not apply it.

Watcher/plugin/skill validation:

1. Inspect current Watcher doctor and validator `--help` before running them.
2. Run the supported read-only Watcher skill doctor using the actual repo-root contract.
3. Locate and run current plugin/skill validators for Workflow, Watcher, `orchestrate-subagents`, `doc-alignment`, and `long-running-goal` when available.
4. Missing validator/dependency is an explicit environment result, not a fabricated pass.

Universal symlink audit:

```bash
"$PY" - <<'PY'
from pathlib import Path
root = Path.home() / '.agents' / 'skills'
for name in ('orchestrate-subagents', 'doc-alignment', 'long-running-goal'):
    path = root / name
    print(name)
    print('  exists=', path.exists())
    print('  symlink=', path.is_symlink())
    if path.is_symlink():
        print('  target=', path.resolve(strict=False))
        print('  skill=', (path / 'SKILL.md').resolve(strict=False))
        print('  metadata=', (path / 'agents' / 'openai.yaml').resolve(strict=False))
PY
```

Review gate: deterministic checks pass or exact environment limitations are recorded; universal links/resources are non-dangling; no command changed installed state.

Checkpoint evidence: `Link/static/validator/doctor outputs, support temporary target, installed-state classification, and symlink/resource inventory.`

Rollback: `Not applicable to read-only installed/runtime checks. Temporary source-validation targets are preserved under the Disabled cleanup policy.`

Hard stop: `A validator proves an identity/runtime contract regression, or a required validation can only proceed by mutating installed/runtime state.`

## M4 Independent Contract Review and Behavioral Sampling

Status: `Not Started`

Objective: Obtain an independent read-only Contract verdict and sample user-visible behavior from a session that is proven to load the candidate when runtime sampling is possible.

Independent review requirement:

- Prefer one read-only `default` or `explorer` reviewer under root broad-review authority; do not invoke `$orchestrate-subagents` unless the user explicitly asks for it.
- A separate fresh Codex review session is also acceptable.
- The reviewer reads only `origin/main...HEAD` plus the frozen parent plan and reports `Blocking findings`, `Non-blocking findings`, `Evidence paths`, `Residual risk`, and `Verdict`.
- A same-agent second pass does not satisfy this final gate.

Review checklist:

1. No callable/qualified/Watcher/alias/distribution identity drift.
2. Broad read-only review does not cross-invoke orchestration.
3. Workers still require exact disjoint writes; parent integration remains authoritative.
4. Subagent blocked/timeout/missing-context/overlap/conflict/incomplete/missing-evidence results remain visible.
5. `doc-alignment` report-only and scheduled modes remain non-mutating.
6. Watcher profile-set, `owner-command`, `authority_paths`, change-alignment, due/skip, and existing-report routing remain reachable.
7. `long-running-goal` preserves Ready/Draft, exact planning fallback, no parallel planning tree, supersession, all branch routes, three-attempt hard stop, temp housekeeping, explicit native goal-tool trigger, token-budget-on-request, checkpoint, and close.
8. No unique semantic owner was removed and no multi-level reference chain was introduced.
9. Frozen surfaces remain unchanged.

Behavior sampling prerequisite: prove `~/.agents/skills` for the changed skills resolves to the candidate checkout loaded by a fresh Codex session. If not, do not relink; mark runtime behavior sampling pending and treat it as a Ready blocker unless an equivalent isolated candidate session can be established without installed-state mutation.

Behavior scenarios:

A. Broad read-only review stays read-only and does not invoke orchestration.

B. Explicit subagent request creates the minimum useful bounded assignments, waits, and parent-integrates.

C. `doc-alignment` report-only on a temporary Git fixture leaves `git status`/`git diff` unchanged.

D. `long-running-goal` create + supersession uses the existing planning area/canonical fallback, makes the correct Draft/Ready decision, and does not advance stale milestone work after an unrelated bounded next request.

E. A recoverable local failure inside a temporary goal continues with a clear in-scope next diagnostic instead of producing a false hard stop.

For each scenario record: `trigger correctness`, `unexpected questions`, `false stops`, `governance-only steps`, `references loaded`, `validation`, and `result`.

Review gate: independent verdict has no blocker and all five behavior scenarios pass in a proven candidate-loaded context.

Checkpoint evidence: `Reviewer identity/session boundary, review report, candidate-load proof, and behavior matrix results.`

Rollback: `Behavior fixtures are temporary and preserved; no installed-state mutation is allowed.`

Hard stop: `No independent reviewer or no safe candidate-loaded runtime context is available.`

## M5 Bounded Repair and Revalidation

Status: `Not Started`

Objective: Repair only failures proven to be introduced by PR #13, then rerun the affected and aggregate gates.

Repair rules:

1. Prove root cause first.
2. Prefer existing PR paths; add a new file only when it is the narrowest owner for a missing reference/test.
3. Do not change frozen identities, universalization architecture, PR #3 skill bodies, installed state, or unrelated source.
4. Preserve existing five semantic commits; add bounded repair commits rather than rewriting history unless the user explicitly requests a rebase/squash.
5. Stage only confirmed paths with `git add -- path...`.
6. After each repair, rerun its focused falsifier; after all repairs, rerun M2-M4 gates affected by the change.

When no repair is required, record `M5: Done / not needed` with evidence that M1-M4 passed unchanged.

Review gate: no unresolved PR-introduced regression; all affected focused/full/validator/review/behavior gates pass after the final source state.

Checkpoint evidence: `Repair commits and rerun logs, or explicit no-repair-needed evidence.`

Rollback: `Revert the bounded repair commit(s) if they worsen the oracle; do not rebaseline tests to accept a regression.`

Hard stop: `A required fix changes frozen semantics or remains technically unresolved after three distinct approaches.`

## M6 PR Ready Handoff

Status: `Not Started`

Objective: Make the PR branch self-describing and prove it is ready for human merge decision without merging it.

Actions:

1. Re-fetch `origin/main` and PR #13 head; ensure the candidate is not behind in a way that invalidates validation evidence.
2. Update this goal with final command results, exact HEAD, Python/tool versions, reviewer verdict, behavior matrix, installed-state classification, repairs, residual risk, and temporary roots.
3. Update the parent `docs/todo/skill-slimming-plan.md` only with concise validation/handoff status; do not duplicate this goal's logs.
4. Commit only confirmed validation/evidence paths and push to `agent/skill-slimming-s0-s1`.
5. Re-run the smallest checks affected by evidence/doc updates, including `git diff --check` and planning/TODO link/index checks.
6. Update PR #13 body or add a concise validation comment with the final evidence and residual risk.
7. Keep the PR Draft until Close archives this validation goal and pushes the final index state.

Review gate: the pushed PR head contains all validation evidence, no new code regression, no unresolved blocker, and the only remaining action is the user's merge decision.

Checkpoint evidence: `Final pre-Close PR head SHA, pushed validation/evidence commit(s), PR comment/body update, and all gates green.`

Rollback: `If evidence updates break a planning/index check, fix the docs before Close. Do not merge or modify main.`

Hard stop: `PR head moved unexpectedly, main changed incompatibly, push/PR-write auth is unavailable, or a new blocker appears.`

## Close Validation Goal Archive

Status: `Not Started`

Close prerequisites:

1. M0-M6 are `Done`, `Review=Passed`, and `Checkpoint=Done`.
2. Focused/full suites, deterministic validators, independent Contract review, and all five behavior scenarios pass on the final source state.
3. No installed/runtime state was mutated.
4. Parent slimming plan remains active and records that validation is complete but merge/archive of the parent is still pending.
5. PR #13 is still Draft before the Close commit.

Close actions:

1. Mark this goal `Closed` and record the final validated PR head before archival.
2. Move this file to `docs/todo/archive/skill-slimming-macos-validation-goal.md`.
3. Remove its active Long-Running Goal entry from `docs/todo/README.md` and add an archive entry.
4. Preserve/report every recorded temporary worktree/log/support/fixture root; do not delete them because Close housekeeping is Disabled.
5. Commit and push the archive/index update to `agent/skill-slimming-s0-s1`.
6. Re-run planning/TODO link/index checks and `git diff --check` on the final pushed head.
7. Update PR #13 with the final validation summary and mark it Ready for review.
8. Do not merge PR #13.

Final validation:

```bash
"$PY" -m unittest -v \
  plugins.workflow.tests.test_invocation_contract \
  plugins.workflow.tests.test_instruction_ownership \
  plugins.workflow.tests.test_long_running_goal_disclosure \
  plugins.watcher.tests.test_doc_alignment_disclosure

git diff --check origin/main...HEAD
"$PY" plugins/workflow/skills/long-running-goal/scripts/check_md_links.py docs/todo
```

Also run the applicable TODO-index checker using its current `--help` contract after the goal is moved to archive.

Close checkpoint evidence: `Archived goal path, final pushed head SHA, final planning/index checks, PR #13 Ready state, final validation comment, and preserved temporary-root inventory.`

Close rollback: `If the archive/index commit fails validation, restore the active goal/index state on the same branch and keep PR #13 Draft until corrected.`

## Acceptance Oracle

The goal is Closed only when all of the following are true:

- PR #13 scope is exact and frozen surfaces are unchanged.
- Focused, root, Workflow, and Watcher tests pass on macOS.
- Current deterministic validators and link/static checks pass or a missing external validator is explicitly non-required and documented by its owner.
- Installed-state drift, if any, is classified without applying it.
- Universal skill links/resources are non-dangling and candidate runtime sampling uses a proven candidate-loaded session.
- Independent read-only Contract review passes.
- All five behavior scenarios pass without routing, mutation, false-stop, or identity regression.
- Any PR-introduced failure was fixed minimally and fully revalidated.
- The final PR branch contains durable validation evidence.
- This validation goal is archived, temporary roots are preserved/reported, and PR #13 is Ready but not merged.

## Recommended Continuation Prompt

```text
Execute the active long-running goal at docs/todo/skill-slimming-macos-validation-goal.md.

Read the newest user request first, then root AGENTS.md, docs/todo/skill-slimming-plan.md, the goal file, current PR #13 metadata, and the live local Git state. Do not rely on chat history or historical SHAs as execution authority.

Resume only the first non-Done milestone and execute the goal continuously inside its frozen YOLO scope. Preserve unrelated dirty work by using the goal's worktree isolation rule. Distinguish source regressions, test-oracle drift, environment failures, installed-state drift, and runtime behavior evidence. Diagnose and fix ordinary in-scope failures without pausing; stop only at the recorded runtime hard stops.

Do not mutate installed skills/config/hooks/cache/runtime state, do not modify frozen PR #3 or identity surfaces, and do not merge PR #13. Push only bounded PR #13 fixes/evidence, obtain an independent read-only Contract review, complete the behavior matrix in a proven candidate-loaded context, archive this validation goal on Close, then mark PR #13 Ready when every gate passes.
```
