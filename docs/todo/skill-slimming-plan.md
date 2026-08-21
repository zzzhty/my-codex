# Skill Instruction Slimming Plan

Status: **Active**

Updated: 2026-08-21

Baseline: `main@4c80da5a04ce190f8a5ee17024da99628a772adc`

Current implementation: **S0 and S1 source candidate implemented on `agent/skill-slimming-s0-s1`; focused semantic validation passed; merge pending.**

This document is the single active authority for the remaining repository-owned instruction slimming work. It supersedes the historical second-pass review and Batch 1 handoff, which are retained under `docs/todo/archive/`.

## Objective

Reduce the instruction load carried by the model while preserving routing, authority, failure behavior, validators, persisted identities, and user-visible workflow guarantees.

The target is a set of deep instruction modules:

- small always-loaded pointers;
- compact `SKILL.md` entry interfaces;
- complete conditional branches behind one-level references;
- deterministic field and format contracts owned by templates, scripts, schemas, and checkers;
- one authoritative owner for each global or workflow-specific meaning.

Size is a triage signal, not the acceptance oracle. A candidate is accepted only when required behavior remains reachable and unnecessary questions, stops, governance-only steps, or duplicate instruction ownership do not increase.

## Current Baseline

### Completed and frozen

PR #3 completed the low-risk Batch 1 source changes for:

- `summary-in-html`;
- `sop`;
- `housekeeping`;
- `prompt-strategy-loop`;
- `skill-compressor`.

Those five skills remain frozen during S0-S4 unless a regression or a later owning-contract change requires a narrowly scoped fix. `skill-maintainer` remains the no-change baseline.

The universal Agent Skills migration and local cleanup are closed. Current architecture now provides:

- repository `SKILL.md` files as the only canonical skill source;
- the retained `plugins/*/skills/*` physical authority;
- accepted native Codex qualified invocation identities under ADR-0004;
- repository-authoritative Watcher callable catalog and non-callable attribution overlays;
- universal discovery without marketplace or plugin-cache source authority.

Slimming must not reopen those decisions.

### Remaining high-value surfaces

| Surface | Baseline size | Current concern |
| --- | ---: | --- |
| `agents/operating-principles.md` | 8.4 KB | Repeats global policy already owned by root `AGENTS.md` |
| `orchestrate-subagents/SKILL.md` | 4.3 KB | Prompt template and generic delegation policy leak into the entry interface |
| `doc-alignment/SKILL.md` | 6.9 KB | Watcher operations, taxonomy, severity, and reporting detail remain inline |
| `long-running-goal/SKILL.md` | 11.1 KB | Templates, checkers, helpers, quality bar, and global authority remain duplicated inline |

The current nine repository-owned `SKILL.md` bodies total approximately 37.9 KB. The three remaining skill targets account for approximately 22.4 KB, so they dominate the remaining skill-level opportunity.

## Instruction Load Model

### 1. Always-on pointer load

Includes root `AGENTS.md` and model-visible skill descriptions.

Rules:

- one compact description sentence;
- list only distinct invocation branches;
- do not enumerate synonyms, implementation detail, or body identity;
- do not change model-invocation behavior as part of slimming.

### 2. Skill entry-interface load

The top-level `SKILL.md` keeps only:

- trigger and route;
- common execution path;
- non-default invariant;
- true guardrail;
- conditional reference pointer;
- completion criterion.

### 3. Conditional branch load

References may carry substantial detail when:

- the pointer names the trigger condition;
- one reference is complete for that branch;
- references do not form discovery chains;
- the meaning has one owner.

### 4. Deterministic contract load

Templates, scripts, schemas, `--help`, validators, and tests own field shape, command syntax, structural rules, and machine-checkable completion. A skill names when to use the deterministic owner and what passing means; it does not cache the implementation.

## Rule Ownership Map

| Meaning | Authoritative owner |
| --- | --- |
| Global mutation, privacy, external-write, and irreversible boundary | root `AGENTS.md` |
| Global failure handling | root `AGENTS.md` |
| Global test policy | root `AGENTS.md` |
| Delegation authority, parent accountability, and subagent-failure consequence | root `AGENTS.md` |
| Repository support-file paths, sync, built-in roles, and assignment-label mapping | `agents/operating-principles.md` |
| Subagent slicing, assignment contract, disjoint worker ownership, waiting, and consolidation | `orchestrate-subagents` plus `references/subagent-recipes.md` |
| Documentation truth and report-only versus implementation mode | `doc-alignment` |
| Watcher CLI, profiles, runtime paths, and config behavior | Watcher README, skill-local operations reference, scripts, and `--help` |
| Goal lifecycle, request supersession, Ready/Draft meaning, and branch routing | `long-running-goal` |
| Goal fields and structural readiness | goal templates and checkers |
| Planning preflight details | `components/planning-preflight.md` |
| Sequence contract | `references/sequence-child-goals.md` |
| Execution, checkpoint, evolution, and close | `references/execute-and-close.md` |
| Prompt candidate and proportional-review policy | `prompt-strategy-loop` |
| Behavior-preserving instruction reduction | `skill-compressor` |
| Callable catalog name | `SKILL.md` frontmatter |
| Native runtime-qualified identity | Codex runtime and ADR-0004 |
| Durable Watcher attribution identity | repository `skill-watcher.json` overlays |

## Frozen Semantic Oracle

Every batch must preserve or intentionally and separately authorize the following:

1. Frontmatter names, Watcher namespaced identities, legacy aliases, plugin distribution identities, and current model-invocation modes.
2. Explicit user-triggered `$orchestrate-subagents` routing; tool availability or task parallelizability alone remain non-triggers.
3. Broad read-only review authorization from root `AGENTS.md` without automatically invoking `$orchestrate-subagents`.
4. Parent ownership of planning, final judgment, integration, cross-slice validation, and user-facing conclusions.
5. Workers require authorized, exact, disjoint write ownership; shared files and integration remain parent-owned.
6. Timeout, blocked, incomplete, conflicting, and missing-evidence subagent results remain visible as partial or blocked coverage.
7. `doc-alignment` scheduled/report-only modes remain non-mutating; implementation mode requires user intent.
8. `long-running-goal` request supersession, Ready/Draft, planned non-stops, runtime hard stops, planning preflight, sequence, checkpoint, production cutover, and close behavior remain reachable.
9. Universal symlink invocation continues to resolve skill-local references, scripts, templates, assets, and interface metadata.
10. The five PR #3 skill interfaces remain behaviorally stable unless a scoped regression fix is justified.

## Semantic Test Strategy

Tests should protect reachability and ownership, not a historical paragraph layout.

Preferred assertions:

- the global owner contains the global policy;
- the local skill contains its workflow delta;
- the entry interface has an explicit pointer to a complete one-level reference;
- each required branch has a completion criterion;
- identity and invocation metadata remain unchanged;
- relative links resolve;
- duplicated generic sections are not reintroduced.

Avoid tests whose only oracle is that a specific heading or command list must remain inline. When a batch moves detail to its correct owner, update the structural test in the same commit and retain a semantic regression test.

## Batch Status

| Batch | Scope | Status |
| --- | --- | --- |
| S0 | Rebaseline, archive stale planning, establish semantic oracle | Implemented; merge pending |
| S1 | Global delegation ownership and `orchestrate-subagents` deep interface | Implemented; merge pending |
| S2 | `doc-alignment` deep interface and Watcher operations disclosure | Not started |
| S3 | `long-running-goal` high-risk entry-interface reduction | Not started |
| S4 | Final global alignment, metadata/docs sync, validation, and archive | Not started |

## S0 — Rebaseline And Oracle

### Implemented scope

- Created this stable semantic active plan.
- Moved the 2026-08-19 second-pass review and Batch 1 validation handoff to `docs/todo/archive/` without treating them as current execution guidance.
- Updated active and archive indexes.
- Added semantic instruction-ownership tests for root policy, repository support mapping, the orchestrate entry interface, and its assignment reference.
- Froze the five PR #3 skill bodies and `skill-maintainer` as no-change surfaces for the remaining plan.

### Validation

- Active TODO navigation contains one current slimming authority.
- Historical review and handoff remain recoverable in the archive.
- Semantic tests distinguish global authority from local workflow detail.
- No PR #3 skill, Matt Pocock mirror skill, identity overlay, runtime script, hook, cache, or installed state changed.

## S1 — Delegation Ownership And Orchestration

### Implemented scope

#### Repository support note

`agents/operating-principles.md` is now a repository map rather than a second global policy document. It owns:

- managed source and installed target;
- durable owner mapping;
- delegation routing between capability, authority, and skill invocation;
- built-in role and assignment-label mapping;
- custom-agent entry boundary;
- sync and validation commands.

Global mutation, failure, test, delegation, and subagent-failure rules remain in root `AGENTS.md`.

#### Orchestration entry interface

`orchestrate-subagents/SKILL.md` now keeps:

- exact user-requested trigger;
- minimum-useful parallelism;
- parent-owned integration and validation;
- one-task assignment boundary;
- read-only role versus authorized disjoint worker boundary;
- waiting, partial coverage, visible failures, and consolidation;
- one pointer to the recipe and assignment reference;
- one completion oracle.

The full assignment prompt template moved to `references/subagent-recipes.md`, which is the conditional implementation owner.

### Size result

| Surface | Before | Candidate | Change |
| --- | ---: | ---: | ---: |
| `agents/operating-principles.md` | 8,429 bytes | 4,359 bytes | -48.3% |
| `orchestrate-subagents/SKILL.md` | 4,296 bytes | 2,490 bytes | -42.0% |
| `subagent-recipes.md` | 8,627 bytes | 9,400 bytes | +9.0% conditional detail |
| Combined three surfaces | 21,352 bytes | 16,249 bytes | -23.9% |

The entry interface shrinks substantially while the complete assignment contract remains one reference hop away.

### Focused validation

The S0/S1 candidate passed seven focused tests covering:

- summary invocation contract remains unchanged;
- orchestrate trigger remains explicitly user-scoped;
- prompt-strategy evaluator delegation does not cross-invoke orchestrate;
- broad read-only review authority remains separate from skill invocation;
- root global policy and support-note mapping have distinct owners;
- the orchestrate entry interface points to a complete assignment contract;
- delegation authority, one-task assignment, disjoint writes, and visible failure semantics remain reachable.

The unchanged support sync utility also passed a temporary-target `--dry-run`, apply, and `--check --prune` round trip with the candidate note. Candidate files passed whitespace validation equivalent to `git diff --check`.

Required development-checkout command:

```bash
python3 -m unittest -v \
  plugins.workflow.tests.test_invocation_contract \
  plugins.workflow.tests.test_instruction_ownership
```

Before merge, also run the current root, Workflow, and Watcher suites and `git diff --check` in a complete checkout.

### Rollback

Revert the S0/S1 commit set. No runtime or installed-state activation is part of this batch.

## S2 — `doc-alignment` Deep Interface

Target top-level content:

- source-of-truth invariant;
- report-only versus implementation mode;
- scheduled audit read-only boundary;
- compact common workflow;
- conditional pointers;
- completion criterion.

Move Watcher command catalog, profile/config detail, file-role taxonomy, severity taxonomy, recursive organization rules, report fields, and surface-specific validation into two one-level owners:

```text
references/watcher-audit.md
references/alignment-reference.md
```

Update `test_doc_alignment_disclosure.py` from inline-heading assertions to semantic reachability and unique-owner assertions. Preserve mode routing, root-cause repair, and validation behavior.

Review budget: top-level approximately 3.5-4.5 KB. This is a review guide, not a hard gate.

## S3 — `long-running-goal` High-Risk Reduction

Target top-level structure:

```text
Trigger And Ready Contract
Request Supersession
Branch Routing
Execution Authority
Harness Goal Tool Boundary
Completion
```

Keep inline:

- when to use and when not to use;
- Ready versus Draft;
- request supersession;
- routing to create/upgrade/Loop, sequence, production cutover, and execute/resume/evolve/close;
- the core planned-non-stop versus runtime-hard-stop distinction;
- native goal-tool boundary;
- overall completion oracle.

Move or delete duplicate field checklists, template mechanics, detailed operation lists, helper command catalog, quality-bar repetition, and checker-owned structural rules.

Update `test_long_running_goal_disclosure.py` so it protects semantic reachability and the correct owner rather than requiring historical headings inline.

Review budget: top-level approximately 6-8 KB. The current lifecycle is richer than the 2026-08-19 version, so the older 600-900-word target is not binding.

## S4 — Final Alignment And Close

- Recheck root `AGENTS.md` for only residual, proven duplication; do not weaken global guardrails.
- Align `agents/openai.yaml`, Workflow/Watcher README files, Watcher attribution overlays, and active documentation without renaming identities.
- Run the behavioral matrix and current full test suites.
- Record size and behavior results.
- Archive this plan and remove stale active navigation when all batches pass.

## Behavioral Matrix

| Scenario | Required behavior | Friction signal |
| --- | --- | --- |
| Ordinary complex implementation | Does not automatically become a long-running goal | governance detour |
| Explicit long-running-goal creation | Correct create/preflight branch | unnecessary questions or missing contract |
| Resume an existing goal | Request supersession and resume remain correct | false hard stop |
| One recoverable local failure | Continue when a clear in-scope diagnostic exists | premature user prompt |
| Explicit request for subagents | Dispatch the minimum useful bounded assignments | repeated authorization or oversized prompts |
| Broad read-only review | May use authorized reviewers without cross-invoking orchestrate | routing drift |
| Report-only documentation audit | Does not mutate the target repository | mutation regression |
| Documentation alignment implementation | Smallest owner edit plus focused validation | excessive scan or reporting |
| Universal-profile invocation | Qualified identity, bare request resolution, and implicit routing remain stable | identity drift |
| Symlink-invoked skill resources | References, scripts, templates, assets, and metadata resolve | source-root assumption |

Record for each candidate:

- trigger correctness;
- unnecessary user questions;
- unnecessary stops;
- governance-only versus meaningful task steps;
- top-level instruction footprint;
- conditional references actually loaded;
- validation commands and their falsifying value;
- reviewer disagreement and residual risk.

## Non-Goals

- Editing Matt Pocock mirror skill content.
- Recompressing the five PR #3 skills without regression evidence.
- Renaming callable, qualified runtime, Watcher, legacy, or distribution identities.
- Moving `plugins/*/skills` or changing universal discovery architecture.
- Switching a skill between model-invoked and user-invoked behavior.
- Creating a new meta-skill or second policy catalog.
- Refreshing installed state, hooks, or caches unless activation is separately authorized.
- Optimizing for a fixed word count at the expense of behavior.

## Completion Oracle

The plan closes only when:

- S0-S4 are merged and source-validated;
- one owner exists for every mapped meaning;
- the remaining high-value entry interfaces are smaller without branch loss;
- explicit and implicit routing behavior is preserved;
- user questions, false stops, and governance-only work do not increase in the behavioral matrix;
- identity, universal discovery, Watcher attribution, and symlink resolution remain stable;
- active TODO navigation contains no stale slimming review or handoff;
- the final plan and evidence are archived.
