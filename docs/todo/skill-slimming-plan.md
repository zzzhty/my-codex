# Skill Instruction Slimming Plan

Status: **Active — S0-S4 source candidate complete; macOS validation and PR report pending; merge/archive require later user decision**

Updated: 2026-08-21

Baseline: `main@4c80da5a04ce190f8a5ee17024da99628a772adc`

Candidate: `agent/skill-slimming-s0-s1` / PR #13

Execution handoff: `docs/todo/skill-slimming-macos-validation-goal.md`

This document is the single design and semantic authority for repository-owned instruction slimming. The companion validation goal owns live macOS branch/PR discovery, isolated validation, bounded repair, independent review, behavioral sampling, evidence push, and the final PR #13 report. It does not mark the PR Ready, merge, close, or archive either plan. Those decisions return to the user after the report is published.

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

Those bodies remain unchanged. `skill-maintainer` remains the no-change baseline.

The completed universal Agent Skills migration remains authoritative:

- repository `SKILL.md` files are the only canonical skill source;
- `plugins/*/skills/*` remains the physical authority;
- ADR-0004 owns native qualified invocation identity behavior;
- Watcher derives callable inventory from repository authority;
- Watcher overlays own durable attribution identity and aliases;
- marketplace and plugin cache are not source authority.

No identity, invocation mode, universal discovery, hook, cache, installed state, or Matt Pocock mirror content changes belong to this plan.

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
| S4 | Metadata/docs alignment, aggregate validation, and close preparation | Source implemented; macOS validation/report pending |

## S0-S4 Result

### S0 — Rebaseline And Oracle

- Replaced the pre-universalization active review with this stable-named plan.
- Archived the historical second-pass review and PR #3 handoff without rewriting them.
- Added semantic ownership tests and froze PR #3 skill bodies plus `skill-maintainer`.

### S1 — Delegation Ownership And Orchestration

- `agents/operating-principles.md` is a repository map instead of a duplicate global policy.
- Root `AGENTS.md` remains the authority for delegation, mutation, failure, and parent accountability.
- `orchestrate-subagents/SKILL.md` keeps the explicit trigger, minimum-useful parallelism, local invariants, one reference pointer, and completion.
- The full assignment contract lives in `references/subagent-recipes.md`.

### S2 — `doc-alignment` Deep Interface

- The entry interface owns source-of-truth, mode, scheduled read-only safety, common workflow, pointers, and completion.
- `references/watcher-audit.md` owns deterministic Watcher audit commands, profile-set behavior, trust boundaries, change-alignment, due/skip accounting, existing-report routing, and report review.
- `references/alignment-reference.md` owns inventory, file roles, recursive organization, severity, report shape, surface alignment, and validation.

### S3 — `long-running-goal` High-Risk Reduction

- The entry interface retains lifecycle trigger and Ready/Draft, exact planning fallback, request supersession, branch routing, execution authority, runtime hard stops, task-temp boundary, native goal-tool boundary, deterministic validation entry points, and completion.
- Templates/checkers own field shape and readiness; one-level references own create/Loop, sequence, cutover, execute/evolve/checkpoint, and close detail.

### S4 — Metadata And Documentation Alignment

- `long-running-goal/agents/openai.yaml` and Workflow README match the compact lifecycle interface.
- Root `AGENTS.md`, Watcher README, Watcher overlays, identities, and invocation modes remained unchanged after review.
- Invocation tests bind frontmatter descriptions to interface metadata.

## Size Result

| Surface | Before | Candidate | Change |
| --- | ---: | ---: | ---: |
| `agents/operating-principles.md` | 8,429 | 5,390 | -36.1% |
| `orchestrate-subagents/SKILL.md` | 4,296 | 2,490 | -42.0% |
| `doc-alignment/SKILL.md` | 6,938 | 3,399 | -51.0% |
| `long-running-goal/SKILL.md` | 11,148 | 7,580 | -32.0% |

After the bounded macOS semantic repair, primary entry surfaces fall from 30,811 bytes to 18,859 bytes (-38.8%). The nine repository-owned `SKILL.md` bodies fall by about 8.9 KB, from about 37.9 KB to 29,032 bytes. Conditional references grow where branch completeness requires it; they load only after a matching trigger. Size remains a triage signal rather than the acceptance oracle.

## Source-Review Validation Already Completed

- Isolated semantic/invocation tests for S0-S4 passed against published candidate content.
- Changed Python tests compiled.
- `sync_codex_agents.py` passed temporary-target dry-run, apply, and `--check --prune`.
- Changed Markdown links and whitespace were inspected.
- A same-agent Standards/Contract review found no blocker, but it does not satisfy independent review.

## macOS Validation And PR Report Handoff

Execute:

```text
docs/todo/skill-slimming-macos-validation-goal.md
```

The goal requires the local repository to be inspected from its live entry state, normally `main`. Local `main` is the protected baseline and must not become the repair branch. The actual PR #13 base/head are fetched from GitHub and validated in an isolated worktree. Bounded repairs and evidence are pushed to the actual PR branch.

Current validation status (2026-08-21): `PASS`; recommendation `READY FOR MERGE REVIEW`. The validated source/evidence head before the final M6 checkpoint is `f5103e26c3b5c0721cfec4f833ce4af7a341e870`; the final report at `https://github.com/zzzhty/my-codex/pull/13#issuecomment-5367832010` tracks the resulting PR head. PR #13 remains Draft and unmerged; Ready/merge/close and post-merge archive remain user decisions outside M0-M6.

The validation goal owns:

- exact local main and PR base/head discovery;
- isolated worktree validation;
- diff scope and frozen-surface audit;
- focused/root/Workflow/Watcher suites;
- deterministic/link/support/Watcher/plugin/skill validation;
- installed-state and universal-resource read-only classification;
- independent Contract review;
- behavioral scenarios A-E in a proven candidate-loaded context;
- bounded PR-introduced repair and revalidation;
- durable evidence push and a complete PASS/BLOCKED final report on PR #13.

It explicitly does not own:

- modifying local or remote `main`;
- marking PR #13 Ready;
- enabling auto-merge, merging, closing, or deleting the PR/branch;
- installed/runtime activation;
- identity or universalization changes;
- PR #3 skill-body edits;
- parent-plan or validation-goal archive before the user's decision.

After the final PR report is published, execution stops and the user decides in the originating ChatGPT conversation whether to repair further, mark Ready, merge, close, or defer.

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

The candidate is source-only. Revert the S0-S4 and validation-evidence commits; no installed, hook, cache, or runtime rollback is required because activation is outside PR #13.

## Decision And Archive Gate

Keep this parent plan and the validation goal active while PR #13 awaits the user's decision.

A later explicit instruction may authorize further repair, Draft-to-Ready, merge, close, or defer. Only after PR #13 is merged and merged `main` is verified should this parent plan and the validation goal move to `docs/todo/archive/` and active TODO navigation be replaced with archive entries.
