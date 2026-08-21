# Skill Slimming macOS Validation Long-Running Goal

Overall status: `Ready`

Updated: 2026-08-21

This goal owns macOS validation and evidence handoff for PR #13. The local repository is expected to begin on `main`; `main` is the protected comparison baseline, while the actual PR head is discovered from GitHub and validated in an isolated worktree. The goal may push bounded fixes and validation evidence to the PR branch and publish the final report to PR #13. It must leave the PR Draft and unmerged so the user can make the final decision in the originating ChatGPT conversation.

## Goal Summary

Goal Name: `Skill Slimming macOS Validation`

Goal Description:

1. Validate the complete S0-S4 PR #13 candidate in a real macOS checkout with focused, root, Workflow, and Watcher tests plus current deterministic validators.
2. Prove the frozen routing, read-only, identity, delegation, long-running-goal, universal-resource, and installed-state boundaries with independent review and behavioral sampling.
3. Fix only proven PR #13 regressions, push fixes and durable evidence to the actual PR branch, publish a complete final report on PR #13, and stop without marking Ready or merging.

Goal Status: `Ready`

Goal Owner: `my-codex repository maintainer / executing local Codex agent`

Goal Path: `docs/todo/skill-slimming-macos-validation-goal.md`

Planning root: `docs/todo`

Goal directory: `docs/todo`

Continuation contract: Read the newest user request, root `AGENTS.md`, `docs/todo/skill-slimming-plan.md`, this goal, live local Git state, and current PR #13 metadata before acting. Start from the first non-Done milestone. Treat local `main` as the protected entry checkout and current `origin/main` as the comparison baseline; discover the actual PR base branch, head branch, and head SHA instead of trusting historical values. Validate the PR head in an isolated worktree. Preserve unrelated dirty work, frozen S0-S4 semantics, PR #3 skill bodies, universal discovery state, and installed runtime state. Push only bounded PR fixes/evidence, publish the final report to PR #13, keep the PR Draft, and stop for the user's merge decision.

Planning preflight marker: `preflight:skill-slimming-macos-validation:20260821-mac2`

Planning preflight status: `Done`

Preflight source: `2026-08-21 review of PR #13, the parent slimming plan, root instructions, current validation surfaces, and the user's corrected main-to-PR interaction contract`

Resolved decisions: `Execution begins from the live local repository, normally on main; main is never used as the repair branch; the real PR base/head are fetched before validation; validation uses a detached or dedicated worktree at the actual PR head; bounded fixes and evidence are pushed to that PR branch; the final complete report is published to PR #13; the PR remains Draft and unmerged; final Ready/merge/archive decisions return to the originating ChatGPT conversation.`

Open decisions: `The user will decide after reading the PR final report whether PR #13 should be repaired further, marked Ready, merged, or closed. That decision is outside M0-M6 and is the only planned post-validation interaction gate.`

Docs written: `docs/todo/skill-slimming-plan.md; docs/todo/skill-slimming-macos-validation-goal.md; docs/todo/README.md`

## Preflight Time Assessment

Assessment target: `Ready-to-Closed`

Assessment mode: `Rough range`

Rough elapsed-time estimate: `1-4 hours`

Basis or blocker: `2026-08-21 estimate for live branch/PR discovery, an isolated worktree, focused and full test suites, deterministic validation, read-only installation/resource inspection, independent Contract review, five behavioral scenarios, bounded repair/retest, durable evidence push, and a final PR report. Prolonged authentication, network, unavailable reviewer, or candidate-runtime setup failures are excluded.`

Critical-path time-cost distribution: `Not required: rough range recorded.`

## Task Temporary Cache / Housekeeping

Close housekeeping policy: `Disabled`

Housekeeping decision source: `2026-08-21 user authorized validation and PR-branch writes but did not authorize deletion of temporary worktrees, logs, support targets, or fixtures.`

Task temporary cache root strategy: `Allocate goal-owned worktree, log, support-sync, and fixture roots beneath the macOS-resolved temporary root; record each resolved path before first use and preserve it for the final report.`

Recorded task temporary cache roots: `Resolve and record before first use.`

Housekeeping boundary: `Do not delete temporary roots during this goal. Never delete the shared temporary root. Report preserved paths in the PR final report and user-facing result.`

## M0 Execution Baseline

M0 design-freeze baseline:

1. `docs/todo/skill-slimming-plan.md` is the S0-S4 design and semantic authority.
2. The local entry checkout is expected to be `main`, but live branch, HEAD, upstream, and dirty state must be measured rather than assumed.
3. PR #13 targets `main`, but its current base branch, head branch, head SHA, Draft state, and mergeability must be fetched at execution time.
4. Validation and repair must not occur directly on local `main`; use an isolated worktree created from the actual PR head.
5. PR #13 must receive all bounded fixes, validation evidence, and the final report.
6. PR #13 remains Draft and unmerged after M6, regardless of PASS/BLOCKED outcome.
7. Root `AGENTS.md`, PR #3 skill bodies, Matt Pocock mirror content, Watcher attribution overlays, universal discovery state, hooks, plugin cache, and installed copies remain frozen unless a focused source failure proves a repair is both necessary and inside the existing PR contract.

Current source-of-truth evidence to read:

1. `AGENTS.md`, `docs/todo/README.md`, `docs/todo/skill-slimming-plan.md`, and this goal.
2. Current GitHub PR #13 metadata, changed-file inventory, comments/reviews/checks, and `origin/main...<actual-pr-head>`.
3. Changed `orchestrate-subagents`, `doc-alignment`, and `long-running-goal` sources/references/tests.
4. `scripts/sync_codex_agents.py`, Watcher CLI/README, ADR-0004, repository discovery tooling, and read-only installed/universal state.

## Loop Blueprint / Harness Boundary

Execution mode: `Manual staged execution`

1. Trigger / heartbeat:
   - Start or resume only from an explicit user request to execute or continue this goal.
   - Re-read the newest request before each resume; same-goal evidence/status requests do not change scope.
2. Inputs / sources:
   - This goal, the parent plan, root instructions, live local Git state, current PR #13 metadata/diff, test and validator output, installed-state inventory, independent review, and behavioral evidence.
3. Triage and orchestration:
   - Execute milestones serially. Classify every failure before repair. Keep fixes within PR #13's frozen semantics.
4. Worktree and isolation:
   - Inspect the local entry checkout without switching it away from `main`. Always create a detached or dedicated validation worktree from the actual PR head. Never stash, reset, clean, or overwrite unrelated user work.
5. Skills and context:
   - Use `long-running-goal` for lifecycle execution, `diagnosing-bugs` for failures, and `code-review` for final Contract review. Broad read-only review may use a read-only reviewer under root authorization; do not invoke `$orchestrate-subagents` unless explicitly requested.
6. Connector read/write boundaries:
   - Pre-approved reads: GitHub PR/branch/diff/comments/reviews/checks and local read-only runtime inventories.
   - Pre-approved writes: commits/pushes to the actual PR #13 head branch, PR #13 body/comment updates, and validation evidence in this branch.
   - Not authorized: modifying local or remote `main`, marking PR #13 Ready, enabling auto-merge, merging, closing the PR, deleting branches, or mutating installed/runtime state.
7. Independent verification:
   - Final PASS requires a read-only reviewer independent from the implementation pass: a read-only subagent or a separate fresh Codex review session. Same-agent review may support diagnosis but does not satisfy this gate.
8. Runtime hard stops:
   - Current PR base/head cannot be resolved or no longer represents the requested candidate.
   - GitHub/auth/source access cannot be restored locally.
   - Three distinct in-scope diagnostic/fix approaches fail with no safe next step.
   - Independent review or a safe candidate-loaded behavioral context cannot be obtained.
   - The next fix would alter frozen installed/runtime, identity, universalization, PR #3 skill, or unrelated-user-work boundaries.
   - The next action would mark Ready, merge, close, or otherwise make the final user decision.
9. Durable learning:
   - Write milestone evidence into this goal, concise status into the parent plan, bounded repairs into the PR branch, and a complete PASS/BLOCKED final report into PR #13.

## Pre-Approval / YOLO Boundary

1. Pre-approved YOLO local operations:
   - Git inspection/fetch; PR metadata discovery; temporary worktree creation; read-only source/runtime inventory; repository-owned tooling bootstrap; focused/full tests; compilation; link/static checks; temporary fixtures/support targets; current validators; read-only Watcher doctor; bounded source/test/doc repairs; commits, pushes, and revalidation.
2. Pre-approved external reads/writes:
   - GitHub reads; pushes to the actual PR #13 head branch; PR #13 body/comments containing validation progress and the final report.
3. Runtime hard stops:
   - The hard stops listed above, including unresolved PR identity, unavailable independent verification, installed/runtime mutation, scope-changing semantics, repeated technical impossibility, and any Ready/merge/close action.
4. Non-stops:
   - Milestone transitions, a local main entry branch, temporary worktree creation, expected failing tests with a clear diagnosis, source-only repairs, repeated tests, docs evidence updates, push, and PR report publication.

## Goal Execution Contract

1. Execute strictly `M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6`; do not execute `Close` without a later user decision.
2. Set the active milestone `In Progress` before work and update the status table after each gate.
3. Distinguish `source regression`, `test-oracle drift`, `environment/dependency failure`, `installed-state drift`, and `runtime behavior evidence`.
4. Use the smallest falsifying check first; after a fix, rerun affected focused checks before aggregate suites.
5. Never hide a failed command with fallback success. Record changed CLI contracts and why a replacement is equivalent.
6. Stage only explicit paths with `git add -- path...`; never use broad staging, reset, or clean.
7. Do not switch or modify the local main checkout for PR repair. Work only in the isolated PR worktree/branch.
8. Do not refresh or mutate `~/.agents/skills`, `$CODEX_HOME/agents`, Codex config, hooks, plugin cache, marketplace state, or Watcher runtime state.
9. Read-only installed drift is evidence, not permission to apply it.
10. M5 may be `Done / not needed` when no source repair is required.
11. M6 must push durable evidence and publish a complete final PR report for both PASS and BLOCKED outcomes.
12. After M6, keep PR #13 Draft and unmerged, preserve temporary roots, stop execution, and return the final decision to the user.

## Status Definitions

| Status | Meaning |
| --- | --- |
| `Not Started` | Milestone contract is frozen but no evidence exists. |
| `In Progress` | This is the current validation milestone. |
| `Blocked` | A recorded runtime hard stop prevents safe progress. |
| `Done` | Scope, review, validation, and checkpoint evidence are complete. |

## Milestone Status

| Milestone | Status | Review | Checkpoint |
| --- | --- | --- | --- |
| M0 Live Main/PR State and Isolation | Not Started | Pending | Pending |
| M1 Diff Scope and Frozen Surface Audit | Not Started | Pending | Pending |
| M2 Test Matrix and Source Validation | Not Started | Pending | Pending |
| M3 Deterministic, Installed-State, and Resource Audit | Not Started | Pending | Pending |
| M4 Independent Contract Review and Behavioral Sampling | Not Started | Pending | Pending |
| M5 Bounded Repair and Revalidation | Not Started | Pending | Pending |
| M6 PR Evidence and Final Report Handoff | Not Started | Pending | Pending |
| Close User Merge Decision and Post-Merge Archive | Not Started | Pending | Pending |

## M0 Live Main/PR State and Isolation

Status: `Not Started`

Objective: Measure the local main checkout and current PR #13 identity, then create an isolated validation worktree at the actual PR head.

Required evidence:

- resolved repository path;
- local starting branch, HEAD, upstream, and dirty state;
- current `origin/main` SHA;
- PR #13 number, state, Draft state, mergeability, base branch/SHA, head branch/SHA, and URL;
- whether the PR is behind current main and whether that affects validation;
- validation worktree path and exact checked-out SHA;
- Python/tooling version and recorded temporary roots.

Execution rules:

1. Fetch/prune origin and query GitHub/`gh pr view` for current PR metadata.
2. Do not trust historical SHAs or the historical head branch name when GitHub reports a different one.
3. Do not switch the local main checkout to the PR branch.
4. Create a detached/dedicated worktree from the actual PR head.
5. If the PR is behind main in a way that affects the changed skills/tests/contracts, update the PR branch safely from current main inside the isolated worktree, push, re-fetch PR metadata, and restart M0 evidence at the new head. Do not silently validate an obsolete merge base.

Review gate: local main remains unchanged, the actual PR identity is proven, and validation runs from an isolated worktree at the current PR head.

Checkpoint evidence: `Goal update with all live Git/PR/worktree/Python/temp-root facts; no empty commit required.`

Rollback: `Leave local main and user work untouched. Preserve/report unusable temporary roots and create a new worktree if needed.`

Hard stop: `PR identity cannot be resolved, the PR is no longer the requested candidate, required access is unavailable, or safe isolation is impossible.`

## M1 Diff Scope and Frozen Surface Audit

Status: `Not Started`

Objective: Prove the current PR diff contains only expected S0-S4, validation-goal, evidence, and bounded repair surfaces.

Actions:

1. Compare `origin/main...HEAD` after M0 has established the valid head.
2. Derive the changed-path set from Git/GitHub; do not hardcode a stale count.
3. Classify every path as `S0-S4 source/test/doc`, `validation evidence`, `bounded repair`, or `unexpected`.
4. Verify no PR diff in root `AGENTS.md`, Watcher overlays, PR #3 frozen skill bodies, Matt Pocock mirror, universal discovery/runtime, hooks, config, or cache surfaces.
5. Run `git diff --check origin/main...HEAD`.

Review gate: every changed path is expected and frozen surfaces have no PR diff.

Checkpoint evidence: `Changed-path inventory, classifications, frozen-surface result, and diff-check output.`

Rollback: `No mutation required. Remove or explicitly resolve unexpected scope before continuing.`

Hard stop: `An unexpected path requires identity/runtime/universalization/PR #3 redesign rather than bounded validation repair.`

## M2 Test Matrix and Source Validation

Status: `Not Started`

Objective: Run focused semantic falsifiers and all current root, Workflow, and Watcher suites without skipping later suites after an earlier failure.

Required focused tests:

```bash
"$PY" -m unittest -v \
  plugins.workflow.tests.test_invocation_contract \
  plugins.workflow.tests.test_instruction_ownership \
  plugins.workflow.tests.test_long_running_goal_disclosure \
  plugins.watcher.tests.test_doc_alignment_disclosure
```

Required aggregate suites:

```bash
"$PY" -m unittest discover -s tests -p 'test_*.py' -v
"$PY" -m unittest discover -s plugins/workflow/tests -p 'test_*.py' -v
"$PY" -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v
```

Also compile changed tests and run `git diff --check`. Save complete logs in a recorded goal-owned log root.

Review gate: every suite has an exact result; failures are classified and either pass after bounded repair or become an explicit blocker.

Checkpoint evidence: `Test counts/results, log paths, tool versions, and classified failures.`

Rollback: `Tests are non-mutating outside recorded temporary artifacts.`

Hard stop: `A required suite remains unavailable after three distinct local approaches or repair requires scope expansion.`

## M3 Deterministic, Installed-State, and Resource Audit

Status: `Not Started`

Objective: Validate deterministic owners and resource resolution without applying installed/runtime changes.

Required checks:

1. Markdown relative-link validation for `docs/todo`, Workflow skills, and Watcher skills using the current helper contract.
2. `sync_codex_agents.py` dry-run/apply/check against a temporary target.
3. Read-only `sync_codex_agents.py --check --prune` against the real installed support path; classify drift without applying.
4. Current read-only Watcher skill doctor.
5. Available plugin/skill validators for Workflow, Watcher, `orchestrate-subagents`, `doc-alignment`, and `long-running-goal` using their real `--help` contracts.
6. Read-only inventory of `~/.agents/skills/{orchestrate-subagents,doc-alignment,long-running-goal}`, symlink targets, `SKILL.md`, references, scripts/templates/assets, and `agents/openai.yaml`.

Review gate: deterministic source checks pass or exact non-source environment limits are recorded; no installed/runtime mutation occurred.

Checkpoint evidence: `Link, support-sync, doctor, validator, installed-drift, symlink/resource, and mutation-boundary results.`

Rollback: `Not applicable to read-only installed checks; preserve/report temporary targets.`

Hard stop: `A required check can proceed only by mutating installed/runtime state or proves a frozen identity/runtime contract regression.`

## M4 Independent Contract Review and Behavioral Sampling

Status: `Not Started`

Objective: Obtain an independent read-only Contract verdict and sample behavior from a context proven to load the PR candidate.

Independent review:

- Use a read-only subagent or separate fresh Codex review session.
- Review only current `origin/main...HEAD`, the parent plan, and frozen boundaries.
- Report `Blocking findings`, `Non-blocking findings`, `Evidence paths`, `Residual risk`, and `Verdict`.
- Same-agent review does not satisfy this final gate.

Required review semantics:

- identities and invocation modes unchanged;
- broad read-only review does not cross-invoke orchestration;
- exact disjoint worker writes and parent integration retained;
- blocked/timeout/missing-context/overlap/conflict/incomplete/missing-evidence results remain visible;
- `doc-alignment` report-only/scheduled behavior remains non-mutating;
- Watcher profile-set, `owner-command`, `authority_paths`, change-alignment, due/skip, and existing-report routing remain reachable;
- `long-running-goal` retains Ready/Draft, planning fallback/no parallel tree, supersession, all branch routes, three-attempt hard stop, temp housekeeping, explicit goal-tool trigger, token-budget-on-request, checkpoint, and close;
- no unique owner removed and no multi-level reference chain introduced.

Behavioral sampling requires proof that the test session loads the candidate without mutating real installed state. Run and record:

A. Broad read-only review without orchestration.

B. Explicit subagent request with minimum useful bounded assignments and parent integration.

C. `doc-alignment` report-only against a temporary Git fixture with no target diff.

D. `long-running-goal` creation and subsequent unrelated-request supersession.

E. Recoverable local failure that continues while an in-scope diagnostic exists.

For each scenario record trigger correctness, unexpected questions, false stops, governance-only work, references loaded, validation, and result.

Review gate: independent verdict has no blocker and A-E pass in a proven candidate-loaded context.

Checkpoint evidence: `Reviewer/session boundary, report, candidate-load proof, and behavioral matrix.`

Rollback: `Behavior fixtures remain temporary and preserved; no installed-state mutation.`

Hard stop: `No independent reviewer or no safe candidate-loaded context is available.`

## M5 Bounded Repair and Revalidation

Status: `Not Started`

Objective: Fix only PR #13 regressions proven by M1-M4, then rerun affected and aggregate gates.

Repair rules:

1. Prove root cause first.
2. Prefer existing PR paths; add a file only when it is the narrowest missing owner/test.
3. Preserve frozen identities, universalization, PR #3 skill bodies, installed state, and unrelated source.
4. Add bounded repair commits; do not rewrite history unless separately requested.
5. Stage only explicit paths.
6. Push repairs to the actual PR head branch and verify PR #13 reports the new SHA.
7. Rerun focused falsifiers, affected suites/validators/behavior, then all aggregate gates needed for the final state.

When no repair is required, record `M5: Done / not needed` with evidence.

Review gate: no unresolved PR-introduced regression remains on the final pushed head.

Checkpoint evidence: `Repair commits and rerun evidence, or explicit no-repair-needed evidence.`

Rollback: `Revert bounded repair commits that weaken the oracle; never rebaseline tests to accept a regression.`

Hard stop: `A necessary fix changes frozen semantics or remains unresolved after three distinct approaches.`

## M6 PR Evidence and Final Report Handoff

Status: `Not Started`

Objective: Make the PR branch and PR conversation contain everything needed for the user to decide whether to merge.

Actions:

1. Re-fetch `origin/main` and PR #13 metadata; confirm validation evidence still applies to the actual final PR head.
2. Update this goal with M0-M6 status, exact commands/results, final head, tools, reviewer verdict, behavior matrix, installed-state classification, repairs, residual risk, and preserved temporary roots.
3. Update `docs/todo/skill-slimming-plan.md` with only concise validation status and the fact that merge/archive awaits user decision.
4. Commit/push the final evidence to the actual PR branch and verify PR #13 head.
5. Re-run planning/link/diff checks affected by evidence updates.
6. Publish a PR #13 Conversation comment titled `## macOS validation final report` for both PASS and BLOCKED outcomes.
7. The report must include local starting branch, current main SHA, PR base/head, worktree, changed scope, frozen surfaces, all tests, deterministic validators, installed/resource audit, independent review, A-E behavior, repairs, mutation statement, preserved temporary roots, residual risk, and recommendation `READY FOR MERGE REVIEW` or `DO NOT MERGE`.
8. Update stale PR body validation claims when necessary, preserving useful history.
9. Explicitly state that installed/runtime mutation was `NONE` or accurately disclose any accidental mutation.
10. Keep PR #13 Draft. Do not mark Ready, enable auto-merge, merge, close, or archive this goal.
11. Stop and return the final result to the user for decision in the originating conversation.

Review gate: PR #13 contains the final pushed evidence and final report, the reported head matches GitHub, no unresolved result is hidden, and no final-decision action occurred.

Checkpoint evidence: `Final PR head SHA, evidence commit, PR report URL/comment ID, PASS/BLOCKED recommendation, and preserved root inventory.`

Rollback: `Correct inaccurate evidence/reporting on the PR branch; do not change main or merge.`

Hard stop: `PR head moves unexpectedly, main changes incompatibly, push/report authorization is unavailable, or a final Ready/merge/close decision is requested without fresh user instruction.`

## Close User Merge Decision and Post-Merge Archive

Status: `Not Started`

This section is intentionally not executed by the macOS validation run. After M6, the user reviews the PR final report in the originating ChatGPT conversation and decides whether to request further repair, mark Ready, merge, close, or defer.

Any Ready/merge/archive action requires a fresh explicit user instruction. Post-merge archival must verify the merged `main` revision before moving this goal and the parent slimming plan to the archive and updating TODO navigation.

Review gate: `Fresh user decision and, for archival, verified merged main.`

Checkpoint evidence: `Future user instruction and resulting PR/main/archive evidence.`

Rollback: `Keep PR Draft and both plans active when no decision is authorized.`

Hard stop: `No fresh user decision.`

## Acceptance Oracle For Validation Handoff

M6 is complete only when:

- the local entry checkout and current `main` remained unchanged;
- the actual PR base/head were discovered and the final head was validated in an isolated worktree;
- scope and frozen surfaces are proven;
- focused, root, Workflow, and Watcher suites have exact results;
- deterministic/link/support/doctor/validator checks have exact results;
- installed-state drift is classified without applying it;
- universal resources are audited read-only;
- independent Contract review is recorded;
- behavior scenarios A-E have exact results in a proven candidate-loaded context;
- repairs, if any, are pushed and revalidated;
- the final evidence is committed to the PR branch;
- PR #13 contains a complete final report and recommendation;
- installed/runtime mutation is explicitly stated;
- temporary roots are preserved and reported;
- PR #13 remains Draft and unmerged.

## Recommended Continuation Prompt

```text
Execute the active long-running goal at docs/todo/skill-slimming-macos-validation-goal.md from the live local my-codex repository. Follow its main-entry/isolated-PR-worktree contract, complete M0-M6 continuously, push bounded fixes and evidence to PR #13, publish the complete final report there, keep the PR Draft and unmerged, then stop for the user's decision.
```
