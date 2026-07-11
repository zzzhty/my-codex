# Conditional Alignment Reference

Read only the sections triggered by the target named in `../SKILL.md`. The main skill owns mode selection, audit safety, common review steps, severity, and final reporting.

## Script And Entry-Point Naming

Follow local convention first. Without one, prefer short verb+noun names such as `run_tests.ps1`, `check_runtime.sh`, `start_proxy.bat`, or `sync_docs.py`.

Keep directory naming consistent:

- runtime checks: `check_<target>`
- startup helpers: `start_<target>`
- bootstrap helpers: `bootstrap_<target>`
- cleanup helpers: `clean_<target>`
- sync helpers: `sync_<target>`

Avoid names that encode old product semantics, local machine details, or implementation accidents. After renaming, update wrappers, package commands, `.devcontainer`, CI/workflow config, `.github`, `.codex`, README/runbook examples, and child runner calls. Preserve executable bits and validate syntax with the owning shell/runtime.

Completion criterion: every executable path and caller uses the chosen name, the old name scan is clean outside declared history/compatibility, and the owning parser or runtime accepts the renamed entry point.

## Documentation Tree Alignment

1. Root docs are current overview and execution entry points only.
2. Architecture, API contracts, deployment, validation, runtime audit, templates, TODO plans, and archives belong in typed subdirectories when that structure exists.
3. Archives may keep old terms; active docs must not present deprecated, duplicate, or compatibility-only surfaces as product semantics.
4. If active docs mention old user-facing terms, replace them or explain the real code field, test, migration, compatibility boundary, or archive context.
5. Keep reusable templates free of concrete task state.

Completion criterion: current navigation reaches one typed owner for each live document role, historical material is clearly historical, and templates contain no task state.

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

Completion criterion: active indexes contain only live work, closed/replaced evidence follows local archive rules, and unresolved residual work remains discoverable as a current item.

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

Completion criterion: every changed skill preserves distinct triggers and operational semantics, metadata/resources agree with the body, generated caches remain untouched, and skill validation passes.

## Validation

Match validation to the changed surface. For docs and skills:

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

For Watcher doc-domain validation:

```bash
python3 scripts/watcher doc doctor --config config/repos.example.json
python3 -m compileall -q scripts/watcher_runtime
PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py}"
python3 "$PLUGIN_VALIDATOR" .
```

If a dependency is missing, install it only when allowed; otherwise report the exact module and do not claim validator success. Manual frontmatter/link checks are partial checks, not validator substitutes.

Completion criterion: every changed surface has a passing owning check, every failed command/path is reported exactly, and no partial/manual check is represented as full validation.
