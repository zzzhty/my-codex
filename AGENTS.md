## Failure-handling policy

- Surface failures directly: report the root cause, failing command/path, and exact breakpoint when known.
- Fix the underlying issue first. Do not mask the problem with fallbacks, silent degradation, temporary workarounds, compatibility shims, alternate backends, or fake success states unless explicitly requested.
- Do not route around a failure by switching systems, data paths, implementations, or assumptions just to make the task appear successful.
- If the root cause cannot be fixed yet, stop after collecting the minimal useful diagnostics and report the concrete blocker clearly.

## Delegation policy

- For heavy, parallelizable, or noisy work, prefer using subagents instead of doing all exploration, auditing, testing, and implementation in one main session.
- Before starting heavy work, first decide whether parts of the task should be delegated to subagents; if yes, delegate them before doing broad exploration in the main session.
- Delegate only bounded tasks with clear inputs, expected outputs, and stopping conditions.
- Good candidates for subagents include codebase exploration, impact analysis, test discovery, failure triage, log review, API/schema inspection, and independent implementation options.
- Keep the main agent responsible for task planning, final decisions, integration, verification, and user-facing conclusions.
- Do not use subagents for tiny tasks, tightly coupled edits, sequential debugging steps, or changes where multiple agents may race on the same files.
- Subagents must report concise findings with relevant file paths, commands run, evidence, and unresolved blockers.

## Subagent failure handling

- Treat subagent failures as first-class failures, not as ignorable missing results.
- If a subagent fails, times out, cannot access required files/tools, or returns incomplete findings, the main agent must surface that limitation explicitly.
- Do not silently replace a failed subagent with assumptions, fabricated findings, or a different implementation path just to continue.
- The main agent may run minimal follow-up diagnostics to confirm the failure or narrow the blocker, but must not hide the original subagent failure.
- If the failed subagent was responsible for a required part of the task, stop integration until the blocker is resolved or explicitly accepted by the user.
- If the failed subagent was optional or exploratory, the main agent may continue only after clearly marking the result as partial and explaining what coverage is missing.