from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit_runtime import repo_read_status  # noqa: E402
from commit_counter import load_state, mark_current, repo_status  # noqa: E402
from generate_report import finding_delta, finding_records  # noqa: E402


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


class DocWatcherIncrementalTests(unittest.TestCase):
    def test_config_hash_changes_force_commit_dependent_due(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            state_dir = root / "state"
            repo.mkdir()
            run(["git", "init"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)
            run(["git", "config", "user.name", "Test User"], repo)
            (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
            run(["git", "add", "README.md"], repo)
            run(["git", "commit", "-m", "init"], repo)

            config = {
                "name": "demo",
                "path": str(repo),
                "docs": ["README.md"],
                "source_of_truth": ["README.md"],
                "commit_threshold": 10,
            }
            state = load_state(state_dir)
            first = repo_status(config, state)
            mark_current(state_dir, state, [first])
            state = load_state(state_dir)
            unchanged = repo_status(config, state)
            changed = repo_status({**config, "watch_terms": ["old-name"]}, state)

        self.assertTrue(first["due"])
        self.assertFalse(unchanged["due"])
        self.assertTrue(changed["due"])
        self.assertTrue(changed["config_changed"])

    def test_read_model_status_uses_same_runtime_hash_and_due_logic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            state_dir = root / "state"
            repo.mkdir()
            run(["git", "init"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)
            run(["git", "config", "user.name", "Test User"], repo)
            (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
            run(["git", "add", "README.md"], repo)
            run(["git", "commit", "-m", "init"], repo)

            config = {
                "name": "demo",
                "path": str(repo),
                "docs": ["README.md"],
                "source_of_truth": ["README.md"],
                "commit_threshold": 10,
            }
            state = load_state(state_dir)
            cli_status = repo_status(config, state)
            read_status = repo_read_status(config, state)

        self.assertEqual(read_status["status"], "ok")
        self.assertEqual(read_status["config_hash"], cli_status["config_hash"])
        self.assertEqual(read_status["commits_since_audit"], cli_status["commits_since_audit"])
        self.assertEqual(read_status["due"], cli_status["due"])

    def test_finding_records_diff_new_resolved_and_still_open(self) -> None:
        previous_result = {
            "findings": [
                {"severity": "High", "title": "Missing doc", "evidence": "README.md"},
                {"severity": "Medium", "title": "Stale term", "evidence": "docs/old.md:1"},
            ]
        }
        current_result = {
            "findings": [
                {"severity": "Medium", "title": "Stale term", "evidence": "docs/old.md:1"},
                {"severity": "High", "title": "Broken link", "evidence": "README.md:3 -> missing.md"},
            ]
        }

        delta = finding_delta(
            previous=finding_records(previous_result),
            current=finding_records(current_result),
        )

        self.assertEqual([item["title"] for item in delta["new"]], ["Broken link"])
        self.assertEqual([item["title"] for item in delta["resolved"]], ["Missing doc"])
        self.assertEqual([item["title"] for item in delta["still_open"]], ["Stale term"])


if __name__ == "__main__":
    unittest.main()
