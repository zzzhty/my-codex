# Second-Pass Skill Slimming Review

Generated: 2026-08-19

Status: review complete; report-only. No source `SKILL.md`, generated plugin cache, installed copy, runtime hook, or validator was changed by this review.

Baseline: `agent/merge-dev-into-main-20260819` at `97905d1e66ed550b188fb9899da9b5e03b621098`.

## Executive Decision

A second slimming pass is justified.

The first pass solved real structural problems: it aligned invocation metadata, added report-only prompt review, disclosed branch-heavy long-running-goal and doc-alignment detail, and hardened deterministic validators. That work should remain the semantic baseline. The new problem is that the resulting instruction system still assumes a weaker, less autonomous agent than the current model baseline.

The dominant failure mode is no longer missing procedure. It is **governance-induced passivity**: the same safety, evidence, failure, delegation, and validation meanings are repeated across `AGENTS.md`, `agents/operating-principles.md`, top-level skills, references, templates, and checkers. The repeated negative and procedural wording makes the agent more likely to ask, stop, narrate governance, or over-produce evidence instead of taking the smallest useful action.

The target is not “short prompts” in isolation. The target is a set of **deep skills**:

- a small model-facing interface;
- precise trigger branches;
- only non-default behavior and repository-specific invariants inline;
- conditional detail behind strong pointers;
- field-heavy contracts and deterministic truth owned by templates, scripts, and validators;
- completion criteria that demand correct outcomes without micromanaging capable-agent legwork.

The `mattpocock-skills` tree is an upstream byte-preserved mirror and is review input only. Do not edit it during this work.

## Review Method

This review applies existing repository skills rather than inventing a new rubric.

### Standards axis

Use `mattpocock-skills:writing-for-agents` and its skill mechanics:

- prune always-loaded descriptions hardest;
- keep one trigger per real branch, not one synonym per phrase;
- distinguish context load from human cognitive load;
- keep steps and common invariants inline, disclose conditional reference;
- co-locate one meaning under one owner;
- remove no-ops, environmental caches, sediment, and duplicated meaning;
- prefer positive target behavior over prohibition-heavy steering;
- use clear, demanding completion criteria instead of exhaustive process narration;
- make a skill model-invoked only when autonomous reach or cross-skill reach is required.

Use `mattpocock-skills:codebase-design` as the architecture lens: a top-level skill is the interface; references, templates, scripts, and tests are its implementation. A useful skill should provide substantial behavioral leverage behind a small interface.

### Contract axis

Use the current source, tests, prior semantic inventories, templates, and checkers as the specification. Preserve behavior that exists because of an observed failure, permission boundary, external contract, or deterministic validator. Do not preserve wording merely because it already exists.

Use `watcher:skill-compressor` and `workflow:prompt-strategy-loop` for writeback:

- retain a recoverable no-change baseline;
- freeze a candidate-specific oracle;
- compare only affected trigger, permission, stop, failure, validator, and edge-case meanings;
- require independent review proportionally, not ceremonially;
- stop at a proposal when mutation or required review is not authorized.

`mattpocock-skills:code-review` supplies the two-axis structure, but an implementation agent may run the axes sequentially when no subagent runtime is available. Parallel reviewers are not themselves an acceptance criterion.

## Current Footprint

The nine repository-owned `SKILL.md` files total approximately 44.8 KB before references, templates, examples, and global instructions. Root `AGENTS.md` and `agents/operating-principles.md` add approximately 15.3 KB of always-present or commonly loaded guidance.

| Surface | Approx. size | Review verdict |
| --- | ---: | --- |
| `workflow/long-running-goal` | 11.1 KB | Highest-impact compression target; high semantic risk. |
| `watcher/doc-alignment` | 6.9 KB | High-impact disclosure and ownership target. |
| `workflow/summary-in-html` | 4.8 KB | Low-risk deepening pilot; schema leakage is obvious. |
| `watcher/housekeeping` | 4.4 KB | Moderate target; prohibition-heavy and list-heavy. |
| `workflow/sop` | 4.3 KB | Moderate target; template/checker detail leaks into interface. |
| `workflow/orchestrate-subagents` | 4.3 KB | High behavioral impact; heavily duplicates global delegation policy. |
| `workflow/prompt-strategy-loop` | 3.9 KB | Moderate target; review policy duplicates compressor rules. |
| `watcher/skill-compressor` | 3.5 KB | Mostly healthy; candidate for shared-policy deduplication only. |
| `watcher/skill-maintainer` | 1.6 KB | No-change baseline. |

Raw size is only a triage signal. A longer reference that is loaded only for one real branch may be healthier than a short description that is permanently loaded and repeats synonyms.

## Findings

### F1. One meaning has several owners

The same behavior is often stated at four or five layers:

- delegation authority, parent ownership, failure reporting, and write boundaries appear in root `AGENTS.md`, `agents/operating-principles.md`, and `orchestrate-subagents`;
- long-running-goal invocation, Draft/Ready, YOLO scope, and runtime stops appear in root guidance, operating principles, the top-level skill, references, templates, and checker expectations;
- evidence and validation rules recur in nearly every skill even when a deterministic checker already owns the contract;
- proposal-versus-mutation and independent-review wording is repeated in `prompt-strategy-loop`, `skill-compressor`, `skill-maintainer`, and global policy.

This is not defensive depth. It is duplicated interface area. It raises context load, increases the chance of semantic drift, and overweights governance relative to execution.

### F2. Model-facing descriptions enumerate vocabulary instead of branches

Several descriptions contain long synonym chains such as “creating, upgrading, executing, resuming, continuing, evolving, or closing.” These are usually two or three real branches written many times. Because descriptions are always-loaded pointers, this is the most expensive place for synonym sprawl.

Descriptions should lead with the task noun or verb and name only distinct invocation branches. Body identity and examples do not belong in the pointer.

### F3. Deterministic implementation leaks into the prompt interface

Top-level skills restate:

- template fields;
- helper commands and their detailed behavior;
- JSON member shapes and renderer type rules;
- file-role taxonomies;
- validator checks;
- report field lists.

These facts already live in templates, scripts, `--help`, tests, or references. Repeating them makes the prompt a stale cache of the environment. The skill should tell the agent when to use the deterministic owner and what successful completion means.

### F4. Negative steering creates avoidant behavior

The current system contains many repetitions of “do not,” “never,” “stop,” “report instead,” and “do not claim.” Some are real hard guardrails, but many are ordinary routing or quality guidance expressed as prohibition.

For a stronger agent, repeated negative concepts increase the salience of failure and permission checks. Replace them with positive defaults where possible:

- “delete only inventoried disposable generated artifacts” instead of a long list of things not to delete;
- “continue while the next in-scope diagnostic is clear” instead of enumerating every non-stop;
- “write the smallest evidence that falsifies the changed behavior” instead of demanding a standard report bundle for every edit.

Keep explicit prohibitions only for destructive, privacy-sensitive, externally visible, persisted-contract, or source/cache boundary violations that cannot be stated safely as a positive target.

### F5. Review and evidence are sometimes ceremony rather than falsification

Independent evaluators and risk reviewers are valuable for invocation, permission, destructive, privacy, external-write, or persisted-contract changes. They are not automatically useful for every wording reduction. Likewise, a fixed bundle of commands, paths, reports, and artifacts can become evidence theater when one focused check would falsify the candidate.

The repository already states that verification should use the smallest check that can falsify changed behavior. Skill-level review policy should inherit that default instead of rebuilding a larger process.

### F6. The first disclosure pass preserved too much top-level summary

The previous long-running-goal and doc-alignment work successfully moved branch detail to references. However, the top-level skills still contain extensive summaries, field lists, helper explanations, quality bars, and repeated global constraints. The next pass should deepen the module rather than merely move paragraphs sideways.

### F7. Global guidance is part of the skill problem

`AGENTS.md` should own global invariants. `agents/operating-principles.md` should map those invariants to repository paths and workflows. It currently repeats substantial delegation and long-running execution policy also present in skills.

If global ownership is not clarified first, individual skills will continue re-adding wording “for safety.” The second pass therefore needs an explicit rule-ownership map before source compression.

## Target Design Rules

These are review heuristics, not rigid validators.

1. **Teach only the delta from capable-agent defaults.** Planning, repository inspection, ordinary summarization, choosing a narrow tool, and reporting a concrete failure need no repeated instruction unless an observed failure proves otherwise.
2. **One rule, one owner.** Other layers may point to the owner or state a local delta; they should not paraphrase the same contract.
3. **Deep skill interface.** The top-level skill carries trigger, route, non-default invariants, conditional pointers, and completion oracle. Templates, scripts, references, and tests carry implementation detail.
4. **Positive execution default.** State what to do. Reserve prohibitions for true guardrails.
5. **One-level behavioral disclosure.** A conditional branch may load one reference that is complete for that branch. Avoid reference chains that require repeated discovery.
6. **Deterministic truth stays deterministic.** Field schemas, command syntax, and structural validation live in templates, scripts, or `--help`.
7. **Proportional proof.** The candidate receives only the checks and reviewer coverage needed for its affected semantics.
8. **Descriptions pay rent.** A model-facing description should usually be one compact sentence and contain only real trigger branches. A description longer than roughly 300 characters requires a branch-coverage rationale.
9. **Completion over choreography.** Prefer a checkable exhaustive result over a long sequence of obvious micro-steps.
10. **Model invocation is a design choice.** Keep model invocation when natural-language autonomous routing matters. Use `disable-model-invocation: true` when only explicit slash/name invocation is useful and another skill does not need to reach it.

Provisional top-level budgets:

- ordinary skill: approximately 300–500 words;
- high-risk lifecycle or permission skill: approximately 600–900 words;
- more than 1,000 words requires a written reason, an observed failure it protects, and an A/B result showing the extra text helps.

Budgets guide attention; semantic ownership and behavior decide acceptance.

## Rule Ownership Map

| Meaning | Authoritative owner |
| --- | --- |
| Global destructive, privacy, external-send, irreversible, and mutation-intent boundary | Root `AGENTS.md` |
| Repository-specific application paths and managed support-note mapping | `agents/operating-principles.md` |
| Goal lifecycle, Draft/Ready meaning, request supersession, and goal-specific runtime-stop delta | `long-running-goal` plus its template/checkers |
| General delegation authority and parent accountability | Root `AGENTS.md` |
| Subagent slicing, assignment, disjoint writes, wait/consolidation protocol | `orchestrate-subagents` and its recipes |
| Evidence/oracle/candidate/writeback decision process | `prompt-strategy-loop` |
| Behavior-preserving instruction reduction | `skill-compressor` |
| Watcher-log-backed proposal generation | `skill-maintainer` |
| Documentation truth and report-only versus implementation mode | `doc-alignment` |
| Cleanup classification and safe disposable-artifact mutation | `housekeeping` |
| SOP field shape and readiness | SOP template and checker |
| Summary artifact schema and renderer constraints | Summary schema reference, renderer, and checker |
| Upstream Matt Pocock skill content | Upstream mirror and lock; no local editing |

A future candidate should delete local restatements once the authoritative owner is reachable and the local delta remains explicit.

## Per-Skill Recommendations

### Impact P0: `long-running-goal`

Current interface problems:

- the description lists many synonymous verbs and implementation concepts;
- the top-level skill repeats global permission language, template fields, checker behavior, helper explanations, and an eleven-question quality bar;
- deterministic readiness and sequence rules have strong templates and large checkers, yet the prompt still narrates much of their implementation;
- repeated stop wording can make recoverable failures feel like permission boundaries.

Keep inline:

- compact trigger and when-not-to-use boundary;
- the meaning of `Ready` versus `Draft`;
- request supersession;
- the goal-specific distinction between planned non-stops and true runtime hard stops;
- strong branch pointers;
- one completion criterion.

Move or delete:

- contract field enumeration already represented by the template/checker;
- helper command explanations available from scripts or a short operations reference;
- duplicated global external/destructive boundaries, retaining only the goal-specific delta;
- the quality-bar list when the same criteria are structurally owned by the template/checker;
- examples and repeated phrases not tied to a recorded regression.

Candidate target: 600–900 words, with high-risk semantics tested against the accepted 2026-07-10 inventory. Implement late in the sequence because impact and risk are both high.

### Impact P0: `orchestrate-subagents`

Current interface problems:

- parent responsibility, authority, failure reporting, bounded scope, and worker write rules repeat root guidance;
- role descriptions and the full prompt template occupy the top-level interface even though recipes can own them;
- negative boundaries dominate the action protocol.

Keep inline:

- explicit user/natural-language trigger;
- minimum-useful parallelism test;
- parent-owned integration;
- disjoint write ownership for workers;
- wait, consolidate, and partial-coverage completion rule;
- pointer to recipes.

Move:

- full prompt template and role examples to `references/subagent-recipes.md`;
- general authority/failure wording to root `AGENTS.md`;
- repeated evidence field lists to one recipe-level output contract.

Candidate target: 250–450 words. Keep model invocation unless the project intentionally gives up automatic routing from natural-language “use subagents” requests.

### Impact P0: `doc-alignment`

Current interface problems:

- audit commands, profile configuration caveats, file-role taxonomy, severity taxonomy, recursive organization rules, and report fields all live in the interface;
- the existing conditional reference is useful but does not yet own enough branch-specific detail;
- review and implementation modes are clear and should remain the center.

Keep inline:

- source-of-truth invariant;
- report-only versus implementation mode;
- compact common workflow;
- conditional pointer and completion criterion.

Move:

- Watcher command catalog and config/profile semantics to an operations reference or plugin README;
- role/severity taxonomies to the review reference;
- detailed validation command selection to the existing conditional reference.

Candidate target: 450–700 words.

### Execution pilot P1: `summary-in-html`

This is the safest first implementation candidate because ownership is obvious.

Keep inline:

- two document types;
- output contract;
- evidence → plan → structured input → render → validate workflow;
- visual-assets branch;
- completion criterion.

Move:

- full JSON example;
- nested member type validation;
- source-walkthrough field grammar;
- detailed HTML rules that the renderer/checker already enforce.

Create one `references/artifact-schema.md` only if the schema cannot be obtained cleanly from renderer help or an existing machine-readable schema. Candidate target: 300–500 words.

### P1: `sop`

Keep stable-workflow suitability, create/execute/update routing, and completion. Let the template and readiness checker own field lists, placeholder semantics, and structural requirements. Replace broad “do not use” prose with positive routing to exploration, strategy tuning, or long-running planning. Candidate target: 350–550 words.

### P1: `prompt-strategy-loop`

Keep evidence, frozen oracle, no-change candidate, proportional evaluation, selection, and authorized writeback. Move the detailed independent-review threshold to one shared plain reference used by both this skill and `skill-compressor`, or let root policy own it where applicable. Avoid adding a new model-invoked policy skill solely for deduplication. Candidate target: 300–450 words.

### P2: `housekeeping`

Retain the inspect/classify/delete-or-report loop and destructive boundary. Move long candidate lists to a reference or reduce them to three classes: disposable generated artifacts, active semantic drift, and approval-required state. Lead with the positive default. Candidate target: 300–500 words.

### P2: `skill-compressor`

Use as a no-change baseline except for deduplicating proportional-review policy with `prompt-strategy-loop` and shortening metadata. Its current workflow already focuses on affected semantics and deterministic validation.

### No-change: `skill-maintainer`

It is short, single-purpose, proposal-first, and delegates detail to references and Watcher commands. Change only when usage evidence identifies a real failure.

## Implementation Order

Impact order and execution order should differ. Start with a low-risk pilot to calibrate the rubric before touching permission-sensitive skills.

1. **Batch 0 — ownership baseline**
   - freeze this rule-ownership map;
   - inventory exact duplicated meanings across root guidance and target skill;
   - define benchmark tasks and current baseline outputs;
   - make no source compression yet.
2. **Batch 1 — low-risk pilot**
   - slim `summary-in-html`;
   - validate renderer/checker behavior and source-walkthrough branch;
   - use the result to calibrate word budgets and pointer quality.
3. **Batch 2 — passivity reduction**
   - slim `orchestrate-subagents`;
   - then `doc-alignment`;
   - verify fewer unnecessary questions/stops without expanding authority or mutation.
4. **Batch 3 — template-owned processes**
   - slim `sop`;
   - deduplicate `prompt-strategy-loop` and `skill-compressor` review policy;
   - optionally slim `housekeeping`.
5. **Batch 4 — high-risk lifecycle**
   - slim `long-running-goal` against its accepted semantic inventory and current checker behavior;
   - preserve all tested request-supersession, Draft/Ready, sequence, preflight, and true hard-stop contracts.
6. **Batch 5 — global layer cleanup**
   - reduce `agents/operating-principles.md` to repository mapping and examples;
   - keep root `AGENTS.md` as the single owner of global invariants;
   - rerun cross-skill routing and activation checks.

Use one skill or one tightly coupled owner pair per commit. Do not combine the entire pass into one rewrite.

## Behavioral Evaluation Matrix

Static semantic review is necessary but insufficient. Run fixed baseline and candidate sessions against the same bounded scenarios.

| Scenario | Required invariant | Friction signal to measure |
| --- | --- | --- |
| Small one-off implementation | No long-running-goal conversion or governance detour. | Unnecessary questions, plans, reports, and validators. |
| Create a long-running goal | Complete continuation contract and correct `Draft`/`Ready`. | Repeated restatement and premature permission prompts. |
| Resume after one recoverable local failure | Continue with a clear in-scope diagnostic. | False hard stops and ritual retry loops. |
| Documentation audit, report-only | No target mutation; evidence-backed findings. | Excess inventories and report boilerplate. |
| Documentation alignment implementation | Smallest sufficient edit plus focused validation. | Unrelated scans, duplicated validation, and hesitation. |
| Explicit “use subagents” request | Bounded useful dispatch and parent consolidation. | Extra authorization questions, oversized prompts, idle waiting. |
| Generate an HTML summary | Correct artifact and validation. | Schema narration, unnecessary auxiliary artifacts. |
| Compress a low-risk skill | Behavior-preserving smaller candidate. | Unnecessary independent reviewers and evidence bundles. |

Record:

- trigger/routing correctness;
- invariant pass/fail;
- unnecessary user questions;
- unnecessary stops;
- governance-only steps versus meaningful task steps;
- loaded instruction footprint;
- validation commands and whether each could falsify the changed behavior;
- material reviewer disagreement.

A candidate is acceptable only when required invariants do not regress, unnecessary questions/stops do not increase, and the smaller interface still reaches every conditional branch needed by the scenario. Size reduction alone is not acceptance evidence.

## Validation Contract

For each batch:

1. Preserve the source baseline in Git and list only affected meanings.
2. Validate changed skill frontmatter and relative links.
3. Run the owning plugin tests and only the domain checker affected by the candidate.
4. Run `git diff --check -- <changed-paths>`.
5. Run the fixed behavioral scenarios for changed branches.
6. Apply the Standards and Contract review axes.
7. Use an independent evaluator only when the candidate changes invocation/routing, permissions, destructive/privacy/external behavior, recurring automation, persisted contracts, or removes a stop/validation gate.
8. Refresh installed caches or hooks only when activation is explicitly in scope.

Do not add snapshot hashes, duplicate golden files, or broad regression suites solely to prove diligence. Add a deterministic test when it protects a changed branch or a previously observed failure.

## Non-Goals

- Editing the upstream `plugins/mattpocock-skills/skills/` mirror.
- Removing deterministic validators merely because prompts become shorter.
- Weakening destructive, privacy, external-write, source/cache, report-only, or proposal/mutation boundaries.
- Replacing current skills with a large new meta-skill or importing overlapping Superpowers workflows.
- Optimizing for line count at the expense of branch reach or completion quality.
- Activating source changes in installed caches during a report-only phase.

## Reusable Invocation

Use this document as the controlling plan for future implementation:

```text
Use docs/todo/skill-slimming-v2-review.md as the controlling plan.
Implement only <batch or target skill>.
Apply mattpocock writing-for-agents and codebase-design as the Standards axis,
and the current skill/tests/templates/checkers plus prior semantic inventories as the Contract axis.
Use watcher skill-compressor and workflow prompt-strategy-loop for the candidate and review boundary.
Keep plugins/mattpocock-skills/skills unchanged.
Start from the no-change baseline, preserve the rule-ownership map, run only affected validation and benchmark scenarios,
and stop before installed-cache or hook activation unless that activation is explicitly requested.
```

## Selected Next Step

The recommended first source-edit batch is `summary-in-html`, not `long-running-goal`. It provides a low-risk test of the deep-skill model because the renderer and checker already own most of the leaked schema. After the rubric is calibrated, use `orchestrate-subagents` to test whether slimming actually reduces passivity without expanding delegation authority.

This document authorizes review and planning only. Each source-edit batch requires a separate implementation request.