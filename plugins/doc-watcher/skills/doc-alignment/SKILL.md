---
name: doc-alignment
description: Use within DocWatcher to audit or align documentation, scripts, skills, runbooks, operational entry points, and planning folders across configured local repositories so current guidance, names, references, ownership, and validation gates match the current source of truth.
---

# Doc Alignment

Use this skill to audit and align documentation semantics for configured local repositories. Keep the work source-of-truth driven: names, entry points, references, ownership boundaries, active guidance, archives, and validation must agree.

This is the DocWatcher version of the alignment workflow. Do not defer semantic rules to a separate skill; maintain the alignment contract here.

## Core Contract

1. Identify the current source of truth before editing: root instructions, active overview docs, current plans, runtime guides, script indexes, package commands, CI, configuration files, or generated DocWatcher audit reports.
2. Keep current guidance separate from history. Archives may preserve old terminology and conclusions, but active docs and entry points must point at the current workflow.
3. Normalize names around user-facing semantics, not legacy implementation names. Preserve real code identifiers when required, but label them as compatibility surfaces, field names, migrations, or historical terms.
4. Update references wherever people or tools will follow them, including hidden/config directories such as `.devcontainer`, `.github`, `.codex`, package scripts, READMEs, runbooks, and skill folders.
5. Treat broken links, stale paths, failed validation commands, inconsistent naming, and failed audit commands as first-class failures. Fix the root cause before claiming alignment.
6. In scheduled DocWatcher audits, keep target repositories read-only and write reports only under `~/.codex/doc-watcher/` or an explicit output path.

## Mode Selection

Before editing, determine whether the user requested review-only work or implementation.

Before carrying over prior context, re-read the newest user request and the target area. If the newest request changed from implementation to planning, explanation, skill editing, archive cleanup, or review-only work, follow the newest scope and stop any older task thread from steering the turn.

If an active long-running goal or prior implementation thread exists, treat it as background only unless the newest request explicitly asks to continue it. Alignment work should not advance old milestones, update old evidence, or run unrelated validation just because that context is present.

Use read-only mode when the user asks for review, audit, analysis, comparison, assessment, daily report, scheduled scan, "only inspect", "do not edit", or similar language. In read-only mode:

1. Do not move, rename, delete, archive, or rewrite files in target repositories.
2. Inspect the target area and report findings, affected paths, recommended edits, validation gaps, and open questions.
3. Mark proposed moves or rewrites as proposals only.
4. Run non-mutating commands only.
5. If a fix is obvious, describe the exact edit but wait for an explicit implementation request before applying it.

Use implementation mode when the user asks to align, update, reorganize, prune, rename, fix, or otherwise make changes. In implementation mode, apply the smallest edits that satisfy the requested alignment and validate them.

## DocWatcher Audit Workflow

For configured repository audits, start with deterministic evidence collection:

```bash
python3 scripts/doctor.py --config config/repos.example.json
python3 scripts/commit_counter.py --config config/repos.example.json
python3 scripts/daily_report.py --config config/repos.example.json --print-report
```

Use `config/repos.json` instead of the example when a private local config exists.

For a single repository:

```bash
python3 scripts/audit_repo.py --repo <repo-path> --name <repo-name> --print-report
```

When `daily_report.py --mode commit-dependent` skips a repo, report it as skipped rather than audited. When any repo fails, surface the failing repo, command/path, and exact failure text.

Review the generated report with these checks:

- Are active docs still pointing at the current workflow?
- Are archive or historical notes mixed into active guidance?
- Do entry points name the same product, commands, paths, and validation gates?
- Did recent commits change behavior, scripts, config, APIs, or operations without matching documentation updates?
- Do configured watch terms indicate stale product language?
- Are broken links or missing referenced files present?

## Review Workflow

1. Inventory the target area and nearby references. Prefer `rg` because it works well across platforms:

```bash
rg --files <target>
rg --hidden -n "<old-term>|<old-path>|<disputed-term>" <target> . --glob '!**/.git/**' --glob '!**/node_modules/**'
```

2. Read entry points first:

- root instructions such as `AGENTS.md`
- root or area `README.md`
- current development, usage, or operations guide
- current checklist, TODO index, or goal plan
- package commands, devcontainer config, CI/workflow files, runbook references
- subdirectory indexes, active planning files, and skill metadata
- DocWatcher reports under `~/.codex/doc-watcher/reports/` or `~/.codex/doc-watcher/audits/`

3. Decide each file's role:

- **Overview**: current navigation and execution posture.
- **Guide**: current commands and expected environment.
- **Architecture / Contract**: current ownership, relationships, wire shapes, and compatibility boundaries.
- **Validation / Audit**: commands, pass signals, and active blockers.
- **Template**: reusable skeleton only, no real task state.
- **TODO / Goal**: unfinished work, ordered milestones, or planned cleanup.
- **Archive**: dated or replaced material only.
- **Script / Runner**: executable entry point with a stable, discoverable name.
- **Skill**: reusable agent procedure with concise trigger metadata and body instructions.

4. Align recursively:

- Move misplaced files into their typed owner directory when the project already has that structure.
- Update root docs so they summarize current posture and link to typed subfolders instead of duplicating details.
- Update subfolder docs to use the same owner terms as root.
- Move dated or replaced reviews to the project's archive location when one exists; otherwise mark them historical and remove them from current navigation.
- Record future cleanup in the active TODO/goal location rather than scattering notes.

## Finding Severity

Group audit findings by severity:

- `High`: active docs contradict current source of truth, send users to broken commands, link to missing required files, or describe a removed workflow.
- `Medium`: stale terminology, incomplete docs for recent behavior changes, duplicated guidance, unclear source-of-truth ownership, or watch-term hits in active docs.
- `Low`: cleanup-only wording drift, minor index issues, optional archive labeling, or future documentation polish.

Each finding must include file paths or command evidence, the reasoning, and a recommended next action.

## Script And Entry-Point Naming

When aligning scripts or operational entry points:

1. Follow the local naming convention first. If there is no convention, prefer short verb+noun names such as `run_tests.ps1`, `check_runtime.sh`, `start_proxy.bat`, or `sync_docs.py`.
2. Keep each directory internally consistent:
   - runtime checks: `check_<target>`
   - startup helpers: `start_<target>`
   - bootstrap helpers: `bootstrap_<target>`
   - cleanup helpers: `clean_<target>`
   - sync helpers: `sync_<target>`
3. Avoid names that encode old product semantics, local machine details, or implementation accidents.
4. After renaming, update all callers and docs, not just obvious direct references:
   - wrapper scripts
   - package manager commands
   - `.devcontainer` and CI/workflow config
   - `.github` and `.codex` automation/skill references
   - README / runbook examples
   - child runner calls inside parent scripts
5. Preserve executable bits where relevant and validate syntax with the shell or runtime that owns each script.

## Documentation Tree Alignment

For documentation or planning trees:

1. Root docs should be current overview and execution entry points only.
2. Architecture, API contracts, deployment, validation, runtime audit, templates, TODO plans, and archives belong in typed subdirectories when that structure exists.
3. Archives may keep old terminology, but active docs must not present deprecated, duplicate, or compatibility-only surfaces as product semantics.
4. If current docs mention old user-facing terms, either replace them with the current term or explicitly explain why the old string is a real code field, test, migration, compatibility boundary, or archived history.
5. Keep reusable templates free of concrete task state.

## Planning/TODO Tree Alignment

When aligning TODO, goal, or planning folders:

1. Treat the active index files as navigation and execution posture only. They should point to current unresolved work, not preserve completed checkpoint history.
2. Active TODO/goal files should contain next actions, gates, and close criteria. Move completed evidence, historical checkpoint logs, and replaced plans to the existing archive location when one exists.
3. Archive files may keep historical names, old conclusions, and prior metrics. Do not rewrite archive content merely to match current terminology unless the archive index or summary is wrong.
4. Open editor tabs, stale filenames, or old goal documents are not source of truth by themselves. Compare them against current code, docs, and active indexes before deleting, archiving, or reactivating them.
5. Before deleting an old TODO, verify whether the underlying code path or failure mode still exists. If it still exists, keep it active or rewrite it as a current next-step item.
6. When closing a goal, remove it from active navigation, add or update the archive entry, and keep residual/future work as a separate active item instead of burying it in the closed goal.

Use the bundled helper when it fits the tree:

```bash
python <skill-folder>/scripts/check_planning_tree.py <planning-root>
```

## Skill Alignment

When the target area contains Codex skills:

1. Use the skill-creation/update workflow as the companion source of truth when available, especially for frontmatter, resource layout, `agents/openai.yaml`, and validation.
2. Keep `SKILL.md` frontmatter limited to `name` and `description`.
3. Put all trigger conditions in `description`; the body is loaded only after the skill triggers.
4. Keep the body imperative and procedural. Remove process history, repo-only assumptions, and redundant explanation.
5. Refer to bundled resources with paths relative to the skill folder, such as `templates/example.md`.
6. Replace repo-specific paths and source-of-truth filenames with generic placeholders plus examples, unless the path is intrinsic to the skill's purpose.
7. Inspect `agents/openai.yaml` when present. Regenerate or edit it if the display name, short description, or default prompt no longer matches `SKILL.md`.
8. Do not edit cache/build artifacts such as `__pycache__`, compiled bytecode, temporary validation output, or generated logs unless the user explicitly asks for cleanup.
9. Validate with the skill validator when available.

When aligning multiple skills in one request:

1. Process them in the user's requested order. If no order is given, align the foundational workflow skill before the skill that depends on it.
2. Finish and validate each skill before moving to the next when the first skill defines rules the second skill will rely on.
3. Keep trigger descriptions distinct so the skills do not fire for the same task unless that overlap is intentional.
4. Move shared generic rules into the broader skill only when both skills need them; otherwise keep specialized rules local to the narrower skill.
5. Avoid copying long validation snippets between skills when a bundled script or referenced helper can express the same check.
6. After editing all skills, run validation per skill and one cross-skill check for stale references, duplicated obsolete terms, and broken relative links.

## Validation

Run validation that matches the changed surface.

For docs and skills:

```bash
git diff --check -- <changed-paths>
```

If the changed skills live outside the current Git worktree, do not imply that `git diff --check` covered them. Run the skill validator and link/resource checks against the actual skill paths, and report `git diff --check` as not applicable for those external paths.

If Markdown files moved or links changed, run a relative-link check scoped to the changed tree:

```bash
python - <<'PY'
from pathlib import Path
import re
root = Path("<docs-or-skill-path>")
pat = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
missing = []
for f in root.rglob("*.md"):
    text = f.read_text(encoding="utf-8")
    for m in pat.finditer(text):
        target = m.group(1).strip()
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        p = (f.parent / target).resolve()
        ok = p.is_dir() if target.endswith("/") else p.exists()
        if not ok:
            line = text[:m.start()].count("\n") + 1
            missing.append((str(f), line, m.group(1)))
if missing:
    for f, line, target in missing:
        print(f"{f}:{line} missing {target}")
    raise SystemExit(1)
print("all markdown relative links resolve")
PY
```

For script renames, choose checks for the actual script types present:

```bash
bash -n <script>.sh
powershell -NoProfile -Command { [System.Management.Automation.PSParser]::Tokenize((Get-Content -Raw -LiteralPath '<script>.ps1'), [ref]$null) > $null }
rg --hidden -n "<old-script-name>|<old-path>" . --glob '!**/.git/**' --glob '!**/node_modules/**'
git diff --check -- <changed-paths>
```

Add lightweight dry-runs or `--summary` commands when entry points provide them. Do not run heavyweight runtime suites for naming-only alignment unless behavior or gates changed.

For DocWatcher plugin validation:

```bash
python3 scripts/doctor.py --config config/repos.example.json
python3 -m py_compile scripts/*.py
cd backend && uv run python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/doc-watcher
```

If the validator cannot run because a dependency is missing, install the missing dependency when the user allowed dependency installation. Otherwise report the exact missing module and do not claim validator success. A manual frontmatter or link check may be reported only as a separate partial check, not as a substitute validator pass.

## Final Report

Report:

1. Which directories or entry points were reviewed.
2. What semantics or naming conventions changed.
3. What was moved, archived, renamed, or intentionally left historical.
4. Exact validation commands and results.
5. Any unresolved conflicts or intentionally preserved legacy identifiers.
