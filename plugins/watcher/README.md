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

Packaged skills:

- `doc-alignment`: audit or align documentation, scripts, skills, runbooks, operational entry points, and planning folders against current source of truth.
- `housekeeping`: clean temporary files, generated caches, stale runtime artifacts, obsolete active documentation, outdated paths, and post-migration clutter.
- `skill-maintainer`: analyze skill usage evidence and propose bounded `SKILL.md` maintenance updates without automatic source mutation.
- `skill-compressor`: reduce skill or plugin instruction footprint while preserving operational semantics.

Current first-batch migration scope:

- Source skills and direct skill resources have moved under `plugins/watcher/skills/`.
- Current report/audit scripts have moved under `plugins/watcher/scripts/doc/` and `plugins/watcher/scripts/skill/`.
- DocWatcher cockpit backend/frontend and legacy patch/PR/provider/webhook surfaces are not active in this plugin batch.

Use domain-qualified scripts until the unified `scripts/watcher` CLI is completed:

```bash
python3 scripts/doc/generate_report.py --config config/repos.example.json --print-report
python3 scripts/skill/generate_report.py --since 7d
```
