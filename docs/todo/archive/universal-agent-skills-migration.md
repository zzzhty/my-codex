# Universal Agent Skills Migration Long-Running Goal

Overall status: `Closed`

Updated: 2026-08-21

This archived file is the closed record for the universal Agent Skills migration. M0 through M5 and Close are `Done`; Draft PR #10 merged the final universal implementation and M5 evidence, while Close Draft PR #11 owns only archive, index, validation, and final-status evidence. The controlled cutover established the final universal live profile with every runtime, repository, Contract review, and closure gate passed. This archive is no longer an execution authority.

## Goal Summary

Goal Name: `Universal Agent Skills Migration`

Goal Description:

1. Make the Git repository the only skill source authority and make `~/.agents/skills` the normal universal discovery projection.
2. Remove runtime dependence on the personal Codex marketplace/plugin cache while preserving an optional, mutually exclusive skills-bearing plugin distribution profile for compatibility and rollback.
3. Decouple Watcher metadata and shared runtime from marketplace authority and perform a controlled universal cutover on the current macOS environment without adding a zero-skill adapter.

Goal Status: `Closed`

Goal Owner: `my-codex repository maintainer`

Goal Path: `docs/todo/archive/universal-agent-skills-migration.md`

Planning root: `docs/todo`

Goal directory: `docs/todo/archive`

Continuation contract: Closed. Do not resume this archive as an execution authority. The independently reviewed candidate, rollback rehearsal, and final-universal sequence completed on 2026-08-21 under the evolved native-qualified identity contract. The current Mac has exactly 34 repository-owned universal links as its only active my-codex skills path; the three skills-bearing my-codex plugins are not installed, repo-owned hooks remain healthy, protected rollback material is retained, and live Watcher durable state is unchanged. Preserve that final state unless the separately authorized [Universal Agent Skills Local Cleanup](../universal-agent-skills-cleanup.md) goal advances through its own Ready contract, independent review, and exact destructive boundary.

Planning preflight marker: `preflight:universal-agent-skills:20260820-grill3`

Planning preflight status: `Done`

Preflight source: `grill-with-docs`

Planning preflight evidence: `grill-with-docs rounds 1-3 completed on 2026-08-20 after repository, runtime, GitHub, and domain-language audits. The decision frontier became empty, the complete shared understanding was presented, and the user explicitly confirmed it before this marker was recorded.`

Resolved decisions: `The one-off Phase 1b prompt and prototype were retired. The current Mac is the sole M5 cutover target. Bare SKILL.md frontmatter names are catalog skill names and universal-link basenames. For the current canonical plugin-owned source layout, Codex invocation identities are the exact native ${plugin}:${catalog-name} forms in both plugin and universal profiles; a bare prompt-level request reference may resolve to that qualified identity but is not itself the promised runtime identity. Watcher durable identities retain their namespaced spelling and persisted attribution meaning, while distribution package identities remain separate. The existing plugins/*/skills/* physical authority is retained; no neutral copy, source relocation, or projection workaround will erase plugin context. Discovery profile selection is an explicit required CLI argument. Universal mode uses repo-owned hooks without a zero-skill adapter and retains an inactive mutually exclusive skills-bearing plugin profile. M6 cleanup is a future independent goal. Conditional Git/GitHub milestone writes are authorized. Task temporary cache policy is Not applicable. M5 may mutate only inventory-confirmed my-codex skills-bearing plugin state, repository-owned universal links, and the minimum my-codex marketplace, plugin, hook, and agent-support state required for the profile transition; unrelated or unmanaged state, Watcher durable state, and cleanup remain excluded. Cleanup eligibility remains at least five successful universal sessions across at least three working days. ADR-0004 supersedes ADR-0003 and records the native invocation-identity decision. M5 uses an owner-only durable backup outside Watcher state, performs plugin-to-universal-to-plugin-to-final-universal comparison, validates each mode in a fresh non-interactive Codex CLI process without restarting Desktop, and retains the proven plugin rollback baseline until a separately Ready cleanup goal authorizes deletion.`

Open decisions: `None. The 2026-08-21 user decision accepts native qualified Codex invocation identities and rejects a neutral-layout workaround. The evolved oracle and cutover artifacts completed independent review, and the user then explicitly resumed live M5 execution under this contract.`

Docs written: `docs/todo/archive/universal-agent-skills-migration.md; docs/todo/universal-agent-skills-cleanup-follow-up.md; docs/todo/README.md; docs/todo/archive/README.md; README.md; CONTEXT.md; docs/adr/0003-universal-skill-discovery-authority.md; docs/adr/0004-accept-native-codex-skill-invocation-identities.md`

## Preflight Time Assessment

Assessment target: `current-milestone-to-Closed`

Assessment mode: `Rough range`

Rough elapsed-time estimate: `30-90 minutes`

Basis or blocker: `As of 2026-08-21, the 30-90 minute Close estimate was met: review fixes, checkpoint publication, final status confirmation, and Draft PR #11 creation are complete. Only the already-authorized merge and safe merged-branch deletion remain as mechanical handoff actions; no goal work or cleanup remains.`

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
| `SKILL.md` frontmatter `name` | Bare catalog skill name and universal-link basename authority |
| Resolved canonical plugin provenance plus catalog name | Native Codex invocation identity `${plugin}:${catalog-name}` for both supported profiles |
| `~/.agents/skills/**` | Managed universal discovery projection, never source or cache |
| `~/.codex/plugins/cache/**` | Optional skills-bearing plugin distribution cache only |
| `.agents/plugins/*.json` | Optional distribution metadata, never universal source catalog |
| `.codex-plugin/skill-watcher.json` or successor overlay | Non-callable Watcher attribution metadata only |
| `$CODEX_HOME/watcher/**` | Runtime state and evidence only |

### Identity contract

1. Bare `SKILL.md` frontmatter names such as `sop`, `doc-alignment`, and `long-running-goal` are catalog skill names and universal-link basenames, not promised Codex runtime identities.
2. For every canonical plugin-owned skill, the accepted Codex invocation identity is exactly `${plugin}:${catalog-name}`, such as `workflow:sop` or `watcher:doc-alignment`, in both plugin and universal profiles.
3. A bare prompt-level skill request reference may resolve to the exact qualified Codex invocation identity. M5 records both the requested reference and resolved identity instead of treating the request spelling as the runtime identity.
4. Watcher durable identities remain unchanged. Their spelling intentionally aligns with the current Codex invocation identities, but their ownership and meaning remain persisted attribution rather than runtime discovery authority.
5. Distribution package identities such as `workflow@my-codex` remain separate from catalog names, Codex invocation identities, and Watcher identities.
6. Directory changes never imply identity renames, and this evolution authorizes no physical source move or neutral packaging projection.
7. Any later catalog-name, Codex invocation, Watcher, or distribution identity migration requires a new consumer inventory, compatibility plan, explicit authorization, and independent review.

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
- Do not move or copy canonical skill source merely to erase Codex's native plugin-qualified invocation context.
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
| M3 Physical Layout Verification — No Move | Done | Passed | Done |
| M4 Optional Plugin Distribution Packaging | Done | Passed | Done |
| M5 Controlled Universal Profile Cutover | Done | Passed | Done |
| Close Goal Closure and Archive | Done | Passed | Done |

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
2. Derive the canonical catalog from `plugins/*/skills/*/SKILL.md` and frontmatter catalog name, independent of marketplace metadata.
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
- Use frontmatter `name` as the bare catalog skill name, even when the physical directory name differs.
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
- No skill content, catalog name, observed Codex invocation identity, Watcher identity, or slimming baseline changed.

Evidence to record:

- Scoped diff, focused and full test logs, CLI help output, Unix and PowerShell wrapper tests, failure-injection ordering evidence, and a real-environment read-only discovery inventory.

Execution evidence:

- Execution started on 2026-08-20 from clean `main` revision `3da1d41a1044218e39a0394ea827f105ed268710` on goal-owned branch `codex/universal-agent-skills-m1`; `origin/main` matched and no open PR existed.
- Initial read-only caller inventory covered the five required entry points, root README, current tests, marketplace and install metadata references, and legacy skip/prune flags. No memory entry supplied an alternate implementation source.
- Initial integrated implementation commit `80e8a8a` added the repository catalog, owned universal projection, explicit profile policy, rollback-capable transitions, complete closure checks, wrapper propagation, current documentation, and focused tests without changing skill content or catalog names.
- The independent Standards and Spec reviews found strict-parser, duplicate-authority, transition-interface, alternate-marketplace, selector-scope, universal-link-removal rollback, shared-manifest behavior-coverage, dead-helper, and wrapper-bootstrap gaps. The branch now fails closed on malformed CLI rows and config disagreement, centralizes plugin and marketplace identity parsing, rejects or precisely removes alternate-marketplace copies, limits selectors to the canonical catalog and chosen marketplace, uses direction-specific transition runtimes, rolls back partial universal-link removal, exercises manifest schema and identity failures through the shared closure, removes superseded helper surfaces, and uses the bootstrap Python only to establish the tooling venv before running profile helpers with its PyYAML-capable Python. Final independent re-review of `3da1d41...d78eccb` passed both Standards and Spec with no actionable findings; each reviewer independently reran all 52 focused tests.
- Post-fix validation on 2026-08-21 passed the required 52 focused tests, all 71 root tests, all 64 Workflow tests, and all 62 Watcher tests with three platform skips; owner-venv byte compilation, shell syntax, CLI help, Markdown links, goal readiness, and `git diff --check` also passed. The bare system `python3` correctly remained unsuitable because it lacks PyYAML, so all supported checks used `/Users/max/.codex/venvs/my-codex/bin/python` as frozen.
- A real-environment read-only inventory parsed all current `codex plugin list` rows, confirmed the canonical three `my-codex` packages enabled at one exact cache version each with 34 catalog entries and plugin-profile closure, and confirmed `/Users/max/.agents/skills` is absent. No refresh, check, link, plugin, hook, cache, or durable-state mutation was run against the live installation during M1.
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

Status: `Done`

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

- M3 started from merged `main` revision `01c7f21fc58fc3d237ccd0e86eb60cb9e2c4ebcd` on `codex/universal-agent-skills-m3` after the reviewed M2 branch and remote ref were safely removed. No skill source path, skill content, catalog name, observed Codex invocation identity, plugin manifest, updater lock, or runtime state was moved or changed.
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
- The first Standards review found that the live directory-link probe skipped every `OSError`, which could hide an I/O, read-only-filesystem, or space failure. Commit `2eb8a6e` limits skips to explicit unsupported-platform, unsupported-filesystem, and Windows symlink-privilege cases; injected `EIO` now produces a test error rather than a skip.
- Final independent Standards and Contract reviews of `01c7f21fc58fc3d237ccd0e86eb60cb9e2c4ebcd...2eb8a6efcd66db2f517198b59deb4e689ac5cd9f` both returned clean on 2026-08-21. Each reviewer reran the focused and root gates; Contract independently reproduced the 34-skill, 119-file, 13-consumer, 38-link, two-placeholder inventory and found no physical-layout blocker. The read-only live check confirmed hooks still point to the repo-owned Watcher CLI but have not yet received M2's explicit `--repo-root`; that expected pre-cutover drift remains an M5 apply item and does not require a source move.
- [PR #8](https://github.com/zzzhty/my-codex/pull/8) merged the reviewed M3 branch to `main` as `dbf157ccad5c6171dbb24e263986aae12f5e4b72` after GitHub reported it clean and mergeable with no repository CI checks configured. The merged remote and local M3 branches contained no commits absent from `main` and were deleted before M4 started from that merge.

Checkpoint component: Done

Checkpoint type: git merge

Revision: dbf157ccad5c6171dbb24e263986aae12f5e4b72

Changed files: docs/todo/universal-agent-skills-migration.md; scripts/sync_agents_skills.py; tests/test_sync_agents_skills.py

Validation recorded: 10 focused, 73 root, 64 Workflow, and 70 Watcher tests passed; three Watcher platform tests skipped; 34-skill and 119-file projection, directory-link portability, 13-consumer inventory, three package validators, docs, static, and independent Standards and Contract gates passed on 2026-08-21

Out-of-scope dirty changes: none observed before merge or at the M4 branch point

Rollback: `No source path changes occur, so no path rollback is required.`

Hard stops:

- Evidence demonstrates a required physical relocation; an external or persisted path consumer contradicts the frozen layout; Matt mirror ownership would be violated; invocation identity would change; or Windows projection behavior cannot be established.

Authorization and review: `The reviewed no-change verification and its source milestone Git/GitHub operations are pre-approved. Physical relocation is not authorized and requires formal goal evolution.`

Completion criterion: `The current physical authority is retained and validated without path or identity changes.`

## M4 Optional Plugin Distribution Packaging

Status: `Done`

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

Execution evidence:

- M4 started from merged `main` revision `dbf157ccad5c6171dbb24e263986aae12f5e4b72` on `codex/universal-agent-skills-m4`. The optional install manifest is now schema 2 with explicit `discoveryProfile: plugin`; every marketplace package remains `AVAILABLE`, and universal mode never installs a plugin or a zero-skill adapter.
- The repository-authoritative catalog validates all three source packages before any Codex marketplace mutation. Each package manifest must expose `./skills/`; the package name, version, catalog names, loaded skill directories, and complete package tree must remain inside and match the validated checkout. Local distribution binds to that exact checkout; Git distribution binds to its canonical remote and exact clean HEAD revision. Explicit Git source or ref failures stop directly, while only automatic Git selection may choose the same validated local checkout.
- Package inventory at reviewed head `2dcdf43a3de0545d8ce2d3f0c2e5558bf7f06386` is 34 skills across three packages: `mattpocock-skills` version `1.2.3+codex.20260812033502` with 25 skills and 80 tracked files; `watcher` version `0.1.0+codex.20260817071906` with 4 skills and 47 tracked files; and `workflow` version `0.1.0+codex.20260814091823` with 5 skills and 54 tracked files.
- Profile transition tests prove exactly one active discovery path, rollback after partial plugin activation, universal plugin-free hook installation, package-content closure, and rejection of universal links while the plugin profile is active. Wrapper entry points now pass raw Codex selection to the canonical Python preflight, so an invalid distribution fails before Codex resolution or marketplace mutation on Unix and PowerShell contracts.
- Explicit pruning uses a structured plan that separates config-proven plugin removals from cache-only deletion targets. Cache structure is validated before targeting; CLI enabled-state closure is checked before marketplace or cache mutation; dry-run and real execution reject an enabled CLI-only/cache-name collision without deleting the cache; and complete profile closure is restored after an actual prune.

Validation evidence:

- All 91 root tests, 64 Workflow tests, and 70 Watcher tests passed; three existing Watcher platform tests were skipped on macOS. Actual Watcher and Workflow plugin validators, Matt `--validate-only`, owner-venv byte compilation, Unix shell syntax, goal readiness, Markdown links, active TODO index, managed agent-support check, and `git diff --check` passed.
- Independent Standards and Contract review iterated over package-source binding, source-tree containment, policy closure, mutation ordering, wrapper parity, and exact prune planning. Final review of `dbf157ccad5c6171dbb24e263986aae12f5e4b72...2dcdf43a3de0545d8ce2d3f0c2e5558bf7f06386` returned clean from both reviewers on 2026-08-21 with no P0-P2 or actionable Contract findings.
- [PR #9](https://github.com/zzzhty/my-codex/pull/9) merged the reviewed M4 branch to `main` as `a06b431cfaf06f1986fe3861fbed53174cad9c15` after GitHub reported it mergeable with no repository CI checks configured. The merged remote and local M4 branches contained no commits absent from `main` and were deleted before M5 started from that merge. No M4 command changed live plugins, marketplace state, universal links, hooks, agent-support files, caches, or Watcher durable state.

Checkpoint evidence: `M4 commits and PR, built artifact identity, package-content checks, and coexistence or mutual-exclusion evidence.`

Checkpoint component: Done

Checkpoint type: git merge

Revision: a06b431cfaf06f1986fe3861fbed53174cad9c15

Changed files: .agents/plugins/install-manifest.json; .agents/plugins/marketplace.json; README.md; docs/todo/universal-agent-skills-migration.md; plugins/watcher/tests/test_skill_watcher.py; plugins/watcher/tests/test_watcher_runtime_cli.py; scripts/check_my_codex.py; scripts/check_skill_discovery.py; scripts/refresh_my_codex.py; scripts/upgrade_my_codex.ps1; scripts/upgrade_my_codex.sh; tests/test_check_discovery_profile.py; tests/test_check_my_codex.py; tests/test_refresh_discovery_profile.py; tests/test_refresh_profile_integration.py; tests/test_upgrade_my_codex.py

Validation recorded: 91 root, 64 Workflow, and 70 Watcher tests passed with three existing Watcher platform skips; three package-owner validators, syntax, goal/docs/index, package inventory, source authority, mutual exclusion, wrapper ordering, prune safety, and final independent Standards and Contract gates passed on 2026-08-21

Out-of-scope dirty changes: none observed before merge or at the M5 branch point

Rollback: `Revert the packaging source PR. No real plugin is installed during M4; the current plugin profile remains the M5 rollback baseline.`

Hard stops:

- Universal hook operation depends on plugin cache; package build requires a second catalog; the plugin package cannot remain mutually exclusive; or optional packaging would alter catalog names or qualified Codex invocation identities.

Authorization and review: `Source and package work, commits, goal-owned branch push, Draft PR creation and updates, independent review, and merge after every gate passes are pre-approved. Real plugin-profile mutation remains part of the M5 boundary, not M4.`

Completion criterion: `Optional plugin packaging builds and validates independently from canonical source, while universal mode remains plugin-free and no active overlap is possible.`

## M5 Controlled Universal Profile Cutover

Status: `Done`

Objective: Move one real, rollback-capable environment from the skills-bearing plugin profile to the universal profile and prove exact-once discovery and behavior.

Production-cutover adaptation:

- Simultaneous full-shadow skill injection is forbidden because it violates the frozen single-active-path contract.
- Comparison uses sequential isolated sessions: baseline plugin profile, candidate universal profile, and rollback rehearsal or profile restoration.

Preconditions:

1. M1-M4 are Done and merged.
2. Real machine access, Codex CLI capabilities, repository checkout, and rollback artifacts are available.
3. Read-only inventory records exact `pwd`, repository, HEAD, upstream and dirty state, `~/.agents/skills`, Codex config, enabled plugins, cache versions, hooks, Watcher state, and visible skill inventory.
4. No unmanaged same-name skill or unclassified enabled my-codex plugin remains unresolved.
5. The evolved fresh-process prompt, schema, and deterministic gate derive each expected Codex invocation identity as `${plugin}:${catalog-name}`, preserve the bare catalog mapping and requested-reference-to-resolved-identity check, and verify profile-specific source locators.
6. An independent read-only cutover review passes on the evolved artifacts, and the user explicitly requests live execution under this evolved contract after the 2026-08-21 pause.
7. The exact apply, backup, retained-state, and rollback boundary remains frozen by the completed planning preflight and the protected evidence root.

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
| Candidate universal | `~/.agents/skills` only; repo-owned hooks remain active | Target production behavior | Exact-once inventory, canonical qualified identities, bare catalog mapping, request resolution, routing, universal source locators, symlink and resource resolution |
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
10. Capture final-universal evidence in a fourth fresh process and validate discovery, qualified-identity mapping and routing, source locators, resource resolution, Watcher core, hooks, and rollback readiness.
11. Record the inactive retained-state inventory and leave every cleanup candidate untouched.

Minimal falsifying validation:

- Every canonical skill appears exactly once.
- Removing or disabling the personal marketplace does not remove universal skills.
- Every model-visible skill's Codex invocation identity equals `${plugin}:${catalog-name}` from the canonical inventory in baseline, candidate, rollback, and final evidence; no duplicate bare catalog name exists.
- Bare catalog names remain exact, the explicit bare `long-running-goal` request reference resolves to `workflow:long-running-goal`, and implicit docs-alignment and SOP routing remain `watcher:doc-alignment` and `workflow:sop`.
- Plugin mode source locators resolve under the exact plugin cache version, while candidate and final universal locators resolve through `/Users/max/.agents/skills/${catalog-name}/SKILL.md` without depending on active plugin installation or cache.
- Every referenced script, reference, template, asset, and harness metadata file resolves from symlink invocation.
- Universal profile works with plugin cache absent from the validation fixture or isolated environment.
- Watcher core functions without marketplace catalog authority.

Review gate:

- An independent read-only reviewer verifies inventory, sequence, backup, exact mutation set, evolved identity and source-locator oracle, validation commands, and rollback before apply.
- The post-apply comparison matrix has no critical regression or duplicate or missing identity.

Evidence to record:

- The protected backup path and redacted manifest; before, candidate, rollback, and final config and link inventories; `codex plugin list`; cache inventory; visible skill list; invocation scenarios; Watcher doctor and report output; hook checks; and rollback-rehearsal result. Raw backup material remains local.

Runtime hard-stop evidence: `Resolved on 2026-08-21. Candidate universal discovery preserved exact-once loading but contradicted the former bare-runtime-identity contract; the plugin rollback completed successfully, and the user then explicitly accepted Codex-native plugin-qualified invocation identities while rejecting the neutral-layout direction.`

Identity-contract evolution and compatibility inventory:

- The canonical inventory contains 34 skills: 20 are model-visible and 14 are explicit-only. For all 20 model-visible skills, the candidate universal output exactly equals the inventory-derived `${plugin}:${catalog-name}` identity mapping, with no missing, extra, or duplicate bare catalog names.
- The fresh candidate process accepted the bare `long-running-goal` request reference and resolved it to `workflow:long-running-goal`. The two implicit routing scenarios matched the plugin baseline exactly: docs and scripts alignment selected `watcher:doc-alignment`, and stable-workflow SOP creation selected `workflow:sop`.
- All 34 repository attribution overlays already use the corresponding namespaced Watcher identities. Existing Watcher events and durable keys therefore require no rewrite; shared spelling does not make Watcher state a discovery authority.
- Candidate source locators resolved through `/Users/max/.agents/skills/${catalog-name}/SKILL.md`, while baseline and rollback locators resolved through exact plugin-cache versions. Qualified invocation identity can therefore remain stable while the active discovery source changes, preserving the Git-only universal authority objective.
- Current user-facing examples such as `$long-running-goal` are classified as skill request references, not runtime identity declarations. They remain compatible with the observed bare-request resolution and are not bulk-rewritten to an unverified colon-token syntax.
- Official OpenAI [Build skills](https://learn.chatgpt.com/docs/build-skills) documentation establishes `$HOME/.agents/skills` as the user discovery root, support for symlinked skill folders, and plugins as the native reusable-distribution mechanism. It does not promise a particular namespace spelling, so the exact qualified-identity oracle is grounded in the recorded `codex-cli 0.148.0-alpha.21` baseline, candidate, and rollback processes and must be revalidated on every M5 phase.

- M5 pre-apply source `625e3bdcbfe64085c7ddbeec2601c5c5e0077ff1` added an exact canonical name-to-source transition boundary. Both directions fail before plugin mutation on mapping drift or an extra repo-target link, use no generic stale-link prune, and remove only canonical links. All 95 root tests and the exact live dry-run passed. An independent second pre-apply review returned Clean.
- The owner-only protected backup and raw evidence root is `/Users/max/.codex/backups/my-codex/universal-agent-skills/20260820T184942Z`; directories are mode `0700`, raw and generated evidence files are mode `0600`, and the sole executable evidence gate `qualified-identity-gate.zsh` is mode `0700`. It retains the complete pre-cutover config and hooks, three exact cache archives, metadata, all comparison outputs, and targeted rollback material. Raw content remains local and uncommitted.
- Baseline plugin discovery produced 20 unique model-visible canonical skills with exact plugin-qualified identities and cache locators. The deterministic external gate passed. Baseline Watcher health recorded one known defect: the four managed hook commands lacked explicit `--repo-root`; this was the reviewed M2 apply item rather than a waived candidate gate.
- Candidate universal apply removed only `mattpocock-skills@my-codex`, `watcher@my-codex`, and `workflow@my-codex`, created exactly 34 canonical links, and repaired only the four managed Watcher commands. Universal closure and Watcher doctor passed with zero warnings; all 119 tracked skill files resolved byte-identically through the links; the three package caches were inactive; unrelated config, agent support, and live Watcher durable state were unchanged.
- The distinct candidate fresh process loaded all 20 canonical model-visible skills exactly once from `/Users/max/.agents/skills/*/SKILL.md` and reported every invocation identity as plugin-qualified. In particular, explicit `long-running-goal` resolved to `workflow:long-running-goal`, docs alignment routed to `watcher:doc-alignment`, and stable SOP routed to `workflow:sop`. The former fail-fast bare-identity gate exited `1`; that failure remains preserved as correct evidence against the old contract and is not reclassified as a false positive.
- A follow-up read-only loader isolation used `codex-cli 0.148.0-alpha.21` and `codex debug prompt-input` with a fresh temporary HOME, an empty CODEX_HOME, and no installed-plugin configuration. Symlinks from `$HOME/.agents/skills` to the canonical `plugins/*/skills/*` targets still exposed `workflow:long-running-goal`, `watcher:doc-alignment`, and `workflow:sop`; replacing only those targets with neutral physical copies exposed the bare names, and symlinking to the neutral copies preserved the bare names. OpenAI's current [Build skills](https://learn.chatgpt.com/docs/build-skills) documentation confirms both the USER discovery root and that Codex follows symlink targets. Together these results isolate the current loader behavior to resolved target plugin provenance rather than active plugin installation or cache state. The temporary isolation root was deleted. At the time this established that no projection-only fix existed inside the frozen layout and correctly triggered formal goal evolution; the 2026-08-21 user decision resolved that stop by accepting the native qualified surface without relocating source.
- The exact breakpoint is the universal branch of the deterministic fresh-output gate after successful candidate closure, resource, hook, and doctor checks. The final-universal phase was not attempted.
- The reviewed rollback removed the 34 canonical links and reinstalled the same three package selectors at versions `1.2.3+codex.20260812033502`, `0.1.0+codex.20260817071906`, and `0.1.0+codex.20260814091823`. Plugin closure and isolated Watcher doctor passed with zero warnings. A third fresh process reproduced the baseline 20 identity, bare-identity, and cache-locator triples exactly, with no duplicates. Live Watcher durable-state stat inventory remained exactly unchanged, and the protected pre-cutover cache archives remain available.
- Immediately before the resumed apply, the safe state is the single active plugin discovery profile with the repo-owned hooks repaired and healthy; `/Users/max/.agents/skills` is inactive and empty. No retained backup, Watcher state, unrelated plugin, marketplace, config, or user entry was deleted. The evolved artifacts and independent review passed, and the user explicitly resumed live execution under this contract on 2026-08-21.
- Blocked-state evidence revision `ca23a10b4195db852b31a156b530e9ce6d484911` and completion-evidence revision `58dd5825907758b0691e49b643bcf1e15db195d4` are published in Draft [PR #10](https://github.com/zzzhty/my-codex/pull/10). All M5 gates now pass; the PR is ready for its authorized final update and merge.
- Independent post-rollback review returned Clean: the candidate hard stop is not a prompt, schema, or oracle false positive; final universal was never executed; live rollback closure is complete; and the Draft PR/no-merge boundary is accurate. The reviewer also confirmed a non-blocking cache fact: reinstalling from current canonical source preserves the exact selectors, manifest versions, skill identities, and health gates but does not promise byte identity with the pre-cutover emergency archives, which remain protected.
- The resumed apply used repository revision `0ef5a9440098ae1a6f967be3489809ba372305bd`; the complete diff from reviewed runtime source ancestor `625e3bdcbfe64085c7ddbeec2601c5c5e0077ff1` contains only the seven declared Markdown files. The qualified prompts, schema, exact gate, and plan remained local under the protected evidence root.
- Baseline plugin closure and isolated Watcher doctor passed with zero warnings. A fresh process exposed exactly 20 model-visible my-codex skills with exact `${plugin}:${catalog-name}` identities, plugin-cache locators, no duplicate catalog names, bare request `long-running-goal` resolving to `workflow:long-running-goal`, and the expected `watcher:doc-alignment` and `workflow:sop` implicit routes.
- Two added assertions outside the reviewed oracle returned nonzero after otherwise successful candidate checks. The first incorrectly required marketplace selector strings to disappear instead of accepting their correct `not installed` catalog rows. Its immediate targeted rollback passed closure and doctor; the first recovery fresh output was then correctly rejected for adding a `file: ` label to exact locators. The four prompts were clarified to require unlabeled absolute paths, an independent follow-up review returned Clean, and a new recovery process passed and matched the resumed baseline triples. The second added assertion incorrectly required removed live plugin caches to remain present even though the frozen target requires cache-independent universal discovery and protects tar archives as rollback material. It also triggered an immediate targeted rollback whose closure, doctor, fresh gate, and exact baseline comparison passed. Both failures remain preserved and are not reclassified as successful product checks.
- The reviewed candidate universal phase then passed without expanding the oracle: exact 34-link ownership and target mapping, 119 Git-tracked files resolving byte-identically through the links, target selectors `not installed`, protected archives present, hooks and agent support unchanged, live Watcher durable state unchanged, universal closure and isolated doctor at zero warnings, and the exact fresh qualified-identity/source-locator gate.
- The formal rollback rehearsal removed exactly the 34 canonical links and restored only the three exact target selectors and versions. Plugin closure and isolated doctor passed with zero warnings, live Watcher durable state remained unchanged, the fresh plugin gate passed, and all 20 sorted identity, catalog-name, and plugin-cache-locator triples equaled the resumed baseline exactly.
- Final universal activation repeated the reviewed transition and every candidate validation. The final fresh gate passed, and all 20 sorted identity, catalog-name, and universal-locator triples equaled the candidate exactly. The semantic config diff from the protected baseline is limited to removal of the three target plugin entries; the marketplace, four managed hooks, agent support, unrelated config and plugins, repository source, and live Watcher durable state are unchanged. The exact live plugin cache trees are absent, while all three protected cache archives and targeted rollback material remain retained.
- Independent post-apply review returned Clean. It independently reproduced universal closure with zero warnings, exact 34-link and 119-file parity, three `not installed` selectors, empty live my-codex cache, exact hook and agent-support hashes, the three-entry-only config diff, unchanged Watcher durable-state inventory, all four official fresh gates, baseline-to-rollback and candidate-to-final triple equality, archive integrity, and owner-only protected-tree permissions.
- Owner-only local execution evidence is summarized at `/Users/max/.codex/backups/my-codex/universal-agent-skills/20260820T184942Z/evidence/qualified-identity-execution-summary.md`. Raw outputs, the two recovery failures, prior hard-stop evidence, protected archives, and rollback material remain local and uncommitted.

Checkpoint evidence: `M5 preflight authorization record, exact commands, before and after evidence, comparison matrix, retained-state inventory, and rollback rehearsal.`

Checkpoint component: Done. The runtime comparison, independent post-apply review, repository validation, final Contract review, and completion-evidence publication all passed.

Checkpoint revision: `625e3bdcbfe64085c7ddbeec2601c5c5e0077ff1` is the reviewed runtime source, `0ef5a9440098ae1a6f967be3489809ba372305bd` is the exact resumed-apply repository revision, and `58dd5825907758b0691e49b643bcf1e15db195d4` records the reviewed M5 completion evidence in Draft PR #10.

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

Authorization and review: `The user authorized formal identity-contract evolution on 2026-08-21, the evolved oracle and artifacts completed independent cutover review, and the user explicitly resumed execution under this contract. The exact reviewed M5 apply, rollback rehearsal, and final universal operations are complete and passed independent post-apply review. No further live mutation is part of M5 checkpoint finalization; any broader mutation remains a runtime hard stop.`

Completion criterion: `The current Mac runs universal profile with exact-once discovery, the exact canonical plugin-qualified Codex invocation identities, preserved bare catalog-name mapping and request resolution, exact routing, universal source locators, working resources, repo-owned hooks, protected Watcher durable state, a retained plugin rollback baseline, and a proven rollback path.`

## Close Goal Closure and Archive

Status: `Done`

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
/Users/max/.codex/venvs/my-codex/bin/python plugins/workflow/skills/long-running-goal/scripts/check_goal_ready.py docs/todo/archive/universal-agent-skills-migration.md
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

## Close Execution Evidence

- M5 [PR #10](https://github.com/zzzhty/my-codex/pull/10) merged as `606f45f1f722404dff0669175cb2dd16913a0392`. The local and remote M5 branches were deleted only after `git merge-base --is-ancestor` and an empty `main..branch` revision set proved no unmerged commits remained.
- Close branch `codex/universal-agent-skills-close` started from that exact merge commit. The active goal path was moved to `docs/todo/archive/universal-agent-skills-migration.md`; active long-running-goal navigation was removed, and both TODO indexes now point to the archive record.
- The planning-time Task Temporary Cache / Housekeeping decision remains `Not applicable`. No goal-owned temporary cache root was created, so Close has no task-temporary deletion action.
- The protected root `/Users/max/.codex/backups/my-codex/universal-agent-skills/20260820T184942Z`, all cache archives, raw and generated evidence, recovery failures, targeted rollback material, Watcher durable state, hooks, and inactive plugin rollback identities remain retained. Close performs no cleanup.
- Final validation from merged `main` passed: 95 root tests; 64 Workflow tests; 70 Watcher tests with three existing Windows skips; universal profile closure with zero warnings; archived-goal readiness; TODO planning-tree structure; Markdown relative links; closed-index ownership; and `git diff --check`.
- Independent Close Contract review returned Clean after two findings were fixed: the readiness example now targets the archived goal, while the closed-index command intentionally retains the absent old active path; and the time assessment now reflects only the actual remaining Close mechanics.
- Archive/index checkpoint revision `a493bd37343341d9e8257464e0a08f97c5664886` is published in Draft [PR #11](https://github.com/zzzhty/my-codex/pull/11). The PR contains only the 94%-similarity goal move and the two index updates; GitHub reports it mergeable with no repository status checks configured.

Temporary cache / housekeeping evidence:

- Recorded policy: `Not applicable`
- No task temporary cache roots were created.
- Action: No task-temporary cleanup was performed; protected rollback material and Watcher durable evidence remain retained.

Checkpoint evidence: `Done. M5 merge 606f45f1f722404dff0669175cb2dd16913a0392; Close archive/index revision a493bd37343341d9e8257464e0a08f97c5664886; archive path docs/todo/archive/universal-agent-skills-migration.md; merged PR #10 and Draft Close PR #11; 95/64/70-test validation matrix with three existing skips; universal closure at zero warnings; archived readiness, planning-tree, Markdown-link, closed-index, and diff gates passed; independent Close review Clean; housekeeping Not applicable with no task root; protected rollback and Watcher evidence retained.`

Close rollback: `Restore the active goal and index entry if closure validation reveals incomplete work; do not reopen old runtime authority silently.`

## Close Continuation Boundary

This goal is `Closed` and has no remaining implementation or Close milestone. Do not resume this archive as an execution authority. Preserve the final universal live state. Retained-state cleanup is owned only by the separately authorized [Universal Agent Skills Local Cleanup](../universal-agent-skills-cleanup.md) goal and its exact preservation and deletion gates.
