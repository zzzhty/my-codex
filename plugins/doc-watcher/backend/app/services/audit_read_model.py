from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from app.config import settings

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from audit_repo import AuditFailure  # noqa: E402
from audit_runtime import (  # noqa: E402
    list_reports,
    load_config,
    load_state,
    read_text,
    report_metadata,
    repo_statuses,
    resolve_audit_state_dir,
    resolve_config_path,
    safe_child_path,
)


class AuditReadError(RuntimeError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class AuditReadModel:
    def __init__(self, config_path: str | None = None, state_dir: str | None = None):
        self.plugin_root = PLUGIN_ROOT
        self.config_path = resolve_config_path(
            plugin_root=self.plugin_root,
            raw=config_path,
            configured=settings.docwatcher_config_path,
        )
        self.state_dir = resolve_audit_state_dir(
            raw=state_dir,
            configured=settings.docwatcher_state_dir,
        )
        self.state_path = self.state_dir / "repo-state.json"
        self.reports_dir = self.state_dir / "reports"

    def overview(self) -> dict[str, Any]:
        config = self.load_config()
        state, state_exists = self.load_state()
        reports = self.list_reports()
        return {
            "config": {
                "path": str(self.config_path),
                "exists": self.config_path.exists(),
                "repo_count": len(config["repos"]),
            },
            "state": {
                "dir": str(self.state_dir),
                "path": str(self.state_path),
                "exists": state_exists,
                "repo_count": len(state.get("repos", {})),
            },
            "reports": {
                "dir": str(self.reports_dir),
                "exists": self.reports_dir.exists(),
                "count": len(reports),
                "latest": reports[0] if reports else None,
            },
            "repos": repo_statuses(config, state),
            "last_run": reports[0] if reports else None,
        }

    def repo_list(self) -> dict[str, Any]:
        config = self.load_config()
        state, _state_exists = self.load_state()
        repos = repo_statuses(config, state)
        return {"repos": repos, "total": len(repos)}

    def repo_detail(self, name: str) -> dict[str, Any]:
        config = self.load_config()
        state, _state_exists = self.load_state()
        for repo in repo_statuses(config, state):
            if repo["name"] == name:
                return repo
        raise AuditReadError(f"repo not found: {name}", status_code=404)

    def report_list(self) -> dict[str, Any]:
        reports = self.list_reports()
        return {
            "reports": reports,
            "total": len(reports),
            "reports_dir": str(self.reports_dir),
            "reports_dir_exists": self.reports_dir.exists(),
        }

    def report_detail(self, report_id: str) -> dict[str, Any]:
        path = self._safe_report_path(report_id)
        if not path.exists() or not path.is_file():
            raise AuditReadError(f"report not found: {report_id}", status_code=404)
        try:
            metadata = report_metadata(path)
            metadata["content"] = read_text(path)
            return metadata
        except AuditFailure as exc:
            raise AuditReadError(str(exc)) from exc

    def last_run(self) -> dict[str, Any]:
        reports = self.list_reports()
        return {
            "last_run": reports[0] if reports else None,
            "reports_dir": str(self.reports_dir),
            "reports_dir_exists": self.reports_dir.exists(),
        }

    def load_config(self) -> dict[str, Any]:
        try:
            return load_config(self.config_path)
        except AuditFailure as exc:
            status_code = 404 if str(exc).startswith("config file does not exist:") else 400
            raise AuditReadError(str(exc), status_code=status_code) from exc

    def load_state(self) -> tuple[dict[str, Any], bool]:
        exists = self.state_path.exists()
        try:
            return load_state(self.state_dir), exists
        except AuditFailure as exc:
            raise AuditReadError(str(exc)) from exc

    def list_reports(self) -> list[dict[str, Any]]:
        try:
            return list_reports(self.reports_dir)
        except AuditFailure as exc:
            raise AuditReadError(str(exc)) from exc

    def _safe_report_path(self, report_id: str) -> Path:
        try:
            return safe_child_path(self.reports_dir, report_id, label="report id")
        except AuditFailure as exc:
            raise AuditReadError(str(exc), status_code=400) from exc
