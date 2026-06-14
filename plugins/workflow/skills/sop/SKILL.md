---
name: sop
description: Use when creating, updating, executing, validating, or reusing a Standard Operating Procedure for a repeatable manual, agent-executed, or automated workflow whose trigger, inputs, execution harness, permissions, ordered steps, outputs, validation, stop conditions, escalation, failure handling, and durable writeback are already known or can be made explicit.
---

# SOP

Use this skill when a repeated workflow should become a reusable standard operating procedure.

Do not use it for exploratory planning, unresolved design work, or long-running milestone execution. Use `prompt-strategy-loop` when prompt, rubric, or agent-strategy behavior is not yet stable. Use `long-running-goal` when the work needs ordered milestones, review gates, checkpoint evidence, and close/archive hygiene.

## SOP Boundary

An SOP is appropriate when the workflow has:

1. A stable trigger.
2. Known required inputs.
3. Ordered steps.
4. Expected outputs.
5. Validation evidence.
6. Clear stop conditions.
7. Failure handling or escalation.
8. Execution harness boundaries for agent-executed or automated procedures.
9. A known owner or durable home.

If these cannot be made explicit, first produce a report, run a planning workflow, or create a long-running goal instead of writing an SOP.

Any prompt, rubric, evaluator instruction, or agent strategy that affects the SOP's behavior must be named as an explicit input, step asset, or validation artifact. Do not leave required prompt behavior implicit in the executing model's judgment.

For agent-executed or automated SOPs, make the execution harness explicit: execution mode, orchestration, isolation, connector permissions, independent verification, human escalation, and durable writeback. For simple manual SOPs, write `Not applicable` with a reason instead of inventing machinery.

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
   - automated SOP
   - report-only SOP
   - validation SOP
   - release or maintenance SOP
   - incident or failure SOP
3. Copy `templates/sop_template.md` to the chosen durable location.
4. Replace every placeholder and keep commands marked as expected unless they have been verified.
5. Fill the execution harness. Use `Not applicable` with a reason for fields that truly do not apply.
6. Add a reuse prompt that names the SOP path, trigger, execution harness, expected output, mutation permission, and stop conditions.
7. Validate the SOP:

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
4. Update the execution harness when prompt/strategy inputs, orchestration, isolation, connector permissions, independent verification, escalation, or writeback rules change.
5. Use evidence-backed review, usually via `prompt-strategy-loop`, before changing prompts, rubrics, agent strategies, connector permissions, automation triggers, or independent verification rules.
6. Re-run the bundled ready and link checks.
7. Report what changed, why it changed, and what evidence validates the new procedure.

## Quality Bar

A useful SOP must answer:

1. When is this procedure triggered?
2. What inputs are required?
3. Where must the agent run it?
4. What prompt, rubric, or strategy inputs affect execution?
5. What harness constrains orchestration, isolation, permissions, verification, escalation, and writeback?
6. What exact steps are performed?
7. What is allowed and forbidden?
8. What validates success?
9. What evidence must be reported?
10. What stops execution?
11. How are failures escalated?
12. How should the SOP be reused next time?
