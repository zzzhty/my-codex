#!/usr/bin/env python3
"""Render a structured summary JSON file to standalone HTML."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SHARED = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SHARED))
DEFAULT_TEMPLATE = SCRIPT_DIR.parent / "templates" / "summary.html"

from summary_artifact import SummaryArtifactError, load_summary_artifact  # noqa: E402


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "section"


def paragraph(text: str) -> str:
    return f"<p>{esc(text)}</p>"


def render_list(items: list[Any]) -> str:
    if not items:
        return ""
    lis = "\n".join(f"<li>{esc(item)}</li>" for item in items)
    return f"<ul>\n{lis}\n</ul>"


def render_files(files: list[dict[str, Any]]) -> str:
    if not files:
        return ""
    rows: list[str] = []
    for item in files:
        path = esc(item.get("path", ""))
        note = item.get("note")
        note_html = f"<div class=\"muted\">{esc(note)}</div>" if note else ""
        rows.append(f"<li><code>{path}</code>{note_html}</li>")
    return "<h3>Referenced Files</h3>\n<ul class=\"file-list\">\n" + "\n".join(rows) + "\n</ul>"


def render_code_blocks(blocks: list[dict[str, Any]]) -> str:
    rendered: list[str] = []
    for block in blocks:
        language = esc(block.get("language", "text"))
        text = esc(block.get("text", ""))
        rendered.append(f"<pre><code data-language=\"{language}\">{text}</code></pre>")
    return "\n".join(rendered)


def render_sections(sections: list[dict[str, Any]]) -> tuple[str, str]:
    nav_items: list[str] = []
    section_items: list[str] = []
    used_ids: set[str] = set()
    for index, section in enumerate(sections, start=1):
        title = str(section.get("title") or f"Section {index}")
        base_id = slugify(title)
        section_id = base_id
        counter = 2
        while section_id in used_ids:
            section_id = f"{base_id}-{counter}"
            counter += 1
        used_ids.add(section_id)
        nav_items.append(f"<a href=\"#{section_id}\">{esc(title)}</a>")

        parts: list[str] = [f"<section id=\"{section_id}\">", f"<h2>{esc(title)}</h2>"]
        summary = section.get("summary")
        if summary:
            parts.append(paragraph(str(summary)))
        for item in section.get("paragraphs", []) or []:
            parts.append(paragraph(str(item)))
        parts.append(render_list(section.get("bullets", []) or []))
        parts.append(render_files(section.get("files", []) or []))
        parts.append(render_code_blocks(section.get("code", []) or []))
        parts.append("</section>")
        section_items.append("\n".join(part for part in parts if part))
    return "\n".join(nav_items), "\n".join(section_items)


def render_meta(data: dict[str, Any]) -> str:
    rows: list[str] = []
    for label, key in [
        ("Scope", "scope_label"),
        ("Source root", "source_root"),
        ("Generated", "generated_at"),
    ]:
        value = data.get(key)
        if value:
            rows.append(f"<div><strong>{label}:</strong> <code>{esc(value)}</code></div>")
    evidence = data.get("evidence", []) or []
    if evidence:
        chips = []
        for item in evidence:
            label = item.get("label", "Evidence")
            path = item.get("path", "")
            chips.append(f"<span class=\"pill\">{esc(label)}: {esc(path)}</span>")
        rows.append("<div>" + " ".join(chips) + "</div>")
    if not rows:
        return ""
    return "<div class=\"meta\">\n" + "\n".join(rows) + "\n</div>"


def render_visuals(assets: list[dict[str, Any]]) -> str:
    if not assets:
        return ""
    figures: list[str] = []
    for asset in assets:
        src = esc(asset.get("path", ""))
        alt = esc(asset.get("alt", ""))
        caption = esc(asset.get("caption", asset.get("alt", "")))
        figures.append(
            "<figure class=\"visual\">"
            f"<img src=\"{src}\" alt=\"{alt}\">"
            f"<figcaption>{caption}</figcaption>"
            "</figure>"
        )
    return "\n".join(figures)


def render_blind_spots(items: list[Any]) -> str:
    if not items:
        return ""
    return "<section id=\"blind-spots\">\n<h2>Blind Spots</h2>\n" + render_list(items) + "\n</section>"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Structured summary JSON file.")
    parser.add_argument("--out", required=True, type=Path, help="Output HTML file.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    args = parser.parse_args()

    try:
        artifact = load_summary_artifact(args.input)
    except SummaryArtifactError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    data = artifact.data
    artifact.ensure_generated_at()
    title = artifact.title
    nav, sections_html = render_sections(artifact.sections)
    subtitle = data.get("subtitle")
    subtitle_html = f"<p class=\"subtitle\">{esc(subtitle)}</p>" if subtitle else ""
    footer = "Generated by the summary-in-html workflow."

    try:
        template = args.template.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"failed to read template: {args.template}: {exc}", file=sys.stderr)
        return 1

    replacements = {
        "{{title}}": esc(title),
        "{{heading}}": esc(data.get("heading", title)),
        "{{subtitle}}": subtitle_html,
        "{{nav}}": nav,
        "{{meta}}": render_meta(data),
        "{{visuals}}": render_visuals(data.get("assets", []) or []),
        "{{sections}}": sections_html,
        "{{blind_spots}}": render_blind_spots(data.get("blind_spots", []) or []),
        "{{footer}}": esc(data.get("footer", footer)),
    }
    html_text = template
    for needle, value in replacements.items():
        html_text = html_text.replace(needle, value)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html_text, encoding="utf-8")
    print(f"wrote html: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
