# Subagent Recipes

Use these recipes with `$orchestrate-subagents` when the user explicitly asks
for subagents. Adjust role names to the current Codex environment. The parent
agent remains responsible for final judgment, integration, validation, and
user-facing reporting.

Single-task rule: each subagent must have exactly one outcome-oriented
assignment. Split mapping, review, implementation, validation, and docs checks
into separate subagents instead of bundling them into one prompt.

## Atomic Assignment Checklist

Before spawning, check every subagent assignment:

- One primary verb: map, review, reproduce, identify, inspect, implement, or
  validate.
- One bounded scope: branch diff, failure log, module, schema surface, docs
  root, or implementation slice.
- One expected output: map, finding list, reproduction result, compatibility
  assessment, changed slice, or validation gap list.
- Evidence requirements do not create a second task. A worker can run tests for
  its own slice, but separate test strategy or cross-slice validation belongs
  to another subagent.
- If the assignment needs "and then", split it.

## Shared Output Contract

Every subagent should return:

- assignment label and single-task statement
- status: `done`, `partial`, or `blocked`
- paths inspected or changed
- commands run and results
- findings tied to evidence
- blockers, unknowns, and stop-condition status

## Prompt Skeleton Rule

The parent prompt skeletons below describe the whole orchestration request. When
actually spawning each subagent, expand that subagent into the full prompt
template from `../SKILL.md`, including assignment label, single task, context,
ownership, expected output, stop condition, and boundaries.

## Recipe Selection Matrix

| User intent | Recipe |
| --- | --- |
| Review a branch, PR, or diff | PR Or Branch Review |
| Diagnose a failing command, test, run, or report | Debugging Or Failure Triage |
| Plan a feature, migration, refactor, or architecture change | Implementation Planning |
| Implement disjoint slices in parallel | Bounded Parallel Implementation |
| Inspect API, schema, serialization, migration, or client compatibility | API Or Schema Inspection |
| Align docs, runbooks, skills, plans, or stale terms | Documentation Alignment |

## PR Or Branch Review

Use when:

- the user asks to review a branch, PR, local diff, or planned merge
- the work is read-only and can be split into mapping, risk review, and test
  review

Do not use when:

- there is no meaningful diff or base/head context and the user only needs a
  narrow file review
- the user asked for implementation, not review

Suggested subagents:

- `explorer` as `code-mapper`: map changed files, affected symbols, call
  paths, config changes, and risky areas.
- `default` as `implementation-reviewer`: review correctness, security,
  regression, compatibility, and contract risks.
- `default` as `test-verifier`: identify missing tests and validation gaps.

Required evidence:

- base and head refs, or exact diff scope if no branch base exists
- paths inspected by each subagent
- commands run, including diff, tests, lint, or static checks when available
- blocking issues with file paths and evidence
- coverage gaps if any subagent could not inspect required context

Parent prompt skeleton:

```text
Use $orchestrate-subagents.

Task: Review this branch against <base>.

Spawn bounded read-only subagents:
- explorer as code-mapper: identify changed files, affected symbols, call
  paths, config changes, and risky areas.
- default as implementation-reviewer: review correctness, security,
  regression, compatibility, and contract risks.
- default as test-verifier: identify missing tests and validation gaps.

Context:
- base/head: <base>...<head>
- commands already run: <commands or none>
- important constraints: <constraints>

Boundaries:
- Do not edit files.
- Each subagent has one task only.
- Do not report success without paths, commands, and evidence.

Wait for all selected subagents. Consolidate blocking issues, non-blocking
risks, missing tests, evidence, coverage gaps, and recommended next action.
```

## Debugging Or Failure Triage

Use when:

- the user gives a failing command, error, test, CI job, log, or reproducible
  symptom
- evidence can be split into reproduction, nearby code inspection, and test or
  diagnostic planning

Do not use when:

- no failing command, log, error text, or affected path is available
- the problem requires sequential interactive debugging where parallel work
  would duplicate effort

Suggested subagents:

- `default` as `failure-classifier`: reproduce or classify the failure from
  logs and commands.
- `explorer` as `code-path-mapper`: inspect nearby code paths, configuration,
  and recent changes.
- `default` as `test-diagnostic-planner`: propose focused regression tests or
  diagnostics.

Required evidence:

- failing command, test name, CI job, log path, or error excerpt
- reproduction result or explicit reason reproduction was not possible
- likely failing path or boundary, with file paths
- diagnostic commands or regression tests that would distinguish hypotheses

Parent prompt skeleton:

```text
Use $orchestrate-subagents.

Task: Diagnose <failure>.

Spawn bounded subagents:
- default as failure-classifier: reproduce or classify the failure using the
  provided command/log/error.
- explorer as code-path-mapper: inspect nearby code paths, configuration, and
  recent changes that could explain the failure.
- default as test-diagnostic-planner: propose focused regression tests or
  diagnostics.

Context:
- failing command/log/error: <exact command, log path, or error text>
- affected files or area: <paths or unknown>
- recent changes: <refs, files, or unknown>

Boundaries:
- Do not guess when required evidence is missing.
- Do not edit files unless the parent later authorizes a fix.
- Each subagent has one task only.

Stop if no subagent can access the failing command, log, or relevant files.
Wait for all selected subagents and consolidate root-cause candidates,
blocking evidence, missing diagnostics, and next action.
```

## Implementation Planning

Use when:

- the user asks for a plan before implementation
- the work may affect multiple modules, contracts, tests, or docs

Do not use when:

- the user has already approved a narrow implementation and no architectural
  uncertainty remains
- the work needs immediate sequential diagnosis before planning

Suggested subagents:

- `explorer` as `architecture-mapper`: map existing architecture, ownership
  boundaries, and related tests.
- `default` as `option-reviewer`: compare implementation options and risks.
- `default` as `validation-planner`: identify validation gates and rollback
  paths.

Required evidence:

- relevant modules, ownership boundaries, and current entry points
- existing tests or validation commands
- recommended option with tradeoffs and rejected alternatives
- rollback or containment strategy for risky changes

Parent prompt skeleton:

```text
Use $orchestrate-subagents.

Task: Plan <feature, migration, refactor, or architecture change>.

Spawn bounded read-only subagents:
- explorer as architecture-mapper: map current architecture, ownership
  boundaries, entry points, and related tests.
- default as option-reviewer: compare viable implementation options and risks.
- default as validation-planner: identify validation gates, missing tests, and
  rollback paths.

Context:
- goal: <goal>
- known constraints: <constraints>
- likely affected areas: <paths or unknown>

Boundaries:
- Do not edit files.
- Do not spawn workers until write scopes are explicit and implementation is
  requested.
- Each subagent has one task only.

Wait for all selected subagents. Consolidate the recommended plan, alternatives
rejected, validation gates, rollback path, and unresolved decisions.
```

## Bounded Parallel Implementation

Use when:

- the user authorized implementation
- work can be split into disjoint write scopes
- shared files, final integration, and final validation can remain parent-owned

Do not use when:

- two workers would need to edit the same file or generated artifact
- the task depends on a single sequential debugging loop
- local mutation boundaries or user approval are unclear

Suggested subagents:

- `worker` as `slice-a-implementer`: implement one disjoint module, file group,
  or adapter.
- `worker` as `slice-b-implementer`: implement another disjoint module, file
  group, or adapter.
- `default` as `integration-risk-reviewer`: review integration risks without
  editing files.

Required evidence:

- exact files or directories owned by each worker
- files each worker must not edit
- commands run by each worker and results
- changed files and behavior impact for each implementation slice
- conflicts, skipped scope, or rollback notes

Parent prompt skeleton:

```text
Use $orchestrate-subagents.

Task: Implement <task> using disjoint worker scopes.

Parent-owned shared files:
- <shared files, docs, config, lockfiles, or generated artifacts>

Spawn bounded subagents:
- worker as slice-a-implementer:
  Ownership: may edit only <scope-a>.
  Single task: implement <scope-a>.
  Must not edit <blocked-files>.
  Validation evidence: <commands or dry-runs for scope-a>.
- worker as slice-b-implementer:
  Ownership: may edit only <scope-b>.
  Single task: implement <scope-b>.
  Must not edit <blocked-files>.
  Validation evidence: <commands or dry-runs for scope-b>.
- default as integration-risk-reviewer:
  Ownership: read-only.
  Single task: review integration risks.
  Inspect integration risks across the planned scopes.

Boundaries:
- Each worker has one implementation slice only.
- Validation commands are evidence for that slice, not a second task.
- Workers must not revert edits made by others.
- Workers must stop if their required edits leave their owned scope.
- Workers must report changed files, commands run, blockers, and rollback
  notes.

Wait for all selected subagents. The parent owns conflict resolution, shared
files, final integration, final validation, and user-facing summary.
```

## API Or Schema Inspection

Use when:

- the task depends on API compatibility, schema shape, serializers, migrations,
  clients, fixtures, or wire contracts
- claims need exact paths and command evidence before implementation or review

Do not use when:

- the task is only a UI or docs change with no contract surface
- the relevant schema or API source cannot be accessed

Suggested subagents:

- `explorer` as `schema-mapper`: locate schema definitions, serializers,
  migrations, clients, and tests.
- `default` as `compatibility-reviewer`: review compatibility and contract
  risks.
- `default` as `fixture-verifier`: identify validation commands and fixture
  gaps.

Required evidence:

- schema, migration, serializer, client, and test paths inspected
- known consumers or compatibility boundaries
- validation commands and fixture gaps
- explicit compatibility risks, including backward/forward compatibility when
  relevant

Parent prompt skeleton:

```text
Use $orchestrate-subagents.

Task: Inspect API or schema compatibility for <change>.

Spawn bounded read-only subagents:
- explorer as schema-mapper: locate schema definitions, serializers,
  migrations, clients, and tests.
- default as compatibility-reviewer: review compatibility and contract risks.
- default as fixture-verifier: identify validation commands and fixture gaps.

Context:
- suspected contract surface: <paths, endpoints, schemas, or unknown>
- consumers: <known consumers or unknown>
- proposed or observed change: <change>

Boundaries:
- Do not edit files.
- Each subagent has one task only.
- Do not accept compatibility claims without exact paths and command evidence.

Wait for all selected subagents. Consolidate contract surfaces, compatibility
risks, missing fixtures, validation commands, and unresolved unknowns.
```

## Documentation Alignment

Use when:

- the task is to audit or align current docs, runbooks, plans, skills, scripts,
  entry points, or terminology
- active guidance may have drifted from current source of truth

Do not use when:

- the user only asks for a narrow wording edit
- archive or historical docs should remain unchanged and are the only hits

Suggested subagents:

- `explorer` as `doc-inventory-mapper`: inventory active docs, indexes, entry
  points, and stale terms.
- `default` as `doc-drift-reviewer`: classify findings by severity and
  recommend edits.
- `default` as `link-validation-reviewer`: check validation and link coverage.

Required evidence:

- active docs and indexes inspected
- source-of-truth files used for comparison
- stale terms, broken links, missing entry points, or outdated commands
- distinction between active current guidance and archive/historical material

Parent prompt skeleton:

```text
Use $orchestrate-subagents.

Task: Align documentation for <area>.

Spawn bounded read-only subagents:
- explorer as doc-inventory-mapper: inventory active docs, indexes, entry
  points, and stale terms.
- default as doc-drift-reviewer: classify semantic drift by severity and
  recommend edits.
- default as link-validation-reviewer: check validation and link coverage.

Context:
- docs root or scope: <paths>
- source of truth: <code, scripts, manifests, skills, or plans>
- terms or commands to audit: <terms or commands>

Boundaries:
- Do not edit archive or historical docs unless explicitly requested.
- Do not treat an archive-only hit as current user guidance.
- Each subagent has one task only.

Wait for all selected subagents. Consolidate active-doc findings, severity,
recommended edits, validation commands, link coverage, and unresolved gaps.
```

## Anti-patterns

- Do not spawn subagents for tiny tasks that one agent can inspect faster.
- Do not send the whole parent task to every subagent.
- Do not combine mapping, review, implementation, validation, and docs checks in
  one subagent.
- Do not let multiple workers edit the same file, lockfile, generated artifact,
  or shared config.
- Do not let a subagent make the final product or merge decision.
- Do not report success when paths, commands, or evidence are missing.
- Do not use subagents to bypass user authorization, sandbox limits, or local
  mutation boundaries.
- Do not hide timeouts, missing tools, incomplete findings, or conflicting
  claims.
