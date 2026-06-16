---
name: skill-compressor
description: Use when reducing the instruction footprint of one or more Codex skills, plugin skill sets, skill references, templates, or UI prompts while preserving operational semantics through snapshots, semantic inventories, validation commands, and independent review for semantic drift.
---

# Skill Compressor

Use this skill to compress Codex skill instructions without changing their behavior. The goal is fewer tokens and clearer attention, not weaker rules.

Do not use it to redesign workflows, change safety/permission behavior, remove validation gates, or refactor deterministic scripts. Use `skill-maintainer` when Skill Watcher log evidence should produce a maintenance proposal instead of direct compression.

## Core Rule

Do not claim semantic equivalence unless:

1. The old and new versions were compared against an explicit semantic inventory.
2. Validation passed and an independent review found no blocking drift.

If independent review is unavailable, report the compression as unverified.

## Workflow

1. Define scope:
   - Include skill folders, plugin README/manifest metadata, `agents/openai.yaml`, references, templates, and helper scripts in scope.
   - Treat scripts as validation surfaces by default; edit or refactor them only when explicitly asked.
   - Note dirty worktree files and avoid reverting unrelated changes.

2. Snapshot first:
   - Copy scoped files to `/tmp/<slug>_pre_compression/` or equivalent.
   - Record baseline size with `wc -l -w`.
   - Keep the snapshot for review.

3. Build a semantic inventory:
   - Trigger/use boundaries and cross-skill routing.
   - Required inputs, outputs, permissions, stop conditions, escalation, and failure handling.
   - Execution harness, orchestration, subagent roles, worktree/isolation, connector boundaries, and independent verification.
   - Validation commands, readiness checks, generated artifact rules, writeback targets, rollback/close hygiene, and forbidden shortcuts.
   - Unique edge-case rules not implied by generic wording.

4. Compress by moving attention, not meaning:
   - Keep high-frequency rules and routing in `SKILL.md`.
   - Keep field-heavy contracts in templates, references, or scripts when they are already execution surfaces.
   - Preserve frontmatter trigger coverage and important trigger terms.
   - Replace repeated examples with one compact rule only when no unique condition is lost.
   - Keep UI metadata and README descriptions discoverable enough for routing.
   - Use `apply_patch` for manual edits and avoid cache/build artifacts.

5. Validate:
   - Run skill validators for every changed skill.
   - Run plugin validation when a plugin skill set changed.
   - Run exposed readiness, link, template, or syntax checks.
   - Run `git diff --check -- <changed-paths>`.
   - If installed from this repo, refresh the local plugin cache with the repo's refresh command and diff source against cache.

6. Run independent semantic review:
   - Give the reviewer the snapshot, current files, and semantic inventory.
   - Ask for `equivalent`, `mostly equivalent with caveats`, or `semantic change`.
   - Require file/line findings for drift.
   - Fix blocking findings, rerun validation, and repeat review.
   - Restore concise wording or report residual risk for caveats that reduce discoverability or copy-paste usability.

7. Report files compressed, size change, validation results, review verdict, semantics intentionally left in templates/references/scripts, and residual risks.

## Heuristics

- Prefer one procedural rule over several explanatory paragraphs.
- Remove process history, motivation, and obvious advice.
- Preserve negative rules: do not mutate, ask permission, fabricate success, bypass validation, or run untrusted commands when the source forbids it.
- Preserve exact stop conditions affecting autonomy, permissions, privacy, destructive actions, external writes, or failure reporting.
- Keep examples only when they disambiguate behavior or provide reusable prompt shape.
- Keep references one level from `SKILL.md`; add new references only for conditional detail or context-budget pressure.
- Do not compress away evidence requirements. Behavioral claims still need paths, commands, artifacts, reviewer status, or validation results.

## Independent Review Prompt

```text
Read-only semantic review.

Compare pre-compression snapshot: <snapshot-path>
with current source: <current-path>.

Do not edit files. Decide whether operational semantics are preserved, allowing detailed fields to live in templates, references, or scripts.

Focus on trigger/use boundaries, cross-skill routing, permissions, stop conditions, failure handling, validation gates, template/reference/script support, UI/README discoverability, and unique old rules now absent or only implied.

Return:
- verdict: equivalent / mostly equivalent with caveats / semantic change
- findings with old/current file references and why they matter
- whether any finding blocks semantic preservation
```

## Validation Checklist

Use the repo's actual tooling. For `my-codex`, prefer:

```bash
/Users/max/.codex/venvs/my-codex/bin/python /Users/max/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>
/Users/max/.codex/venvs/my-codex/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py <plugin-dir>
git diff --check -- <changed-paths>
python3 scripts/refresh_my_codex.py --plugin <plugin-name>
python3 scripts/check_my_codex.py
```

Add skill-specific ready/link checks, cache diffs, and `find <path> -name __pycache__ -o -name '*.pyc'` cleanup checks when relevant.
