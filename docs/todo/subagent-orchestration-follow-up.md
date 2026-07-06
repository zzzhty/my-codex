# Subagent Orchestration Follow-Up

Status: Future TODO.

This note tracks the deferred work for strengthening `workflow` subagent orchestration without importing the full Superpowers methodology.

## Future Scope

- Validate and refine the read-only review subagent contracts now prompted from `AGENTS.md` and `agents/operating-principles.md`, especially for broad PR, branch, architecture, skill, prompt, docs, and contract review tasks.
- Decide whether repeated validated reviewer prompts should become custom-agent TOML, and document the model, sandbox, fallback, sync validation, rollback, and parent integration boundaries before adding any TOML.
- Mine Superpowers for targeted workflow ideas only, especially staged implementer plus spec-reviewer plus quality-reviewer loops, while preserving `workflow` as the owning Codex surface.
- Keep parent-agent ownership of planning, write-scope decisions, final judgment, integration, validation, and user-facing conclusions.

## Non-Goals

- Do not import Superpowers wholesale.
- Do not add custom-agent TOML before built-in roles plus assignment labels prove insufficient in real review runs.
- Do not expand review-only authorization into worker edits or implicit mutation.
