# Skill Instruction Slimming Plan

Status: **Active — source implementation complete; macOS validation delegated to active long-running goal; merge/archive pending**

Updated: 2026-08-21

Baseline: `main@4c80da5a04ce190f8a5ee17024da99628a772adc`

Candidate: `agent/skill-slimming-s0-s1` / PR #13

Execution handoff: `docs/todo/skill-slimming-macos-validation-goal.md`

This document is the single active design and semantic authority for repository-owned instruction slimming. S0-S4 source implementation is complete in the candidate branch. The companion macOS validation goal owns checkout isolation, full validation, bounded repair, independent review, behavioral sampling, evidence writeback, and the PR #13 Draft-to-Ready transition. PR merge and this parent plan's archive remain outside that validation goal.

## Objective

Reduce model-facing instruction load while preserving routing, authority, failure behavior, validators, identities, universal discovery, and user-visible workflow guarantees.

The target is a set of deep instruction modules:

- compact always-loaded descriptions;
- small `SKILL.md` entry interfaces;
- complete conditional branches behind one-level references;
- field and format contracts owned by templates, scripts, schemas, and checkers;
- one authoritative owner for each global or workflow-specific meaning.

Size is a triage signal, not the acceptance oracle.

## Frozen Baseline

PR #3 remains the accepted low-risk baseline for:

- `summary-in-html`;
- `sop`;
- `housekeeping`;
- `prompt-strategy-loop`;
- `skill-compressor`.

Those bodies remain unchanged in this candidate. `skill-maintainer` remains the no-change baseline.

The completed universal Agent Skills migration remains authoritative:

- repository `SKILL.md` files are the only canonical skill source;
- `plugins/*/skills/*` remains the physical authority;
- ADR-0004 owns native qualified invocation identity behavior;
- Watcher derives callable inventory from repository authority;
- Watcher overlays own durable attribution identity and aliases;
- marketplace and plugin cache are not source authority.

No identity, invocation mode, universal discovery, hook, cache, installed state, or Matt Pocock mirror content changes in this plan.

## Instruction Ownership

| Meaning | Authoritative owner |
| --- | --- |
| Global mutation, privacy, external-write, irreversible, failure, test, delegation, and subagent-failure policy | root `AGENTS.md` |
| Repository support paths, sync, built-in roles, and assignment labels | `agents/operating-principles.md` |
| Subagent slicing, assignments, disjoint worker ownership, waiting, and consolidation | `orchestrate-subagents` and `references/subagent-recipes.md` |
| Documentation truth and report-only versus implementation mode | `doc-alignment` |
| Watcher audit commands, profiles, and trust boundary | `doc-alignment/references/watcher-audit.md`, Watcher README, scripts, and `--help` |
| Documentation classification, severity, reporting, and surface validation | `doc-alignment/references/alignment-reference.md` |
| Goal lifecycle, Ready/Draft, request supersession, branch routing, execution authority, and goal-tool boundary | `long-running-goal` |
| Goal fields and structural readiness | goal templates and checkers |
| Planning preflight detail | `components/planning-preflight.md` |
| Goal branch implementations | `references/create-and-loop.md`, `sequence-child-goals.md`, `production-cutover.md`, and `execute-and-close.md` |
| Callable catalog names | `SKILL.md` frontmatter |
| Native runtime-qualified identities | Codex runtime and ADR-0004 |
| Durable Watcher attribution identities | repository `skill-watcher.json` overlays |

## Frozen Semantic Oracle

The candidate must preserve:

1. Frontmatter names, Watcher namespaced identities, aliases, distribution identities, and model-invocation modes.
2. Explicit user-triggered `$orchestrate-subagents` routing; tool availability and task parallelism alone remain non-triggers.
3. Broad read-only review authorization without cross-invoking `$orchestrate-subagents`.
4. Parent planning, judgment, integration, cross-slice validation, and user-facing ownership.
5. Exact disjoint worker write ownership and visible partial or blocked results.
6. `doc-alignment` report-only and scheduled read-only behavior; implementation requires user intent.
7. `long-running-goal` Ready/Draft, request supersession, planning preflight, sequence, cutover, checkpoint, execution authority, runtime hard stops, task-temporary-cache policy, goal-tool boundary, and close behavior.
8. Universal symlink resolution of references, scripts, templates, assets, and interface metadata.
9. The five PR #3 skill interfaces remain unchanged.

Tests protect semantic reachability and owner boundaries rather than historical heading placement.

## Batch Status

| Batch | Scope | Status |
| --- | --- | --- |
| S0 | Rebaseline, archive stale plans, establish semantic oracle | Source implemented; focused validation passed |
| S1 | Global delegation ownership and `orchestrate-subagents` | Source implemented; focused validation passed |
| S2 | `doc-alignment` entry interface and conditional operations disclosure | Source implemented; focused validation passed |
| S3 | `long-running-goal` high-risk entry-interface reduction | Source implemented; focused semantic validation passed |
| S4 | Metadata/docs alignment, aggregate validation, and close preparation | Source implemented; macOS validation goal pending |

## S0 — Rebaseline And Oracle

Implemented:

- replaced the pre-universalization active review with this stable-named plan;
- archived the historical second-pass review and PR #3 handoff without rewriting them;
- updated active and archive indexes;
- added semantic ownership tests;
- froze PR #3 skill bodies and `skill-maintainer`.

## S1 — Delegation Ownership And Orchestration

Implemented:

- `agents/operating-principles.md` is now a repository map rather than a duplicate global policy;
- root `AGENTS.md` remains the authority for delegation, mutation, failure, and parent accountability;
- `orchestrate-subagents/SKILL.md` keeps only the explicit trigger, minimum-useful parallelism, local invariants, one reference pointer, and completion;
- the full assignment contract lives in `references/subagent-recipes.md`;
- invocation and failure semantics are protected by semantic tests.

Size:

| Surface | Before | Candidate | Change |
| --- | ---: | ---: | ---: |
| `agents/operating-principles.md` | 8,429 | 4,359 | -48.3% |
| `orchestrate-subagents/SKILL.md` | 4,296 | 2,490 | -42.0% |
| `subagent-recipes.md` | 8,627 | 9,400 | +9.0% conditional detail |

## S2 — `doc-alignment` Deep Interface

Implemented:

- entry interface now owns source-of-truth, mode, scheduled read-only safety, common workflow, two one-hop pointers, and completion;
- new `references/watcher-audit.md` owns deterministic Watcher audit commands, profile-set behavior, trust boundary, change-alignment semantics, due/skip accounting, existing-report routing, and report review;
- `references/alignment-reference.md` owns inventory, file roles, recursive organization, severity, report shape, script/tree/TODO/skill alignment, and validation;
- disclosure tests now verify reachability, one-level ownership, report-only safety, and unchanged identities rather than historical headings.

Size:

| Surface | Before | Candidate | Change |
| --- | ---: | ---: | ---: |
| `doc-alignment/SKILL.md` | 6,938 | 3,399 | -51.0% |
| `alignment-reference.md` | 6,475 | 8,921 | +37.8% conditional detail |
| `watcher-audit.md` | — | 3,155 | new conditional branch |

## S3 — `long-running-goal` High-Risk Reduction

Implemented:

- entry interface now contains the lifecycle trigger and Ready contract, exact planning-area fallback, request supersession, branch routing, execution authority, runtime hard stops, task-temporary-cache boundary, native goal-tool boundary, deterministic validation entry points, and completion;
- templates and checkers remain the field and structural owners;
- existing branch references remain the detailed owners for create/Loop, sequence, production cutover, execute/evolve/checkpoint, and close;
- duplicated field checklists, component explanations, detailed operation catalogs, helper explanations, and the 11-question Quality Bar were removed from the entry interface;
- semantic tests retain the three-attempt hard-stop threshold, preflight timing, housekeeping, sequence aliases and registers, branch completion, planning-path constraints, goal-tool token-budget rule, and identity behavior.

Size:

| Surface | Before | Candidate | Change |
| --- | ---: | ---: | ---: |
| `long-running-goal/SKILL.md` | 11,148 | 6,723 | -39.7% |

## S4 — Final Alignment And Validation Boundary

Implemented:

- root `AGENTS.md` was re-read and remains unchanged; its global guardrails have no proven residual duplication requiring mutation;
- `long-running-goal/agents/openai.yaml` now matches the compact lifecycle interface;
- Workflow README describes the current lifecycle without repeating field-heavy implementation detail;
- Watcher README and both attribution overlays were inspected and remain semantically aligned; no identity or alias edit is required;
- invocation tests now bind `long-running-goal` frontmatter description to its interface metadata;
- this plan and TODO navigation record the complete candidate and the remaining validation/close gate.

Aggregate primary-entry result:

```text
agents/operating-principles.md
+ orchestrate-subagents/SKILL.md
+ doc-alignment/SKILL.md
+ long-running-goal/SKILL.md

30,811 bytes -> 16,971 bytes (-44.9%)
```

The nine repository-owned `SKILL.md` bodies fall by approximately 9.8 KB, from about 37.9 KB to about 28.1 KB. Conditional references grow where branch completeness requires it; this is intentional because they are loaded only after a matching trigger.

## Validation Completed In The Source-Review Environment

The exact candidate text passed isolated semantic tests for:

- S0/S1 invocation and ownership;
- `doc-alignment` entry, Watcher operations reference, classification reference, and identity;
- `long-running-goal` lifecycle entry, branch pointers, exact planning-area fallback, sequence identity/aliases, planning preflight timing, temporary-cache policy, goal-tool behavior, and branch completion;
- `long-running-goal` metadata alignment.

Also completed:

- Python syntax compilation for changed tests;
- support-note sync dry-run, apply, and `--check --prune` against a temporary target;
- changed Markdown relative-link inspection;
- whitespace validation equivalent to `git diff --check`;
- a separate read-only Standards/Contract pass by the same agent.

Reviewer-independence limitation: no independent subagent runtime was used. This limitation is owned by the companion macOS validation goal.

## macOS Validation Execution Handoff

Execute:

```text
docs/todo/skill-slimming-macos-validation-goal.md
```

That Ready long-running goal owns:

- live macOS checkout/worktree isolation;
- exact PR scope and frozen-surface audit;
- focused/root/Workflow/Watcher tests;
- deterministic/link/support/Watcher/plugin/skill validation;
- installed-state and universal-resource read-only classification;
- independent Contract review;
- five behavior scenarios in a proven candidate-loaded context;
- minimal PR-introduced repair and full revalidation;
- durable validation evidence, validation-goal archive, and PR #13 Draft-to-Ready.

It explicitly does not own PR merge, main mutation, installed/runtime activation, identity changes, universalization changes, or PR #3 skill-body edits.

## Behavioral Matrix

| Scenario | Required behavior |
| --- | --- |
| Ordinary complex implementation | Does not automatically become a long-running goal |
| Explicit goal creation | Selects create/preflight and produces a complete Draft or Ready contract |
| Resume an existing goal | Applies request supersession before milestone work |
| Recoverable local failure | Continues while a clear in-scope diagnostic or fix exists |
| Explicit subagent request | Dispatches the minimum useful bounded assignments |
| Broad read-only review | May delegate under root authority without invoking orchestrate |
| Report-only documentation audit | Leaves target repositories unchanged |
| Documentation implementation | Edits the narrowest owner and runs focused validation |
| Universal-profile invocation | Preserves qualified identity, bare request resolution, and implicit routing |
| Symlink-invoked resource | Resolves references, scripts, templates, assets, and metadata |

## Rollback

The candidate is source-only. Revert the S0-S4 commits; no installed, hook, cache, or runtime rollback is required because activation is outside PR #13.

## Close Gate

Keep this parent plan active while the companion validation goal is active.

After the validation goal closes successfully, PR #13 may be Ready but remains unmerged. Merge requires a separate user decision. After PR #13 is merged and `main` is verified, move this parent file to `docs/todo/archive/skill-slimming-plan.md`, replace the active TODO entry with an archive entry, and record the merged revision and final validation evidence.
