---
name: housekeeping
description: Use within Watcher to remove inventoried disposable artifacts or repair stale active guidance after migration, validation, or audit work while preserving user work and durable state.
---

# Housekeeping

Use this skill for bounded implementation-mode cleanup. Use `doc-alignment` for semantic review or scheduled audits that must keep target repositories read-only.

## Core Contract

Delete only artifacts whose ownership and disposability are established by inspection. Preserve everything else unless the user approves the exact path or class.

Classify candidates into three groups:

1. **Disposable generated artifacts** — ignored Python/test caches, OS/editor noise, files under known temporary/cache roots, and confirmed superseded local plugin cache versions. These may be removed after inventory.
2. **Active semantic drift** — current README, AGENTS, runbook, hook, script, skill, TODO, or index content that points at stale names, paths, commands, or workflow claims. Align the active owner instead of deleting history.
3. **Protected or approval-required state** — tracked or untracked source-looking files, local/private configuration, databases, reports, audit/runtime state, dependency installs, build/deploy output, migrations, and unknown binaries. Preserve and report these unless explicitly authorized.

Archives remain historical unless active navigation or their current summary is wrong.

## Workflow

1. Read current truth: root instructions, relevant README/plugin docs, `.gitignore`, manifests, hook configuration, TODO indexes, and validation guidance.
2. Inventory the target and ignored state:

```bash
git status --short
git status --ignored --short
find <target> ... -name __pycache__ -o -name .pytest_cache ...
rg --hidden -n "<old-term>|<old-path>|<old-command>" <target> . --glob '!**/.git/**' --glob '!**/node_modules/**'
```

3. Record the classification and reason for each candidate class.
4. Remove disposable artifacts with exact paths or tightly bounded patterns. Repair active semantic drift in its owning file. Keep protected state untouched and identify the approval needed.
5. Re-run the relevant inventory or stale-term scan. Use `git diff --check -- <changed-paths>` and the owning validator when manifests, skills, hooks, scripts, or current documentation contracts changed.
6. When a tool or hook recreates an artifact, fix that bounded local root cause when in scope; otherwise report the recreating command and blocker.

## Completion

Report what was removed or aligned, what was preserved, the evidence supporting each classification, validation results, and unresolved approval-required state. A cleanup is complete only when the targeted noise or active drift is gone without losing user work, durable state, or historical evidence.
