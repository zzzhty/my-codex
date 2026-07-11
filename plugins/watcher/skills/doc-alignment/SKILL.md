---
name: doc-alignment
description: Use within Watcher to audit or align documentation, scripts, skills, runbooks, operational entry points, and planning folders across configured local repositories so current guidance, names, references, ownership, and validation gates match the current source of truth.
---

# Doc Alignment

Use this Watcher skill to keep local repository guidance source-of-truth driven. Names, entry points, references, ownership boundaries, active instructions, archives, and validation gates must agree.

Keep the alignment contract here; do not defer Watcher doc-domain semantics to another skill.

## Core Contract

1. Identify current truth before editing: root instructions, active overview docs, current plans, runtime guides, script indexes, package commands, CI, configs, or Watcher doc reports.
2. Keep current guidance separate from history. Archives may preserve old terms; active docs and entry points must point at the current workflow.
3. Normalize user-facing names around current semantics. Preserve real code identifiers only as compatibility fields, migrations, or historical terms.
4. Update every path people or tools follow, including hidden/config folders such as `.devcontainer`, `.github`, `.codex`, package scripts, READMEs, runbooks, and skill folders.
5. Treat broken links, stale paths, failed validation, inconsistent names, and failed audit commands as first-class failures. Fix root causes before claiming alignment.
6. Scheduled Watcher doc audits must keep target repositories read-only and write only under `$CODEX_HOME/watcher/doc/` or an explicit output path.

## Mode Selection

Before using prior context, re-read the newest user request and target area. If the newest request changed scope, it wins. Active long-running goals or old implementation threads are background unless the user explicitly asks to continue them.

Use read-only mode for review, audit, analysis, comparison, assessment, report-only scans, scheduled scans, "only inspect", "do not edit", or similar language:

- Do not move, rename, delete, archive, or rewrite target files.
- Inspect and report findings, affected paths, recommended edits, validation gaps, and open questions.
- Mark proposed moves or rewrites as proposals.
- Run only non-mutating commands.
- Describe obvious fixes but wait for explicit implementation approval.

Use implementation mode when the user asks to align, update, reorganize, prune, rename, fix, or otherwise make changes. Apply the smallest sufficient edits and validate them.

## Watcher Doc Audit Workflow

Start configured repository audits with deterministic evidence:

```bash
python3 scripts/watcher doc doctor --config config/repos.example.json
python3 scripts/watcher doc commit-counter --config config/repos.example.json
python3 scripts/watcher doc report --config config/repos.example.json --mode commit-dependent --mark-audited --digest
```

Use `config/repos.json` when a private config exists. For one repo:

```bash
python3 scripts/watcher doc audit --repo <repo-path> --name <repo-name> --print-report
```

When `scripts/watcher doc report --mode commit-dependent` skips a repo, report it as skipped. Config changes make a repo due even below the commit threshold. If any repo fails, surface the repo, command/path, and exact failure text.

Review reports for stale active guidance, history mixed into current docs, mismatched product/command/path/validation terms, recent behavior changes without docs, watch-term hits, broken links, and missing referenced files.

## Review Workflow

1. Inventory the target and references. Prefer `rg`:

```bash
rg --files <target>
rg --hidden -n "<old-term>|<old-path>|<disputed-term>" <target> . --glob '!**/.git/**' --glob '!**/node_modules/**'
```

2. Read entry points first: `AGENTS.md`, root/area README, current dev/usage/ops guide, checklist/TODO/goal plan, package commands, devcontainer and CI/workflow files, runbooks, subdirectory indexes, active planning files, skill metadata, and Watcher doc reports under `$CODEX_HOME/watcher/doc/reports/` or `$CODEX_HOME/watcher/doc/audits/`.

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

## Conditional Alignment Reference

Before continuing, read `references/alignment-reference.md` when the target touches a script or entry-point name, documentation tree placement, planning/TODO navigation, Codex skill source, or validation command selection. Apply every matching section; for implementation work, always apply its Validation section before claiming completion.

Completion criterion: the common workflow above is satisfied and every triggered reference section meets its own criterion.

## Final Report

Report reviewed directories/entry points, changed semantics or naming conventions, moved/archived/renamed/historical items, exact validation commands/results, and unresolved conflicts or preserved legacy identifiers.
