# Patch Policy

Skill maintenance proposals must be small, auditable, and evidence-backed.

Acceptable proposal types:

- Add one missing rule, workflow step, or validation requirement.
- Replace a confusing or stale instruction with a clearer one.
- Delete an instruction that repeatedly causes failures or conflicts.

Do not propose:

- Full rewrites when a bounded edit will work.
- Rules based only on a low-risk one-off event.
- Edits that embed user secrets, private data, or long task-specific details.
- Runtime behavior that automatically changes source skills without review.

Every proposal should include:

- Evidence window and event counts.
- Observed successes, failures, and user corrections.
- Proposed diff or exact edit description.
- Risk notes.
- Validation plan.
