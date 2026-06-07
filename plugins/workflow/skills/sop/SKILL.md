---
name: sop
description: Use when creating, updating, executing, validating, or reusing a deterministic standard operating procedure for a recurring task whose trigger, inputs, steps, outputs, validation, stop conditions, and failure handling are already known or can be made explicit.
---

# SOP

Use this skill when a repeated workflow should become a reusable standard operating procedure.

Do not use it for exploratory planning, unresolved design work, or long-running milestone execution. Use `long-run-goal` when the work needs ordered milestones, review gates, checkpoint evidence, and close/archive hygiene.

## SOP Boundary

An SOP is appropriate when the workflow has:

1. A stable trigger.
2. Known required inputs.
3. Ordered steps.
4. Expected outputs.
5. Validation evidence.
6. Clear stop conditions.
7. Failure handling or escalation.
8. A known owner or durable home.

If these cannot be made explicit, first produce a report, run a planning workflow, or create a long-running goal instead of writing an SOP.

## Bundled Template

The reusable template is bundled at:

```text
templates/sop_template.md
```

Resolve that path relative to the skill folder. Copy it into the project's SOP, runbook, operations, workflow, or plugin-doc area, then replace all placeholders before marking the SOP `Ready`.

## Location Discovery

Prefer existing conventions in this order:

1. User-specified SOP path.
2. Existing `docs/sop/`, `docs/runbooks/`, `runbooks/`, `docs/workflows/`, or `docs/operations/`.
3. Plugin README or skill README when the SOP belongs to a plugin workflow.
4. If no convention exists and the user wants a new file, use `docs/sop/<sop-slug>.md`.

Do not create a new SOP tree when an equivalent runbook or workflow directory already exists.

## Creation Workflow

1. Read current truth:
   - root instructions such as `AGENTS.md`
   - root `README.md`
   - relevant plugin README, runbook, script, automation memory, report, or prior failure evidence
2. Classify the workflow:
   - manual SOP
   - agent-executed SOP
   - report-only SOP
   - validation SOP
   - release or maintenance SOP
   - incident or failure SOP
3. Copy `templates/sop_template.md` to the chosen durable location.
4. Replace every placeholder and keep commands marked as expected unless they have been verified.
5. Add a reuse prompt that names the SOP path, trigger, expected output, mutation permission, and stop conditions.
6. Validate the SOP:

```bash
python <skill-folder>/scripts/check_sop_ready.py <sop-file>
python <skill-folder>/scripts/check_sop_links.py <sop-root-or-file>
```

## Execution Workflow

When the user asks to run an SOP:

1. Re-read the SOP and the newest user request.
2. Confirm whether the request is execute, update, explain, or dry-run.
3. Follow the SOP steps in order.
4. Stop at the first failed required validation.
5. Record any evidence requested by the SOP.
6. Report outputs, commands, validation result, changed files, generated artifacts, unresolved risks, and blockers.

Do not silently skip required steps, invent missing inputs, or convert a report-only SOP into mutation.

## Update Workflow

When updating an SOP:

1. Re-read the current SOP and source-of-truth files.
2. Preserve verified commands unless new evidence replaces them.
3. Update trigger, inputs, steps, validation, stop conditions, and failure handling together when one changes.
4. Re-run the bundled ready and link checks.
5. Report what changed, why it changed, and what evidence validates the new procedure.

## Quality Bar

A useful SOP must answer:

1. When is this procedure triggered?
2. What inputs are required?
3. Where must the agent run it?
4. What exact steps are performed?
5. What is allowed and forbidden?
6. What validates success?
7. What evidence must be reported?
8. What stops execution?
9. How are failures escalated?
10. How should the SOP be reused next time?
