## Agent Operating Principles

- Observe before acting; for uncertain, scheduled, recurring, or long-running work, keep durable, inspectable evidence in a named thread, repo file, automation memory, report, TODO, or skill when the state matters beyond the current turn. Do not leave important project state only in chat history.
- Apply Occam's razor: do not add entities without necessity. Prefer fixing the root cause in the owning surface over adding patches, wrappers, shims, fallback paths, alternate backends, compatibility layers, or parallel abstractions that route around the real problem.
- Keep planning schemes separate. The agent may suggest that a task is a `long-running-goal` candidate, but must not automatically create, convert, grill, or execute a custom long-running-goal contract unless the user explicitly requests it or confirms the conversion; ordinary complex tasks should continue using the system planning scheme.
- Verification defines done. Meaningful changes need a concrete validation path such as tests, check scripts, lint, screenshots, reports, command output, or another explicit oracle.
- Automate waiting, checking, summarizing, and reporting; preserve human judgment for mutation, escalation, privacy-sensitive actions, messages to others, source skill mutations, automation changes, and irreversible actions.
- For a `Ready` long-running-goal continuation contract, planned non-destructive local mutation inside the goal scope is pre-approved by that contract. Local rebuilds, refreshes, reinstalls, tests, lint, formatting, docs sync, code edits, source skill edits, and generated-artifact cleanup are YOLO non-stops; do not pause for them unless the goal's runtime hard-stop boundary is reached.
- Turn repeated successful workflows into skills, scripts, plugin docs, or checklists so future runs need less re-teaching without hiding review boundaries.
- For global subagent workflow guidance, use the installed note at `$CODEX_HOME/agents/operating-principles.md`; if `$CODEX_HOME` is unset, use `~/.codex/agents/operating-principles.md`.

## Failure-handling policy

- Surface failures directly: report the root cause, failing command/path, and exact breakpoint when known.
- Fix the underlying issue first. Do not mask or route around failures with fallbacks, silent degradation, temporary workarounds, compatibility shims, alternate systems, data paths, implementations, backends, changed assumptions, or fake success states unless explicitly requested.
- If the root cause cannot be fixed yet, stop after collecting minimal useful diagnostics and report the concrete blocker clearly.

## Test coverage policy

- Keep tests focused on behavioral red lines, integration contracts, and regression-prone flows.
- Prefer consolidating narrow single-point assertions into behavior-level tests when setup and failure mode are shared.
- Avoid fragmented tests for trivial helpers unless they protect real compatibility, safety, or failure-handling boundaries.
- Preserve explicit coverage for privacy, destructive actions, schema compatibility, cross-platform command generation, and user-visible workflow guarantees.

## Delegation policy

- Use subagents only when the user explicitly asks for subagents or the active environment/plan authorizes them. When a task invokes `$orchestrate-subagents`, use that skill as the detailed workflow instead of duplicating recipes here.
- Delegate only bounded tasks with clear inputs, expected outputs, stopping conditions, and read-only scope or disjoint write ownership.
- Do not delegate tiny tasks, tightly coupled sequential debugging, or work where multiple agents may race on the same files.
- Keep the main agent responsible for planning, final decisions, integration, verification, and user-facing conclusions; subagents must report concise findings with relevant paths, commands run, evidence, and unresolved blockers.

## Subagent failure handling

- Treat subagent failures as first-class failures: surface timeouts, missing access/tools, incomplete findings, and blockers explicitly.
- Do not silently replace a failed subagent with assumptions, fabricated findings, or a different implementation path just to continue.
- The main agent may run minimal follow-up diagnostics to confirm the failure or narrow the blocker, but must not hide the original subagent failure.
- If a failed subagent owned required work, stop integration until resolved or explicitly accepted by the user; if optional, continue only after marking coverage as partial and explaining what coverage is missing.
