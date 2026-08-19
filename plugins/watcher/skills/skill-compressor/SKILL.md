---
name: skill-compressor
description: Use when reducing the instruction footprint of one or more agent skills, plugin skill sets, skill references, templates, or UI prompts while preserving required behavior through a recoverable baseline, scoped comparison, and validation owned by the changed surface.
---

# Skill Compressor

Use this skill to compress agent skill instructions without changing their behavior. The goal is fewer tokens and clearer attention, not weaker rules.

Use `prompt-strategy-loop` when the requested change intentionally redesigns workflow, permission, safety, or validation behavior. Treat deterministic scripts as out of scope unless the user explicitly asks to change them. Use `skill-maintainer` when Watcher usage evidence should produce a proposal instead of direct compression.

## Core Rule

Compare the candidate with a recoverable prior version and the operational rules affected by the edit. Do not claim unchanged behavior when trigger or routing coverage, permissions, stop or failure behavior, domain validators, or unique edge cases drift.

Require an independent evaluator only when the edit affects invocation or routing, permissions, safety or privacy, destructive or external actions, automation or recurring execution, persisted or external contracts, or removes an existing stop or validation gate. Add a separate risk or counterexample pass only for permission, safety or privacy, destructive-action, or external-write changes. Otherwise compare the baseline and candidate directly against a scoped oracle.

If required independent evaluation is unavailable, report the compression as unverified. An explicit request to use this skill authorizes only the required read-only semantic evaluation; it does not authorize unrelated delegation or mutation.

## Workflow

1. Define the exact skill, metadata, references, templates, and helper surfaces that may be affected. Note dirty files and preserve unrelated work.
2. Establish a recoverable baseline. Use Git history or diff for clean tracked files; copy only dirty, untracked, or non-Git inputs that otherwise lack a recoverable prior version. Measure line or word count only when size reduction is a stated goal. Do not generate content hashes as generic completion evidence.
3. Inventory only affected trigger or routing behavior, permissions, stops and failure handling, domain validators, and unique edge cases.
4. Compress by moving attention, not meaning. Keep trigger coverage and common rules inline; leave field-heavy contracts on existing execution surfaces and disclose conditional detail one level deep. Remove history, motivation, obvious advice, and repeated examples unless one disambiguates behavior. Preserve affected safety, permission, privacy, destructive or external-write, stop, failure, and domain-validation rules.
5. Validate the changed surface. Run the skill validator for each changed skill, add a plugin or domain checker only when its contract or metadata changed, and run `git diff --check -- <changed-paths>`. Refresh installed state only when activation is authorized.
6. When the Core Rule requires independent evaluation, give the evaluator the baseline, candidate, and scoped oracle without a preferred verdict. Fix blocking drift and rerun only affected checks.
7. Report changed files, behavior impact, checks run, required reviewer status, blockers, and residual risk. Report size change only when it was part of the goal.
