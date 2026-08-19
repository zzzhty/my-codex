---
name: prompt-strategy-loop
description: Use when improving prompts, agent instructions, skill guidance, workflow strategy, reviewer rubrics, or orchestration prompts from evidence; use for prompt A/B comparisons, failed-agent-output analysis, recurring workflow tuning, strategy regression review, and bounded writeback decisions with evaluation proportional to the affected behavior.
---

# Prompt Strategy Loop

Use this skill to improve prompts or agent strategy from evidence rather than preference. The output may be a recommendation, patch proposal, or applied edit when the user requested mutation.

## Core Rule

Freeze the evaluation oracle before writing candidates and use review proportional to the affected behavior.

Require an independent evaluator when a change affects invocation or routing, permissions, safety or privacy, destructive or external actions, automation or recurring execution, persisted or external contracts, or removes an existing stop or validation gate. Add a separate risk or counterexample pass only for permission, safety or privacy, destructive-action, or external-write changes. Otherwise the proposer may compare the no-change baseline and candidate directly against the frozen oracle and an affected-surface counterexample.

If required independent evaluation is unavailable, stop at an unverified proposal. Do not claim the new prompt is better.

## Report-Only Branch

When the user asks for an audit, recommendation, or implementation plan without requesting mutation, collect evidence, freeze the oracle, compare bounded candidates with the no-change baseline, apply the Core Rule, return the recommendation, and stop before writing source prompts, generated caches, or installed copies. Write a durable report only when requested.

## Workflow

1. Define target, failure mode or desired improvement, non-goals, and mutation boundaries.
2. Collect raw evidence: real failures, successful examples, logs, feedback, diffs, reports, benchmark tasks, or source artifacts. Do not tune against hidden assumptions or a single anecdote unless the user scoped it that way.
3. Freeze observable improvement criteria and regressions to avoid.
4. Compare the no-change baseline with the smallest viable candidate. Add alternatives only when evidence exposes a real design branch.
5. Apply the Core Rule. When using evaluators, give each one a bounded task, raw evidence, and a stop condition without leaking a preferred answer. Use subagents only when the active environment or plan authorizes delegation.
6. Select the smallest candidate that satisfies the oracle. Record material disagreement, missing evidence, regressions, rejected alternatives, and residual risk.
7. Write back only with authorization. Put durable learning in the owning source when it will matter beyond the current turn; do not update generated caches or installed copies unless activation is in scope.

## Evidence Contract

Final recommendations state the evidence and frozen oracle, selected and materially rejected alternatives, required reviewer coverage, writeback boundary, affected-surface validation, blockers, and residual risk.

## Stop Conditions

Stop and report instead of optimizing when there is no evidence or oracle, required evaluation is unavailable, blocking reviewer results conflict, mutation is unauthorized, a candidate weakens correctness, permissions, safety, privacy, failure handling, or an owning contract, or the work needs staged milestones and close hygiene owned by `long-running-goal`.

## Workflow Boundaries

Use `long-running-goal` when prompt or strategy iteration becomes a durable multi-milestone objective. Evaluator delegation does not invoke `orchestrate-subagents`; use that skill only when the user names it or explicitly asks for subagent orchestration. Keep this skill focused on evidence, oracle, candidates, proportional evaluation, selection, and bounded writeback.
