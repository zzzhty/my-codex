# AGENTS Future Plan

Updated: 2026-06-25

Status: active future plan only. Closed items from the AGENTS prompt optimization pass are intentionally not tracked here.

## Open Item

### C2: Long-Running Goal Safety Wording

Goal:

- Reduce restatement between root `AGENTS.md`, `agents/operating-principles.md`, and `plugins/workflow/skills/long-running-goal/SKILL.md` only if the edit preserves the same planning and permission boundaries.

Current source of truth:

- Root `AGENTS.md` keeps planning-scheme separation and the `Ready long-running-goal` YOLO/hard-stop boundary inline.
- `plugins/workflow/skills/long-running-goal/SKILL.md` owns the detailed continuation contract.
- `docs/todo/long-running-goal-skill-compression-proposal.md` owns the semantic inventory and future source-edit gate for long-running-goal compression.

Do not start source edits until:

1. The long-running-goal compression proposal has an accepted candidate diff or a fresh semantic inventory.
2. One evaluator confirms semantic preservation.
3. One risk-reviewer finds no blocker around YOLO non-stops, runtime hard stops, request supersession, Draft/Ready gates, or Codex goal-tool boundaries.

Validation for any future source edit:

```bash
git diff --check -- AGENTS.md agents/operating-principles.md docs/todo
/Users/max/.codex/venvs/my-codex/bin/python plugins/workflow/skills/long-running-goal/scripts/check_md_links.py docs/todo
/Users/max/.codex/venvs/my-codex/bin/python scripts/check_my_codex.py --skip-agents
```

Close when:

- The accepted source edit is applied and validated, or the future review records a durable no-change decision that no longer needs active tracking.
