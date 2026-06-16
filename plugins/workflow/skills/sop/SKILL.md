---
name: sop
description: Use when creating, updating, executing, validating, or reusing a Standard Operating Procedure for a repeatable manual, agent-executed, or automated workflow whose trigger, inputs, execution harness, permissions, ordered steps, outputs, validation, stop conditions, escalation, failure handling, and durable writeback are already known or can be made explicit.
---

# SOP

Use this skill when a repeated workflow should become a reusable standard operating procedure.

Do not use it for exploratory planning, unresolved design, or long-running milestone execution. Use `prompt-strategy-loop` when prompt/rubric/agent-strategy behavior is not stable. Use `long-running-goal` when work needs ordered milestones, review gates, checkpoint evidence, and close/archive hygiene.

## Boundary

An SOP is appropriate only when these can be explicit:

1. Stable trigger and required inputs.
2. Ordered steps and expected outputs.
3. Validation evidence.
4. Stop conditions plus failure handling/escalation.
5. Execution harness for agent-executed or automated procedures.
6. Known owner or durable home.

If not, first produce a report, run planning, use `prompt-strategy-loop`, or create a long-running goal.

Any prompt, rubric, evaluator instruction, or agent strategy that affects behavior must be named as an input, step asset, or validation artifact. For agent-executed or automated SOPs, explicitly state execution mode, orchestration, isolation, connector permissions, independent verification, human escalation, and durable writeback. For simple manual SOPs, write `Not applicable` with a reason.

## Template And Location

Use `templates/sop_template.md`. Copy it into the existing SOP/runbook/operations/workflow/plugin-doc area, replace all placeholders, then mark the SOP `Ready`.

Prefer locations in this order: user-specified path; existing `docs/sop/`, `docs/runbooks/`, `runbooks/`, `docs/workflows/`, or `docs/operations/`; plugin README or skill README when the SOP belongs to a plugin; otherwise `docs/sop/<sop-slug>.md`. Do not create a new SOP tree when an equivalent runbook/workflow directory exists.

## Create

1. Read current truth: `AGENTS.md`, README, relevant plugin README, runbook, script, automation memory, report, or prior failure evidence.
2. Classify the SOP: manual, agent-executed, automated, report-only, validation, release/maintenance, or incident/failure.
3. Copy the template, replace placeholders, and leave unverified commands marked as expected.
4. Fill the execution harness; use `Not applicable` only with a reason.
5. Add a reuse prompt naming SOP path, trigger, harness, expected output, mutation permission, and stop conditions.
6. Validate:

```bash
python <skill-folder>/scripts/check_sop_ready.py <sop-file>
python <skill-folder>/scripts/check_sop_links.py <sop-root-or-file>
```

## Execute

When the user asks to run an SOP:

1. Re-read the SOP and newest user request.
2. Classify the request as execute, update, explain, or dry-run.
3. Follow steps in order.
4. Stop at the first failed required validation or stop condition.
5. Record requested evidence.
6. Report outputs, commands, validation result, changed files, generated artifacts, unresolved risks, and blockers.

Do not skip required steps, invent missing inputs, or convert report-only SOPs into mutation.

## Update

1. Re-read the SOP and source-of-truth files.
2. Preserve verified commands unless new evidence replaces them.
3. Update trigger, inputs, steps, validation, stop conditions, failure handling, and execution harness together when affected.
4. Use evidence-backed review, usually via `prompt-strategy-loop`, before changing prompts, rubrics, agent strategies, connector permissions, automation triggers, or independent verification rules.
5. Re-run ready/link checks and report what changed, why, and what evidence validates the new procedure.

## Quality Bar

A useful SOP must answer: trigger, inputs, working location, prompt/rubric/strategy inputs, harness boundaries, exact steps, allowed and forbidden actions, success validation, evidence to report, stop conditions, escalation path, and reuse prompt.
