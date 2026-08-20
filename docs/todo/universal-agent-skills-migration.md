# Universal Agent Skills Migration Long-Running Goal

Overall status: `In Progress`

Updated: 2026-08-21

This file is the single active planning authority for completing the universal Agent Skills migration from M1 through M5 after the completed M0 contract freeze. The goal is `In Progress` at M3 after the explicit 2026-08-20 execution request and the merged M1 and M2 checkpoints. Work starts each milestone from current `main` and does not rely on chat history, a separate Phase 1b prompt, an archived prototype branch, or an unpublished patch.

## Goal Summary

Goal Name: `Universal Agent Skills Migration`

Goal Description:

1. Make the Git repository the only skill source authority and make `~/.agents/skills` the normal universal discovery projection.
2. Remove runtime dependence on the personal Codex marketplace/plugin cache while preserving an optional, mutually exclusive skills-bearing plugin distribution profile for compatibility and rollback.
3. Decouple Watcher metadata and shared runtime from marketplace authority and perform a controlled universal cutover on the current macOS environment without adding a zero-skill adapter.

Goal Status: `In Progress`

Goal Owner: `my-codex repository maintainer`

Goal Path: `docs/todo/universal-agent-skills-migration.md`

Planning root: `docs/todo`

Goal directory: `docs/todo`

Continuation contract: Read this file, root `AGENTS.md`, current `main`, the active milestone branch or PR, and the newest user request before acting. M0 through M2 are complete and M3 is the unique `In Progress` milestone after explicit execution authorization. Resume only the first non-Done milestone. Preserve callable skill identities, the frozen slimming baseline, user-owned installation state, and the single-active-discovery-path invariant. Do not depend on prior chat, deleted prompts, temporary branches, or unpublished artifacts.

Planning preflight marker: `preflight:universal-agent-skills:20260820-grill3`

Planning preflight status: `Done`

Preflight source: `grill-with-docs`

Planning preflight evidence: `grill-with-docs rounds 1-3 completed on 2026-08-20 after repository, runtime, GitHub, and domain-language audits. The decision frontier became empty, the complete shared understanding was presented, and the user explicitly confirmed it before this marker was recorded.`

Resolved decisions: `The one-off Phase 1b prompt and prototype were retired. The current Mac is the sole M5 cutover target. Bare SKILL.md frontmatter names are callable identities; namespaced forms remain Watcher or distribution identities. Discovery profile selection is an explicit required CLI argument. Universal mode uses repo-owned hooks without a zero-skill adapter and retains an inactive mutually exclusive skills-bearing plugin profile. M6 cleanup is a future independent goal. M3 freezes no physical move. Conditional Git/GitHub milestone writes are authorized. Task temporary cache policy is Not applicable. M5 may mutate only inventory-confirmed my-codex skills-bearing plugin state, repository-owned universal links, and the minimum my-codex marketplace, plugin, hook, and agent-support state required for the profile transition; unrelated or unmanaged state, Watcher durable state, and cleanup remain excluded. Cleanup eligibility remains at least five successful universal sessions across at least three working days. ADR-0003 records the discovery-authority trade-off. M5 uses an owner-only durable backup outside Watcher state, performs plugin-to-universal-to-plugin-to-final-universal comparison, validates each mode in a fresh non-interactive Codex CLI process without restarting Desktop, and retains the proven plugin rollback baseline until a separately Ready cleanup goal authorizes deletion.`

Open decisions: `None.`

Docs written: `docs/todo/universal-agent-skills-migration.md; docs/todo/universal-agent-skills-cleanup-follow-up.md; docs/todo/README.md; CONTEXT.md; docs/adr/0003-universal-skill-discovery-authority.md`

## Preflight Time Assessment

Assessment target: `current-milestone-to-Closed`

Assessment mode: `Rough range`

Rough elapsed-time estimate: `1-3 weeks`

Basis or blocker: `2026-08-20 initial-execution rebaseline remains 1-3 weeks from M1 to Closed, based on five serial implementation and cutover milestones, focused and full-suite validation, independent reviews, cross-platform wrapper checks, and conditional GitHub PR and review waits. The repository currently has no CI workflow, and the separately scoped cleanup observation window is excluded. The range assumes serial milestone execution on the current Mac and excludes prolonged credential, machine-access, or upstream-tool outages.`

Critical-path time-cost distribution: `Not required: rough range recorded.`

## Task Temporary Cache / Housekeeping

Close housekeeping policy: `Not applicable`

Housekeeping decision source: `User explicitly confirmed Not applicable during grill-with-docs round 1 on 2026-08-20.`

Task temporary cache root strategy: `Not applicable: no goal-owned task temporary cache roots will be created or used. Test-framework temporary directories remain self-cleaning and are not shared across goal steps.`

Recorded task temporary cache roots: `Not applicable`

Housekeeping boundary: `No task temporary cache roots are created or used. Close performs no task-temporary-cache cleanup. Plugin caches, tooling environments, backups, Watcher logs, reports, proposals, snapshots, and other runtime or durable evidence remain outside this policy.`

## Current Execution Baseline

M0 design-freeze baseline:

1. Current `main` contains the merged low-risk skill slimming baseline and the M0 planning-only contract recorded by revision `26934904c7e1bb586725f9dd4faec3677d5aabc0`; no universalization implementation source was admitted by the planning milestone.
2. No universalization runtime or source implementation has been accepted merely because an earlier prototype existed. M1 must implement and validate an internally complete batch from current `main`.
3. The one-off Phase 1b execution prompt and temporary prototype refs are not dependencies. Their durable requirements are integrated into M1 below.
4. The current physical authority remains `plugins/*/skills/*/SKILL.md`; no top-level skill relocation is approved.
5. The current Mac under `/Users/max` is the sole M5 production-cutover target. Its discovery, plugin config, plugin cache, hook, and Watcher runtime state must be re-inventoried immediately before M5 apply.
6. `main` is the only development baseline. Every milestone branch starts from the then-current `main` and is disposable after merge or closure.

Current source-of-truth evidence read:

1. `AGENTS.md`, root `README.md`, `docs/todo/README.md`, the merged slimming review and validation handoff, and current GitHub branch and PR state.
2. `plugins/workflow/skills/long-running-goal/SKILL.md`, its planning-preflight, checkpoint, execution, and production-cutover contracts.
3. `scripts/sync_agents_skills.py`, `scripts/refresh_my_codex.py`, `scripts/check_my_codex.py`, platform wrappers, marketplace and install manifests, plugin manifests, and Watcher metadata and runtime code.
4. Existing tests and persisted identity surfaces for callable skills, Watcher attribution, plugin distribution, hooks, and runtime state.

## Frozen Architecture Contract

### Authority model

| Surface | Target responsibility |
| --- | --- |
| Git `plugins/*/skills/**` | Sole canonical skill source authority |
| `SKILL.md` frontmatter `name` | Callable universal identity authority |
| `~/.agents/skills/**` | Managed universal discovery projection, never source or cache |
| `~/.codex/plugins/cache/**` | Optional skills-bearing plugin distribution cache only |
| `.agents/plugins/*.json` | Optional distribution metadata, never universal source catalog |
| `.codex-plugin/skill-watcher.json` or successor overlay | Non-callable Watcher attribution metadata only |
| `$CODEX_HOME/watcher/**` | Runtime state and evidence only |

### Identity contract

1. Bare `SKILL.md` frontmatter names such as `sop`, `doc-alignment`, and `long-running-goal` are the sole callable identities.
2. Watcher durable identities such as `workflow:sop` and `watcher:doc-alignment` remain unchanged but are attribution identities, not alternate callable identities.
3. Distribution identities such as `workflow@my-codex` remain separate from callable and Watcher identities.
4. Plugin-qualified invocation spelling is a distribution selector; a profile change may expose the same callable identity through a different selector without creating a second callable identity.
5. Directory changes never imply identity renames.
6. Any callable, Watcher, or distribution identity migration requires a separate consumer inventory, compatibility plan, explicit authorization, and independent review; it is outside this goal unless the goal is formally evolved.

### Discovery contract

1. One runtime has exactly one active skills discovery path for every canonical skill.
2. Universal and skills-bearing plugin profiles are mutually exclusive.
3. No fallback, dual-read, dual-write, compatibility shim, or second hand-maintained skill catalog may hide an incomplete transition.
4. Universal mode installs no zero-skill adapter; repo-owned scripts continue to manage Codex hooks and agent-support files directly.
5. An unmanaged same-name entry fails closed; repository tooling never overwrites another source.
6. The canonical universal catalog must be derived from repository `SKILL.md` files and directory structure, not marketplace metadata.

### Frozen baseline and non-goals

- Preserve the current slimming result; do not reopen wording or token optimization.
- Do not edit Matt Pocock mirror skill content outside its updater-owned workflow.
- Do not move skills merely for directory aesthetics.
- Do not migrate invocation identities as part of path changes.
- Do not make Watcher logs, reports, proposals, or plugin cache a source authority.
- Do not perform real installation-state mutation before M5 authorization.
- Do not create a zero-skill adapter in this goal.
- Do not delete obsolete plugin, marketplace, cache, config, hook-backup, or Watcher runtime paths in this goal; a later cleanup goal owns that decision after M5 stability evidence exists.
- Do not retain a temporary implementation branch as a hidden source of truth.

## Loop Blueprint / Harness

Execution mode: `Manual staged execution`

Harness applicability: `Not applicable: manual staged execution. The work is sequential, repository-coupled, and contains explicit review and runtime-cutover gates, so it does not need an automated loop or mandatory subagent orchestration.`

1. Trigger / heartbeat:
   - A user request explicitly asks to execute, resume, advance, review, or close this goal.
   - The newest request supersedes stale milestone work when it redirects scope.
2. Inputs / sources:
   - This goal file, current `main`, the active milestone branch or PR, relevant scripts, tests and docs, GitHub CI and reviews, and read-only live-state inventories.
3. Triage and orchestration:
   - Execute milestones in order. Convert each failing gate into a bounded fix inside the same milestone. Do not begin a later milestone while the current gate is unresolved.
4. Worktree and isolation:
   - Use one dedicated branch per milestone or tightly coupled batch. Serialize edits to shared refresh, check, wrapper, or Watcher-runtime files. Preserve unrelated dirty work.
5. Skills and context:
   - Always read `long-running-goal`; use `code-review` for Standards and Contract review, `diagnosing-bugs` for failures, and `writing-for-agents` only when instruction surfaces must change.
6. Connector read/write boundaries:
   - Pre-approved: repository reads; goal-owned branches, commits, pushes, Draft PR creation or updates, available CI and review reads; gated milestone merges and safe deletion of merged goal-owned branches; and the exact M5 local backup, profile transition, rollback rehearsal, and final cutover after its frozen preconditions pass.
   - Not pre-approved: messages to other people, external writes outside the frozen GitHub operations, cleanup or deletion outside the exact M5 profile transition and merged-branch boundary, or any local state mutation beyond the frozen M5 owner and category set.
7. Independent verification:
   - Each source milestone requires focused tests, applicable full suites, scoped static checks, and an independent read-only Contract review. M5 requires a separate read-only cutover review before apply.
8. Runtime hard stops:
   - Missing real-machine access or required credentials; evidence that changes frozen authority or identity semantics; an unclassified active plugin; an unmanaged conflicting discovery entry; a destructive or external action without explicit authorization; or three distinct in-scope diagnostic or fix attempts with no safe next step.
9. Durable learning:
   - Update this goal, focused tests, current README, runbook or ADR surfaces, validation evidence, and the current milestone checkpoint. Do not leave decisions only in chat or PR comments.

## Pre-Approval / YOLO

Ready activation: The following pre-approvals became active when the planning preflight completed, every approval-sensitive surface was settled, and the goal reached `Ready`; they remain active while the goal is `In Progress`.

1. Pre-approved YOLO local operations:
   - Non-destructive local repository code, docs, and test edits for M1-M4; branch creation; local dependency restore; focused and full tests; lint, formatting, and static checks; read-only inventories; generated test fixtures; Git commits and pushes; Draft PR updates; and fixes inside the current milestone.
   - No real plugin, cache, config, hook, or link mutation is implied before M5.
   - After M1-M4, the fresh inventory, protected backup, and independent cutover review pass, the exact M5 my-codex plugin/profile mutations, repository-owned link changes, fresh CLI validation processes, targeted rollback rehearsal, final universal activation, and retained-state recording are pre-approved within the frozen M5 boundary.
2. Pre-approved external reads/writes:
   - GitHub repository reads; goal-owned branch and commit pushes; Draft PR creation and updates; review and available CI reads; merge after every milestone gate and independent review pass; and deletion of merged goal-owned remote branches only when they contain no commits absent from `main`.
3. Runtime hard stops:
   - A proposed M5 mutation falls outside the frozen owner and category boundary; a protected backup cannot be created or restored safely; configuration drift prevents targeted restoration; ownership or identity remains unclassified; required machine state is inaccessible; transition ordering cannot preserve the discovery invariant; or repeated technical attempts leave no safe in-plan path.
4. Non-stops:
   - Milestone boundaries, checkpoints, expected test failures with a clear local fix, rebase or update of a clean milestone branch, docs synchronization, timing rebaseline, or review findings that can be fixed inside the frozen milestone.

## Goal Execution Contract

1. M0 planning is complete; do not begin M1 implementation until the newest user request explicitly asks to execute, resume, continue, or advance this goal.
2. Once execution is requested, execute strictly `M1 -> M2 -> M3 -> M4 -> M5 -> Close`.
3. Update the status table and current milestone evidence before and after work.
4. A milestone reaches `Done` only when its review gate passes, checkpoint evidence is recorded, and required current docs are synchronized.
5. Use the smallest falsifying validation first, then broader suites required by the milestone.
6. Keep source authority and installed or runtime state as separate evidence domains.
7. Do not merge a milestone PR when its branch is internally inconsistent or its active entry points are broken.
8. Do not use simultaneous plugin and universal skill injection as a diagnostic shadow mode. M5 comparisons use sequential isolated sessions or restored profiles.
9. Preserve old plugin, marketplace, cache, config, hook-backup, and Watcher state required for rollback; cleanup belongs to a later independent goal.
10. Record root cause, failed command, paths, breakpoint, and next fix for every material failure.
11. Only runtime hard stops require user input after the goal becomes `Ready`; ordinary local fixes then continue within scope.
12. Start every milestone branch from current `main`; do not resume from a stale or archived implementation branch.
13. After a milestone branch is merged or closed, treat `main` as the sole continuation baseline and remove or neutralize temporary refs when tooling permits.

## Status Definitions

| Status | Meaning |
| --- | --- |
| `Not Started` | Scope is frozen but implementation has not begun. |
| `In Progress` | The milestone owns current implementation or review work. |
| `Blocked` | A documented runtime hard stop prevents safe progress. |
| `Done` | Scope, review, validation, evidence, docs, and checkpoint are complete. |

## Milestone Status

| Milestone | Status | Review | Checkpoint |
| --- | --- | --- | --- |
| M0 Contract, Plan, and Baseline Freeze | Done | Passed | Done |
| M1 Repository-Authoritative Discovery and Profile Integration | Done | Passed | Done |
| M2 Watcher Metadata and Shared-Runtime Decoupling | Done | Passed | Done |
| M3 Physical Layout Verification — No Move | In Progress | Pending | Pending |
| M4 Optional Plugin Distribution Packaging | Not Started | Pending | Pending |
| M5 Controlled Universal Profile Cutover | Not Started | Pending | Pending |
| Close Goal Closure and Archive | Not Started | Pending | Pending |

## M0 Contract, Plan, and Baseline Freeze

Status: `Done`

Scope:

- Freeze authority, identities, compatibility, discovery profiles, milestone order, validation model, rollback, and authorization boundaries.
- Complete or explicitly skip the required grill, record the user's housekeeping choice, settle approval-sensitive surfaces, and make the readiness contract machine-checkable.
- Integrate all durable M1 requirements into this goal.
- Remove the redundant one-off prompt and retire temporary implementation refs so current `main` is the sole development baseline.
- Keep incomplete universalization source out of `main`.

Review gate:

- `main` contains only M0 planning and domain documents plus the frozen existing source baseline; no universalization implementation source is present.
- No `SKILL.md`, runtime script, manifest, hook, config, or cache changed during M0 cleanup.
- No open PR remains from the planning or prototype work.
- No continuation step requires a deleted prompt or temporary branch.
- The planning preflight, housekeeping choice, authorization boundary, milestone lifecycle, and checkpoint evidence satisfy the current `long-running-goal` contract.
- The default readiness checker passes before M0 becomes `Done` and M1 becomes the unique `Ready` milestone.

Draft-format validation:

```bash
python plugins/workflow/skills/long-running-goal/scripts/check_goal_ready.py --allow-draft docs/todo/universal-agent-skills-migration.md
python plugins/workflow/skills/long-running-goal/scripts/check_md_links.py docs/todo
python plugins/workflow/skills/long-running-goal/scripts/check_todo_index.py --mode active docs/todo/universal-agent-skills-migration.md docs/todo/README.md
git diff --check
```

Ready-promotion validation:

```bash
python plugins/workflow/skills/long-running-goal/scripts/check_goal_ready.py docs/todo/universal-agent-skills-migration.md
```

Evidence:

- The merged skill slimming baseline remains unchanged.
- The active goal is `docs/todo/universal-agent-skills-migration.md`.
- `docs/todo/README.md` contains the single active long-running-goal pointer.
- M0 contract revision `26934904c7e1bb586725f9dd4faec3677d5aabc0` and [PR #5](https://github.com/zzzhty/my-codex/pull/5) preserve the source-baseline and review evidence.
- The 2026-08-20 readiness audit failed on preflight, lifecycle, housekeeping, heading, timing, and checkpoint-format requirements, so M0 was reopened rather than leaving a false `Ready` state.
- Three grill-with-docs rounds, final shared-understanding confirmation, the corrected contract scan, and the default readiness gate resolved every M0 review finding.

Checkpoint evidence:

Checkpoint component: Done

Checkpoint type: git commit

Revision: 26934904c7e1bb586725f9dd4faec3677d5aabc0

Changed files: CONTEXT.md; docs/adr/0003-universal-skill-discovery-authority.md; docs/todo/README.md; docs/todo/universal-agent-skills-cleanup-follow-up.md; docs/todo/universal-agent-skills-migration.md

Validation recorded: Draft-format readiness passed before the checkpoint; default readiness, Markdown-link, active-index, and diff checks passed after lifecycle promotion on 2026-08-20

Out-of-scope dirty changes: none observed before this format correction

Rollback: `Revert the M0 planning-document changes. No runtime state was changed.`

Hard stop: `The M0 planning diff contains any universalization implementation source or changes a frozen skill.`

Completion criterion: `The preflight and housekeeping decisions are truthfully recorded, approval-sensitive surfaces are settled, the default readiness checker passes, M0 is Done/Passed/Done with final checkpoint evidence, and M1 is the unique Ready milestone.`

## M1 Repository-Authoritative Discovery and Profile Integration

Status: `Done`

Objective: Land the repository-derived catalog and managed projection together with all refresh, check, and wrapper callers so the source batch is internally consistent before merge.

Scope:

1. Start from current `main` and inventory every existing refresh, check, wrapper, marketplace, plugin, and projection caller.
2. Derive the canonical catalog from `plugins/*/skills/*/SKILL.md` and frontmatter identity, independent of marketplace metadata.
3. Add one shared explicit discovery-profile policy supporting only `universal` and `plugin`.
4. Update `sync_agents_skills.py`, `refresh_my_codex.py`, `check_my_codex.py`, `upgrade_my_codex.sh`, and `upgrade_my_codex.ps1` as one integrated contract.
5. Reject legacy skip-flag combinations that can create dual-active or zero-active discovery.
6. Add focused tests for catalog authority, projection ownership, profile selection, transition ordering, wrapper parity, and failure rollback.
7. Keep all real installation-state changes out of this milestone.

Non-scope:

- Watcher metadata internals, plugin packaging redesign, real cutover, cleanup, skill relocation, or identity changes.

Preconditions:

- The implementation branch is based on current `main` and has no unclassified dirty changes.
- Every existing refresh, check, and wrapper caller is inventoried before interface changes.
- The current source tree, tests, manifests, and goal are sufficient; no external prototype or patch is authoritative.

Canonical catalog requirements:

- Scan `plugins/*/skills/*/SKILL.md` directly.
- Use frontmatter `name` as callable identity, even when the physical directory name differs.
- Reject duplicate identities, malformed frontmatter, missing `SKILL.md`, and source or file symlink escape outside repository authority.
- Do not read marketplace or plugin manifests to decide the universal catalog.
- Do not introduce a second hand-maintained catalog.

Explicit profile requirements:

- Support exactly `universal` and `plugin`.
- Require `--discovery-profile universal|plugin` on refresh, check, Unix wrapper, and PowerShell wrapper entry points.
- Do not add an environment, persisted-config, or implicit-default selection path.
- Missing or invalid profile fails closed.
- Refresh, check, and Unix and PowerShell wrappers propagate the same resolved profile.
- Treat the new required argument as an authorized breaking CLI change and update every supported invocation in current docs and tests in the same milestone.

Universal profile requirements:

- Does not require marketplace metadata or plugin cache.
- Does not require the Codex CLI when no enabled skills-bearing plugin must be removed.
- Does not execute `codex plugin add`.
- Allows no enabled skills-bearing `my-codex` plugin.
- Manages only symlinks proven to target direct skill directories in this checkout.
- Fails closed on unmanaged same-name directories, files, or external symlinks.
- Repairs owned drift and prunes only stale owned links.
- Preserves unrelated user skills.

Plugin profile requirements:

- Performs complete marketplace, manifest, source-package, CLI-capability, and cache-contract preflight before removing universal links.
- Requires repository-owned universal links to be inactive.
- Requires every expected skills-bearing plugin to be enabled with one inspectable cache version.
- Compares cached skill identities to canonical repository source.
- Treats cache as projection, never authority.

Required transition semantics:

- Plugin to universal: preflight all universal targets -> identify exact enabled skills-bearing plugins -> remove or disable those exact plugins -> verify old active path inactive -> create or repair repo-owned links -> universal closure check.
- Universal to plugin: preflight package inputs and commands -> confirm the replacement can activate -> remove only repo-owned universal links -> install or enable plugin profile -> plugin closure check.
- Never create a temporary dual-active state.
- Never remove the only active path before the replacement passes its preflight.
- On removal or activation failure, report the exact breakpoint and preserve the recoverable prior profile whenever possible.

Legacy bypass handling:

- `--skip-marketplace`, `--skip-plugins`, `--skip-agents-skills`, and `--prune-plugins` cannot weaken the selected profile invariant.
- Conflicting combinations fail closed with a clear error; they are not silently reinterpreted.

Minimal falsifying validation:

```bash
/Users/max/.codex/venvs/my-codex/bin/python -m unittest -v \
  tests.test_repo_skill_catalog \
  tests.test_skill_discovery_profiles \
  tests.test_sync_agents_skills \
  tests.test_discovery_profile_runtime \
  tests.test_refresh_discovery_profile \
  tests.test_check_discovery_profile \
  tests.test_refresh_profile_integration \
  tests.test_check_my_codex \
  tests.test_upgrade_my_codex
```

Broader validation:

```bash
/Users/max/.codex/venvs/my-codex/bin/python -m unittest discover -s tests -p 'test_*.py' -v
/Users/max/.codex/venvs/my-codex/bin/python -m unittest discover -s plugins/workflow/tests -p 'test_*.py' -v
/Users/max/.codex/venvs/my-codex/bin/python -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v
/Users/max/.codex/venvs/my-codex/bin/python -m py_compile scripts/repo_skill_catalog.py scripts/skill_discovery_profiles.py scripts/check_skill_discovery.py scripts/sync_agents_skills.py scripts/discovery_profile_runtime.py scripts/refresh_my_codex.py scripts/check_my_codex.py
git diff --check
```

Review gate:

- Independent read-only review confirms invocation identity, ownership and prune safety, wrapper parity, bypass rejection, transition ordering, and rollback breakpoints.
- Universal closure does not require marketplace, cache, or Codex CLI when no plugin removal is needed.
- Plugin closure compares installed and cached identities to canonical repository source.
- Every supported public invocation and current doc is updated for the authorized required profile argument.
- No skill content, callable identity, Watcher identity, or slimming baseline changed.

Evidence to record:

- Scoped diff, focused and full test logs, CLI help output, Unix and PowerShell wrapper tests, failure-injection ordering evidence, and a real-environment read-only discovery inventory.

Execution evidence:

- Execution started on 2026-08-20 from clean `main` revision `3da1d41a1044218e39a0394ea827f105ed268710` on goal-owned branch `codex/universal-agent-skills-m1`; `origin/main` matched and no open PR existed.
- Initial read-only caller inventory covered the five required entry points, root README, current tests, marketplace and install metadata references, and legacy skip/prune flags. No memory entry supplied an alternate implementation source.
- Initial integrated implementation commit `80e8a8a` added the repository catalog, owned universal projection, explicit profile policy, rollback-capable transitions, complete closure checks, wrapper propagation, current documentation, and focused tests without changing skill content or callable identities.
- The independent Standards and Spec reviews found strict-parser, duplicate-authority, transition-interface, alternate-marketplace, selector-scope, universal-link-removal rollback, shared-manifest behavior-coverage, dead-helper, and wrapper-bootstrap gaps. The branch now fails closed on malformed CLI rows and config disagreement, centralizes plugin and marketplace identity parsing, rejects or precisely removes alternate-marketplace copies, limits selectors to the canonical catalog and chosen marketplace, uses direction-specific transition runtimes, rolls back partial universal-link removal, exercises manifest schema and identity failures through the shared closure, removes superseded helper surfaces, and uses the bootstrap Python only to establish the tooling venv before running profile helpers with its PyYAML-capable Python. Final independent re-review of `3da1d41...d78eccb` passed both Standards and Spec with no actionable findings; each reviewer independently reran all 52 focused tests.
- Post-fix validation on 2026-08-21 passed the required 52 focused tests, all 71 root tests, all 64 Workflow tests, and all 62 Watcher tests with three platform skips; owner-venv byte compilation, shell syntax, CLI help, Markdown links, goal readiness, and `git diff --check` also passed. The bare system `python3` correctly remained unsuitable because it lacks PyYAML, so all supported checks used `/Users/max/.codex/venvs/my-codex/bin/python` as frozen.
- A real-environment read-only inventory parsed all current `codex plugin list` rows, confirmed the canonical three `my-codex` packages enabled at one exact cache version each with 34 callable identities and plugin-profile closure, and confirmed `/Users/max/.agents/skills` is absent. No refresh, check, link, plugin, hook, cache, or durable-state mutation was run against the live installation during M1.
- [PR #6](https://github.com/zzzhty/my-codex/pull/6) merged the reviewed M1 branch to `main` as `9f6e3a739c00e0c780d8c71946600ba578f1f892` after GitHub reported it mergeable with no repository CI checks configured. The merged remote and local M1 branches contained no commits absent from `main` and were deleted before M2 started from that merge.

Checkpoint component: Done

Checkpoint type: git merge

Revision: 9f6e3a739c00e0c780d8c71946600ba578f1f892

Changed files: README.md; docs/todo/README.md; docs/todo/skill-slimming-batch-1-validation.md; docs/todo/universal-agent-skills-migration.md; scripts/check_my_codex.py; scripts/check_skill_discovery.py; scripts/discovery_profile_runtime.py; scripts/refresh_my_codex.py; scripts/repo_skill_catalog.py; scripts/skill_discovery_profiles.py; scripts/sync_agents_skills.py; scripts/upgrade_my_codex.ps1; scripts/upgrade_my_codex.sh; focused root tests

Validation recorded: 52 focused, 71 root, 64 Workflow, and 62 Watcher tests passed; three Watcher platform tests skipped; static, docs, lifecycle, wrapper, failure-injection, real-environment read-only inventory, and independent Standards and Spec gates passed on 2026-08-21

Out-of-scope dirty changes: none observed before merge or at the M2 branch point

Rollback: `Revert the source PR. Because M1 performs no real cutover, no user installation rollback is required.`

Hard stops:

- Any callable or Watcher identity drift; an unmanaged target would be overwritten; wrapper parity cannot be established; a failure path can leave both or neither discovery path active; or the real environment exposes an unclassified enabled plugin.

Authorization and review: `Repository source work, commits, goal-owned branch push, Draft PR creation and updates, independent review, and merge after every gate passes are pre-approved by the 2026-08-20 preflight. A merged goal-owned remote branch with no commits absent from main may then be deleted.`

Completion criterion: `The integrated source PR is merged to main, all callers use the explicit profile contract, and no runtime state was activated.`

## M2 Watcher Metadata and Shared-Runtime Decoupling

Status: `Done`

Objective: Make Watcher core work from canonical repository source and stable runtime locators without marketplace catalog or plugin-cache authority.

Scope:

1. Replace Watcher callable-skill enumeration through marketplace or plugin manifests with the canonical repository catalog.
2. Retain role, aliases, supporting skills, logical groups, and legacy names as a separately owned attribution overlay.
3. Resolve repository and shared runtime through an explicit repository-root contract, not by assuming a plugin-cache or adapter path.
4. Keep `$CODEX_HOME/watcher` as runtime state only.
5. Preserve historical logs and namespaced identities without rewriting events.
6. Update Watcher doctor, SessionStart metadata refresh, CLI, docs, and tests.

Non-scope:

- Callable identity rename, log rewrite, physical skill relocation, real profile cutover, or old-cache deletion.

Preconditions:

- M1 is merged; repository catalog API and explicit profiles are stable.
- Existing Watcher metadata schema, legacy mappings, runtime paths, and consumers are inventoried.

Minimal falsifying validation:

- Remove or redirect the marketplace catalog in a fixture; Watcher metadata discovery and reports still resolve the canonical skill set.
- Existing namespaced identities and legacy mappings produce the same canonical attribution.
- Running from repository source and through universal skill symlinks resolves the same shared runtime modules and assets.

Broader validation:

```bash
/Users/max/.codex/venvs/my-codex/bin/python -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v
/Users/max/.codex/venvs/my-codex/bin/python -m unittest discover -s tests -p 'test_*.py' -v
/Users/max/.codex/venvs/my-codex/bin/python plugins/workflow/skills/long-running-goal/scripts/check_md_links.py plugins/watcher
```

The Watcher suite must include a `TemporaryDirectory`-backed doctor integration scenario. Do not run doctor against the real `$CODEX_HOME/watcher` during M2 validation.

Review gate:

- Standards review confirms one owner for the callable catalog and one owner for non-callable attribution metadata.
- Contract review confirms no marketplace read is required for core Watcher operation, no persisted identity changes, and no runtime cache becomes source authority.

Evidence to record:

- Metadata fixture comparison, legacy-name tests, report snapshots or diffs, runtime-locator tests, isolated doctor-test output, and updated Watcher architecture docs.

Execution evidence:

- M2 started from merged `main` revision `9f6e3a739c00e0c780d8c71946600ba578f1f892` on `codex/universal-agent-skills-m2` after the M1 branch and remote ref were safely removed.
- Watcher now loads the exact M1 `scripts/repo_skill_catalog.py` implementation from an explicit validated repository root and derives its durable namespaced identities from that catalog. Marketplace JSON, plugin manifests, plugin cache, adapter ancestry, and runtime state no longer enumerate callable skills.
- Repository `.codex-plugin/skill-watcher.json` files remain the sole non-callable attribution overlays. Compatibility assertions preserve the pre-M2 baseline of 34 Watcher identities, 11 legacy mappings, 145 aliases, 11 supporting-skill edges, and the exact role distribution; existing legacy attribution scenarios remain unchanged.
- Installed hook commands embed `--repo-root`; SessionStart, hook validation, refresh/check callers, and doctor share that contract. A subprocess test produced the same attribution from repository and universal-symlink working directories, and a complete doctor integration used only `TemporaryDirectory` state, hook target, validator, and sample-event paths.
- A malformed marketplace and malformed plugin manifest were ignored while catalog discovery, SessionStart cache creation, and report rendering still resolved the canonical skill and attribution overlay. The derived runtime cache remained a runtime projection rather than a discovery authority.
- The first independent review found three in-scope transition gaps: catalog or overlay symlink escape, unproven quoting for space-bearing repository roots, and `reset-schema` mutating logs before a missing repository root failed. M2 now resolves every executable or readable authority path inside the explicit root, covers POSIX and Windows command serialization with a valid space-bearing root, and completes metadata discovery before any schema-reset mutation; focused escape and failure-ordering regressions pass.
- Post-fix validation on 2026-08-21 passed all 70 Watcher tests with three platform skips and all 71 root tests; owner-venv syntax compilation, actual Watcher plugin validation, observe/install-hook/doctor/reset-schema help, Watcher Markdown links, goal readiness, active TODO index, and `git diff --check` passed. No command targeted the real `$CODEX_HOME/watcher`, hooks, plugins, cache, or universal links.
- Independent Standards and Contract re-reviews of `9f6e3a739c00e0c780d8c71946600ba578f1f892...0a8214795ee73ed5bfc9a04041eefcec9e81698d` both returned clean on 2026-08-21. Each reviewer independently reran the 70-test Watcher suite, 71-test root suite, scoped diff and Markdown checks; Standards confirmed authority containment and cross-platform command serialization, while Contract confirmed `reset-schema` prevalidation ordering, marketplace independence, identity stability, and runtime-cache non-authority.
- [PR #7](https://github.com/zzzhty/my-codex/pull/7) merged the reviewed M2 branch to `main` as `01c7f21fc58fc3d237ccd0e86eb60cb9e2c4ebcd` after GitHub reported it clean and mergeable with no repository CI checks configured. The merged remote and local M2 branches contained no commits absent from `main` and were deleted before M3 started from that merge.

Checkpoint component: Done

Checkpoint type: git merge

Revision: 01c7f21fc58fc3d237ccd0e86eb60cb9e2c4ebcd

Changed files: CONTEXT.md; README.md; docs/todo/universal-agent-skills-migration.md; plugins/watcher/README.md; plugins/watcher/scripts/watcher_runtime/repository_source.py; plugins/watcher/scripts/watcher_runtime/skill/codex_hook_adapter.py; plugins/watcher/scripts/watcher_runtime/skill/codex_hook_config.py; plugins/watcher/scripts/watcher_runtime/skill/doctor.py; plugins/watcher/scripts/watcher_runtime/skill/install_codex_hook.py; plugins/watcher/scripts/watcher_runtime/skill/migrate_skill_watcher_schema.py; plugins/watcher/tests/test_skill_watcher.py; scripts/check_my_codex.py; scripts/refresh_my_codex.py

Validation recorded: 70 Watcher and 71 root tests passed; three Watcher platform tests skipped; catalog and overlay escape, space-bearing command serialization, schema-reset failure ordering, isolated doctor, marketplace independence, runtime locator, docs, static, actual plugin-validator, and independent Standards and Contract gates passed on 2026-08-21

Out-of-scope dirty changes: none observed before merge or at the M3 branch point

Rollback: `Revert M2 while remaining on a non-cutover environment. Do not rewrite runtime logs during rollout, so source rollback is sufficient.`

Hard stops:

- Historical attribution would change; the metadata overlay requires a second callable catalog; runtime cannot be located without cache authority; or a migration would rewrite existing logs or proposals.

Authorization and review: `Source work, commits, goal-owned branch push, Draft PR creation and updates, independent review, and merge after every gate passes are pre-approved by the 2026-08-20 preflight.`

Completion criterion: `Watcher core, doctor, reports, and metadata refresh pass with marketplace catalog absent, while all existing durable identities remain stable.`

## M3 Physical Layout Verification — No Move

Status: `In Progress`

Objective: Verify that `plugins/*/skills` remains the canonical physical layout and complete the milestone without moving skill source paths.

Frozen decision: `No move`

Verification gate:

1. Inventory symlink resolution, shared-runtime references, updater assumptions, plugin validation, and external path consumers after M2.
2. Record whether any concrete blocker is caused by physical layout rather than dependency direction.
3. If no blocker exists, mark M3 Done with a no-change architecture decision and proceed.
4. If evidence shows that a move is required, stop and formally evolve this goal; relocation is outside the frozen execution scope.

Minimal falsifying validation:

- All skill-local references, scripts, and assets resolve through universal links.
- Watcher and updater tests pass without relying on physical plugin-cache location.
- No current external consumer requires a new top-level path.

Review gate:

- Independent review confirms the current layout has no portability or packaging blocker and no external consumer requires a new top-level path.
- Directory aesthetics, convention preference, or shorter paths cannot reopen the frozen no-move decision.

Evidence to record:

- Portability matrix, path-consumer search, symlink resolution tests on supported platforms, and the no-change decision record.

Execution evidence:

- M3 started from merged `main` revision `01c7f21fc58fc3d237ccd0e86eb60cb9e2c4ebcd` on `codex/universal-agent-skills-m3` after the reviewed M2 branch and remote ref were safely removed. No skill source path, skill content, callable identity, plugin manifest, updater lock, or runtime state was moved or changed.
- The repository-authoritative catalog contains 34 skills across the three existing plugin roots and 119 Git-tracked skill-tree files, with no tracked symlink inside a skill tree. A `TemporaryDirectory` universal projection created all 34 links and proved every tracked `SKILL.md`, reference, template, script, agent manifest, and supporting file resolved through the callable-name link to the same repository-contained source entry. The projected Markdown inventory contained 38 relative links; the only two non-materialized targets are the documented child-name placeholders in the long-running-goal sequence template.
- The platform audit found one projection bug rather than a layout blocker: `Path.symlink_to()` had relied on its default file-target interpretation. M3 now declares `target_is_directory=True`; local Python documents that Windows requires this for directory targets and POSIX ignores it. A focused cross-platform contract test asserts the directory flag on every generated link, while the live macOS projection test validates the complete current tree.
- The active repository path-consumer search found 13 current files. They classify as canonical catalog and projection tooling, current docs, Watcher source-audit configuration, tests, the updater-owned Matt mirror contract, and the managed agent-support note; none is an unmanaged or external consumer requiring a top-level skill source. The only matching live non-runtime file is the managed `/Users/max/.codex/agents/operating-principles.md`, and its owner check passes. Live hooks point to the repo-owned Watcher CLI rather than a skill directory, and `/Users/max/.agents/skills` remains absent before M5.
- All three plugin manifests intentionally use plugin-relative `./skills/`; marketplace entries package the plugin roots; the Matt updater validates and replaces only `plugins/mattpocock-skills/skills`; and Watcher resolves its plugin-local doctor layout plus the explicit repository-root shared runtime. These are compatible with the retained layout and would gain no dependency-direction benefit from a physical move.

Portability matrix:

| Surface | macOS / POSIX evidence | Windows evidence | M3 result |
| --- | --- | --- | --- |
| Universal directory links | Actual temporary projection resolved all 34 links and 119 tracked files | `target_is_directory=True` is asserted for every link; Python ignores the flag only on non-Windows | Portable without moving source |
| Skill-local resources | Complete tracked tree and non-placeholder relative Markdown targets resolve through callable-name links | Directory-link semantics expose the same tree; no platform-specific skill-relative path is generated | No resource blocker |
| Watcher shared runtime | Repository and universal-link working directories produce identical attribution | Space-bearing root command serialization is covered by the Windows branch | No cache or physical-layout dependency |
| Plugin package and Matt mirror | Watcher and Workflow plugin validators plus Matt validate-only pass from existing plugin roots | Manifests use portable plugin-relative `./skills/`; PowerShell wrapper contracts pass in the root suite | Existing layout is the packaging-compatible layout |

Validation evidence:

- Focused `tests.test_sync_agents_skills` passed 10 tests, including explicit directory-link generation and every-tracked-resource projection.
- All 73 root tests, 64 Workflow tests, and 70 Watcher tests passed; three Watcher platform tests were skipped on macOS.
- Actual Watcher and Workflow plugin validation, Matt `--validate-only`, owner-venv syntax compilation, Unix shell syntax, goal readiness, active TODO index, managed agent-support check, consumer inventory, and `git diff --check` passed. No command changed live plugins, links, hooks, caches, agent-support files, or Watcher durable state.
- Independent compatibility review remains pending before the frozen no-change decision passes its gate.

Checkpoint evidence: `M3 no-change decision, validation evidence, and compatibility review.`

Rollback: `No source path changes occur, so no path rollback is required.`

Hard stops:

- Evidence demonstrates a required physical relocation; an external or persisted path consumer contradicts the frozen layout; Matt mirror ownership would be violated; invocation identity would change; or Windows projection behavior cannot be established.

Authorization and review: `The reviewed no-change verification and its source milestone Git/GitHub operations are pre-approved. Physical relocation is not authorized and requires formal goal evolution.`

Completion criterion: `The current physical authority is retained and validated without path or identity changes.`

## M4 Optional Plugin Distribution Packaging

Status: `Not Started`

Objective: Keep the skills-bearing plugin profile buildable as an optional compatibility and rollback distribution without making it a universal source authority.

Frozen target:

- Universal skills come only from `~/.agents/skills` and repo-owned scripts continue to manage hooks and agent-support files.
- The optional skills-bearing plugin profile is generated or validated directly from canonical repository source, is never a second hand-maintained catalog, and is mutually exclusive with universal links.
- No zero-skill adapter is created or installed in this goal.

Scope:

1. Define the optional plugin-profile build, validation, install, and check contract from canonical repository source.
2. Keep Watcher core, hooks, and shared runtime independent of plugin-cache location in universal mode.
3. Update marketplace and install metadata so the plugin package is an explicit `plugin` profile output.
4. Add package-content and mutual-exclusion tests.

Minimal falsifying validation:

- Universal mode installs no plugin package and preserves repo-owned hooks.
- The optional skills-bearing plugin package validates independently and fails closed when universal links are active.
- Package identities, skills, and source versions derive from repository authority.

Review gate:

- Optional plugin distribution remains mutually exclusive with universal discovery and does not become a new runtime or source authority.
- No adapter entity, second skill catalog, fallback discovery, or duplicate injection path is introduced.

Evidence to record:

- Package manifest and tree inventory, build commands, hook tests, universal discovery inventory, plugin-profile inventory, mutual-exclusion evidence, and rollback commands.

Checkpoint evidence: `M4 commits and PR, built artifact identity, package-content checks, and coexistence or mutual-exclusion evidence.`

Rollback: `Revert the packaging source PR. No real plugin is installed during M4; the current plugin profile remains the M5 rollback baseline.`

Hard stops:

- Universal hook operation depends on plugin cache; package build requires a second catalog; the plugin package cannot remain mutually exclusive; or optional packaging would alter callable identities.

Authorization and review: `Source and package work, commits, goal-owned branch push, Draft PR creation and updates, independent review, and merge after every gate passes are pre-approved. Real plugin-profile mutation remains part of the M5 boundary, not M4.`

Completion criterion: `Optional plugin packaging builds and validates independently from canonical source, while universal mode remains plugin-free and no active overlap is possible.`

## M5 Controlled Universal Profile Cutover

Status: `Not Started`

Objective: Move one real, rollback-capable environment from the skills-bearing plugin profile to the universal profile and prove exact-once discovery and behavior.

Production-cutover adaptation:

- Simultaneous full-shadow skill injection is forbidden because it violates the frozen single-active-path contract.
- Comparison uses sequential isolated sessions: baseline plugin profile, candidate universal profile, and rollback rehearsal or profile restoration.

Preconditions:

1. M1-M4 are Done and merged.
2. Real machine access, Codex CLI capabilities, repository checkout, and rollback artifacts are available.
3. Read-only inventory records exact `pwd`, repository, HEAD, upstream and dirty state, `~/.agents/skills`, Codex config, enabled plugins, cache versions, hooks, Watcher state, and visible skill inventory.
4. No unmanaged same-name skill or unclassified enabled my-codex plugin remains unresolved.
5. The exact apply, backup, retained-state, and rollback boundary is frozen by the completed planning preflight.

Frozen mutation boundary:

1. After M1-M4, the fresh inventory, and independent cutover review pass, M5 may disable, remove, restore, or reinstall only inventory-confirmed skills-bearing plugins owned by the `my-codex` marketplace. The current read-only inventory identifies `watcher@my-codex`, `workflow@my-codex`, and `mattpocock-skills@my-codex`; the immediately pre-apply inventory is authoritative if installed state changes before M5.
2. M5 may create, repair, prune, or roll back only universal entries under `~/.agents/skills` whose ownership is proven by the repository tooling and whose resolved target is the current `my-codex` checkout. An unmanaged entry, same-name conflict, or different target fails closed.
3. M5 may modify only the minimum `my-codex` marketplace, plugin-install, plugin-cache, hook, and agent-support entries required to transition between the two frozen profiles and prove rollback. It may not use that authority for general refresh, upgrade, or cleanup.
4. M5 excludes every other marketplace and plugin, unrelated Codex configuration, unmanaged skills, user files, the source checkout, and all Watcher logs, reports, proposals, snapshots, backups, and other durable runtime state.
5. Deletion or pruning of retained rollback artifacts, old configuration, cache, hook backups, or Watcher state is outside this goal. Any mutation beyond this exact ownership and category boundary is a runtime hard stop and requires formal goal evolution or separately scoped authorization.

Protected backup and evidence boundary:

1. Before the first mutation, create one durable backup directory beneath `/Users/max/.codex/backups/my-codex/universal-agent-skills/` with a unique basic-ISO-8601 UTC timestamp component, for example `20260820T153045Z`. Record the fully resolved path in M5 evidence. The directory is owner-only mode `0700`; raw backup files are mode `0600`.
2. Back up the complete pre-cutover `config.toml` and `hooks.json` when present; exact my-codex marketplace and plugin-install metadata; the three inventory-confirmed plugin package and cache trees at their exact versions; the repository-owned universal-link inventory without dereferencing canonical source content; `codex plugin list`; and repository HEAD, upstream, and dirty-state evidence.
3. Do not copy unrelated plugin or marketplace trees, Watcher state, the repository skill source, credentials stored outside the exact backed-up files, or the rest of the Codex home. Backup package content is an inactive rollback artifact, never canonical source authority.
4. Raw configuration, package, and environment evidence stays local and is never committed or attached to a PR. Only a redacted summary, exact owned paths, version identities, commands, and validation outcomes enter repository or GitHub evidence.
5. A later configuration or hook drift forbids blanket file replacement. Re-inventory and restore only the frozen my-codex entries after review; if targeted restoration cannot preserve intervening user changes, stop before mutation.
6. This directory is durable rollback evidence, not a task temporary cache root, and is therefore outside the `Not applicable` housekeeping policy.

Comparison matrix:

| Mode | Active skills path | Purpose | Required evidence |
| --- | --- | --- | --- |
| Baseline plugin | Skills-bearing plugin only | Capture current behavior and rollback baseline | Exact inventory, invocation checks, Watcher health |
| Candidate universal | `~/.agents/skills` only; repo-owned hooks remain active | Target production behavior | Exact-once inventory, callable-identity routing, symlink and resource resolution |
| Rollback rehearsal | Restored plugin profile on the current Mac | Prove real recovery before final cutover | Targeted restoration commands, exact-once identity inventory, no data loss or unrelated-state overwrite |
| Final universal | `~/.agents/skills` only; retained plugin artifacts inactive | Establish the production end state | Repeated exact-once inventory, behavior comparison, protected rollback baseline |

Fresh-process isolation boundary:

1. Baseline plugin, candidate universal, rollback rehearsal, and final universal evidence each comes from a distinct, freshly spawned, non-interactive Codex CLI process against the real current Codex home.
2. Do not use the current Desktop task, an inherited prompt, or an already-running CLI process as discovery or invocation evidence because they may retain previously loaded skill context.
3. Do not quit or relaunch the Codex Desktop application during the cutover. Desktop-visible follow-up may be recorded later, but it is not an M5 gate or a substitute for the fresh-process evidence.
4. Start a validation process only after the intended phase has exactly one active skills discovery path. No process is launched during a transient zero-active transition step.

Apply sequence inside the frozen M5 boundary:

1. Revalidate source and target conflicts.
2. Create and validate the protected backup, then record its redacted manifest and the exact targeted restoration commands.
3. Capture the plugin-profile baseline in a fresh non-interactive Codex CLI process.
4. Disable or remove only the inventory-confirmed skills-bearing my-codex plugins and verify the old discovery path is inactive.
5. Create or repair only repository-owned universal links while preserving repo-owned hooks and agent-support files without installing an adapter.
6. Capture the candidate-universal evidence in a second fresh process.
7. Remove only repository-owned universal links and restore the exact plugin profile through targeted my-codex entry restoration.
8. Capture rollback-rehearsal evidence in a third fresh process and prove that no unrelated or durable state changed.
9. Repeat the reviewed plugin deactivation, inactive-path verification, and repository-owned universal-link activation.
10. Capture final-universal evidence in a fourth fresh process and validate discovery, callable-identity behavior, resource resolution, Watcher core, hooks, and rollback readiness.
11. Record the inactive retained-state inventory and leave every cleanup candidate untouched.

Minimal falsifying validation:

- Every canonical skill appears exactly once.
- Removing or disabling the personal marketplace does not remove universal skills.
- Bare callable identities and implicit routing match baseline semantics; plugin-qualified selector spelling is not required to remain literal across profiles.
- Every referenced script, reference, template, asset, and harness metadata file resolves from symlink invocation.
- Universal profile works with plugin cache absent from the validation fixture or isolated environment.
- Watcher core functions without marketplace catalog authority.

Review gate:

- An independent read-only reviewer verifies inventory, sequence, backup, exact mutation set, validation commands, and rollback before apply.
- The post-apply comparison matrix has no critical regression or duplicate or missing identity.

Evidence to record:

- The protected backup path and redacted manifest; before, candidate, rollback, and final config and link inventories; `codex plugin list`; cache inventory; visible skill list; invocation scenarios; Watcher doctor and report output; hook checks; and rollback-rehearsal result. Raw backup material remains local.

Checkpoint evidence: `M5 preflight authorization record, exact commands, before and after evidence, comparison matrix, retained-state inventory, and rollback rehearsal.`

Rollback:

1. Remove only repository-owned universal links.
2. Re-inventory live config and hooks, compare them to the protected backup, and stop if intervening changes make targeted restoration unsafe.
3. Restore only the exact known-good my-codex marketplace or plugin entries and package versions.
4. Start a fresh non-interactive Codex CLI process and verify plugin-profile closure and Watcher health.
5. Preserve failure evidence and all retained rollback state for M5 rework.

Retained rollback state:

1. Retain the protected backup directory, the exact known-good versions of `watcher@my-codex`, `workflow@my-codex`, and `mattpocock-skills@my-codex`, their inactive package or cache trees, the targeted marketplace and configuration snapshots, hook and agent-support backups, and all M5 comparison evidence.
2. Retain all existing Watcher logs, reports, proposals, snapshots, backups, metadata, and other durable runtime state in place; do not duplicate, rewrite, or classify it as a cleanup candidate during this goal.
3. Goal Close does not delete or prune retained state. Eligibility requires at least five successful universal sessions across at least three working days, followed by a separate planning preflight, exact inventory, independent review, a `Ready` cleanup goal, and explicit destructive authorization.

Hard stops:

- The apply set exceeds the frozen preflight boundary; protected backup or targeted rollback cannot be proven; raw evidence cannot be kept private; intervening config drift makes restoration unsafe; an unmanaged conflict or unknown plugin exists; required CLI or machine access is missing; sequential fresh-process comparison cannot establish exact-once discovery; or the next action would remove the only active path without a preflighted replacement.

Authorization and review: `Read-only inventory and the exact M5 apply and rollback operations recorded by the completed planning preflight are pre-approved after M1-M4, the inventory, and independent cutover review pass. Any broader mutation is a runtime hard stop.`

Completion criterion: `The current Mac runs universal profile with exact-once discovery, bare callable identities, working resources, repo-owned hooks, protected Watcher durable state, a retained plugin rollback baseline, and a proven rollback path.`

## Close Goal Closure and Archive

Status: `Not Started`

Close prerequisites:

1. M1-M5 are `Done`, `Review=Passed`, and `Checkpoint=Done`.
2. The frozen acceptance oracle below has evidence.
3. Root README, relevant plugin and Watcher docs, wrappers, and runbooks describe the target architecture.
4. Active TODO navigation points only to current work.
5. The explicit Task Temporary Cache / Housekeeping policy recorded during planning preflight has been honored.

Frozen acceptance oracle:

- Git is the only skill source authority.
- Removing or disabling the personal marketplace does not prevent Codex from discovering repository skills through `~/.agents/skills`.
- Every canonical skill appears exactly once in the discovery and prompt inventory.
- Explicit invocation and preserved implicit routing do not regress.
- Symlink-invoked scripts, references, templates, assets, and harness metadata resolve.
- Universal profile requires no plugin cache.
- Watcher core requires no marketplace catalog.
- Optional plugin profile builds independently and is mutually exclusive with universal skills.
- Universal mode uses repo-owned hooks without installing a zero-skill adapter.
- Installer and sync tooling modifies only repository-owned links and fails closed on conflicts.
- No dangling links, second catalog, dual active discovery authority, or source and cache confusion remains.
- Retained plugin configuration, package, cache, hook backups, and other rollback artifacts are inventoried, inactive where required, and explicitly protected for the later cleanup goal.
- The merged slimming behavior is preserved.
- Callable identity, routing, hook, permission, and transition changes received independent read-only review.

Final validation:

```bash
/Users/max/.codex/venvs/my-codex/bin/python -m unittest discover -s tests -p 'test_*.py' -v
/Users/max/.codex/venvs/my-codex/bin/python -m unittest discover -s plugins/workflow/tests -p 'test_*.py' -v
/Users/max/.codex/venvs/my-codex/bin/python -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v
/Users/max/.codex/venvs/my-codex/bin/python plugins/workflow/skills/long-running-goal/scripts/check_goal_ready.py docs/todo/universal-agent-skills-migration.md
/Users/max/.codex/venvs/my-codex/bin/python plugins/workflow/skills/long-running-goal/scripts/check_md_links.py docs/todo
/Users/max/.codex/venvs/my-codex/bin/python plugins/workflow/skills/long-running-goal/scripts/check_todo_index.py --mode closed --archived-goal docs/todo/archive/universal-agent-skills-migration.md docs/todo/universal-agent-skills-migration.md docs/todo/README.md
git diff --check
```

Close actions:

1. Record final comparison, validation, rollback, and retained-state evidence, including the future cleanup eligibility boundary.
2. Move this file to `docs/todo/archive/universal-agent-skills-migration.md`.
3. Replace the active index entry with an archive entry and remove stale active navigation.
4. Close remaining completed PRs or issues and delete merged goal-owned branches only when they contain no commits absent from `main`.
5. Mark overall status `Closed` only after the archive and index gate passes.

Close checkpoint evidence: `Final merge or revision, archive path, closed PRs, validation logs, acceptance matrix, and retained rollback evidence.`

Close rollback: `Restore the active goal and index entry if closure validation reveals incomplete work; do not reopen old runtime authority silently.`

## Recommended Continuation Prompt

```text
Continue the long-running goal at docs/todo/universal-agent-skills-migration.md.

Read the newest user request first and confirm it still advances the same universal Agent Skills migration. Read the goal file, root AGENTS.md, current main, current branch or PR state, and the source and testing surfaces named by the first non-Done milestone. Do not rely on chat history, deleted prompts, archived prototypes, or unpublished patches.

If the overall goal is Draft, complete M0 planning preflight, approval freezing, readiness validation, and checkpoint evidence; do not execute M1-M5. Once the goal is Ready, execute only the first non-Done implementation milestone and start its branch from current main. Preserve the Git-only source authority, bare callable identities, Watcher identities, frozen slimming baseline, one-active-discovery-path invariant, unmanaged-user-state protection, and milestone-specific authorization boundary. Use non-destructive local YOLO operations inside the frozen scope, continue through ordinary failures when the next local diagnostic is clear, and stop only at a recorded runtime hard stop.

Before marking the milestone Done, run its minimal falsifying checks, required broader validation, independent read-only Contract review, docs synchronization, and checkpoint evidence. Perform M5 only inside its frozen apply and rollback boundary. Do not delete retained plugin, marketplace, cache, hook-backup, or Watcher state; cleanup belongs to a later independent goal.
```
