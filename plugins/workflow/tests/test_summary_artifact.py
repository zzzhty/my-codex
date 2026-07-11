from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "scripts"
RENDERER = ROOT / "skills" / "summary-in-html" / "scripts" / "render_summary_html.py"
sys.path.insert(0, str(SHARED))

from summary_artifact import SummaryArtifactError, artifact_from_data, validate_summary_artifact  # noqa: E402


def minimal_artifact() -> dict[str, object]:
    return {"title": "Demo", "sections": [{"title": "Overview"}]}


class SummaryArtifactTests(unittest.TestCase):
    def test_record_lists_reject_non_object_members(self) -> None:
        cases = [
            ("files", "sections[1].files[1] must be an object"),
            ("code", "sections[1].code[1] must be an object"),
            ("evidence", "root.evidence[1] must be an object"),
            ("assets", "root.assets[1] must be an object"),
        ]
        for field, expected in cases:
            with self.subTest(field=field):
                data = minimal_artifact()
                if field in {"files", "code"}:
                    data["sections"][0][field] = ["invalid"]  # type: ignore[index]
                else:
                    data[field] = ["invalid"]

                self.assertEqual(validate_summary_artifact(data), [expected])
                with self.assertRaises(SummaryArtifactError) as raised:
                    artifact_from_data(data)
                self.assertEqual(str(raised.exception), expected)

    def test_root_and_section_shape_errors_remain_deterministic(self) -> None:
        self.assertEqual(
            validate_summary_artifact({"title": "Demo"}),
            ["summary JSON must include a non-empty sections list"],
        )
        self.assertEqual(
            validate_summary_artifact({"sections": [{"title": ["not", "text"]}]}),
            ["sections[1].title must be a string"],
        )

    def test_nested_errors_are_aggregated_in_schema_order(self) -> None:
        data = {
            "sections": [
                {
                    "paragraphs": ["valid", 2],
                    "bullets": [{}],
                    "files": [{}, {"path": "README.md", "note": 3}],
                    "code": [{}, {"text": "print('ok')", "language": 4}],
                }
            ],
            "evidence": [{}, {"path": "report.json", "label": 5}],
            "assets": [{}],
            "blind_spots": [False],
        }

        self.assertEqual(
            validate_summary_artifact(data),
            [
                "sections[1].paragraphs[2] must be a string",
                "sections[1].bullets[1] must be a string",
                "sections[1].files[1].path must be a non-empty string",
                "sections[1].files[2].note must be a string",
                "sections[1].code[1].text must be a string",
                "sections[1].code[2].language must be a string",
                "root.evidence[1].path must be a non-empty string",
                "root.evidence[2].label must be a string",
                "root.assets[1].path must be a non-empty string",
                "root.assets[1].alt must be a non-empty string",
                "root.assets[1].caption must be a non-empty string",
                "root.blind_spots[1] must be a string",
            ],
        )

    def test_visual_fields_must_be_present_and_non_empty(self) -> None:
        data = minimal_artifact()
        data["assets"] = [{"path": " ", "alt": "", "caption": None}]

        self.assertEqual(
            validate_summary_artifact(data),
            [
                "root.assets[1].path must be a non-empty string",
                "root.assets[1].alt must be a non-empty string",
                "root.assets[1].caption must be a non-empty string",
            ],
        )

    def test_documented_nested_artifact_renders_compatibly(self) -> None:
        data = {
            "title": "Workflow & Runtime",
            "evidence": [{"label": "Inventory", "path": "inputs.json"}],
            "assets": [
                {
                    "path": "assets/architecture.png",
                    "alt": "Architecture overview",
                    "caption": "Runtime architecture",
                }
            ],
            "sections": [
                {
                    "title": "Purpose",
                    "summary": "What this scope owns.",
                    "paragraphs": ["One paragraph."],
                    "bullets": ["Developer-facing point"],
                    "files": [{"path": "README.md", "note": "Entry point"}],
                    "code": [{"language": "python", "text": "print('ok')"}],
                }
            ],
            "blind_spots": ["Tests were not run."],
        }

        artifact = artifact_from_data(data)
        self.assertEqual(artifact.title, "Workflow & Runtime")

        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "summary.json"
            output_path = Path(tmp) / "summary.html"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(RENDERER), "--input", str(input_path), "--out", str(output_path)],
                capture_output=True,
                check=False,
                text=True,
            )
            html = output_path.read_text(encoding="utf-8") if output_path.exists() else ""

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Workflow &amp; Runtime", html)
        self.assertIn('<img src="assets/architecture.png" alt="Architecture overview">', html)
        self.assertIn("Runtime architecture", html)
        self.assertIn("README.md", html)
        self.assertIn("print(&#x27;ok&#x27;)", html)

    def test_renderer_reports_contract_error_without_traceback(self) -> None:
        data = minimal_artifact()
        data["sections"][0]["files"] = ["README.md"]  # type: ignore[index]

        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "invalid.json"
            output_path = Path(tmp) / "summary.html"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(RENDERER), "--input", str(input_path), "--out", str(output_path)],
                capture_output=True,
                check=False,
                text=True,
            )
            output_exists = output_path.exists()

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stderr.strip(), "sections[1].files[1] must be an object")
        self.assertNotIn("Traceback", completed.stderr)
        self.assertFalse(output_exists)


if __name__ == "__main__":
    unittest.main()
