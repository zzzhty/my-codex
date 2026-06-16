---
name: housekeeping
description: Use within DocWatcher when cleaning temporary files, generated caches, stale runtime artifacts, obsolete active documentation, outdated paths, old plugin cache versions, or post-migration repo clutter; use this for implementation-mode cleanup that should follow doc-alignment semantics while preserving user work, audit history, dependency installs, and source-of-truth evidence.
---

# Housekeeping

Use this DocWatcher skill for bounded cleanup after migration, validation, audit, or doc-alignment work. It applies `doc-alignment` semantics to disposable artifacts and stale active guidance.

Do not use it for scheduled DocWatcher audits that must keep targets read-only. Use `doc-alignment` for semantic review without cleanup.

## Core Contract

1. Inspect before deleting. Record each candidate class and why removal is safe or unsafe.
2. Preserve user work. Never delete tracked changes, untracked non-ignored files, local configs, databases, reports, or runtime state unless the user explicitly asks for that exact path or class.
3. Separate active docs from history. Fix stale names, paths, commands, or workflow claims in active docs and entry points; leave archives/history intact unless their index or current summary is wrong.
4. Fix bounded local root causes of recurring cleanup noise, such as hooks writing `__pycache__`.
5. Verify cleanup with command evidence.

## Candidate Classes

Safe after inventory:

- Python/test caches: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`.
- OS/editor noise: `.DS_Store`, `Thumbs.db`, swap files.
- Tool temp files clearly under ignored temp/cache directories.
- Superseded local plugin cache versions after `codex plugin list` or equivalent confirms the active version.

Report first, do not delete by default:

- Dependency installs: `node_modules/`, `.venv/`, package-manager stores, downloaded SDKs.
- Build/deploy artifacts: `dist/`, `build/`, coverage reports, generated static bundles.
- Runtime state and audit history: `$CODEX_HOME/doc-watcher/`, `$CODEX_HOME/skill-watcher/`, logs, reports, snapshots, SQLite files.
- Untracked source-looking files, local config, private repo config, generated migrations, or unknown binaries.

Align rather than delete:

- Active README, AGENTS, runbook, hook, script, skill, or TODO content pointing at old names, stale commands, removed paths, outdated validation gates, or replaced workflow semantics.
- Indexes that still navigate to closed work as current.
- Templates containing concrete task state.

## Workflow

1. Read current truth: root `AGENTS.md`, relevant README/plugin README/skill README, target `.gitignore`, current plugin manifests, hook configs, TODO indexes, and validation docs.
2. Inventory candidates:

```bash
git status --short
git status --ignored --short
find <target> ... -name __pycache__ -o -name .pytest_cache ...
rg --hidden -n "<old-term>|<old-path>|<old-command>" <target> . --glob '!**/.git/**' --glob '!**/node_modules/**'
```

3. Decide per candidate: delete only disposable generated artifacts or confirmed superseded cache versions; update active stale docs; leave archives alone unless active navigation or archive summaries are wrong; report anything needing explicit approval.
4. Clean with exact paths or tightly scoped `find`; exclude `.git`, `node_modules`, `.venv`, package-manager stores, and configured runtime state by default. Do not run broad destructive commands from repo root unless the pattern is fully constrained and inventoried.
5. Validate by repeating stale-term and cache scans, running `git diff --check -- <changed-paths>`, and running plugin/repo validators when cleanup touched manifests, skills, hooks, scripts, or current documentation contracts. If a cache reappears because a hook or tool recreates it, report that and fix the root cause when in scope.

## Stop Conditions

Stop and report instead of cleaning when:

1. A candidate is untracked, not ignored, and looks like source, config, data, migration, report, or private state.
2. Deleting would remove dependency installs, build artifacts, runtime databases, reports, or audit history without explicit approval.
3. Stale text appears only in archive/history and current navigation is correct.
4. Validation shows a command, hook, or script still recreates the artifact and the root cause is outside scope.
