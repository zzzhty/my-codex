# Doc Alignment Progressive Disclosure Proposal

Generated: 2026-06-25

Status: proposal only. Do not edit `plugins/doc-watcher/skills/doc-alignment/SKILL.md` from this artifact without a later source-edit pass, fresh oracle, independent review, and validation.
This proposal does not authorize direct installed-cache edits or cache writeback under `/Users/max/.codex/plugins/cache/`.

## Target

Reduce branch-heavy reference in `doc-alignment` while preserving DocWatcher's audit-first semantics. The no-change baseline remains acceptable because the current skill keeps read-only audit behavior, implementation-mode boundaries, and validation expectations explicit.

## Evidence And Oracle

Evidence:

- `plugins/doc-watcher/skills/doc-alignment/SKILL.md`
- `plugins/doc-watcher/README.md`
- `docs/todo/skill-prompt-optimization.md`
- `mattpocock-skills:writing-great-skills` rubric: information hierarchy, context pointers, co-location, single source of truth, and sprawl control.
- `workflow:prompt-strategy-loop` rubric: no-change baseline, frozen oracle, independent evaluation, bounded writeback, and source/cache separation.

Future disclosure must improve skill legibility without weakening:

- DocWatcher report-first and target-repo read-only default.
- Mode selection between read-only review and implementation.
- Implementation-mode requirement for explicit user authorization before target file changes.
- Audit workflow commands and failure reporting.
- Root-cause fixing over fallback or silent degradation.
- Cleanup split: `housekeeping` owns temporary files, generated artifacts, stale runtime artifacts, and obsolete active docs cleanup.
- Source/cache separation and plugin validation expectations.

## Keep Inline In `SKILL.md`

These sections are core execution steps or high-risk boundaries and should remain in the main skill unless a later reviewer proves a stronger structure:

| Section | Reason to keep inline |
| --- | --- |
| Frontmatter and invocation metadata | The `description` is the model-facing trigger and must keep the audit/alignment scope visible. |
| Core Contract | Every branch needs source-of-truth alignment, current/history separation, path coverage, failure handling, and read-only scheduled audits. |
| Mode Selection | Prevents report-only requests from becoming mutation work and defines implementation-mode authorization. |
| DocWatcher Audit Workflow | Names deterministic audit commands, config selection, skip semantics, and failure reporting. |
| Review Workflow | Gives the common inventory/read/classify/align sequence that drives all branches. |
| Finding Severity | Keeps findings checkable and consistently reported. |
| Final Report | Defines the completion artifact every branch needs. |

## Disclose Behind One Strong Pointer

A future source-edit candidate should first prefer one disclosed reference file, not several scattered files, to preserve co-location and avoid weak pointer routing:

```text
plugins/doc-watcher/skills/doc-alignment/references/alignment-reference.md
```

The main skill should point to it with wording equivalent to:

> Read `references/alignment-reference.md` when the target touches script or entry-point names, documentation tree placement, planning/TODO navigation, Codex skill source files, or validation command selection.

Candidate sections for that reference file:

| Current section | Disclosure reason |
| --- | --- |
| Script And Entry-Point Naming | Branch-specific naming convention reference, needed only for script/runner rename work. |
| Documentation Tree Alignment | Branch-specific tree placement rules, needed when docs are misplaced or stale. |
| Planning/TODO Tree Alignment | Branch-specific active/archive navigation rules, needed for TODO or goal tree alignment. |
| Skill Alignment | Branch-specific Codex skill rules, needed only when aligning skill source files. |
| Validation | Command reference selected by changed surface; keep a short validation reminder inline, move detailed command matrix to the reference. |

## No-Change Baseline

Keep the current source skill unchanged if future disclosure cannot prove reliable pointer firing. A longer inline skill is preferable to a shorter skill that forgets read-only mode, implementation authorization, target-repo safety, or validation failure reporting.

## Future Candidate Boundaries

A future source-edit candidate may:

- Add the single strong context pointer above.
- Move only branch-heavy reference into `references/alignment-reference.md`.
- Leave a concise inline validation reminder that changed surfaces must be validated.
- Preserve all current headings inside the reference file so reviewers can map old meanings to new locations.

A future source-edit candidate must not:

- Move Core Contract, Mode Selection, DocWatcher Audit Workflow, Review Workflow, Finding Severity, or Final Report behind a reference pointer.
- Turn scheduled or report-only audits into target-repo mutations.
- Merge `housekeeping` cleanup behavior into `doc-alignment`.
- Remove explicit failure reporting for broken links, stale paths, failed validation, or failed audit commands.
- Edit installed cache copies or generated runtime artifacts.

## Review And Validation Required Before Source Edit

Before editing the source skill, run a fresh `prompt-strategy-loop` pass:

1. Freeze candidate-specific oracle and no-change baseline.
2. Produce an old-to-new section map showing every moved rule.
3. Use one evaluator to check semantic preservation and one risk-reviewer to search for report-only, cleanup-boundary, validation, and source/cache regressions.
4. Validate DocWatcher:

```bash
/Users/max/.codex/venvs/my-codex/bin/python scripts/check_my_codex.py --skip-agents --plugin doc-watcher
/Users/max/.codex/venvs/my-codex/bin/python plugins/workflow/skills/long-running-goal/scripts/check_md_links.py docs/todo
git diff --check -- plugins/doc-watcher/skills/doc-alignment/SKILL.md docs/todo
```

## Residual Risk

The likely failure mode is pointer under-triggering: an agent may skip the disclosed reference and miss a branch-specific rule. Future edits should keep the pointer explicit, preserve the old headings in the reference file, and prefer no-change if reviewers cannot prove the new structure is at least as predictable as the current inline skill.
