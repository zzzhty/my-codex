# Subagent Recipes

Use these recipes with `$orchestrate-subagents` when the user explicitly asks
for subagents. Adjust role names to the current Codex environment.

## PR Or Branch Review

Suggested subagents:

- `explorer`: map changed files, affected symbols, call paths, config changes,
  and risky areas.
- `default`: review correctness, security, regression, compatibility, and
  contract risks.
- `default`: identify missing tests and validation gaps.

Parent consolidation:

- blocking bugs first
- non-blocking risks second
- missing tests and exact validation commands
- files inspected by each subagent
- unresolved coverage gaps

## Debugging Or Failure Triage

Suggested subagents:

- `default`: reproduce or classify the failure from logs and commands.
- `explorer`: inspect nearby code paths, configuration, and recent changes.
- `default`: propose focused regression tests or diagnostics.

Stop if no subagent can access the failing command, log, or relevant files.
Report the missing evidence instead of guessing.

## Implementation Planning

Suggested subagents:

- `explorer`: map existing architecture, ownership boundaries, and related
  tests.
- `default`: compare implementation options and risks.
- `default`: identify validation gates and rollback paths.

Do not spawn workers until the user asks for implementation and write scopes
can be made disjoint.

## Bounded Parallel Implementation

Use only when implementation is explicitly requested.

Suggested subagents:

- `worker`: one disjoint module, file group, or adapter.
- `worker`: another disjoint module, file group, or adapter.
- `default`: review integration risks without editing files.

Every worker prompt must include:

- exact owned files or directories
- files it must not edit
- expected tests or dry-runs
- instruction not to revert edits made by others
- rollback notes for its slice

The parent owns final integration, conflict resolution, shared docs, and final
validation.

## API Or Schema Inspection

Suggested subagents:

- `explorer`: locate schema definitions, serializers, migrations, clients, and
  tests.
- `default`: review compatibility and contract risks.
- `default`: identify validation commands and fixture gaps.

Require exact paths and command evidence before accepting compatibility claims.

## Documentation Alignment

Suggested subagents:

- `explorer`: inventory active docs, indexes, entry points, and stale terms.
- `default`: classify findings by severity and recommend edits.
- `default`: check validation and link coverage.

Keep archive or historical docs separate from active current guidance.
