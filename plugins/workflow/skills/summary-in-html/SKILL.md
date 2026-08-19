---
name: summary-in-html
description: Generate a standalone HTML developer reference or source-code walkthrough for a project, repository, directory, module, feature area, documentation chapter, or user-specified scope. Use for scoped summaries and for step-by-step code handoffs that start from real entry points; generate visual assets only when the user explicitly asks for images.
---

# Summary In HTML

Turn a bounded scope into one standalone HTML developer reference. Choose one document type:

- `summary` (default): explain ownership, structure, behavior, and developer operations.
- `source_walkthrough`: help a developer take over unfamiliar code by following real entry points and function handoffs step by step.

Do not use it for documentation drift audits; use Watcher `doc-alignment` when the task is to find stale or contradictory docs.

## Output Contract

Produce an inspectable HTML artifact and report scope, output path, supporting asset paths, evidence collection files/commands, validation result, and blind spots.

Defaults:

```text
docs/summaries/<scope-slug>.html
docs/summaries/assets/
```

If the user provides an output path, use it and place assets in a sibling `assets/` directory unless told otherwise.

## Workflow

1. Determine scope and document type. Read `references/scope_contract.md` when boundaries are ambiguous. For a source walkthrough, read `references/source_walkthrough_contract.md`.
2. Collect read-only evidence:

```bash
python <skill-folder>/scripts/collect_summary_inputs.py --root <repo-root> --scope <scope-path> --out <artifact>.inputs.json
```

3. Inspect relevant source entry points, README/AGENTS files, package config, tests, scripts, and nearby docs. Trace actual callers and returns for a source walkthrough; do not infer a route from filenames.
4. Draft a chapter plan. For a regular summary, read `references/chapter_contract.md` unless the summary is trivial. For a source walkthrough, put the complete route map before the numbered steps.
5. Write structured summary JSON next to the target HTML and render:

```bash
python <skill-folder>/scripts/render_summary_html.py --input <summary>.json --out <summary>.html
```

6. Validate:

```bash
python <skill-folder>/scripts/check_summary_html.py <summary>.html
```

Stop and report the blocker if required paths are missing, evidence collection fails, rendering fails, requested image assets are missing, or validation fails.

## Summary JSON Shape

Include only useful fields:

```json
{
  "title": "Workflow Plugin Summary",
  "subtitle": "Developer reference for plugins/workflow",
  "scope_label": "plugins/workflow",
  "source_root": "/absolute/repo/path",
  "evidence": [{"label": "Inventory", "path": "docs/summaries/workflow.inputs.json"}],
  "assets": [{"path": "assets/workflow-architecture.png", "alt": "Architecture overview", "caption": "Workflow plugin summary architecture"}],
  "sections": [
    {
      "title": "Purpose",
      "summary": "What this scope owns.",
      "bullets": ["Developer-facing point"],
      "files": [{"path": "plugins/workflow/README.md", "note": "Plugin entry point"}]
    }
  ],
  "blind_spots": ["Tests were not run."]
}
```

For a source walkthrough, add `"document_type": "source_walkthrough"`, `source_revision`, current-source evidence, and a non-empty `completion_check` only to sections that are actual steps. Each step also declares its entry symbol plus receives/does/handoff/return lists. Keep overview, context, and follow-up sections unnumbered. The renderer links walkthrough `files` to `source_root`, numbers only validated completion-check sections, and adds progressively enhanced local progress tracking.

The renderer validates nested list members before writing HTML: paragraphs, bullets, blind spots, and completion checks are strings; files use `{path, note?}`; code blocks use `{text, language?}`; evidence uses `{path, label?, role?}`; and assets use `{path, alt, caption}`. File and evidence paths must be non-empty, and every asset field must be non-empty.

## Visual Assets

Only when the user explicitly requests visuals, read `references/visual_asset_contract.md` and follow its diagram, imagegen, placement, accessibility, and evidence rules.

## HTML Rules

- Keep HTML standalone: inline CSS, no remote fonts, no external scripts.
- Make it skimmable: navigation, short sections, file references, blind spots.
- Preserve developer usefulness over polish; do not invent unsupported architecture.
- Treat walkthrough checkboxes as reader navigation, never as validation evidence or a project checkpoint.
- Keep generated summaries separate from source docs unless replacement is requested.
- Do not overwrite existing summaries unless requested; otherwise create a versioned or more specific filename.
