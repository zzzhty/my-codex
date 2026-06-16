---
name: summary-in-html
description: Use when generating a standalone HTML reference summary for a project, repository, directory, module, feature area, documentation chapter, or user-specified scope, with structured sections for developer reference and optional generated visual assets when the user explicitly asks for images.
---

# Summary In HTML

Use this skill to turn a bounded scope into a standalone HTML developer reference. Scope may be a project, directory, module, feature area, documentation chapter, or user-provided source material.

Do not use it for documentation drift audits; use `doc-alignment` or DocWatcher when the task is to find stale or contradictory docs.

## Output Contract

Produce an inspectable HTML artifact and report scope, output path, supporting asset paths, evidence collection files/commands, validation result, and blind spots.

Defaults:

```text
docs/summaries/<scope-slug>.html
docs/summaries/assets/
```

If the user provides an output path, use it and place assets in a sibling `assets/` directory unless told otherwise.

## Workflow

1. Determine scope: whole repo, directory/package, module/feature, documentation chapter, or user-provided material. Read `references/scope_contract.md` when boundaries are ambiguous.
2. Collect read-only evidence:

```bash
python <skill-folder>/scripts/collect_summary_inputs.py --root <repo-root> --scope <scope-path> --out <artifact>.inputs.json
```

3. Inspect relevant source entry points, README/AGENTS files, package config, tests, scripts, and nearby docs.
4. Draft a chapter plan. Read `references/chapter_contract.md` unless the summary is trivial.
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

## Visual Assets

Generate or place images only when the user explicitly asks for visuals. Read `references/visual_asset_contract.md` before creating or placing image assets.

Prefer deterministic Mermaid, SVG, or styled HTML for exact architecture, sequence, module, dependency, or state diagrams. Use `imagegen` only for requested raster images, illustrative visuals, infographics, conceptual graphics, or user-specified generated images. Move selected project-bound images into the HTML asset directory and reference that local path; never leave referenced project assets only under `$CODEX_HOME/generated_images/`.

## HTML Rules

- Keep HTML standalone: inline CSS, no remote fonts, no external scripts.
- Make it skimmable: navigation, short sections, file references, blind spots.
- Preserve developer usefulness over polish; do not invent unsupported architecture.
- Keep generated summaries separate from source docs unless replacement is requested.
- Do not overwrite existing summaries unless requested; otherwise create a versioned or more specific filename.
