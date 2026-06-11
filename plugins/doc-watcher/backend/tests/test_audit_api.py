import json
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.audit_runner import AuditCommandRunner


def run(command: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout.strip()


def init_repo(path: Path) -> str:
    path.mkdir()
    run(["git", "init"], path)
    (path / "README.md").write_text("# Sample\n", encoding="utf-8")
    run(["git", "add", "README.md"], path)
    run(
        [
            "git",
            "-c",
            "user.name=DocWatcher Test",
            "-c",
            "user.email=docwatcher@example.test",
            "commit",
            "-m",
            "Initial docs",
        ],
        path,
    )
    return run(["git", "rev-parse", "HEAD"], path)


def write_config(path: Path, repo: Path, threshold: int = 2) -> Path:
    config = {
        "repos": [
            {
                "name": "sample",
                "path": str(repo),
                "docs": ["README.md"],
                "source_of_truth": ["README.md"],
                "watch_terms": ["old-term"],
                "commit_threshold": threshold,
            }
        ]
    }
    config_path = path / "repos.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


def test_audit_status_reads_config_state_and_git_status(tmp_path):
    repo = tmp_path / "repo"
    init_repo(repo)
    config_path = write_config(tmp_path, repo)
    state_dir = tmp_path / "state"

    client = TestClient(app)
    response = client.get(
        "/api/v1/audit/status",
        params={"config_path": str(config_path), "state_dir": str(state_dir)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["config"]["repo_count"] == 1
    assert payload["state"]["exists"] is False
    assert payload["reports"]["exists"] is False
    assert payload["reports"]["latest"] is None
    repo_status = payload["repos"][0]
    assert repo_status["name"] == "sample"
    assert repo_status["status"] == "ok"
    assert repo_status["due"] is True
    assert repo_status["commits_since_audit"] == 1
    assert repo_status["findings"] == []


def test_audit_repo_detail_and_reports_read_state_records(tmp_path):
    repo = tmp_path / "repo"
    head = init_repo(repo)
    config_path = write_config(tmp_path, repo)
    state_dir = tmp_path / "state"
    reports_dir = state_dir / "reports"
    reports_dir.mkdir(parents=True)
    (state_dir / "repo-state.json").write_text(
        json.dumps(
            {
                "repos": {
                    "sample": {
                        "path": str(repo),
                        "last_audited_revision": head,
                        "config_hash": "older-hash",
                        "findings": [
                            {
                                "fingerprint": "abc123",
                                "severity": "Medium",
                                "title": "Stale term",
                                "evidence": "README.md mentions old-term",
                            }
                        ],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    report = reports_dir / "20260610T120000Z-all-audit-report.md"
    report.write_text(
        "\n".join(
            [
                "# DocWatcher Audit Report",
                "",
                "- Generated: 2026-06-10T12:00:00+08:00",
                f"- Config: `{config_path}`",
                "- Audited repos: 1",
                "- Skipped repos: 0",
                "- Failed repos: 0",
                "",
                "## Repo: sample",
                "",
                "Sample report body.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    client = TestClient(app)
    params = {"config_path": str(config_path), "state_dir": str(state_dir)}

    repo_response = client.get("/api/v1/audit/repos/sample", params=params)
    assert repo_response.status_code == 200
    repo_payload = repo_response.json()
    assert repo_payload["findings"][0]["fingerprint"] == "abc123"
    assert repo_payload["config_changed"] is True

    reports_response = client.get("/api/v1/audit/reports", params=params)
    assert reports_response.status_code == 200
    reports_payload = reports_response.json()
    assert reports_payload["total"] == 1
    assert reports_payload["reports"][0]["id"] == report.name
    assert reports_payload["reports"][0]["audited_repos"] == 1

    report_response = client.get(f"/api/v1/audit/reports/{report.name}", params=params)
    assert report_response.status_code == 200
    report_payload = report_response.json()
    assert report_payload["title"] == "DocWatcher Audit Report"
    assert report_payload["repo_sections"] == ["sample"]
    assert "Sample report body." in report_payload["content"]

    last_run_response = client.get("/api/v1/audit/last-run", params=params)
    assert last_run_response.status_code == 200
    assert last_run_response.json()["last_run"]["id"] == report.name


def test_audit_status_reports_malformed_state_as_error(tmp_path):
    repo = tmp_path / "repo"
    init_repo(repo)
    config_path = write_config(tmp_path, repo)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    (state_dir / "repo-state.json").write_text("{", encoding="utf-8")

    client = TestClient(app)
    response = client.get(
        "/api/v1/audit/status",
        params={"config_path": str(config_path), "state_dir": str(state_dir)},
    )

    assert response.status_code == 400
    assert "invalid state JSON" in response.json()["detail"]


def test_commit_counter_run_records_command_result(tmp_path):
    repo = tmp_path / "repo"
    init_repo(repo)
    config_path = write_config(tmp_path, repo)
    state_dir = tmp_path / "state"

    client = TestClient(app)
    response = client.post(
        "/api/v1/audit/runs/commit-counter",
        json={"config_path": str(config_path), "state_dir": str(state_dir)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["kind"] == "commit_counter"
    assert payload["success"] is True
    assert payload["exit_code"] == 0
    assert "commit_counter.py" in payload["command"][1]
    assert "# DocWatcher Commit Counter" in payload["stdout"]
    assert payload["failure_breakpoint"] is None
    run_record = state_dir / "runs" / f"{payload['id']}.json"
    assert run_record.exists()

    runs_response = client.get(
        "/api/v1/audit/runs",
        params={"config_path": str(config_path), "state_dir": str(state_dir)},
    )
    assert runs_response.status_code == 200
    assert runs_response.json()["total"] == 1

    run_response = client.get(
        f"/api/v1/audit/runs/{payload['id']}",
        params={"config_path": str(config_path), "state_dir": str(state_dir)},
    )
    assert run_response.status_code == 200
    assert run_response.json()["id"] == payload["id"]


def test_generate_report_run_can_mark_audited_after_success(tmp_path):
    repo = tmp_path / "repo"
    head = init_repo(repo)
    config_path = write_config(tmp_path, repo)
    state_dir = tmp_path / "state"

    client = TestClient(app)
    response = client.post(
        "/api/v1/audit/runs/generate-report",
        json={
            "config_path": str(config_path),
            "state_dir": str(state_dir),
            "mode": "commit-dependent",
            "mark_audited": True,
            "digest": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["kind"] == "generate_report"
    assert payload["success"] is True
    assert payload["report_path"]
    assert payload["updated_state_path"] == str(state_dir / "repo-state.json")
    assert "--mark-audited" in payload["command"]
    state = json.loads((state_dir / "repo-state.json").read_text(encoding="utf-8"))
    assert state["repos"]["sample"]["last_audited_revision"] == head
    assert "state not updated" not in payload["stdout"]


def test_generate_report_run_surfaces_failures_without_advancing_state(tmp_path):
    config_path = tmp_path / "repos.json"
    config_path.write_text(
        json.dumps(
            {
                "repos": [
                    {
                        "name": "missing",
                        "path": str(tmp_path / "missing"),
                        "commit_threshold": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    state_dir = tmp_path / "state"

    client = TestClient(app)
    response = client.post(
        "/api/v1/audit/runs/generate-report",
        json={
            "config_path": str(config_path),
            "state_dir": str(state_dir),
            "mode": "commit-dependent",
            "mark_audited": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is False
    assert payload["exit_code"] == 1
    assert payload["report_path"]
    assert "exit=1" in payload["failure_breakpoint"]
    assert "state not updated because at least one audit failed" in payload["stdout"]
    assert not (state_dir / "repo-state.json").exists()


def test_repo_audit_run_uses_configured_repo_args(tmp_path):
    repo = tmp_path / "repo"
    init_repo(repo)
    config_path = write_config(tmp_path, repo)
    state_dir = tmp_path / "state"

    client = TestClient(app)
    response = client.post(
        "/api/v1/audit/repos/sample/runs/audit",
        json={"config_path": str(config_path), "state_dir": str(state_dir)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["kind"] == "audit_repo"
    assert payload["success"] is True
    assert payload["audit_path"]
    assert "--docs" in payload["command"]
    assert "--source-of-truth" in payload["command"]
    assert "--watch-term" in payload["command"]
    assert not (repo / "repo-state.json").exists()


def test_command_runs_reject_conflicting_config_state_run(tmp_path):
    repo = tmp_path / "repo"
    init_repo(repo)
    config_path = write_config(tmp_path, repo)
    state_dir = tmp_path / "state"
    runner = AuditCommandRunner(config_path=str(config_path), state_dir=str(state_dir))
    key = runner._lock_key("config")
    lock = runner._lock_for(key)
    assert lock.acquire(blocking=False)
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/audit/runs/commit-counter",
            json={"config_path": str(config_path), "state_dir": str(state_dir)},
        )
    finally:
        lock.release()

    assert response.status_code == 409
    assert "already running" in response.json()["detail"]
