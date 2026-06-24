from __future__ import annotations

import datetime as dt
import json
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from app.services.audit_read_model import AuditReadError, AuditReadModel

from audit_repo import AuditFailure, audit_repository, default_audit_path, render_report, write_report  # noqa: E402
from commit_counter import run_commit_counter as execute_commit_counter  # noqa: E402
from generate_report import run_generate_report as execute_generate_report  # noqa: E402

MAX_STREAM_CHARS = 12000
_RUN_LOCKS: dict[str, threading.Lock] = {}
_RUN_LOCKS_GUARD = threading.Lock()


class AuditRunConflict(AuditReadError):
    def __init__(self, key: str):
        super().__init__(f"an audit command is already running for {key}", status_code=409)


class AuditCommandRunner:
    def __init__(self, config_path: str | None = None, state_dir: str | None = None):
        self.read_model = AuditReadModel(config_path=config_path, state_dir=state_dir)
        self.plugin_root = self.read_model.plugin_root
        self.scripts_dir = self.plugin_root / "scripts"
        self.config_path = self.read_model.config_path
        self.state_dir = self.read_model.state_dir
        self.runs_dir = self.state_dir / "runs"

    def list_runs(self) -> dict[str, Any]:
        if not self.runs_dir.exists():
            return {
                "runs": [],
                "total": 0,
                "runs_dir": str(self.runs_dir),
                "runs_dir_exists": False,
            }
        runs = []
        for path in self.runs_dir.glob("*.json"):
            try:
                runs.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
        runs.sort(key=lambda item: item.get("started_at") or "", reverse=True)
        return {
            "runs": runs,
            "total": len(runs),
            "runs_dir": str(self.runs_dir),
            "runs_dir_exists": True,
        }

    def get_run(self, run_id: str) -> dict[str, Any]:
        path = self._safe_run_path(run_id)
        if not path.exists() or not path.is_file():
            raise AuditReadError(f"run not found: {run_id}", status_code=404)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AuditReadError(
                f"invalid run JSON {path}: line {exc.lineno}, column {exc.colno}"
            ) from exc

    def run_commit_counter(self) -> dict[str, Any]:
        command = [
            sys.executable,
            str(self.scripts_dir / "commit_counter.py"),
            "--config",
            str(self.config_path),
            "--state-dir",
            str(self.state_dir),
        ]
        return self._run(
            "commit_counter",
            command,
            lock_target="config",
            execute=lambda: self._execute_commit_counter(),
        )

    def run_generate_report(
        self,
        *,
        mode: str = "all",
        mark_audited: bool = False,
        digest: bool = False,
        print_report: bool = False,
    ) -> dict[str, Any]:
        command = [
            sys.executable,
            str(self.scripts_dir / "generate_report.py"),
            "--config",
            str(self.config_path),
            "--state-dir",
            str(self.state_dir),
            "--mode",
            mode,
        ]
        if mark_audited:
            command.append("--mark-audited")
        if digest:
            command.append("--digest")
        if print_report:
            command.append("--print-report")
        return self._run(
            "generate_report",
            command,
            lock_target="config",
            execute=lambda: self._execute_generate_report(
                mode=mode,
                mark_audited=mark_audited,
                digest=digest,
                print_report=print_report,
            ),
        )

    def run_repo_audit(
        self,
        *,
        repo_name: str,
        print_report: bool = False,
    ) -> dict[str, Any]:
        repo_config = self._repo_config(repo_name)
        command = [
            sys.executable,
            str(self.scripts_dir / "audit_repo.py"),
            "--repo",
            str(repo_config["path"]),
            "--name",
            repo_name,
            "--state-dir",
            str(self.state_dir),
        ]
        docs = list(repo_config.get("docs") or [])
        if docs:
            command.append("--docs")
            command.extend(str(item) for item in docs)
        source_of_truth = list(repo_config.get("source_of_truth") or [])
        if source_of_truth:
            command.append("--source-of-truth")
            command.extend(str(item) for item in source_of_truth)
        for term in list(repo_config.get("watch_terms") or []):
            command.extend(["--watch-term", str(term)])
        if repo_config.get("recent_limit") is not None:
            command.extend(["--recent", str(int(repo_config["recent_limit"]))])
        if repo_config.get("since_ref"):
            command.extend(["--since-ref", str(repo_config["since_ref"])])
        if print_report:
            command.append("--print-report")
        return self._run(
            "audit_repo",
            command,
            lock_target=f"repo:{repo_name}",
            execute=lambda: self._execute_repo_audit(
                repo_name=repo_name,
                repo_config=repo_config,
                print_report=print_report,
            ),
        )

    def _run(
        self,
        kind: str,
        command: list[str],
        *,
        lock_target: str,
        execute: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        key = self._lock_key(lock_target)
        lock = self._lock_for(key)
        if not lock.acquire(blocking=False):
            raise AuditRunConflict(key)
        try:
            return self._execute(kind=kind, command=command, lock_key=key, execute=execute)
        finally:
            lock.release()

    def _execute(
        self,
        *,
        kind: str,
        command: list[str],
        lock_key: str,
        execute: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        run_id = f"{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}-{kind}-{uuid.uuid4().hex[:8]}"
        started_at = dt.datetime.now().astimezone()
        started = time.monotonic()
        try:
            result = execute()
        except AuditFailure as exc:
            result = {
                "exit_code": 1,
                "stdout": "",
                "stderr": str(exc),
            }
        completed_at = dt.datetime.now().astimezone()
        duration_ms = int((time.monotonic() - started) * 1000)
        raw_stdout = str(result.get("stdout") or "")
        raw_stderr = str(result.get("stderr") or "")
        exit_code = int(result.get("exit_code") or 0)
        stdout = _summarize_stream(raw_stdout)
        stderr = _summarize_stream(raw_stderr)
        record = {
            "id": run_id,
            "kind": kind,
            "lock_key": lock_key,
            "command": command,
            "cwd": str(self.plugin_root),
            "config_path": str(self.config_path),
            "state_dir": str(self.state_dir),
            "started_at": started_at.isoformat(timespec="seconds"),
            "completed_at": completed_at.isoformat(timespec="seconds"),
            "duration_ms": duration_ms,
            "exit_code": exit_code,
            "success": exit_code == 0,
            "stdout": stdout["text"],
            "stdout_truncated": stdout["truncated"],
            "stderr": stderr["text"],
            "stderr_truncated": stderr["truncated"],
            "report_path": str(result["report_path"]) if result.get("report_path") else _extract_prefixed_value(raw_stdout, "report:"),
            "audit_path": str(result["audit_path"]) if result.get("audit_path") else _extract_prefixed_value(raw_stdout, "audit:"),
            "updated_state_path": str(result["updated_state_path"])
            if result.get("updated_state_path")
            else _extract_prefixed_value(raw_stdout, "updated state:"),
            "failure_breakpoint": None,
        }
        if exit_code != 0:
            record["failure_breakpoint"] = _failure_breakpoint(
                command=command,
                exit_code=exit_code,
                stdout=raw_stdout,
                stderr=raw_stderr,
            )
        self._write_run(record)
        return record

    def _execute_commit_counter(self) -> dict[str, Any]:
        stdout, _statuses = execute_commit_counter(
            config_path=self.config_path,
            state_dir=self.state_dir,
        )
        return {
            "exit_code": 0,
            "stdout": stdout,
            "stderr": "",
        }

    def _execute_generate_report(
        self,
        *,
        mode: str,
        mark_audited: bool,
        digest: bool,
        print_report: bool,
    ) -> dict[str, Any]:
        return execute_generate_report(
            config_path=self.config_path,
            state_dir=self.state_dir,
            mode=mode,
            mark_audited=mark_audited,
            digest=digest,
            print_report=print_report,
        )

    def _execute_repo_audit(
        self,
        *,
        repo_name: str,
        repo_config: dict[str, Any],
        print_report: bool,
    ) -> dict[str, Any]:
        result = audit_repository(
            repo=Path(str(repo_config["path"])),
            name=repo_name,
            docs=list(repo_config.get("docs") or []),
            source_of_truth=list(repo_config.get("source_of_truth") or []),
            watch_terms=list(repo_config.get("watch_terms") or []),
            recent_limit=int(repo_config.get("recent_limit") or 5),
            since_ref=repo_config.get("since_ref"),
        )
        report = render_report(result)
        output = default_audit_path(self.state_dir, repo_name)
        write_report(output, report)
        stdout = f"audit: {output}\nfindings: {len(result['findings'])}\n"
        if print_report:
            stdout += f"\n{report}"
        return {
            "exit_code": 0,
            "stdout": stdout,
            "stderr": "",
            "audit_path": output,
        }

    def _write_run(self, record: dict[str, Any]) -> None:
        path = self._safe_run_path(record["id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError as exc:
            raise AuditReadError(f"failed to write audit run record {path}: {exc}") from exc

    def _safe_run_path(self, run_id: str) -> Path:
        if "/" in run_id or "\\" in run_id or not run_id:
            raise AuditReadError(f"invalid run id: {run_id}", status_code=400)
        path = (self.runs_dir / f"{run_id.removesuffix('.json')}.json").resolve()
        runs_dir = self.runs_dir.resolve()
        try:
            path.relative_to(runs_dir)
        except ValueError as exc:
            raise AuditReadError(f"invalid run id: {run_id}", status_code=400) from exc
        return path

    def _repo_config(self, repo_name: str) -> dict[str, Any]:
        config = self.read_model.load_config()
        for repo in config["repos"]:
            name = str(repo.get("name") or Path(str(repo.get("path", ""))).name)
            if name == repo_name:
                return repo
        raise AuditReadError(f"repo not found: {repo_name}", status_code=404)

    def _lock_key(self, target: str) -> str:
        return f"{self.config_path.resolve()}::{self.state_dir.resolve()}::{target}"

    def _lock_for(self, key: str) -> threading.Lock:
        with _RUN_LOCKS_GUARD:
            lock = _RUN_LOCKS.get(key)
            if lock is None:
                lock = threading.Lock()
                _RUN_LOCKS[key] = lock
            return lock


def _summarize_stream(value: str) -> dict[str, Any]:
    if len(value) <= MAX_STREAM_CHARS:
        return {"text": value, "truncated": False}
    head = value[: MAX_STREAM_CHARS // 2]
    tail = value[-MAX_STREAM_CHARS // 2 :]
    return {
        "text": f"{head}\n... truncated {len(value) - MAX_STREAM_CHARS} chars ...\n{tail}",
        "truncated": True,
    }


def _extract_prefixed_value(stdout: str, prefix: str) -> str | None:
    for line in stdout.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None


def _failure_breakpoint(
    *,
    command: list[str],
    exit_code: int,
    stdout: str,
    stderr: str,
) -> str:
    message = stderr.strip() or _last_non_empty_line(stdout) or "command failed without output"
    return f"command failed: {' '.join(command)}; exit={exit_code}; breakpoint={message}"


def _last_non_empty_line(value: str) -> str:
    for line in reversed(value.splitlines()):
        if line.strip():
            return line.strip()
    return ""
