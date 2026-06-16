---
name: doc-alignment
description: Use within DocWatcher to audit or align documentation, scripts, skills, runbooks, operational entry points, and planning folders across configured local repositories so current guidance, names, references, ownership, and validation gates match the current source of truth.
---

# Doc Alignment

Use this DocWatcher skill to keep local repository guidance source-of-truth driven. Names, entry points, references, ownership boundaries, active instructions, archives, and validation gates must agree.

Keep the alignment contract here; do not defer DocWatcher semantics to another skill.

## Core Contract

1. Identify current truth before editing: root instructions, active overview docs, current plans, runtime guides, script indexes, package commands, CI, configs, or DocWatcher reports.
2. Keep current guidance separate from history. Archives may preserve old terms; active docs and entry points must point at the current workflow.
3. Normalize user-facing names around current semantics. Preserve real code identifiers only as compatibility fields, migrations, or historical terms.
4. Update every path people or tools follow, including hidden/config folders such as `.devcontainer`, `.github`, `.codex`, package scripts, READMEs, runbooks, and skill folders.
5. Treat broken links, stale paths, failed validation, inconsistent names, and failed audit commands as first-class failures. Fix root causes before claiming alignment.
6. Scheduled DocWatcher audits must keep target repositories read-only and write only under `$CODEX_HOME/doc-watcher/` or an explicit output path.

## Mode Selection

Before using prior context, re-read the newest user request and target area. If the newest request changed scope, it wins. Active long-running goals or old implementation threads are background unless the user explicitly asks to continue them.

Use read-only mode for review, audit, analysis, comparison, assessment, report-only scans, scheduled scans, "only inspect", "do not edit", or similar language:

- Do not move, rename, delete, archive, or rewrite target files.
- Inspect and report findings, affected paths, recommended edits, validation gaps, and open questions.
- Mark proposed moves or rewrites as proposals.
- Run only non-mutating commands.
- Describe obvious fixes but wait for explicit implementation approval.

Use implementation mode when the user asks to align, update, reorganize, prune, rename, fix, or otherwise make changes. Apply the smallest sufficient edits and validate them.

## DocWatcher Audit Workflow

Start configured repository audits with deterministic evidence:

```bash
python3 scripts/doctor.py --config config/repos.example.json
python3 scripts/commit_counter.py --config config/repos.example.json
python3 scripts/generate_report.py --config config/repos.example.json --mode commit-dependent --mark-audited --digest
```

Use `config/repos.json` when a private config exists. For one repo:

```bash
python3 scripts/audit_repo.py --repo <repo-path> --name <repo-name> --print-report
```

When `generate_report.py --mode commit-dependent` skips a repo, report it as skipped. Config changes make a repo due even below the commit threshold. If any repo fails, surface the repo, command/path, and exact failure text.

Review reports for stale active guidance, history mixed into current docs, mismatched product/command/path/validation terms, recent behavior changes without docs, watch-term hits, broken links, and missing referenced files.

## Review Workflow

1. Inventory the target and references. Prefer `rg`:

```bash
rg --files <target>
rg --hidden -n "<old-term>|<old-path>|<disputed-term>" <target> . --glob '!**/.git/**' --glob '!**/node_modules/**'
```

2. Read entry points first: `AGENTS.md`, root/area README, current dev/usage/ops guide, checklist/TODO/goal plan, package commands, devcontainer and CI/workflow files, runbooks, subdirectory indexes, active planning files, skill metadata, and DocWatcher reports under `$CODEX_HOME/doc-watcher/reports/` or `$CODEX_HOME/doc-watcher/audits/`.

3. Classify each file role:
   - **Overview**: current navigation and execution posture.
   - **Guide**: current commands and expected environment.
   - **Architecture / Contract**: ownership, relationships, wire shapes, and compatibility boundaries.
   - **Validation / Audit**: commands, pass signals, and active blockers.
   - **Template**: reusable skeleton only, no real task state.
   - **TODO / Goal**: unfinished work, ordered milestones, or planned cleanup.
   - **Archive**: dated or replaced material only.
   - **Script / Runner**: executable entry point with stable, discoverable name.
   - **Skill**: reusable agent procedure with concise trigger metadata and body instructions.

4. Align recursively:
   - Move misplaced files into the existing typed owner directory.
   - Keep root docs as current posture plus links, not duplicated detail.
   - Use the same owner terms in root and subfolder docs.
   - Move dated/replaced reviews to the existing archive, or mark historical and remove from current navigation.
   - Put future cleanup in the active TODO/goal location.

## Finding Severity

- `High`: active docs contradict current truth, route users to broken commands, link to missing required files, or describe removed workflows.
- `Medium`: stale terminology, missing docs for recent behavior changes, duplicated guidance, unclear ownership, or active watch-term hits.
- `Low`: cleanup-only wording drift, minor index issues, archive labeling, or future polish.

Each finding needs file paths or command evidence, reasoning, and recommended next action.

## Script And Entry-Point Naming

Follow local convention first. Without one, prefer short verb+noun names such as `run_tests.ps1`, `check_runtime.sh`, `start_proxy.bat`, or `sync_docs.py`.

Keep directory naming consistent:

- runtime checks: `check_<target>`
- startup helpers: `start_<target>`
- bootstrap helpers: `bootstrap_<target>`
- cleanup helpers: `clean_<target>`
- sync helpers: `sync_<target>`

Avoid names that encode old product semantics, local machine details, or implementation accidents. After renaming, update wrappers, package commands, `.devcontainer`, CI/workflow config, `.github`, `.codex`, README/runbook examples, and child runner calls. Preserve executable bits and validate syntax with the owning shell/runtime.

## Documentation Tree Alignment

1. Root docs are current overview and execution entry points only.
2. Architecture, API contracts, deployment, validation, runtime audit, templates, TODO plans, and archives belong in typed subdirectories when that structure exists.
3. Archives may keep old terms; active docs must not present deprecated, duplicate, or compatibility-only surfaces as product semantics.
4. If active docs mention old user-facing terms, replace them or explain the real code field, test, migration, compatibility boundary, or archive context.
5. Keep reusable templates free of concrete task state.

## Planning/TODO Tree Alignment

1. Active index files are navigation and execution posture, not completed checkpoint history.
2. Active TODO/goal files contain next actions, gates, and close criteria. Archive completed evidence, historical checkpoint logs, and replaced plans.
3. Archives may keep historical names, old conclusions, and prior metrics. Do not rewrite archive content unless the archive index or summary is wrong.
4. Open editor tabs, stale filenames, and old goal docs are not source of truth. Compare them against current code, docs, and active indexes before deleting, archiving, or reactivating them.
5. Before deleting an old TODO, verify whether the underlying code path or failure mode still exists. If it does, keep it active or rewrite it as a current next-step item.
6. When closing a goal, remove it from active navigation, update the archive entry, and keep residual/future work as a separate active item.

Use the helper when it fits:

```bash
python <skill-folder>/scripts/check_planning_tree.py <planning-root>
```

## Skill Alignment

For Codex skills:

1. Use the skill-creation/update workflow as companion truth for frontmatter, resource layout, `agents/openai.yaml`, and validation.
2. Keep `SKILL.md` frontmatter to `name` and `description`.
3. Put all trigger conditions in `description`; the body loads only after trigger.
4. Keep bodies imperative and procedural. Remove process history, repo-only assumptions, and redundant explanation.
5. Refer to bundled resources relative to the skill folder.
6. Prefer generic placeholders plus examples over repo-specific paths, unless the path is intrinsic.
7. Inspect and update `agents/openai.yaml` when display name, short description, or default prompt no longer matches.
8. Do not edit cache/build artifacts such as `__pycache__`, bytecode, temp validation output, or generated logs unless explicitly asked.
9. Validate with the skill validator when available.

When aligning multiple skills, process them in user order or foundational-first; finish and validate a dependency skill before its dependents; keep trigger descriptions distinct; move shared generic rules only when both skills need them; avoid duplicated validation snippets when scripts or helpers cover them; finish with a cross-skill stale-reference, obsolete-term, and broken-link check.

## Validation

Match validation to the changed surface.

For docs and skills:

```bash
git diff --check -- <changed-paths>
```

If changed skills are outside the current Git worktree, say `git diff --check` is not applicable for those paths and validate the actual skill paths directly.

If Markdown moved or links changed, run a relative-link check scoped to the changed tree. Report every missing local target with file and line; ignore anchors, `http(s)`, `mailto`, and empty targets.

For script renames, use the owning parser and stale-reference scan:

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
PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py}"
(cd backend && uv run python "$PLUGIN_VALIDATOR" ..)
```

If a dependency is missing, install it only when allowed; otherwise report the exact module and do not claim validator success. Manual frontmatter/link checks are partial checks, not validator substitutes.

## Final Report

Report reviewed directories/entry points, changed semantics or naming conventions, moved/archived/renamed/historical items, exact validation commands/results, and unresolved conflicts or preserved legacy identifiers.
