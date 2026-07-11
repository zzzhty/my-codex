# AGENTS Prompt Optimization Record

Updated: 2026-07-10

Status: C2 implemented, independently reviewed, validated, and archived.

## Scope

Reduce duplicated long-running-goal safety wording in root `AGENTS.md` without moving the pre-trigger planning and permission boundary out of root guidance.

## Preserved Semantic Inventory

- Ordinary complex work uses system planning; `long-running-goal` remains an explicit user choice.
- Authorizing creation or conversion includes its required planning preflight, but does not authorize implementation or execution.
- Only a `Ready` contract pre-approves planned, non-destructive local work inside its frozen scope; a `Draft` does not.
- Scoped work remains a YOLO non-stop and pauses only at a declared runtime hard stop.
- Request supersession, Codex goal-tool boundaries, full YOLO examples, and hard-stop details remain owned by `plugins/workflow/skills/long-running-goal/SKILL.md`, its references/components, and `agents/operating-principles.md`.

## Implemented Compression

- Replaced the repeated root operation list with the high-risk boundary and routed detailed examples to their existing owners.
- Clarified that create/convert authorization includes required preflight while execution needs a separate explicit request.
- Reduced root `AGENTS.md` from 680 to 662 words without changing its 38-line structure.
- Snapshot SHA-256: `98DCDE5C575B36C99F391B7E0D2AE33FA814C5A474E5412FF6901D5414E87077`.
- Accepted source SHA-256: `3CA65D5F3D005247AE9AC80E59EF4DC1091C8C40FF227A4FC2A3ABF9F83DEA43`.

## Independent Review

- Semantic evaluator verdict: `equivalent`, no blocker.
- Risk reviewer verdict: `equivalent`, no blocker or candidate-specific permission caveat.
- Both reviewers confirmed Draft/Ready, preflight-versus-execution, frozen local YOLO scope, runtime hard stops, request supersession, goal-tool boundaries, and failure handling remain intact.

## Validation

- Root 12/12, Workflow 32/32, and Watcher 42/42 tests passed.
- Workflow skill and plugin validators passed.
- TODO planning-tree, relative-link, and `check_todo_index.py --mode closed` checks passed.
- Workflow source/cache identity matched after reinstall; repository final checks passed with 0 warnings.

## Close Decision

C2 is closed. Detailed long-running-goal rules remain in the skill and managed operating-principles note; no active follow-up is required for this wording change.
