#!/usr/bin/env python3
"""Typed helpers for summary-in-html JSON artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SummaryArtifactError(ValueError):
    pass


@dataclass(frozen=True)
class SummaryArtifact:
    data: dict[str, Any]
    sections: list[dict[str, Any]]
    title: str

    @property
    def heading(self) -> str:
        return str(self.data.get("heading") or self.title)

    def ensure_generated_at(self) -> None:
        self.data.setdefault("generated_at", datetime.now(timezone.utc).isoformat())


def require_string_field(mapping: dict[str, Any], key: str, *, context: str, errors: list[str]) -> None:
    value = mapping.get(key)
    if value is not None and not isinstance(value, str):
        errors.append(f"{context}.{key} must be a string")


def require_list_field(mapping: dict[str, Any], key: str, *, context: str, errors: list[str]) -> None:
    value = mapping.get(key)
    if value is not None and not isinstance(value, list):
        errors.append(f"{context}.{key} must be a list")


def validate_summary_artifact(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["summary JSON root must be an object"]

    errors: list[str] = []
    for key in ("title", "heading", "subtitle", "scope_label", "source_root", "generated_at", "footer"):
        require_string_field(data, key, context="root", errors=errors)

    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append("summary JSON must include a non-empty sections list")
    else:
        for index, section in enumerate(sections, start=1):
            section_context = f"sections[{index}]"
            if not isinstance(section, dict):
                errors.append(f"{section_context} must be an object")
                continue
            require_string_field(section, "title", context=section_context, errors=errors)
            require_string_field(section, "summary", context=section_context, errors=errors)
            for key in ("paragraphs", "bullets", "files", "code"):
                require_list_field(section, key, context=section_context, errors=errors)

    for key in ("evidence", "assets", "blind_spots"):
        require_list_field(data, key, context="root", errors=errors)
    return errors


def artifact_from_data(data: Any) -> SummaryArtifact:
    errors = validate_summary_artifact(data)
    if errors:
        raise SummaryArtifactError("; ".join(errors))
    assert isinstance(data, dict)
    sections = data["sections"]
    assert isinstance(sections, list)
    title = str(data.get("title") or "Developer Summary")
    return SummaryArtifact(data=data, sections=sections, title=title)


def load_summary_artifact(path: Path) -> SummaryArtifact:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SummaryArtifactError(f"failed to read summary JSON: {path}: {exc}") from exc
    return artifact_from_data(data)
