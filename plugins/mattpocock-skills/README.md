# Matt Pocock Skills

Skill-only Codex plugin for the local Codex-adapted copy of Matt Pocock's skills.

Upstream: https://github.com/mattpocock/skills

Adapted from: `v1.0.1` (`2454c95dc305c158b21a0cdafeb728879dd0359a`)

## Skills

- `ask-matt`
- `codebase-design`
- `diagnosing-bugs`
- `domain-modeling`
- `grill-me`
- `grill-with-docs`
- `grilling`
- `handoff`
- `improve-codebase-architecture`
- `prototype`
- `setup-matt-pocock-skills`
- `tdd`
- `teach`
- `to-issues`
- `to-prd`
- `triage`
- `writing-great-skills`

## Compatibility Notes

This plugin flattens the upstream Claude plugin skill paths into Codex's `skills/<name>/` layout while preserving each published skill directory's contents.

Upstream 1.0.x made these breaking changes:

- `diagnose` was renamed to `diagnosing-bugs`.
- `write-a-skill` was replaced by `writing-great-skills`.
- `caveman` and `zoom-out` were removed upstream and are no longer packaged here.

This plugin is the source of truth for these third-party skills in this Codex setup. Do not maintain separate copies under `$CODEX_HOME/skills`.
