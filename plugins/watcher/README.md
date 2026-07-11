# Watcher

Watcher consolidates the former DocWatcher and Skill Watcher plugin surfaces into one package while preserving separate skill invocation boundaries.

The plugin owns two runtime domains:

```text
$CODEX_HOME/watcher/
├── doc/
│   ├── audits/
│   ├── reports/
│   └── repo-state.json
└── skill/
    ├── logs/events.jsonl
    ├── reports/
    ├── proposals/
    ├── turns/
    ├── schema-version.json
    └── skill-metadata-cache.json
```

On `SessionStart`, Watcher rebuilds `skill-metadata-cache.json` from the local marketplace catalog and plugin-owned manifests. Catalog/plugin identity mismatches, malformed manifests, unsupported metadata schemas, and invalid skill relationships stop the refresh with a visible error; Watcher does not fall back to scanning `plugins/*`.

Packaged skills:

- `doc-alignment`: audit or align documentation, scripts, skills, runbooks, operational entry points, and planning folders against current source of truth.
- `housekeeping`: clean temporary files, generated caches, stale runtime artifacts, obsolete active documentation, outdated paths, and post-migration clutter.
- `skill-maintainer`: analyze skill usage evidence and propose bounded `SKILL.md` maintenance updates without automatic source mutation.
- `skill-compressor`: reduce skill or plugin instruction footprint while preserving operational semantics.

Current migration scope:

- Source skills and direct skill resources have moved under `plugins/watcher/skills/`.
- Report/audit scripts live behind the unified `plugins/watcher/scripts/watcher` entrypoint.
- Python implementations live in the named `scripts/watcher_runtime/skill` and `scripts/watcher_runtime/doc` packages; callers and tests use those modules through `main(argv)`, not direct script paths.
- The former DocWatcher cockpit backend/frontend and legacy patch/PR/provider/webhook surfaces were not migrated into the active plugin source. Git history remains the recovery path for those retired experiments.

Use the unified CLI from the Watcher plugin root:

```bash
python3 scripts/watcher doc report --config config/repos.example.json --print-report
python3 scripts/watcher skill report --since 7d
python3 scripts/watcher migrate-state --dry-run
```

Run `python3 scripts/watcher migrate-state --apply` to move `$CODEX_HOME/skill-watcher/` to `$CODEX_HOME/watcher/skill/` and `$CODEX_HOME/doc-watcher/` to `$CODEX_HOME/watcher/doc/`. The migration refuses to merge if the target already exists.
