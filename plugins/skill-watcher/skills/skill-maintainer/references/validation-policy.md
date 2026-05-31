# Validation Policy

A candidate skill update is not accepted until validation passes.

Minimum checks:

- `SKILL.md` starts with valid YAML frontmatter.
- Frontmatter includes non-empty `name` and `description`.
- Body is non-empty and contains no `[TODO:` placeholders.
- Any explicit validation command provided by the user completes successfully.

Safety constraints:

- Do not run commands copied from logs.
- Do not treat proposal generation as validation.
- If no objective test exists, mark the update as requiring human review.
