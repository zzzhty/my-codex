---
name: skill-compressor
description: Reduce the instruction footprint of agent skills and their references while preserving trigger coverage, required behavior, and validation owned by the changed surface.
---

# Skill Compressor

Use this skill for behavior-preserving instruction reduction. Use `prompt-strategy-loop` when the requested change intentionally redesigns routing, permissions, safety, failure, or validation behavior. Use `skill-maintainer` when Watcher usage evidence should produce a proposal rather than direct compression. Deterministic scripts remain out of scope unless the user explicitly includes them.

## Core Rule

Compare the candidate with a recoverable baseline and a scoped inventory of affected meanings. A smaller file is not equivalent when trigger coverage, permissions, stop or failure behavior, validators, or unique edge cases drift.

Apply the proportional review rule owned by `prompt-strategy-loop`: independent evaluation is required when compression changes invocation or routing, permissions, safety/privacy, destructive or external actions, recurring automation, persisted or external contracts, or removes a stop or validation gate. If required review is unavailable, mark the candidate unverified.

Invoking this skill authorizes only the read-only semantic comparison needed for compression; mutation and unrelated delegation still follow the active request and environment.

## Workflow

1. Bound the editable skill metadata, body, references, templates, and helper surfaces. Preserve unrelated dirty work.
2. Establish a recoverable baseline through Git history or diff. Copy only dirty, untracked, or non-Git inputs that otherwise lack recovery.
3. Inventory the affected trigger/routing branches, permissions, stops, failure handling, validators, and unique edge cases.
4. Compress attention, not meaning:
   - keep common execution steps and non-default invariants inline;
   - disclose conditional detail one level deep behind a strong pointer;
   - leave field-heavy contracts with existing templates, scripts, schemas, or checkers;
   - remove duplicated meaning, stale history, motivation, obvious advice, and repeated examples unless one disambiguates behavior;
   - prefer positive target behavior while retaining true destructive, privacy, external-write, and source/cache guardrails.
5. Validate only the affected surface: skill/frontmatter validation, relative links, owning plugin or domain checks when their contract changed, and `git diff --check -- <changed-paths>`.
6. Run required semantic review against the baseline and oracle, fix blocking drift, and repeat only affected checks.
7. Refresh installed state only when activation is authorized.

## Completion

Report changed files, size change when relevant, preserved and intentionally changed behavior, checks run, reviewer status, blockers, and residual risk. Claim equivalence only when every affected meaning remains reachable and the candidate passes its scoped oracle.
