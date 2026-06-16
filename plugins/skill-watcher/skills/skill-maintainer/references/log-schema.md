# Skill Watcher Log Schema

Skill Watcher writes one redacted JSON object per line to `$CODEX_HOME/skill-watcher/logs/events.jsonl`.

Core fields:

- `schema_version`: current value `1`.
- `event_id`: collector-generated UUID when absent.
- `timestamp`: collector-generated UTC ISO-8601 timestamp when absent.
- `agent`: defaults to `codex`.
- `event_type`: lifecycle label such as `user_prompt_submit`, `post_tool_use`, `turn_summary`, `user_feedback`, or `failure`.
- `workspace`, `session_id`, `skill_name`, `skill_version`, `trigger_reason`.
- `tools_used`: array of tool or command names.
- `files_touched`: array of paths, without file contents.
- `outcome`: `success`, `failure`, `partial`, or `unknown`.
- `failure_type`: optional category such as `tool_error`, `wrong_assumption`, `missed_validation`, `format_error`, or `user_correction`.
- `tests_or_checks`: array of validation actions.
- `user_feedback` and `notes`: short factual summaries.
- `codex`: hook metadata, turn id, attribution fields, and redacted summaries.

Codex attribution fields:

- `codex.skill_attribution`: `provided`, `prompt_mention`, `assistant_announcement`, or `unknown`.
- `codex.skill_confidence`: `high`, `medium`, `low`, or `unknown`.
- `codex.monitored_skill`: whether the event matched the monitored allowlist.
- `codex.user_skill_context`: redacted summary/hash of extra user context.
- `codex.turn_summary`: per-turn tool/failure counts written on `Stop` for active monitored skills.

Collectors must avoid full prompts, file contents, complete command transcripts, secrets, and private business data. Store summaries, hashes, counts, and explicit skill context signals instead.
