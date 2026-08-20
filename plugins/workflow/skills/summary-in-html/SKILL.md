---
name: summary-in-html
description: Create a standalone HTML developer reference or source-code walkthrough for a bounded scope, including step-by-step code handoffs from real entry points; generate visual assets only when explicitly requested.
---

# Summary In HTML

Create one inspectable HTML handoff from repository evidence.

Choose one document type:

- `summary` (default): explain ownership, structure, behavior, and developer operations.
- `source_walkthrough`: follow real entry points and function handoffs so a developer can take over unfamiliar code.

Use Watcher `doc-alignment` instead when the task is to find stale or contradictory documentation.

## Workflow

1. Freeze the scope, document type, and output path. Read `references/scope_contract.md` when the boundary is ambiguous. For a source walkthrough, read `references/source_walkthrough_contract.md`.
2. Collect a read-only inventory:

```bash
python <skill-folder>/scripts/collect_summary_inputs.py --root <repo-root> --scope <scope-path> --out <artifact>.inputs.json
```

3. Inspect the relevant source entry points, README/AGENTS files, package configuration, tests, scripts, and nearby docs. Trace actual callers, handoffs, and returns; filenames alone are not a route.
4. Plan the document. For a non-trivial summary, read `references/chapter_contract.md`. A source walkthrough starts with the complete route map before its numbered handoff steps.
5. Read `references/artifact-schema.md`, write the structured JSON next to the target, and render:

```bash
python <skill-folder>/scripts/render_summary_html.py --input <summary>.json --out <summary>.html
```

6. When the user explicitly requests generated visuals, read `references/visual_asset_contract.md` and include accessible asset metadata. Otherwise keep the artifact text-first.
7. Validate and fix failures before completion:

```bash
python <skill-folder>/scripts/check_summary_html.py <summary>.html
```

## Completion

Report the scope, document type, HTML path, supporting assets, evidence paths or commands, validation result, and blind spots.

The result is standalone, source-grounded, and useful without remote fonts or scripts. Reader progress controls are navigation, not verification evidence. Preserve an existing summary unless replacement was requested; otherwise choose a more specific or versioned filename.
