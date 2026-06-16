# Subagent Recipes

Use these recipes with `$orchestrate-subagents` only when the user explicitly asks for subagents. Use built-in roles with task-local assignment labels. The parent owns final judgment, integration, validation, and user-facing reporting.

Single-task rule: each subagent gets one outcome-oriented assignment. Split mapping, review, implementation, validation, and docs checks into separate subagents.

## Shared Contract

Before spawning, check every assignment:

- one primary verb: map, review, reproduce, identify, inspect, implement, or validate
- one bounded scope: branch diff, failure log, module, schema surface, docs root, or implementation slice
- one expected output: map, finding list, reproduction result, compatibility assessment, changed slice, or validation gap list
- evidence requirements do not become a second task; a worker can run tests for its slice, but test strategy or cross-slice validation is separate
- if the assignment needs "and then", split it

Every subagent should return assignment label, single-task statement, status (`done`, `partial`, `blocked`), paths inspected/changed, commands and results, evidence-tied findings, blockers, unknowns, and stop-condition status.

Parent prompt skeletons below describe the whole orchestration request. When spawning a specific subagent, expand it with the full prompt template from `../SKILL.md`: assignment label, single task, context, ownership, expected output, stop condition, and boundaries.

Reusable parent prompt spine:

```text
Use $orchestrate-subagents.
Task: <parent task>.
Spawn bounded subagents:
- <role as label>: <single task; ownership; evidence required>.
Context: <base/head, paths, commands, constraints, unknowns>.
Boundaries: <no edits or exact write scope; one task each; evidence required>.
Wait for selected subagents, then consolidate blockers, risks, evidence, gaps, and next action.
```

## Recipe Matrix

| User intent | Recipe |
| --- | --- |
| Review a branch, PR, diff, or planned merge | PR Or Branch Review |
| Diagnose a failing command, test, run, CI job, report, log, or symptom | Debugging Or Failure Triage |
| Plan a feature, migration, refactor, or architecture change | Implementation Planning |
| Implement disjoint write slices in parallel | Bounded Parallel Implementation |
| Inspect API, schema, serialization, migration, fixture, client, or wire compatibility | API Or Schema Inspection |
| Align docs, runbooks, skills, plans, scripts, entry points, or stale terms | Documentation Alignment |

## PR Or Branch Review

Use for read-only branch/PR/diff review when work can split into mapping, risk review, and test review. Avoid when there is no meaningful diff/base/head context, the user only needs a narrow file review, or the user asked for implementation.

Suggested subagents:

- `explorer as code-mapper`: changed files, affected symbols, call paths, config changes, risky areas.
- `default as implementation-reviewer`: correctness, security, regression, compatibility, contract risks.
- `default as test-verifier`: missing tests and validation gaps.

Required evidence: base/head or exact diff scope, paths inspected, commands run when available, blocking issues with file paths/evidence, and coverage gaps.

Parent prompt must include: `Use $orchestrate-subagents`, task `Review this branch against <base>`, bounded read-only subagents above, base/head and constraints, no edits, one task per subagent, no success without paths/commands/evidence, wait for all selected subagents, then consolidate blockers, risks, missing tests, evidence, gaps, and next action.

## Debugging Or Failure Triage

Use when the user provides a failing command, error, test, CI job, log, report, or reproducible symptom and evidence can split into reproduction/classification, nearby code inspection, and diagnostic planning. Avoid when no failure evidence or affected path is available, or the problem needs sequential interactive debugging.

Suggested subagents:

- `default as failure-classifier`: reproduce or classify from logs and commands.
- `explorer as code-path-mapper`: inspect nearby code paths, config, recent changes.
- `default as test-diagnostic-planner`: propose focused regression tests or diagnostics.

Required evidence: failing command/log/error, reproduction result or why unavailable, likely failing path/boundary, and diagnostic commands/tests that distinguish hypotheses.

Parent prompt must include: `Use $orchestrate-subagents`, task `Diagnose <failure>`, the bounded subagents above, exact failure evidence, affected files or unknowns, recent changes, no guessing when evidence is missing, no edits unless later authorized, one task per subagent, stop if no subagent can access required failure context, then consolidate root-cause candidates, blocking evidence, missing diagnostics, and next action.

## Implementation Planning

Use when the user asks for a plan before implementation and the work may affect multiple modules, contracts, tests, or docs. Avoid when a narrow implementation is already approved or immediate sequential diagnosis is needed first.

Suggested subagents:

- `explorer as architecture-mapper`: architecture, ownership boundaries, entry points, related tests.
- `default as option-reviewer`: implementation options, tradeoffs, risks.
- `default as validation-planner`: validation gates, missing tests, rollback paths.

Required evidence: relevant modules and owners, current entry points, existing tests/commands, recommended option and rejected alternatives, rollback/containment strategy.

Parent prompt must include: `Use $orchestrate-subagents`, task `Plan <feature/migration/refactor/architecture change>`, bounded read-only subagents above, goal, constraints, affected areas or unknowns, no edits, no workers until write scopes are explicit and implementation requested, one task per subagent, then consolidate plan, rejected alternatives, validation gates, rollback path, and unresolved decisions.

## Bounded Parallel Implementation

Use when implementation is authorized, write scopes are disjoint, and shared files plus final integration/validation stay parent-owned. Avoid when workers would edit the same file, lockfile, generated artifact, or shared config; the task is a single sequential debugging loop; or mutation/approval boundaries are unclear.

Suggested subagents:

- `worker as slice-a-implementer`: implement one disjoint module/file group/adapter.
- `worker as slice-b-implementer`: implement another disjoint module/file group/adapter.
- `default as integration-risk-reviewer`: read-only integration risk review.

Required evidence: exact owned files/directories, files each worker must not edit, commands and results, changed files and behavior impact, conflicts, skipped scope, rollback notes.

Parent prompt must include: `Use $orchestrate-subagents`, task `Implement <task> using disjoint worker scopes`, parent-owned shared files, each worker's allowed scope, blocked files, single implementation task, validation evidence for its slice, integration reviewer read-only scope, no cross-scope edits, tests as evidence not second tasks, no reverting others, stop if required edits leave owned scope, parent owns conflict resolution, shared files, final integration, final validation, and final summary.

## API Or Schema Inspection

Use when work depends on API compatibility, schema shape, serializers, migrations, clients, fixtures, or wire contracts, and claims need exact paths plus command evidence. Avoid for UI/docs-only changes without contract surface or when relevant schema/API sources cannot be accessed.

Suggested subagents:

- `explorer as schema-mapper`: schemas, serializers, migrations, clients, tests.
- `default as compatibility-reviewer`: compatibility and contract risks.
- `default as docs-verifier`: official API/config/version/migration assumptions when relevant.
- `default as fixture-verifier`: validation commands and fixture gaps.

Required evidence: schema/migration/serializer/client/test paths, known consumers, compatibility boundaries, validation commands, fixture gaps, backward/forward compatibility risks.

Parent prompt must include: `Use $orchestrate-subagents`, task `Inspect API or schema compatibility for <change>`, bounded read-only subagents above, suspected contract surface, consumers or unknowns, proposed/observed change, no edits, one task per subagent, no compatibility claims without exact paths and command evidence, then consolidate surfaces, risks, fixtures, validation commands, and unknowns.

## Documentation Alignment

Use to audit or align current docs, runbooks, plans, skills, scripts, entry points, or terminology when active guidance may drift from source of truth. Avoid narrow wording edits and archive-only historical hits unless the user explicitly asks to edit history.

Suggested subagents:

- `explorer as doc-inventory-mapper`: active docs, indexes, entry points, stale terms.
- `default as doc-drift-reviewer`: semantic drift severity and recommended edits.
- `default as link-validation-reviewer`: validation and link coverage.

Required evidence: active docs/indexes inspected, source-of-truth files, stale terms/broken links/missing entry points/outdated commands, and active-vs-archive distinction.

Parent prompt must include: `Use $orchestrate-subagents`, task `Align documentation for <area>`, bounded read-only subagents above, docs root/scope, source of truth, terms/commands to audit, no archive edits unless requested, no archive-only hit as current guidance, one task per subagent, then consolidate active-doc findings, severity, edits, validation commands, link coverage, and unresolved gaps.

## Anti-Patterns

- Do not spawn subagents for tiny tasks.
- Do not send the whole parent task to every subagent.
- Do not combine mapping, review, implementation, validation, and docs checks in one subagent.
- Do not let multiple workers edit the same file, lockfile, generated artifact, or shared config.
- Do not let a subagent make final product or merge decisions.
- Do not report success without paths, commands, and evidence.
- Do not use subagents to bypass user authorization, sandbox limits, or mutation boundaries.
- Do not hide timeouts, missing tools, incomplete findings, or conflicting claims.
