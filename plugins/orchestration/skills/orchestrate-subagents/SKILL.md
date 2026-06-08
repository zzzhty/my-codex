---
name: orchestrate-subagents
description: Use for complex Codex tasks that should explicitly spawn subagents, including PR review, architecture review, debugging, failure triage, migration, refactor planning, impact analysis, test discovery, API/schema inspection, and multi-file implementation planning.
---

# Orchestrate Subagents

Use this skill when the user explicitly invokes `$orchestrate-subagents` or
explicitly asks to use subagents for a complex Codex task.

Do not use this skill to justify implicit delegation. If the user did not
invoke the skill or clearly ask for subagents, follow the active environment's
normal subagent policy.

## Core Contract

1. Decide whether the task is genuinely parallelizable before spawning.
2. Keep the parent agent responsible for planning, final decisions,
   integration, verification, and user-facing conclusions.
3. Give each subagent one task only. Do not combine mapping, review,
   implementation, and validation in the same subagent prompt.
4. Spawn only bounded subagents with clear ownership, expected outputs, stop
   conditions, and file/write boundaries.
5. Do not rely on subagents implicitly inheriting this skill, parent context,
   local plans, or unstated requirements. Put the needed instructions directly
   in each subagent prompt.
6. Wait for all selected subagents, or record exactly which subagent did not
   return and why.
7. Treat subagent failure, timeout, missing tools, incomplete findings,
   conflicting results, and unsafe file overlap as first-class failures.
8. Consolidate evidence before acting. Do not let subagent output replace
   parent review.

## Role Selection

Use the roles available in the current Codex environment. Do not assume custom
agents are installed in every session. When the subagent tool exposes a role
selector, use the selector such as `agent_type` for exact custom-agent
selection; assignment labels in prompts are not proof that a custom-agent TOML
was loaded.

When read-only custom agents are available, prefer:

- `code_mapper` for read-only codebase mapping, impact analysis, test
  discovery, schema inspection, and evidence collection. Fallback:
  `explorer as code-mapper`.
- `reviewer` for correctness, security, regression, compatibility, contract,
  and missing-test review. Fallback: `default as implementation-reviewer`.
- `docs_researcher` for official documentation, API, configuration, version,
  and migration-note verification. Fallback: `default as docs-researcher`.

If a custom agent is unavailable, a pinned model is unavailable, or the runtime
does not expose custom agents, use the built-in fallback only when the
ownership and output contract still fit. Otherwise stop and report partial
coverage.

When exact role proof matters, use parent tool-call evidence plus local session
metadata such as `agent_role`. Child sessions may not expose `AGENT_TYPE` or a
similar self-identity variable. Runtime sandbox overrides can also supersede a
custom agent's `sandbox_mode`, so repeat read-only constraints in each prompt
and report the effective sandbox if it matters for the gate.

Built-in roles remain supported:

- `explorer` for read-only codebase mapping, impact analysis, test discovery,
  schema inspection, and evidence collection.
- `worker` only for implementation subtasks with disjoint write ownership and
  explicit user authorization to edit files.
- `default` for review, triage, and planning when no narrower role is
  available.

When spawning multiple subagents with the same role, add an assignment label in
the prompt, such as `default as test-verifier` or `worker as api-adapter`.

Do not request write-capable custom-agent names such as `impl_worker` or
`test_runner` until they exist in the current environment and have explicit
ownership, rollback, conflict handling, and validation rules. Keep `worker`
rules unchanged for implementation subtasks.

For common patterns, read `references/subagent-recipes.md`.

## Single-Task Fit Check

Before spawning, rewrite each assignment until it has one primary verb, one bounded scope, and one expected output.
Split any assignment that asks a subagent to both map and review, review and
implement, implement and plan, or validate unrelated work.

Validation commands may be required as evidence for an implementation task, but
separate test strategy, missing-test discovery, or cross-slice validation should
be a separate subagent task.

## Parent Workflow

1. Restate the task, success criteria, and non-goals in one short block.
2. Identify parallelizable slices and any shared files that must stay parent
   owned.
3. Choose the minimum useful subagents, with one task per subagent. Do not
   delegate tiny tasks or tightly coupled sequential debugging steps.
4. Spawn selected subagents with task-local prompts.
5. Continue only non-overlapping parent work while subagents run.
6. Wait for all selected subagents before final consolidation unless a failure
   policy in the user request says otherwise.
7. Reject or qualify incomplete outputs. If a subagent lacks paths, commands,
   evidence, blockers, or stop-condition status, mark that coverage partial.
8. Consolidate coverage, blocking issues, non-blocking risks, missing tests,
   evidence, unresolved blockers, and recommended next action.

## Subagent Prompt Template

Use this structure when spawning:

```text
Task:
<specific assignment, not the whole parent task>

Assignment label:
<role plus purpose, such as default as test-verifier>

Single task:
<one primary verb, one bounded scope, one expected output>

Context:
<files, commands, branch/base, goal path, constraints, relevant facts>

Ownership:
<read-only scope or exact disjoint write scope>

Expected output:
- findings or implementation summary
- paths inspected or changed
- commands run and results
- evidence for each claim
- blockers and unknowns
- stop-condition status

Stop condition:
<when to stop, including max scope or exact completion signal>

Boundaries:
- Do not work outside <scope>.
- Do not revert edits made by others.
- Do not fabricate success if tools or evidence are missing.
```

For worker subagents, include a clear statement that they are not alone in the
codebase and must accommodate concurrent or parent edits.

## Consolidation Format

Return a concise parent summary with these fields:

1. Subagent coverage: role, assignment, status, paths, and commands.
2. Blocking issues: failures that prevent safe completion.
3. Non-blocking risks: issues to carry forward.
4. Missing tests or validation gaps.
5. Evidence: command output, files, diffs, screenshots, reports, or logs.
6. Unresolved blockers and partial coverage.
7. Recommended next action.

If implementation happened, include changed files, behavior impact, validation
results, rollback path, and remaining risk.

## Failure Handling

Stop or report partial coverage when:

- subagent tools are unavailable or policy blocks spawning
- a subagent times out, fails, or cannot access required files/tools
- a subagent returns only a generic conclusion without evidence
- two subagents produce conflicting claims that the parent cannot reconcile
- write scopes overlap or create race risk
- validation evidence is missing for a required gate

Do not hide the failure by doing unrelated work, changing scope, or reporting
success with weaker evidence. The parent may run minimal diagnostics to narrow
the blocker, but the original subagent failure must remain visible.
