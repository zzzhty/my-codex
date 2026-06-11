---
name: housekeeping
description: Use within DocWatcher when cleaning temporary files, generated caches, stale runtime artifacts, obsolete active documentation, outdated paths, old plugin cache versions, or post-migration repo clutter; use this for implementation-mode cleanup that should follow doc-alignment semantics while preserving user work, audit history, dependency installs, and source-of-truth evidence.
---

# Housekeeping

Use this skill for bounded cleanup after a migration, validation run, repo audit, or documentation alignment pass. It is based on `doc-alignment`, but focuses on removing disposable artifacts and correcting active guidance that has drifted from the current source of truth.

Do not use it for scheduled DocWatcher audits that must keep target repositories read-only. Use `doc-alignment` for pure semantic review when no cleanup is requested.

## Core Contract

1. Inspect before deleting. Record what category each candidate belongs to and why it is safe or unsafe to remove.
2. Preserve user work. Never delete tracked changes, untracked non-ignored files, local configs, databases, reports, or runtime state unless the user explicitly asks for that exact path or class.
3. Treat active docs differently from history. Update active docs and entry points when they contain stale names, paths, commands, or workflow claims. Leave archive/history content intact unless its index or current summary is wrong.
4. Fix the root cause of recurring cleanup noise when it is local and bounded, such as setting no-bytecode Python execution for hooks that keep writing `__pycache__`.
5. Verify cleanup with command evidence. Do not claim a clean state from intention alone.

## Candidate Classes

Safe to remove after inventory:

- Python bytecode and test caches: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`.
- OS/editor noise: `.DS_Store`, `Thumbs.db`, editor swap files.
- Tool temp files clearly under ignored temp/cache directories.
- Superseded local plugin cache versions only after `codex plugin list` or an equivalent installed-version check confirms the current active version.

Report first, do not delete by default:

- Dependency installs: `node_modules/`, `.venv/`, package-manager stores, downloaded SDKs.
- Build outputs that may be deployment artifacts: `dist/`, `build/`, coverage reports, generated static bundles.
- Runtime state and audit history: `$CODEX_HOME/doc-watcher/`, `$CODEX_HOME/skill-watcher/`, logs, reports, snapshots, local SQLite files.
- Untracked source-looking files, local config, private repo config, generated migrations, or unknown binary artifacts.

Align rather than delete:

- Active README, AGENTS, runbook, hook, script, skill, or TODO content that points at old names, stale commands, removed paths, outdated validation gates, or replaced workflow semantics.
- Indexes that still navigate to closed work as current work.
- Templates that accidentally contain concrete task state.

## Workflow

1. Read current truth:
   - root `AGENTS.md`
   - relevant README / plugin README / skill README
   - `.gitignore` files for the target area
   - current plugin manifests, hook configs, TODO indexes, or validation docs that define expected state

2. Inventory cleanup candidates:
   - `git status --short`
   - `git status --ignored --short`
   - `find <target> ... -name __pycache__ -o -name .pytest_cache ...` with explicit excludes for `.git`, dependency installs, and other heavy directories
   - `rg --hidden -n "<old-term>|<old-path>|<old-command>" <target> . --glob '!**/.git/**' --glob '!**/node_modules/**'`

3. Decide action per candidate:
   - Delete only disposable generated artifacts or confirmed superseded cache versions.
   - Update active docs when stale text is current-facing.
   - Leave archives alone unless active navigation or archive summaries are wrong.
   - Report candidates that need explicit approval.

4. Clean with scoped commands:
   - Use exact paths or tightly scoped `find` commands.
   - Exclude `.git`, `node_modules`, `.venv`, package-manager stores, and configured runtime state by default.
   - Do not run broad destructive commands from repository root unless the pattern is fully constrained and already inventoried.

5. Validate:
   - Repeat stale-term scans for the terms just cleaned.
   - Repeat cache/temp scans with the same excludes.
   - Run `git diff --check -- <changed-paths>` for edited docs/scripts/skills.
   - Run plugin or repo validators when cleanup touched plugin manifests, skills, hooks, scripts, or current documentation contracts.
   - Report any cache that reappears because a still-running hook or tool recreates it, and fix that root cause when in scope.

## Stop Conditions

Stop and report instead of cleaning when:

1. A candidate is untracked but not ignored and looks like source, config, data, migration, report, or private state.
2. Deleting would remove dependency installs, build artifacts, runtime databases, reports, or audit history without explicit user approval.
3. Stale text appears only in archive/history and current navigation is already correct.
4. Validation shows a command, hook, or script still recreates the artifact and the root cause is outside the current scope.
