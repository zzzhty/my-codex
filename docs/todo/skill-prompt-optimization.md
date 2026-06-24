# Skill Prompt Optimization Report

Generated: 2026-06-25

## Summary

This is a report-first audit for custom plugin `SKILL.md` prompt quality. It covers only source skills under `plugins/doc-watcher`, `plugins/skill-watcher`, and `plugins/workflow`; it excludes installed plugin cache copies and the upstream-synced `mattpocock-skills` plugin.

No source `SKILL.md` was modified in this phase. The selected change is to keep the current source skills as the no-change baseline and record bounded follow-up candidates for a later, separately authorized writeback phase.

## Scope And Evidence

Reviewed source skills:

| Plugin | Skill | Lines | Initial verdict |
| --- | --- | ---: | --- |
| `doc-watcher` | `doc-alignment` | 183 | Candidate: progressive disclosure for branch-heavy reference. |
| `doc-watcher` | `housekeeping` | 65 | No-change baseline. |
| `skill-watcher` | `skill-compressor` | 106 | No-change baseline unless usage evidence shows drift. |
| `skill-watcher` | `skill-maintainer` | 32 | Candidate: clarify script path ownership. |
| `workflow` | `long-running-goal` | 184 | Candidate: later semantic-inventory compression only. |
| `workflow` | `orchestrate-subagents` | 92 | Candidate: align description with explicit-invocation body. |
| `workflow` | `prompt-strategy-loop` | 57 | Candidate: add report-only evaluator branch. |
| `workflow` | `sop` | 70 | No-change baseline. |
| `workflow` | `summary-in-html` | 86 | No-change baseline. |

Evidence used:

- Source `SKILL.md` files listed above.
- Plugin contracts in `plugins/doc-watcher/README.md`, `plugins/skill-watcher/README.md`, and `plugins/workflow/README.md`.
- Latest relevant commits: `415d8cc`, `bcf3d9b`, `689f343`, `d194a7a`, `46dab5c`, `3273cb6`.
- Skill Watcher runtime evidence: latest report `/Users/max/.codex/skill-watcher/reports/20260621T200617Z-all-report.md` recorded 117 events, 72 failures, 45 successes, and repeated user context about `long-running-goal` interruption/permission friction.
- Existing Skill Watcher proposal artifact `/Users/max/.codex/skill-watcher/proposals/20260527T165515Z-skill-maintainer-proposal.md` had zero `skill-maintainer` events and remains insufficient evidence for direct source mutation.
- Independent reviewer coverage: one evaluator subagent and one risk-reviewer subagent, both read-only.

## Evaluation Oracle

Use `writing-great-skills` as the quality rubric:

- Improve predictability: the skill should make the agent follow the same process across runs.
- Keep invocation and description precise: one real trigger branch per branch, no loaded description sprawl.
- Preserve information hierarchy: inline only what every run needs; disclose branch-heavy reference behind strong context pointers.
- Strengthen completion criteria only when the current criterion is vague or weak.
- Preserve single source of truth; remove duplication, no-op prose, sediment, and avoid sprawl.

Use `prompt-strategy-loop` as the process rubric:

- Keep this report evidence-backed and report-only.
- Freeze the oracle before candidate writeback.
- Include a no-change baseline.
- Require independent evaluation for high-impact changes.
- Stop before mutation when reviewers identify permission, failure-handling, validation, source/cache, or report-only regressions.

Regression checks for any future writeback:

- Do not weaken proposal-vs-mutation boundaries.
- Do not weaken `long-running-goal` YOLO scope, runtime hard stops, request supersession, or Codex goal-tool boundaries.
- Do not turn report-only DocWatcher/Skill Watcher flows into mutation flows.
- Do not expand subagent authorization beyond explicit user request or skill-local read-only review.
- Do not edit installed cache copies under `/Users/max/.codex/plugins/cache/...`.

## Candidate Summary

### C1: Align `orchestrate-subagents` Invocation Metadata

Evidence:

- Description broadly says to use for complex Codex tasks in `plugins/workflow/skills/orchestrate-subagents/SKILL.md:3`.
- Body says use only when the user invokes `$orchestrate-subagents` or explicitly asks to use subagents in `plugins/workflow/skills/orchestrate-subagents/SKILL.md:8`.

Bounded future edit:

- Narrow the model-facing description to explicit subagent requests only, matching the body.
- Keep parent-owned integration, bounded task prompts, and subagent failure handling unchanged.

Risk:

- Low-to-medium. This is the clearest predictability fix, but it affects invocation behavior and must be validated against expected user-triggered use.

### C2: Clarify `skill-maintainer` Helper Script Paths

Evidence:

- Workflow references `scripts/summarize_logs.py`, `scripts/propose_skill_patch.py`, and `scripts/validate_candidate.py` in `plugins/skill-watcher/skills/skill-maintainer/SKILL.md:12-17`.
- Actual helper scripts live under `plugins/skill-watcher/scripts/`, not the skill folder.

Bounded future edit:

- State that helper scripts are plugin-level scripts under `plugins/skill-watcher/scripts/`, or use `<plugin-root>/scripts/...` wording.
- Keep proposal-first behavior unchanged.

Risk:

- Low. This improves checkable execution and reduces path guessing.

### C3: Add Report-Only Evaluator Branch To `prompt-strategy-loop`

Evidence:

- Current workflow emphasizes candidate generation, selection, writeback, and final recommendation fields in `plugins/workflow/skills/prompt-strategy-loop/SKILL.md:18-28` and `plugins/workflow/skills/prompt-strategy-loop/SKILL.md:41-49`.
- This audit needed a read-only evaluator/risk-reviewer path with no source mutation.

Bounded future edit:

- Add a short branch for read-only prompt/skill audits: collect evidence, freeze oracle, run independent evaluation, publish report, and stop before writeback.
- Keep mutation authorization and stop conditions unchanged.

Risk:

- Medium. This touches a high-impact strategy skill and must not weaken existing evidence/writeback gates.

### C4: Plan Semantic-Inventory Compression For `long-running-goal`

Evidence:

- Description carries many trigger branches in `plugins/workflow/skills/long-running-goal/SKILL.md:3`.
- Body is 184 lines and includes distinct branches: supersession, creation, Loop harness, YOLO boundary, goal tool boundary, production cutover, execution, evolution, and close.
- The permission-sensitive YOLO/hard-stop section is in `plugins/workflow/skills/long-running-goal/SKILL.md:83-107`.

Bounded future edit:

- Do not edit directly from this report. First build a semantic inventory and candidate compression diff.
- Preserve request supersession, Draft/Ready gates, runtime hard stops, YOLO non-stops, Codex goal-tool boundary, production cutover gate, and close hygiene.

Risk:

- High. Default to no-change until semantic inventory plus independent review supports a specific compression.

### C5: Disclose Branch-Heavy Reference From `doc-alignment`

Evidence:

- Read-only mode is clear in `plugins/doc-watcher/skills/doc-alignment/SKILL.md:25-31`.
- Inline reference sections for script naming, documentation tree alignment, planning tree alignment, skill alignment, and validation span `plugins/doc-watcher/skills/doc-alignment/SKILL.md:92-179`.

Bounded future edit:

- Move branch-heavy reference into explicit reference files only if the context pointer is strong enough.
- Keep core DocWatcher semantics, read-only audit behavior, implementation-mode boundary, and validation reporting in `SKILL.md`.

Risk:

- Medium. Progressive disclosure could harm reliability if the pointer wording is weak.

## No-Change Baselines

- `housekeeping`: keep as-is. It has clear candidate classes, report-first boundaries, preservation rules, and stop conditions.
- `sop`: keep as-is. It has clear creation/execution/update flows, boundary criteria, and validation scripts.
- `summary-in-html`: keep as-is. It has a bounded artifact contract, summary JSON shape, renderer/checker flow, and visual-asset branch.
- `skill-compressor`: keep as-is unless usage evidence shows drift. It already requires semantic inventory, validation, and independent review before claiming equivalence.

## Independent Reviewer Coverage

Evaluator result:

- Ranked `orchestrate-subagents`, `skill-maintainer`, `prompt-strategy-loop`, `long-running-goal`, and `doc-alignment` as the top candidate areas.
- Confirmed `housekeeping`, `sop`, `summary-in-html`, and mostly `skill-compressor` as no-change baselines.
- Marked `skill-maintainer` path clarification as a concrete execution fix.
- Marked `long-running-goal` as improvement-worthy only with semantic inventory and independent review.

Risk-reviewer result:

- Warned against blurring proposal vs mutation in `skill-maintainer` and `prompt-strategy-loop`.
- Warned against weakening `skill-compressor` semantic-equivalence gates.
- Warned that `long-running-goal` autonomy boundaries are fragile and must preserve supersession, Draft/Ready gates, YOLO scope, hard stops, and goal-tool boundaries.
- Warned that DocWatcher review vs cleanup boundaries and subagent authorization must not expand.
- Required no-change baseline, independent review, validators, diff checks, source/cache separation, and no cache writeback before any future edit.

Missing coverage:

- No candidate patch was produced.
- No edited-skill validators were run because no source `SKILL.md` was edited.
- No real A/B task benchmark was run; this report is an evidence inventory and planning artifact, not proof that a future wording candidate improves behavior.

## Selected Change And Rejected Alternatives

Selected now:

- Write this report and keep source `SKILL.md` files unchanged.

Rejected for this phase:

- Directly editing high-impact skills from reviewer prose alone.
- Compressing `long-running-goal` without semantic inventory.
- Moving `doc-alignment` reference sections before proving context pointers will fire reliably.
- Refreshing installed plugin cache, because source skills did not change.

## Future Writeback Plan

Recommended order:

1. Workflow batch 1: `orchestrate-subagents` description alignment and `prompt-strategy-loop` report-only branch.
2. Skill Watcher batch: `skill-maintainer` script path wording.
3. Workflow batch 2: `long-running-goal` semantic-inventory compression proposal only.
4. DocWatcher batch: `doc-alignment` progressive-disclosure proposal only.

Each batch should:

- Start from clean `git status --short`.
- Freeze candidate-specific oracle and no-change baseline.
- Use an independent evaluator and risk reviewer.
- Apply only the smallest source edit that satisfies the oracle.
- Validate with the owning plugin validator and repo-level `scripts/check_my_codex.py --skip-agents --plugin <plugin>`.
- Commit independently after validation.

## Validation Results

Report-stage validation passed:

```bash
# expected dirty docs-only state during report creation
git status --short
/Users/max/.codex/venvs/my-codex/bin/python scripts/check_my_codex.py --skip-agents --plugin workflow
/Users/max/.codex/venvs/my-codex/bin/python scripts/check_my_codex.py --skip-agents --plugin skill-watcher
/Users/max/.codex/venvs/my-codex/bin/python scripts/check_my_codex.py --skip-agents --plugin doc-watcher
git diff --check -- docs/todo/skill-prompt-optimization.md docs/todo/README.md
/Users/max/.codex/venvs/my-codex/bin/python plugins/workflow/skills/long-running-goal/scripts/check_md_links.py docs/todo
```

Results:

- `workflow`, `skill-watcher`, and `doc-watcher` repo-level plugin checks passed with 0 warnings.
- `git diff --check` passed for the report and TODO index.
- `docs/todo` Markdown relative links passed.

## Rollback

This phase changes only report/navigation docs. Rollback is removing `docs/todo/skill-prompt-optimization.md` and reverting the `docs/todo/README.md` index entry. No runtime, cache, source skill, hook, API, or frontend behavior changes are expected.
