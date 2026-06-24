---
name: prompt-strategy-loop
description: Use when improving prompts, agent instructions, skill guidance, workflow strategy, reviewer rubrics, or orchestration prompts through evidence-backed iteration; use for prompt A/B comparisons, failed-agent-output analysis, recurring workflow tuning, strategy regression review, and decisions that need independent subagent evaluation before writing changes back to a skill, runbook, automation, or source prompt.
---

# Prompt Strategy Loop

Use this skill to improve prompts or agent strategy from evidence rather than preference. The output may be a recommendation, patch proposal, or applied edit when the user requested mutation.

## Core Rule

The proposer must not be the sole judge of whether a prompt or strategy improved. Use at least one independent evaluator; use multiple independent reviewers for high-impact changes to skills, automations, connector permissions, safety boundaries, recurring workflows, or orchestration prompts.

If independent evaluation is unavailable, stop at an unverified proposal and say so. Do not claim the new prompt is better.

## Report-Only Branch

When the user asks for a prompt, skill, or workflow audit, recommendation, or implementation plan without requesting source mutation, run the loop as a report-only evaluation: collect evidence, freeze the oracle, compare bounded candidates against a no-change baseline, run independent review according to the Core Rule, return the recommendation or write a durable report only when requested, and stop before writing source prompts, generated caches, or installed copies.

## Workflow

1. Define target, failure mode or desired improvement, non-goals, and mutation boundaries.
2. Collect raw evidence: real failures, successful examples, logs, feedback, diffs, reports, benchmark tasks, or source artifacts. Do not tune against hidden assumptions or a single anecdote unless the user scoped it that way.
3. Freeze the evaluation oracle before writing candidates: observable improvement criteria plus regressions to avoid, such as correctness, false positives/negatives, evidence quality, unnecessary escalation, permission prompts, formatting stability, and task completion.
4. Generate bounded candidates: usually 2-4 legible changes plus a no-change baseline when the current behavior may be acceptable.
5. Run independent evaluation:
   - use subagents when available and appropriate
   - give each evaluator one bounded task with expected output, stop condition, and evidence
   - do not reveal a preferred candidate as the expected answer
   - for high-impact changes, require two independent positive signals, or one positive signal plus a separate risk/counterexample pass with no blocker
6. Select the smallest candidate that satisfies the oracle. Record agreement, disagreement, missing evidence, regressions, rejected alternatives, and residual risk.
7. Write back intentionally. Default to report or patch proposal; apply edits only when requested or clearly required. Write durable learnings to the owning skill, prompt source, runbook, TODO, report, validation log, or automation memory. Do not update generated caches or installed copies unless the local workflow requires it.

## Evaluation Roles

Use the minimum useful set:

1. `default as evaluator`: apply the oracle to candidate outputs and score evidence.
2. `default as risk-reviewer`: identify overfitting, ambiguity, permission creep, safety issues, or hidden regressions.
3. `default as counterexample-finder`: find realistic cases where the winning candidate fails.
4. `default as implementation-reviewer`: decide whether the change belongs in a skill, template, runbook, TODO, or automation.

## Evidence Contract

Final recommendations must include:

1. Target and source files or prompt surface.
2. Evidence used, with paths/logs/examples/user text.
3. Evaluation oracle and regression checks.
4. Candidate summary, including no-change baseline when used.
5. Independent reviewer coverage, status, and missing coverage.
6. Selected change and rejected alternatives.
7. Writeback target, validation command, rollback path, and residual risk.

## Stop Conditions

Stop and report instead of optimizing when there is no evidence or oracle, required subagent evaluation is unavailable, reviewer results conflict and cannot be reconciled, mutation would affect skills/automations/connectors/source prompts/recurring workflows without authorization, candidates improve style while weakening correctness/safety/permissions/failure handling, or the work belongs in `long-running-goal` because it needs staged milestones, checkpoint evidence, and close hygiene.

## Workflow Boundaries

Use `long-running-goal` when prompt/strategy iteration becomes a durable multi-milestone objective. Use `orchestrate-subagents` when the current environment exposes subagent tools for evaluation or when the user explicitly asks for subagent orchestration. Keep this skill focused on evidence, candidates, independent evaluation, selection, and writeback.
