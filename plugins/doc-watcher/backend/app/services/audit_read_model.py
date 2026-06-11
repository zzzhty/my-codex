from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from app.config import settings

CONFIG_HASH_KEYS = (
    "path",
    "docs",
    "source_of_truth",
    "watch_terms",
    "recent_limit",
    "since_ref",
    "commit_threshold",
)


class AuditReadError(RuntimeError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class AuditReadModel:
    def __init__(self, config_path: str | None = None, state_dir: str | None = None):
        self.plugin_root = Path(__file__).resolve().parents[3]
        self.config_path = self._resolve_config_path(config_path)
        self.state_dir = self._resolve_state_dir(state_dir)
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
            "repos": self.repo_statuses(config=config, state=state),
            "last_run": reports[0] if reports else None,
        }

    def repo_list(self) -> dict[str, Any]:
        config = self.load_config()
        state, _state_exists = self.load_state()
        repos = self.repo_statuses(config=config, state=state)
        return {"repos": repos, "total": len(repos)}

    def repo_detail(self, name: str) -> dict[str, Any]:
        config = self.load_config()
        state, _state_exists = self.load_state()
        for repo in self.repo_statuses(config=config, state=state):
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
        metadata = self._report_metadata(path)
        metadata["content"] = self._read_text(path)
        return metadata

    def last_run(self) -> dict[str, Any]:
        reports = self.list_reports()
        return {
            "last_run": reports[0] if reports else None,
            "reports_dir": str(self.reports_dir),
            "reports_dir_exists": self.reports_dir.exists(),
        }

    def load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            raise AuditReadError(
                f"config file does not exist: {self.config_path}",
                status_code=404,
            )
        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AuditReadError(
                f"invalid JSON config {self.config_path}: "
                f"line {exc.lineno}, column {exc.colno}"
            ) from exc
        if not isinstance(data, dict) or not isinstance(data.get("repos"), list):
            raise AuditReadError(
                f"config {self.config_path} must contain a top-level repos array"
            )

        config_dir = self.config_path.parent.resolve()
        resolved_repos: list[dict[str, Any]] = []
        for item in data["repos"]:
            if not isinstance(item, dict):
                raise AuditReadError(
                    f"config {self.config_path} repos entries must be objects"
                )
            repo = dict(item)
            raw_path = repo.get("path")
            if isinstance(raw_path, str):
                repo_path = self._expand_path(raw_path)
                if not repo_path.is_absolute():
                    repo_path = (config_dir / repo_path).resolve()
                repo["path"] = str(repo_path)
            resolved_repos.append(repo)
        data["repos"] = resolved_repos
        return data

    def load_state(self) -> tuple[dict[str, Any], bool]:
        if not self.state_path.exists():
            return {"repos": {}}, False
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AuditReadError(
                f"invalid state JSON {self.state_path}: "
                f"line {exc.lineno}, column {exc.colno}"
            ) from exc
        if not isinstance(data, dict):
            raise AuditReadError(f"state file must contain an object: {self.state_path}")
        repos = data.setdefault("repos", {})
        if not isinstance(repos, dict):
            raise AuditReadError(f"state repos must contain an object: {self.state_path}")
        return data, True

    def repo_statuses(
        self,
        *,
        config: dict[str, Any],
        state: dict[str, Any],
    ) -> list[dict[str, Any]]:
        statuses = []
        for repo_config in config["repos"]:
            statuses.append(self._repo_status(repo_config, state))
        return statuses

    def list_reports(self) -> list[dict[str, Any]]:
        if not self.reports_dir.exists():
            return []
        reports = [
            self._report_metadata(path)
            for path in self.reports_dir.glob("*.md")
            if path.is_file()
        ]
        return sorted(reports, key=lambda item: item["modified_at"], reverse=True)

    def _repo_status(
        self,
        repo_config: dict[str, Any],
        state: dict[str, Any],
    ) -> dict[str, Any]:
        name = str(repo_config.get("name") or Path(str(repo_config.get("path", ""))).name)
        raw_path = repo_config.get("path")
        repo_state = self._repo_state(state, name)
        current_config_hash = self._repo_config_hash(repo_config)

        base: dict[str, Any] = {
            "name": name,
            "configured_path": str(raw_path or ""),
            "docs": list(repo_config.get("docs") or []),
            "source_of_truth": list(repo_config.get("source_of_truth") or []),
            "watch_terms": list(repo_config.get("watch_terms") or []),
            "recent_limit": int(repo_config.get("recent_limit") or 5),
            "commit_threshold": int(repo_config.get("commit_threshold") or 0),
            "state": repo_state,
            "findings": self._finding_records(repo_state),
            "config_hash": current_config_hash,
            "last_config_hash": repo_state.get("config_hash"),
        }
        if not raw_path:
            return {
                **base,
                "status": "error",
                "error": f"repo {name} is missing required path",
            }

        try:
            repo = self._require_git_repo(self._expand_path(str(raw_path)))
            head = self._run_git(repo, ["rev-parse", "HEAD"])
            last = repo_state.get("last_audited_revision")
            config_changed = repo_state.get("config_hash") != current_config_hash
            count = self._count_since(repo, last if isinstance(last, str) else None)
            threshold = int(repo_config.get("commit_threshold") or 0)
            due = threshold <= 0 or count >= threshold or not last or config_changed
            return {
                **base,
                "status": "ok",
                "path": str(repo),
                "head": head,
                "last_audited_revision": last,
                "config_changed": config_changed,
                "commits_since_audit": count,
                "due": due,
            }
        except AuditReadError as exc:
            return {
                **base,
                "status": "error",
                "error": str(exc),
                "due": True,
            }

    def _report_metadata(self, path: Path) -> dict[str, Any]:
        text = self._read_text(path)
        lines = text.splitlines()
        title = next((line.removeprefix("# ").strip() for line in lines if line.startswith("# ")), path.name)
        stat = path.stat()
        parsed = self._parse_report_lines(lines[:200])
        return {
            "id": path.name,
            "path": str(path),
            "title": title,
            "modified_at": dt.datetime.fromtimestamp(stat.st_mtime)
            .astimezone()
            .isoformat(timespec="seconds"),
            "size_bytes": stat.st_size,
            **parsed,
        }

    def _parse_report_lines(self, lines: list[str]) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "generated_at": None,
            "config_path": None,
            "audited_repos": None,
            "skipped_repos": None,
            "failed_repos": None,
            "repo_sections": [],
        }
        for line in lines:
            if line.startswith("- Generated:"):
                metadata["generated_at"] = line.split(":", 1)[1].strip()
            elif line.startswith("- Config:"):
                metadata["config_path"] = line.split(":", 1)[1].strip().strip("`")
            elif line.startswith("- Audited repos:"):
                metadata["audited_repos"] = self._parse_int_suffix(line)
            elif line.startswith("- Skipped repos:"):
                metadata["skipped_repos"] = self._parse_int_suffix(line)
            elif line.startswith("- Failed repos:"):
                metadata["failed_repos"] = self._parse_int_suffix(line)
            elif line.startswith("## Repo:"):
                metadata["repo_sections"].append(line.split(":", 1)[1].strip())
        return metadata

    def _safe_report_path(self, report_id: str) -> Path:
        if "/" in report_id or "\\" in report_id:
            raise AuditReadError(f"invalid report id: {report_id}", status_code=400)
        path = (self.reports_dir / report_id).resolve()
        reports_dir = self.reports_dir.resolve()
        try:
            path.relative_to(reports_dir)
        except ValueError as exc:
            raise AuditReadError(f"invalid report id: {report_id}", status_code=400) from exc
        return path

    def _resolve_config_path(self, raw: str | None) -> Path:
        configured = raw or settings.docwatcher_config_path
        if configured:
            path = self._expand_path(configured)
            if not path.is_absolute():
                path = (self.plugin_root / path).resolve()
            return path

        private_config = self.plugin_root / "config" / "repos.json"
        if private_config.exists():
            return private_config
        return self.plugin_root / "config" / "repos.example.json"

    def _resolve_state_dir(self, raw: str | None) -> Path:
        configured = raw or settings.docwatcher_state_dir
        if configured:
            return self._expand_path(configured)
        codex_home = self._expand_path(os.environ.get("CODEX_HOME", "~/.codex"))
        return codex_home / "doc-watcher"

    def _expand_path(self, raw: str | Path) -> Path:
        return Path(os.path.expandvars(str(raw))).expanduser()

    def _repo_state(self, state: dict[str, Any], name: str) -> dict[str, Any]:
        repos = state.get("repos", {})
        if not isinstance(repos, dict):
            return {}
        repo_state = repos.get(name, {})
        return repo_state if isinstance(repo_state, dict) else {}

    def _finding_records(self, repo_state: dict[str, Any]) -> list[dict[str, str]]:
        findings = repo_state.get("findings")
        if not isinstance(findings, list):
            return []
        records: list[dict[str, str]] = []
        for item in findings:
            if not isinstance(item, dict):
                continue
            records.append(
                {
                    "fingerprint": str(item.get("fingerprint") or ""),
                    "severity": str(item.get("severity") or "Unknown"),
                    "title": str(item.get("title") or "Untitled finding"),
                    "evidence": str(item.get("evidence") or ""),
                }
            )
        return records

    def _repo_config_hash(self, repo_config: dict[str, Any]) -> str:
        payload = {
            key: repo_config.get(key)
            for key in CONFIG_HASH_KEYS
            if key in repo_config
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def _require_git_repo(self, repo: Path) -> Path:
        if not repo.exists():
            raise AuditReadError(f"repo path does not exist: {repo}")
        if not repo.is_dir():
            raise AuditReadError(f"repo path is not a directory: {repo}")
        root = self._run_git(repo, ["rev-parse", "--show-toplevel"])
        return Path(root).resolve()

    def _run_git(
        self,
        repo: Path,
        args: list[str],
        *,
        allow_failure: bool = False,
    ) -> str:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            message = (
                f"git command failed in {repo}: git {' '.join(args)}; "
                f"exit={proc.returncode}; stderr={proc.stderr.strip()}"
            )
            if allow_failure:
                return ""
            raise AuditReadError(message)
        return proc.stdout.strip()

    def _count_since(self, repo: Path, last_revision: str | None) -> int:
        if not last_revision:
            output = self._run_git(repo, ["rev-list", "--count", "HEAD"])
            return int(output or "0")
        output = self._run_git(
            repo,
            ["rev-list", "--count", f"{last_revision}..HEAD"],
            allow_failure=True,
        )
        if output.strip().isdigit():
            return int(output)
        total = self._run_git(repo, ["rev-list", "--count", "HEAD"])
        return int(total or "0")

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise AuditReadError(f"failed to read {path}: {exc}") from exc

    def _parse_int_suffix(self, line: str) -> int | None:
        match = re.search(r":\s*(\d+)\s*$", line)
        return int(match.group(1)) if match else None
