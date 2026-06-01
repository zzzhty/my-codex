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

- For heavy, parallelizable, or noisy work, prefer bounded subagent tasks; decide and start them before broad exploration when parallel work is useful.
- Delegate only tasks with clear inputs, expected outputs, stopping conditions, and low risk of racing on the same files.
- Do not delegate tiny tasks, tightly coupled edits, sequential debugging steps, or changes where multiple agents may race on the same files.
- Good candidates include codebase exploration, impact analysis, test discovery, failure triage, log review, API/schema inspection, and independent implementation options.
- Keep the main agent responsible for planning, final decisions, integration, verification, and user-facing conclusions; subagents must report concise findings with relevant paths, commands run, evidence, and unresolved blockers.

## Subagent failure handling

- Treat subagent failures as first-class failures: surface timeouts, missing access/tools, incomplete findings, and blockers explicitly.
- Do not silently replace a failed subagent with assumptions, fabricated findings, or a different implementation path just to continue.
- The main agent may run minimal follow-up diagnostics to confirm the failure or narrow the blocker, but must not hide the original subagent failure.
- If a failed subagent owned required work, stop integration until resolved or explicitly accepted by the user; if optional, continue only after marking coverage as partial and explaining what coverage is missing.
