---
name: summary-in-html
description: Use when generating a standalone HTML reference summary for a project, repository, directory, module, feature area, documentation chapter, or user-specified scope, with structured sections for developer reference and optional generated visual assets when the user explicitly asks for images.
---

# Summary In HTML

Use this skill to turn a bounded scope into a standalone HTML reference artifact
for developers. The scope may be an entire project, one directory, a module, a
feature area, a documentation chapter, or source material named by the user.

Do not treat this as a documentation drift audit. Use `doc-alignment` or
DocWatcher when the task is to find stale or contradictory documentation.

## Output Contract

Produce an inspectable HTML artifact and report:

1. Scope summarized.
2. Output HTML path.
3. Supporting asset paths, if any.
4. Evidence collection command or files inspected.
5. Validation command and result.
6. Any important blind spots.

Default output location:

```text
docs/summaries/<scope-slug>.html
```

Put project-bound generated images under:

```text
docs/summaries/assets/
```

If the user provides an output path, use that path and place assets in a sibling
`assets/` directory unless the user says otherwise.

## Scope Workflow

1. Determine the requested scope:
   - whole project or repository
   - directory or package
   - module or feature area
   - documentation chapter
   - user-provided source material
2. Read `references/scope_contract.md` if scope boundaries are ambiguous.
3. Collect read-only evidence before drafting:

```bash
python <skill-folder>/scripts/collect_summary_inputs.py --root <repo-root> --scope <scope-path> --out <artifact>.inputs.json
```

4. Inspect the most relevant files from the collected inventory. Prefer source
   entry points, README/AGENTS files, package config, tests, scripts, and docs
   near the requested scope.
5. Draft a chapter plan. Read `references/chapter_contract.md` when choosing
   chapters for anything other than a trivial one-file summary.
6. Write a structured summary JSON next to the target HTML, then render it:

```bash
python <skill-folder>/scripts/render_summary_html.py --input <summary>.json --out <summary>.html
```

7. Validate the artifact:

```bash
python <skill-folder>/scripts/check_summary_html.py <summary>.html
```

Stop and report the blocker if required source paths are missing, evidence
collection fails, rendering fails, image assets are missing, or validation fails.

## Summary JSON Shape

Use this shape as the renderer input. Include only fields that are useful for
the current artifact.

```json
{
  "title": "Workflow Plugin Summary",
  "subtitle": "Developer reference for plugins/workflow",
  "scope_label": "plugins/workflow",
  "source_root": "/absolute/repo/path",
  "evidence": [
    {"label": "Inventory", "path": "docs/summaries/workflow.inputs.json"}
  ],
  "assets": [
    {
      "path": "assets/workflow-architecture.png",
      "alt": "Architecture overview",
      "caption": "Workflow plugin summary architecture"
    }
  ],
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

Only generate images when the user explicitly asks for them. Read
`references/visual_asset_contract.md` before creating or placing image assets.

For exact architecture, sequence, module, or dependency diagrams, prefer
deterministic HTML-native diagrams such as Mermaid, SVG, or styled HTML unless
the user explicitly wants an AI-generated raster image or illustration.

When the user explicitly asks for generated raster visuals, use the `imagegen`
skill after extracting a concise visual brief. Move the final selected asset
into the HTML artifact's asset directory and reference that local path in the
summary JSON. Never leave a project-referenced image only under
`$CODEX_HOME/generated_images/`.

## HTML Quality Rules

- Keep the HTML standalone: inline CSS, no remote fonts, no external scripts.
- Make the artifact skimmable: navigation, short sections, file references, and
  explicit blind spots.
- Preserve developer usefulness over polish. Do not invent architecture that is
  not supported by inspected files.
- Keep generated summaries separate from source docs unless the user explicitly
  asks to replace existing documentation.
- Do not overwrite an existing summary unless the user asks for replacement;
  otherwise create a versioned or more specific filename.
