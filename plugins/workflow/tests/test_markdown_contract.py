from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "scripts"
sys.path.insert(0, str(SHARED))

from markdown_contract import (  # noqa: E402
    missing_relative_links,
    placeholder_errors,
    render_link_errors,
    strip_fenced_blocks,
)
from summary_artifact import SummaryArtifactError, artifact_from_data, validate_summary_artifact  # noqa: E402


class MarkdownContractTests(unittest.TestCase):
    def test_placeholder_scan_ignores_fenced_blocks(self) -> None:
        text = "\n".join(
            [
                "Visible <replace-me>",
                "```",
                "Hidden <example-placeholder>",
                "```",
            ]
        )

        visible = strip_fenced_blocks(text)

        self.assertIn("Visible <replace-me>", visible)
        self.assertNotIn("Hidden <example-placeholder>", visible)
        self.assertEqual(
            placeholder_errors(visible),
            ["unresolved placeholders outside code fences: <replace-me>"],
        )

    def test_relative_link_scan_ignores_external_and_reports_missing_local_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "exists.md").write_text("# Exists\n", encoding="utf-8")
            (root / "index.md").write_text(
                "\n".join(
                    [
                        "[ok](exists.md)",
                        "[anchor](#local)",
                        "[external](https://example.com)",
                        "[missing](missing.md)",
                    ]
                ),
                encoding="utf-8",
            )

            issues = missing_relative_links(root)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line, 4)
        self.assertEqual(issues[0].target, "missing.md")

    def test_link_error_renderer_preserves_cli_message_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file_path = root / "index.md"
            file_path.write_text("[missing](missing.md)\n", encoding="utf-8")
            issues = missing_relative_links(root)

            stderr = io.StringIO()
            status = render_link_errors(issues, stderr=stderr)

        self.assertEqual(status, 1)
        self.assertIn(":1: missing missing.md", stderr.getvalue())

    def test_summary_artifact_validates_shape_before_rendering(self) -> None:
        data = {
            "title": "Demo",
            "sections": [
                {
                    "title": "Overview",
                    "summary": "A short summary.",
                    "paragraphs": ["One paragraph."],
                    "files": [{"path": "README.md"}],
                }
            ],
        }

        artifact = artifact_from_data(data)

        self.assertEqual(artifact.title, "Demo")
        self.assertEqual(artifact.sections[0]["title"], "Overview")
        self.assertEqual(validate_summary_artifact({"title": "Demo"}), ["summary JSON must include a non-empty sections list"])
        with self.assertRaises(SummaryArtifactError):
            artifact_from_data({"sections": [{"title": ["not", "text"]}]})


if __name__ == "__main__":
    unittest.main()
