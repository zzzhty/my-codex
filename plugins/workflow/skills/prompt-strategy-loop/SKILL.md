---
name: prompt-strategy-loop
description: Use when improving prompts, agent instructions, skill guidance, workflow strategy, reviewer rubrics, or orchestration prompts through evidence-backed iteration; use for prompt A/B comparisons, failed-agent-output analysis, recurring workflow tuning, strategy regression review, and decisions that need independent subagent evaluation before writing changes back to a skill, runbook, automation, or source prompt.
---

# Prompt Strategy Loop

Use this skill to improve a prompt or agent strategy from evidence rather than preference. The output may be a recommendation, a proposed patch, or an applied edit when the user explicitly asked for mutation.

## Core Rule

Never let the same agent that proposes a prompt or strategy change be the sole judge of whether it improved. Use at least one independent evaluator, and use multiple independent reviewers for high-impact changes to skills, automations, connector permissions, safety boundaries, recurring workflows, or orchestration prompts.

If independent evaluation is unavailable, stop at a proposal and state that the improvement is unverified. Do not claim the new prompt is better.

## Workflow

1. Define the target:
   - Identify the prompt, skill, strategy, rubric, or workflow being improved.
   - State the failure mode or desired improvement.
   - Define non-goals and mutation boundaries.

2. Collect raw evidence:
   - Use real failures, successful examples, logs, user feedback, diffs, reports, or benchmark tasks.
   - Prefer source artifacts over summaries.
   - Do not tune against hidden assumptions or a single anecdote unless the user explicitly scopes it that narrowly.

3. Freeze the evaluation oracle:
   - Define what counts as better before writing candidates.
   - Use observable criteria such as correctness, reduced false positives, fewer missed blockers, stronger evidence, lower unnecessary escalation, fewer permissions, more stable formatting, or better task completion.
   - Include regressions to avoid, not only desired improvements.

4. Generate bounded candidates:
   - Produce 2-4 candidate changes unless the task is a narrow fix.
   - Keep candidate differences legible enough for evaluation.
   - Include a no-change baseline when the current behavior may already be acceptable.

5. Run independent evaluation:
   - Use subagents when available and appropriate.
   - Give each subagent one task only, following `$orchestrate-subagents` principles: bounded scope, expected output, stop condition, evidence, and no final decision authority.
   - Do not pass your preferred candidate as the expected answer.
   - For high-impact changes, use at least two independent reviewer signals, such as evaluator, risk reviewer, counterexample finder, or implementation reviewer.

6. Select and bound the result:
   - Choose the candidate that best satisfies the frozen oracle.
   - Record evaluator agreement, disagreement, missing evidence, and regressions.
   - If evidence is mixed, prefer a smaller change, a follow-up experiment, or no change.

7. Write back intentionally:
   - Default to a report or patch proposal.
   - Apply edits only when the user requested implementation or the current task clearly requires it.
   - Write durable learnings to the owning skill, prompt source, runbook, TODO, report, validation log, or automation memory.
   - Do not update generated caches or installed copies unless the local workflow requires it.

## Subagent Evaluation Patterns

Use the minimum useful set:

1. `default as evaluator`: apply the frozen oracle to candidate outputs and score evidence quality.
2. `default as risk-reviewer`: identify overfitting, ambiguity, permission creep, safety issues, or hidden regressions.
3. `default as counterexample-finder`: find realistic cases where the winning candidate fails.
4. `default as implementation-reviewer`: decide whether the winning change belongs in a skill, template, runbook, TODO, or automation.

For major decisions, do not accept a single positive review. Require either two independent positive signals or one positive signal plus a separate counterexample/risk pass with no blocker.

## Evidence Contract

Every final recommendation must include:

1. Target and source files or prompt surface.
2. Evidence used, with paths, logs, examples, or explicit user-provided text.
3. Evaluation oracle and regression checks.
4. Candidate summary, including the no-change baseline when used.
5. Independent reviewer coverage, status, and missing coverage.
6. Selected change and rejected alternatives.
7. Writeback target, validation command, rollback path, and residual risk.

## Stop Conditions

Stop and report instead of optimizing when:

- there is no evidence or evaluation oracle
- subagent evaluation is required but unavailable
- reviewer results conflict and cannot be reconciled
- the requested writeback would mutate skills, automations, connector permissions, source prompts, or recurring workflow behavior without user authorization
- candidates improve style while weakening correctness, safety, permission boundaries, or failure handling
- the task belongs in `long-running-goal` because it needs staged milestones, checkpoint evidence, and close hygiene

## Relationship To Other Workflow Skills

Use `long-running-goal` when prompt or strategy iteration becomes a durable multi-milestone objective. Use `orchestrate-subagents` when the current environment exposes subagent tools or the user explicitly asks for subagent orchestration. Keep this skill focused on evidence, candidate generation, independent evaluation, selection, and writeback.
