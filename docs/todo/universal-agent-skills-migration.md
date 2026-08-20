# Universal Agent Skills Migration Long-Running Goal

Overall status: `Ready`

Updated: 2026-08-20

This file is the single active authority for completing the universal Agent Skills migration from Phase 1b through Phase 6. It upgrades the earlier universalization design into a continuation-ready long-running goal. Detailed implementation belongs here; `docs/todo/README.md` should contain only the active pointer.

## Goal Summary

Goal Name: `Universal Agent Skills Migration`

Goal Description:

1. Make the Git repository the only skill source authority and make `~/.agents/skills` the normal universal discovery projection.
2. Remove runtime dependence on the personal Codex marketplace/plugin cache while preserving an optional, mutually exclusive Codex adapter/distribution profile.
3. Decouple Watcher metadata and shared runtime from marketplace authority, perform a controlled universal cutover, and remove obsolete owned runtime paths only after evidence-backed stabilization.

Goal Status: `Ready`

Goal Owner: `my-codex repository maintainer`

Goal Path: `docs/todo/universal-agent-skills-migration.md`

Planning root: `docs/todo`

Goal directory: `docs/todo`

Continuation contract: Read this file, the current branch/PR state, and the newest user request before acting. Resume only the first non-Done milestone. Preserve callable skill identities, the frozen slimming baseline, user-owned installation state, and the single-active-discovery-path invariant. Do not depend on chat history.

Planning preflight marker: `preflight:universal-agent-skills:20260820-lrg1`

Planning preflight status: `Done`

Preflight source: `grill-with-docs-equivalent repository and PR evidence review; the inspected architecture left no unresolved question frontier for M1-M4`

Resolved decisions: `This goal file; dev_docs/prompt/universal-agent-skills-phase-1b.md; archive/universal-phase1-candidate-20260820; main@8e29df2faeffb2b0dc3a8b202e3293d00ce2191a`

Open decisions: `M5 runtime apply and M6 destructive cleanup remain explicit runtime hard stops requiring fresh user authorization after their read-only gates pass. M3 physical relocation is conditional on evidence and defaults to no move.`

Docs written: `docs/todo/universal-agent-skills-migration.md; dev_docs/prompt/universal-agent-skills-phase-1b.md; docs/todo/README.md`

## Preflight Time Assessment

Assessment target: `Ready-to-Closed`

Assessment mode: `Rough range`

Rough elapsed-time estimate: `2-4 working weeks`

Basis or blocker: `2026-08-20 estimate based on six serial implementation/cutover milestones, focused and full-suite validation, independent reviews, cross-platform wrapper checks, and a minimum stabilization observation window. The range includes normal GitHub/CI waits and serial milestone merges; it excludes prolonged credential, machine-access, or upstream-tool outages.`

Critical-path time-cost distribution: `Not required: rough range recorded.`

## Task Temporary Cache / Housekeeping

Close housekeeping policy: `Not applicable`

Housekeeping decision source: `Current 2026-08-20 goal scope does not authorize or require a dedicated goal-owned temporary cache root. Future scope evolution must obtain a new explicit policy before first use.`

Task temporary cache root strategy: `Not applicable: no goal-owned task temporary cache root will be created. Tests and packaging use existing repository or tool-managed locations and must not treat them as Close-owned disposable state.`

Recorded task temporary cache roots: `Not applicable`

Housekeeping boundary: `Close performs no task-temporary-cache cleanup. M6 may remove only separately inventoried and explicitly authorized my-codex marketplace/plugin paths whose ownership is proven; that is migration cleanup, not task-cache housekeeping.`

## M0 Execution Baseline

M0 design-freeze baseline:

1. `main@8e29df2faeffb2b0dc3a8b202e3293d00ce2191a` contains the merged low-risk slimming baseline from PR #3.
2. The original PR #4 source candidate is preserved at `archive/universal-phase1-candidate-20260820@1faa330442f2899f3ed5d2b740465132ce3ff51f` and must be treated as prototype evidence, not merge-ready source.
3. The prototype established a repository-derived skill catalog and explicit profile concepts, but its `sync_agents_skills.py` interface was not integrated with refresh/check/wrappers and therefore could not safely merge.
4. The current physical authority remains `plugins/*/skills/*/SKILL.md`; no top-level skill relocation is approved.
5. Real `/home/aefv` discovery, plugin config, plugin cache, hook, and Watcher runtime state must be re-inventoried before M5. Substitute-environment evidence cannot prove the live machine state.

Current source-of-truth evidence read:

1. `AGENTS.md`, root `README.md`, `docs/todo/README.md`, the merged slimming review/handoff, and current GitHub PR state.
2. `plugins/workflow/skills/long-running-goal/SKILL.md`, its creation, preflight, checkpoint, execution, and production-cutover contracts.
3. `scripts/sync_agents_skills.py`, `scripts/refresh_my_codex.py`, `scripts/check_my_codex.py`, platform wrappers, marketplace/install manifests, plugin manifests, and Watcher metadata/runtime code.
4. `dev_docs/prompt/universal-agent-skills-phase-1b.md` and the archived Phase 1 prototype branch.

## Frozen Architecture Contract

### Authority model

| Surface | Target responsibility |
| --- | --- |
| Git `plugins/*/skills/**` | Sole canonical skill source authority |
| `SKILL.md` frontmatter `name` | Callable universal identity authority |
| `~/.agents/skills/**` | Managed universal discovery projection, never source or cache |
| `~/.codex/plugins/cache/**` | Optional Codex adapter/distribution cache only |
| `.agents/plugins/*.json` | Optional distribution metadata, never universal source catalog |
| `.codex-plugin/skill-watcher.json` or successor overlay | Non-callable Watcher attribution metadata only |
| `$CODEX_HOME/watcher/**` | Runtime state/evidence only |

### Identity contract

1. Callable identities such as `sop`, `doc-alignment`, and `long-running-goal` remain unchanged.
2. Watcher durable identities such as `workflow:sop` and `watcher:doc-alignment` remain unchanged.
3. Distribution identities such as `workflow@my-codex` remain separate from callable and Watcher identities.
4. Directory changes never imply identity renames.
5. Any identity migration requires a separate consumer inventory, compatibility plan, explicit authorization, and independent review; it is outside this goal unless the goal is formally evolved.

### Discovery contract

1. One runtime has exactly one active skills discovery path for every canonical skill.
2. Universal and skills-bearing plugin profiles are mutually exclusive.
3. No fallback, dual-read, dual-write, compatibility shim, or second hand-maintained skill catalog may hide an incomplete transition.
4. A zero-skill Codex adapter may coexist with universal discovery only after tests prove it cannot inject overlapping skills.
5. An unmanaged same-name entry fails closed; repository tooling never overwrites another source.

### Frozen baseline and non-goals

- Preserve the current slimming result; do not reopen wording/token optimization.
- Do not edit Matt Pocock mirror skill content outside its updater-owned workflow.
- Do not move skills merely for directory aesthetics.
- Do not migrate invocation identities as part of path changes.
- Do not make Watcher logs, reports, proposals, or plugin cache a source authority.
- Do not perform real installation-state mutation before M5 authorization.

## Loop Blueprint / Harness Boundary

Execution mode: `Manual staged execution`

Reason: The work is sequential, repository-coupled, and contains explicit review and runtime cutover gates. It does not need an automated loop or user-requested subagent orchestration.

1. Trigger / heartbeat:
   - A user request explicitly asks to execute, resume, advance, review, or close this goal.
   - The newest request supersedes stale milestone work when it redirects scope.
2. Inputs / sources:
   - This goal file, current `main`, active milestone branch/PR, relevant scripts/tests/docs, GitHub CI/reviews, and read-only live-state inventories.
3. Triage and orchestration:
   - Execute milestones in order. Convert each failing gate into a bounded fix inside the same milestone. Do not begin a later milestone while the current gate is unresolved.
4. Worktree and isolation:
   - Use one dedicated branch per milestone or tightly coupled batch. Serialize edits to shared refresh/check/wrapper or Watcher-runtime files. Preserve unrelated dirty work.
5. Skills and context:
   - Always read `long-running-goal`; use `code-review` for Standards/Contract review, `diagnosing-bugs` for failures, `writing-for-agents` only when instruction surfaces are necessarily changed, and `housekeeping` only in the separately authorized M6 ownership scope.
6. Connector read/write boundaries:
   - Pre-approved: repository reads, branches, commits, Draft PR creation/update, CI reads, and PR review metadata.
   - Not pre-approved: merging future implementation PRs, modifying real user installation state, sending external messages, or deleting runtime/config/cache paths.
7. Independent verification:
   - Each source milestone requires focused tests, applicable full suites, scoped static checks, and an independent read-only Contract review. M5/M6 require a separate read-only cutover/deletion review before apply.
8. Runtime hard stops:
   - Missing real-machine access or required credentials; evidence that changes the frozen authority/identity semantics; an unclassified active plugin; an unmanaged conflicting discovery entry; a destructive/external action without explicit authorization; or three distinct in-scope diagnostic/fix attempts with no safe next step.
9. Durable learning:
   - Update this goal, focused tests, current README/runbook/ADR surfaces, validation evidence, and the reusable prompt for the next milestone. Do not leave decisions only in chat or PR comments.

## Pre-Approval / YOLO Boundary

1. Pre-approved YOLO local operations:
   - Repository code/docs/test edits for M1-M4, branch creation, local dependency restore, focused/full tests, lint/format/static checks, read-only inventories, generated test fixtures, Git commits, pushes, Draft PR updates, and fixes inside the current milestone.
   - No real plugin/cache/config/hook/link mutation is implied before M5.
2. Pre-approved external reads/writes:
   - GitHub repository reads; branch/commit/push operations; Draft PR creation and updates; CI/review reads. Future implementation PR merge remains a user authorization gate unless a newer request explicitly pre-approves it.
3. Runtime hard stops:
   - M5 apply authorization; M6 deletion authorization; unclassified ownership; identity/consumer conflict; inaccessible required machine state; unsafe transition ordering; or repeated technical impossibility with no in-plan fallback.
4. Non-stops:
   - Milestone boundaries, checkpoints, expected test failures with a clear local fix, rebase/update of a clean milestone branch, docs synchronization, timing rebaseline, or review findings that can be fixed inside the frozen milestone.

## Goal Execution Contract

1. Execute strictly `M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> Close`.
2. Update the status table and the current milestone evidence before and after work.
3. A milestone reaches `Done` only when its review gate passes, checkpoint evidence is recorded, and required current docs are synchronized.
4. Use the smallest falsifying validation first, then broader suites required by the milestone.
5. Keep source authority and installed/runtime state as separate evidence domains.
6. Do not merge a milestone PR when its branch is internally inconsistent or its active entry points are broken.
7. Do not use simultaneous plugin/universal skill injection as a diagnostic shadow mode. M5 comparisons use sequential isolated sessions or restored profiles.
8. Do not delete old runtime paths until M6 observation and ownership gates pass.
9. Record root cause, failed command, paths, breakpoint, and next fix for every material failure.
10. Only runtime hard stops require user input; ordinary local fixes continue within scope.

## Status Definitions

| Status | Meaning |
| --- | --- |
| `Not Started` | Scope is frozen but implementation has not begun. |
| `In Progress` | The milestone owns current implementation/review work. |
| `Blocked` | A documented runtime hard stop prevents safe progress. |
| `Done` | Scope, review, validation, evidence, docs, and checkpoint are complete. |

## Milestone Status

| Milestone | Status | Review | Checkpoint |
| --- | --- | --- | --- |
| M0 Contract and Plan Freeze | Done | Passed | Done |
| M1 Phase 1b Integrated Profile-Aware Source Landing | Not Started | Pending | Pending |
| M2 Watcher Metadata and Shared-Runtime Decoupling | Not Started | Pending | Pending |
| M3 Physical Layout Decision and Conditional Migration | Not Started | Pending | Pending |
| M4 Optional Codex Adapter and Distribution Packaging | Not Started | Pending | Pending |
| M5 Controlled Universal Profile Cutover | Not Started | Pending | Pending |
| M6 Obsolete Marketplace Runtime Cleanup | Not Started | Pending | Pending |
| Close Goal Closure and Archive | Not Started | Pending | Pending |

## M0 Contract and Plan Freeze

Status: `Done`

Scope:

- Freeze authority, identities, compatibility, discovery profiles, milestone order, validation model, rollback, and authorization boundaries.
- Preserve the incomplete Phase 1 prototype on an archive branch rather than merging it into `main`.
- Replace the incomplete source PR with this plan and reusable Phase 1b prompt.

Review gate:

- `main` receives only plan/prompt/index changes.
- Original Phase 1 source remains recoverable at `archive/universal-phase1-candidate-20260820`.
- PR #4 closes without merging known-broken refresh/check integration.

Validation:

```bash
python plugins/workflow/skills/long-running-goal/scripts/check_goal_ready.py docs/todo/universal-agent-skills-migration.md
python plugins/workflow/skills/long-running-goal/scripts/check_md_links.py docs/todo
python plugins/workflow/skills/long-running-goal/scripts/check_todo_index.py --mode active docs/todo/universal-agent-skills-migration.md docs/todo/README.md
git diff --check
```

Evidence:

- Baseline: `main@8e29df2faeffb2b0dc3a8b202e3293d00ce2191a`.
- Prototype archive: `archive/universal-phase1-candidate-20260820@1faa330442f2899f3ed5d2b740465132ce3ff51f`.
- Reusable prompt: `dev_docs/prompt/universal-agent-skills-phase-1b.md`.

Checkpoint evidence: `The plan-only PR merge commit and GitHub history are the M0 revision checkpoint; no empty commit is required.`

Rollback: `Revert the plan-only merge. The archived prototype branch remains unchanged.`

Hard stop: `The PR diff contains any Phase 1 runtime/source implementation file or modifies a frozen SKILL.md.`

## M1 Phase 1b Integrated Profile-Aware Source Landing

Status: `Not Started`

Objective: Land the repository-derived catalog and managed projection together with all refresh/check/wrapper callers so the source batch is internally consistent before merge.

Scope:

1. Start from current `main`; inspect and selectively reuse the archived Phase 1 prototype and the Phase 1b patch evidence.
2. Derive the canonical catalog from `plugins/*/skills/*/SKILL.md` and frontmatter identity, independent of marketplace metadata.
3. Add one shared explicit discovery-profile policy supporting only `universal` and `plugin`.
4. Update `sync_agents_skills.py`, `refresh_my_codex.py`, `check_my_codex.py`, `upgrade_my_codex.sh`, and `upgrade_my_codex.ps1` as one integrated contract.
5. Reject legacy skip-flag combinations that can create dual-active or zero-active discovery.
6. Keep all real installation-state changes out of this milestone.

Non-scope:

- Watcher metadata internals, plugin packaging redesign, real cutover, cleanup, skill relocation, or identity changes.

Preconditions:

- Current branch is based on current `main` and has no unclassified dirty changes.
- The archived prototype and Phase 1b prompt are read as evidence, not blindly applied.
- Every existing refresh/check/wrapper caller is inventoried.

Required transition semantics:

- Plugin to universal: preflight universal targets -> remove exact enabled skills-bearing plugins -> create/repair repo-owned links -> closure check.
- Universal to plugin: preflight adapter/package -> remove only repo-owned universal links -> install/enable plugin profile -> closure check.
- Never create a temporary dual-active state; never remove the only active path before the replacement passes its preflight.

Minimal falsifying validation:

```bash
python3 -m unittest -v \
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
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s plugins/workflow/tests -p 'test_*.py' -v
python3 -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v
python3 -m py_compile scripts/repo_skill_catalog.py scripts/skill_discovery_profiles.py scripts/check_skill_discovery.py scripts/sync_agents_skills.py scripts/discovery_profile_runtime.py scripts/refresh_my_codex.py scripts/check_my_codex.py
git diff --check
```

Review gate:

- Independent read-only review confirms invocation identity, ownership/prune safety, wrapper parity, bypass rejection, and transition ordering.
- Universal closure does not require marketplace/cache/Codex CLI when no plugin removal is needed.
- Plugin closure compares installed/cache identities to canonical repository source.
- Existing public entry points have no missing required arguments.

Evidence to record:

- Scoped diff, focused/full test logs, CLI help output, Unix/PowerShell wrapper tests, failure-injection ordering evidence, and a real-environment read-only discovery inventory.

Checkpoint evidence: `M1 commit(s), PR URL, merge authorization/result, focused/full validation logs, and remaining runtime blockers.`

Rollback: `Revert the source PR. Because M1 performs no real cutover, no user installation rollback is required.`

Hard stops:

- Any callable/Watcher identity drift; an unmanaged target would be overwritten; wrapper parity cannot be established; a failure path can leave both or neither discovery path active; or the real environment exposes an unclassified enabled plugin.

Authorization/review: `Repository source work and Draft PR are pre-approved. Merge requires user authorization after the gate passes.`

Completion criterion: `The integrated source PR is merged to main, all callers use the explicit profile contract, and no runtime state was activated.`

## M2 Watcher Metadata and Shared-Runtime Decoupling

Status: `Not Started`

Objective: Make Watcher core work from canonical repository source and stable runtime locators without marketplace catalog or plugin-cache authority.

Scope:

1. Replace Watcher callable-skill enumeration through marketplace/plugin manifests with the canonical repository catalog.
2. Retain role, aliases, supporting skills, logical groups, and legacy names as a separately owned attribution overlay.
3. Resolve repository/shared runtime through an explicit repo root or installed adapter contract, not by assuming a plugin cache path.
4. Keep `$CODEX_HOME/watcher` as runtime state only.
5. Preserve historical logs and namespaced identities without rewriting events.
6. Update Watcher doctor, SessionStart metadata refresh, CLI, docs, and tests.

Non-scope:

- Callable identity rename, log rewrite, physical skill relocation, real profile cutover, or old-cache deletion.

Preconditions:

- M1 merged; repository catalog API and explicit profiles are stable.
- Existing Watcher metadata schema, legacy mappings, runtime paths, and consumers are inventoried.

Minimal falsifying validation:

- Temporarily remove or point away the marketplace catalog in a fixture; Watcher metadata discovery and reports still resolve the canonical skill set.
- Existing namespaced identities and legacy mappings produce the same canonical attribution.
- Running from repository source and from the planned adapter location resolves the same shared runtime modules/assets.

Broader validation:

```bash
python3 -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 plugins/watcher/scripts/watcher skill doctor
python3 plugins/workflow/skills/long-running-goal/scripts/check_md_links.py plugins/watcher
```

Review gate:

- Standards review confirms one owner for callable catalog and one owner for non-callable attribution metadata.
- Contract review confirms no marketplace read is required for core Watcher operation, no persisted identity changes, and no runtime cache becomes source authority.

Evidence to record:

- Metadata fixture comparison, legacy-name tests, report snapshots/diffs, runtime-locator tests, doctor output, and updated Watcher architecture docs.

Checkpoint evidence: `M2 commits, PR/merge record, metadata comparison evidence, and runtime-locator validation.`

Rollback: `Revert M2 while remaining on a non-cutover environment. Do not rewrite runtime logs during rollout, so source rollback is sufficient.`

Hard stops:

- Historical attribution would change; metadata overlay requires a second callable catalog; runtime cannot be located without cache authority; or a migration would rewrite existing logs/proposals.

Authorization/review: `Source/Draft PR work is pre-approved. Merge requires user authorization and independent review because hooks/routing/persisted interpretation are affected.`

Completion criterion: `Watcher core, doctor, reports, and metadata refresh pass with marketplace catalog absent, while all existing durable identities remain stable.`

## M3 Physical Layout Decision and Conditional Migration

Status: `Not Started`

Objective: Decide from evidence whether `plugins/*/skills` remains the canonical physical layout; move only when a proven portability or packaging blocker cannot be solved cleanly in place.

Default decision: `No move required`

Decision gate:

1. Inventory symlink resolution, shared-runtime references, updater assumptions, plugin validation, and external path consumers after M2.
2. Record concrete blockers that are caused by physical layout rather than dependency direction.
3. If no blocker exists, mark M3 Done with a no-change ADR/update and proceed.
4. If a move is necessary, create a separately reviewed path migration preserving invocation identities and deriving optional packages from the new authority.

Minimal falsifying validation:

- All skill-local references/scripts/assets resolve through universal links.
- Watcher and updater tests pass without relying on physical plugin-cache location.
- No current external consumer requires a new top-level path.

Review gate:

- A move is accepted only when evidence names the blocker, explains why in-place resolution is insufficient, inventories every path consumer, and provides an atomic rollback.
- Directory aesthetics, convention preference, or shorter paths are insufficient reasons.

Evidence to record:

- Portability matrix, path-consumer search, symlink resolution tests on supported platforms, decision ADR/update, and any migration mapping.

Checkpoint evidence: `M3 no-change decision or path-migration PR, validation evidence, and compatibility review.`

Rollback: `No-change branch requires no rollback. A move must be atomic and revertible without identity changes.`

Hard stops:

- An external/persisted path consumer lacks a migration plan; Matt mirror ownership would be violated; invocation identity would change; or Windows projection behavior is unproven for a proposed move.

Authorization/review: `No-change decision is pre-approved after review. Any physical relocation requires explicit user authorization before mutation and merge.`

Completion criterion: `The physical authority decision is documented and validated; either the current layout is retained or an explicitly authorized migration is merged without identity drift.`

## M4 Optional Codex Adapter and Distribution Packaging

Status: `Not Started`

Objective: Isolate genuinely Codex-specific capabilities from universal skill discovery and make marketplace/plugin packaging optional.

Preferred target:

- A zero-skill Codex adapter owns hooks, Codex event normalization, configuration integration, and optional UI metadata.
- Universal skills continue to come only from `~/.agents/skills`.

Compatibility target:

- If a skills-bearing plugin profile must remain, it is generated or validated directly from canonical repository source, is never a second hand-maintained catalog, and is mutually exclusive with universal links.

Scope:

1. Define adapter identity, contents, build/validation path, and install/check contract.
2. Remove skill injection from the zero-skill adapter.
3. Keep Watcher core/shared runtime independent of adapter cache location.
4. Update marketplace/install metadata so distribution artifacts are explicit profile outputs.
5. Add package-content and coexistence tests.

Minimal falsifying validation:

- Zero-skill adapter package contains no `skills/` injection surface.
- Universal profile plus zero-skill adapter exposes each skill once and preserves hooks.
- Optional skills-bearing plugin package validates independently and fails closed when universal links are active.
- Package identities and source versions derive from repository authority.

Review gate:

- Adapter boundaries are Codex-specific and do not become a new runtime/source authority.
- No second skill catalog, fallback discovery, or duplicate injection path is introduced.

Evidence to record:

- Package manifest/tree inventory, build commands, hook tests, universal-plus-adapter discovery inventory, plugin-profile inventory, and rollback commands.

Checkpoint evidence: `M4 commits/PR, built artifact identity, package-content checks, and coexistence/mutual-exclusion evidence.`

Rollback: `Uninstall or disable the adapter package; canonical source and universal projection remain intact. Restore the previous optional plugin package only in plugin profile.`

Hard stops:

- Codex requires the adapter to package overlapping skills; hook operation still depends on marketplace catalog; package build requires a second catalog; or adapter removal would lose core Watcher data.

Authorization/review: `Source/package work and Draft PR are pre-approved. Installing a real adapter or merging a packaging change requires user authorization after independent review.`

Completion criterion: `Optional Codex packaging builds and validates independently, with a zero-skill adapter preferred and no possible active overlap with universal skills.`

## M5 Controlled Universal Profile Cutover

Status: `Not Started`

Objective: Move one real, rollback-capable environment from the skills-bearing plugin profile to the universal profile and prove exact-once discovery and behavior.

Production-cutover adaptation:

- Simultaneous full-shadow skill injection is forbidden because it violates the frozen single-active-path contract.
- Comparison uses sequential isolated sessions: baseline plugin profile, candidate universal profile, and rollback rehearsal/profile restoration.

Preconditions:

1. M1-M4 are Done and merged.
2. Real machine access, Codex CLI capabilities, repository checkout, and rollback artifacts are available.
3. Read-only inventory records exact `pwd`, repo/HEAD/upstream/dirty state, `~/.agents/skills`, Codex config, enabled plugins, cache versions, hooks, Watcher state, and visible skill inventory.
4. No unmanaged same-name skill or unclassified enabled my-codex plugin remains unresolved.
5. The user explicitly authorizes the apply step after reviewing the plan and inventory.

Comparison matrix:

| Mode | Active skills path | Purpose | Required evidence |
| --- | --- | --- | --- |
| Baseline plugin | Skills-bearing plugin only | Capture current behavior and rollback baseline | Exact inventory, invocation checks, Watcher health |
| Candidate universal | `~/.agents/skills` only; optional zero-skill adapter allowed | Target production behavior | Exact-once inventory, explicit/implicit routing, symlink/resource resolution |
| Rollback rehearsal | Restored plugin profile in an isolated/reversible step | Prove recovery | Restoration commands, identity inventory, no data loss |

Apply sequence after authorization:

1. Revalidate source and target conflicts.
2. Back up relevant configuration and record current plugin/link state without copying source skills.
3. Disable/remove exact skills-bearing plugins.
4. Verify the old active discovery path is inactive.
5. Create/repair only repository-owned universal links.
6. Keep or install only the validated zero-skill Codex adapter when applicable.
7. Restart Codex/harness.
8. Validate discovery, invocation behavior, resource resolution, Watcher core, hooks, and rollback readiness.

Minimal falsifying validation:

- Every canonical skill appears exactly once.
- Removing/disablement of the personal marketplace does not remove universal skills.
- Explicit invocation and preserved implicit routing match the baseline.
- Every referenced script/reference/template/asset resolves from symlink invocation.
- Universal profile works with plugin cache absent from the validation fixture or isolated environment.
- Watcher core functions without marketplace catalog authority.

Review gate:

- Independent read-only reviewer verifies inventory, sequence, backup, exact mutation set, validation commands, and rollback before apply.
- Post-apply comparison matrix has no critical regression or duplicate/missing identity.

Evidence to record:

- Before/after config and link inventories, `codex plugin list`, cache inventory, visible skill list, invocation scenarios, Watcher doctor/report output, hook checks, and rollback rehearsal result.

Checkpoint evidence: `M5 authorized cutover record, exact commands, before/after evidence, user authorization context, and rollback rehearsal.`

Rollback:

1. Remove only repository-owned universal links.
2. Restore the exact known-good marketplace/plugin configuration and package version.
3. Restart Codex.
4. Verify plugin profile closure and Watcher health.
5. Preserve failure evidence for M5 rework.

Hard stops:

- No explicit user apply authorization; backup/rollback cannot be proven; unmanaged conflict; unknown plugin; required CLI or machine access missing; sequential comparison cannot establish exact-once discovery; or the next action would remove the only active path without a preflighted replacement.

Authorization/review: `Read-only inventory is pre-approved. Apply is not authorized by this goal file and requires a fresh explicit user instruction.`

Completion criterion: `The real environment runs universal profile with exact-once discovery, preserved invocation behavior, working resources/Watcher/adapter, and a proven rollback path.`

## M6 Obsolete Marketplace Runtime Cleanup

Status: `Not Started`

Objective: Remove only obsolete, owned marketplace/plugin runtime paths after universal production stability is demonstrated.

Preconditions:

1. M5 is Done.
2. Universal profile has passed at least five successful sessions across at least three working days, including explicit invocation, implicit routing, Watcher core, and hook/adapter checks.
3. No core code/doc/test reads the candidate old path.
4. A read-only deletion inventory and independent ownership review are complete.
5. The user explicitly authorizes the exact deletion set.

Scope candidates:

- Disabled stale my-codex skills-bearing plugin config.
- Superseded owned cache versions and marketplace snapshots.
- Old runtime/source-assumption code and active docs proven unused.
- Legacy validation expectations that require plugin cache in universal profile.

Protected state:

- Unrelated plugins/marketplaces, unmanaged skills, Watcher logs/reports/proposals, rollback evidence still inside the observation window, source checkout, user/private config unrelated to my-codex, and historical docs.

Minimal falsifying validation:

- Repository-wide path/term scan finds no active consumer.
- Universal closure passes before deletion.
- Exact owned deletion plan contains no symlink/junction/reparse escape.
- Universal closure, invocation scenarios, Watcher health, and adapter checks pass after deletion and restart.

Review gate:

- Independent deletion review classifies every path as owned, obsolete, and recoverable or no longer required.
- No wildcard/broad-root deletion is accepted without an exact bounded inventory.

Evidence to record:

- Observation log, deletion inventory, ownership evidence, authorization, before/after sizes and paths, commands, restart validation, and residual rollback assets.

Checkpoint evidence: `M6 cleanup commit/config record, authorized deletion log, post-cleanup validation, and final retained-state inventory.`

Rollback: `Restore the known-good plugin/profile artifact only if post-cleanup universal validation regresses; otherwise source remains universal and old cache stays removed.`

Hard stops:

- Explicit deletion authorization missing; ownership uncertain; any current consumer remains; observation window incomplete; deletion would affect unrelated sources or durable Watcher evidence; or rollback artifact must still be retained.

Authorization/review: `No mutation is authorized until the exact deletion set receives fresh user approval and independent read-only review.`

Completion criterion: `Only obsolete owned marketplace runtime paths are removed, universal profile still passes the full oracle, and no source/cache/runtime authority ambiguity remains.`

## Close Goal Closure and Archive

Status: `Not Started`

Close prerequisites:

1. M1-M6 are `Done`, `Review=Passed`, and `Checkpoint=Done`.
2. The frozen acceptance oracle below has evidence.
3. Root README, relevant plugin/Watcher docs, wrappers, and runbooks describe the target architecture.
4. Active TODO navigation points only to current work.
5. No task temporary cache cleanup is attempted because the policy is `Not applicable`.

Frozen acceptance oracle:

- Git is the only skill source authority.
- Removing/disabling the personal marketplace does not prevent Codex from discovering repository skills through `~/.agents/skills`.
- Every canonical skill appears exactly once in the discovery/prompt inventory.
- Explicit invocation and preserved implicit routing do not regress.
- Symlink-invoked scripts, references, templates, assets, and harness metadata resolve.
- Universal profile requires no plugin cache.
- Watcher core requires no marketplace catalog.
- Optional plugin profile builds independently and is mutually exclusive with universal skills.
- Any zero-skill Codex adapter can coexist without overlapping skill injection.
- Installer/sync modifies only repository-owned links and fails closed on conflicts.
- No dangling links, second catalog, dual runtime authority, or source/cache confusion remains.
- The merged slimming behavior is preserved.
- Invocation/routing, hook, permission, transition, and deletion changes received independent read-only review.

Final validation:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s plugins/workflow/tests -p 'test_*.py' -v
python3 -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v
python plugins/workflow/skills/long-running-goal/scripts/check_goal_ready.py docs/todo/universal-agent-skills-migration.md
python plugins/workflow/skills/long-running-goal/scripts/check_md_links.py docs/todo
python plugins/workflow/skills/long-running-goal/scripts/check_todo_index.py --mode closed --archived-goal docs/todo/archive/universal-agent-skills-migration.md docs/todo/universal-agent-skills-migration.md docs/todo/README.md
git diff --check
```

Close actions:

1. Record final comparison, validation, rollback, observation, and retained-state evidence.
2. Move this file to `docs/todo/archive/universal-agent-skills-migration.md`.
3. Replace the active index entry with an archive entry and remove stale active prompts/navigation when no longer useful.
4. Close remaining completed PRs/issues and delete temporary implementation branches when supported and explicitly in scope.
5. Mark overall status `Closed` only after the archive/index gate passes.

Close checkpoint evidence: `Final merge/revision, archive path, closed PRs, validation logs, acceptance matrix, and retained rollback evidence.`

Close rollback: `Restore the active goal/index entry if closure validation reveals incomplete work; do not reopen old runtime authority silently.`

## Recommended Continuation Prompt

```text
Continue the long-running goal at docs/todo/universal-agent-skills-migration.md.

Read the newest user request first and confirm it still advances the same universal Agent Skills migration. Read the goal file, root AGENTS.md, current main/branch/PR state, and the source/testing surfaces named by the first non-Done milestone. Do not rely on chat history.

Execute only the first non-Done milestone. Preserve the Git-only source authority, callable and Watcher identities, frozen slimming baseline, one-active-discovery-path invariant, unmanaged-user-state protection, and milestone-specific authorization boundary. Use local YOLO operations inside the frozen scope, continue through ordinary failures when the next local diagnostic is clear, and stop only at a recorded runtime hard stop.

Before marking the milestone Done, run its minimal falsifying checks, required broader validation, independent read-only Contract review, docs synchronization, and checkpoint evidence. Do not perform real runtime cutover or deletion unless the current milestone explicitly requires it and the goal records fresh user authorization.

For M1, also use dev_docs/prompt/universal-agent-skills-phase-1b.md as the implementation handoff and treat archive/universal-phase1-candidate-20260820 as prototype evidence rather than merge-ready source.
```
