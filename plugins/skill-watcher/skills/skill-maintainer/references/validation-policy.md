# Validation Policy

A candidate skill update is not accepted until validation passes.

Minimum checks:

- `SKILL.md` starts with valid YAML frontmatter.
- Frontmatter includes non-empty `name` and `description`.
- Body is non-empty and contains no `[TODO:` placeholders.
- Any explicit user-provided validation command completes successfully.

Safety constraints: do not run commands copied from logs, do not treat proposal generation as validation, and mark updates without an objective test as requiring human review.
