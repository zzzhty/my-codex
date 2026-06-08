# Agent Operating Model

This document maps the root agent operating principles to this repository's actual workflows, files, reports, automations, and review boundaries. It is the second layer of guidance: `AGENTS.md` defines the rules, this document explains how to apply them here, and each plugin or workflow README defines its own contract.

## Core Loop

```text
Capture -> Persist -> Act -> Review -> Monitor -> Remember
```

## Capture

Capture rough intent and real context before compressing work into a final task shape.

Local inputs:

- the current user request or pinned thread context
- linked notes, transcripts, issue text, reports, or artifacts
- root and plugin README files
- existing TODO, planning, and runtime report files
- recent command output or failure evidence

Do not force early prompt polishing when the task is still exploratory. Preserve enough source context to let later steps verify assumptions.

## Persist

Long-running work should be anchored outside chat history.

Local durable homes:

- root `AGENTS.md` for global agent behavior
- `docs/agents/` for repo-specific agent workflow mapping
- plugin `README.md` files for product and workflow contracts
- skill `SKILL.md` files for reusable agent procedures
- `$CODEX_HOME/<tool>/reports/` for generated reports
- `$CODEX_HOME/automations/<automation-id>/memory.md` for automation state
- TODO or planning files for active open loops

Choose the narrowest durable home that future agents and humans can inspect. If the information only matters for the current turn, keep it in the thread instead of creating documentation churn.

## Act

Agents should use the narrowest tool that can produce real evidence.

Default posture:

- read-only inspection before mutation
- scripts, checkers, and validators before impression-based conclusions
- Browser, Chrome, or Computer Use only when the surface itself matters
- repo-local helpers before new ad hoc implementations
- no destructive, privacy-sensitive, external-send, or irreversible action without explicit user intent

When implementation is requested, act directly after enough context is known. When the root cause is unclear, collect minimal diagnostics and report the concrete blocker instead of routing around it.

## Subagent Delegation

Subagent work has two current layers in this repository.

Current runtime workflow:

- Use the `orchestration` plugin and `$orchestrate-subagents` skill when the user explicitly asks for bounded subagent work.
- Treat `plugins/orchestration/skills/orchestrate-subagents/SKILL.md` and its recipes as the current contract for spawning, assignment labels, evidence, failure handling, and consolidation.
- Use the currently available Codex roles such as `explorer`, `worker`, and `default`, with task-local labels like `code-mapper` or `test-verifier`.
- Keep the parent agent responsible for planning, write-scope decisions, integration, final validation, and the user-facing conclusion.

Custom-agent routing:

- Use `docs/agents/subagent-roster.md` as the current roster and model policy for M1 read-only custom agents.
- Manage source TOML under `codex-home/agents/` and sync managed copies into `$CODEX_HOME/agents/` with `scripts/sync_codex_agents.py`.
- Treat `code_mapper`, `reviewer`, and `docs_researcher` as custom-agent-first read-only roles when available, with built-in fallbacks defined by the orchestration skill.
- Track exact runtime custom-agent selector coverage in `docs/todo/subagent-runtime-selection-validation.md`; until that goal proves selector behavior, report partial coverage when exact custom-agent loading cannot be verified.
- Keep `impl_worker`, `test_runner`, advisor skills, and project-scoped `.codex/agents/` dogfood as Future work unless a separate active plan is created.
- The closed v1 execution record is archived at `docs/todo/archive/subagent-model-routing-v1.md`; do not use archive files as current instructions except for historical evidence.

## Review

Every meaningful output should be inspectable.

Review surfaces:

- Git diff
- Markdown reports
- command output
- generated artifacts
- screenshots when UI is involved
- validation logs
- automation memory files

Reports should state what was checked, where the evidence lives, what failed, what changed, and whether implementation was performed. Do not imply success without command output, a file path, a diff, or another concrete artifact.

## Monitor

Scheduled or repeated workflows should observe and summarize first.

A monitor must define:

- schedule or trigger
- exact command, script, or tool path
- working directory
- output contract
- stop condition when applicable
- allowed actions
- forbidden actions
- report or memory location
- validation or freshness checks

For wall-clock schedules, preserve the user-visible local time unless the user explicitly requests UTC. Verify the written automation state before reporting the schedule back.

## Remember

Only durable, reusable knowledge should be written back.

Remember:

- user preferences that affect future work
- validated commands
- recurring failure modes
- workflow contracts
- open loops and close criteria
- privacy and mutation boundaries

Do not remember:

- full private prompts
- secrets
- full tool responses
- unverified assumptions
- one-off noise
- implementation details that can be cheaply rediscovered from source

Memory updates should be reviewable through file paths, diffs, or report artifacts.

## Workflow Contract Template

Use this template when a repeated workflow becomes important enough to document in a plugin README, skill, automation memory, or planning file.

```md
## Workflow Contract

- Trigger:
- Working directory:
- Command or tool:
- Inputs:
- Outputs:
- Report or memory location:
- Allowed actions:
- Forbidden actions:
- Validation:
- Stop condition:
```

Workflow contracts should stay small and operational. They are not product strategy documents; they define how an agent should run the workflow without expanding scope.
