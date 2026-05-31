# Skill Watcher

Skill Watcher is a source-only Codex plugin for maintaining skills from observed usage evidence. V1 installs user-level Codex hook handlers, records redacted JSONL events, writes daily reports, generates bounded proposal drafts, and validates candidate `SKILL.md` files.

This plugin does not register a marketplace entry and does not modify existing skills automatically.

## Layout

```text
.codex-plugin/plugin.json
skills/skill-maintainer/
hooks/codex/
scripts/
```

Runtime state is written under `~/.codex/skill-watcher/`:

```text
logs/events.jsonl
reports/
proposals/
snapshots/
rejected/
backups/
```

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

## Smoke Test

```bash
printf '%s\n' '{"event_type":"skill_stop","skill_name":"demo","outcome":"failure","failure_type":"tool_error","notes":"token sk-1234567890 should redact","metadata":{"api_key":"secret"}}' \
  | .venv/bin/python scripts/collect_event.py

.venv/bin/python scripts/summarize_logs.py --skill demo --since 1d
.venv/bin/python scripts/propose_skill_patch.py --skill-dir skills/skill-maintainer --skill skill-maintainer --since 1d
.venv/bin/python scripts/validate_candidate.py --candidate-skill skills/skill-maintainer/SKILL.md
```

Validate the plugin:

```bash
.venv/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/codex-marketplace/plugins/skill-watcher
```

## Codex Hook Install

Skill Watcher installs user-level hooks at `~/.codex/hooks.json` and preserves unrelated hook entries. The generated handlers observe `SessionStart`, `UserPromptSubmit`, `PostToolUse`, and `Stop`.

```bash
.venv/bin/python scripts/install_codex_hook.py --dry-run
.venv/bin/python scripts/install_codex_hook.py --apply
```

After applying, open `/hooks` in Codex and review/trust the new command hook definitions. Codex requires this for non-managed command hooks before they run.

Uninstall only Skill Watcher handlers:

```bash
.venv/bin/python scripts/uninstall_codex_hook.py --dry-run
.venv/bin/python scripts/uninstall_codex_hook.py --apply
```

## Runtime Reports

Generate a report-only daily report:

```bash
.venv/bin/python scripts/daily_report.py --since 1d
.venv/bin/python scripts/daily_report.py --skill skill-maintainer --since 1d
```

The Codex automation named `Skill Watcher Daily Report` runs this report workflow daily at 23:30 Asia/Shanghai and returns the report path plus summary counts. It does not generate proposals or modify skills.

## Hook Privacy and Attribution

The Codex hook adapter stores summaries, lengths, hashes, tool names, outcomes, and redacted metadata. It does not store full prompts, full assistant messages, full shell commands, or full tool responses.

Codex hook payloads do not provide a stable native skill identifier. If a hook payload does not include `skill_name`, Skill Watcher records `skill_name: "unknown"` and does not parse transcripts to guess.

## Proposal Status

Generated proposal files include YAML frontmatter with `status: "draft"`. Update status explicitly:

```bash
.venv/bin/python scripts/update_proposal_status.py --proposal ~/.codex/skill-watcher/proposals/<proposal>.md --status needs-validation
.venv/bin/python scripts/update_proposal_status.py --proposal ~/.codex/skill-watcher/proposals/<proposal>.md --status rejected --reason "insufficient evidence"
```

Rejected proposals write a small buffer record under `~/.codex/skill-watcher/rejected/`.

## Diagnostics

```bash
.venv/bin/python scripts/doctor.py
.venv/bin/python -m py_compile scripts/*.py
.venv/bin/python -m unittest discover -s tests
```
