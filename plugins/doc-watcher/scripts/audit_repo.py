#!/usr/bin/env python3
"""Collect read-only documentation drift evidence for one local Git repo."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_STATE_DIR = Path.home() / ".codex" / "doc-watcher"
ENTRY_FILES = ("README.md", "AGENTS.md", "CONTEXT.md", "CHANGELOG.md", "TODO.md", "todo.md")
DOC_DIRS = ("docs", "wiki", ".codex")
DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt", ".yml", ".yaml", ".json", ".toml"}
CODE_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".sh",
    ".ps1",
    ".sql",
}
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
}
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class AuditFailure(RuntimeError):
    """Raised when a required audit step cannot be completed."""


def resolve_state_dir(raw: str | None = None) -> Path:
    return Path(raw or os.environ.get("DOC_WATCHER_STATE_DIR") or DEFAULT_STATE_DIR).expanduser()


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def safe_slug(value: str) -> str:
    slug = "".join(char if char.isalnum() or char in "-_" else "-" for char in value.lower())
    return re.sub(r"-+", "-", slug).strip("-") or "repo"


def run_git(repo: Path, args: list[str], *, allow_failure: bool = False) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        message = (
            f"git command failed in {repo}: git {' '.join(args)}\n"
            f"exit={proc.returncode}\n"
            f"stderr={proc.stderr.strip()}"
        )
        if allow_failure:
            return ""
        raise AuditFailure(message)
    return proc.stdout.strip()


def require_git_repo(repo: Path) -> Path:
    if not repo.exists():
        raise AuditFailure(f"repo path does not exist: {repo}")
    if not repo.is_dir():
        raise AuditFailure(f"repo path is not a directory: {repo}")
    root = run_git(repo, ["rev-parse", "--show-toplevel"])
    return Path(root).resolve()


def safe_repo_path(repo: Path, rel_path: str) -> Path:
    candidate = (repo / rel_path).resolve()
    try:
        candidate.relative_to(repo)
    except ValueError as exc:
        raise AuditFailure(f"configured path escapes repo: {rel_path}") from exc
    return candidate


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def is_doc_path(path: str | Path) -> bool:
    p = Path(path)
    return p.name in ENTRY_FILES or p.suffix.lower() in DOC_EXTENSIONS or any(part in DOC_DIRS for part in p.parts)


def is_code_path(path: str | Path) -> bool:
    p = Path(path)
    return p.suffix.lower() in CODE_EXTENSIONS or any(part in {"scripts", "src", "app", "backend", "frontend"} for part in p.parts)


def discover_doc_files(repo: Path, configured: list[str] | None) -> tuple[list[Path], list[str]]:
    missing: list[str] = []
    files: list[Path] = []

    if configured:
        candidates = configured
    else:
        candidates = [name for name in ENTRY_FILES if (repo / name).exists()]
        candidates.extend(name for name in DOC_DIRS if (repo / name).exists())

    for rel in candidates:
        path = safe_repo_path(repo, rel)
        if not path.exists():
            missing.append(rel)
            continue
        if path.is_file():
            files.append(path)
            continue
        for child in path.rglob("*"):
            if should_skip(child.relative_to(repo)):
                continue
            if child.is_file() and child.suffix.lower() in DOC_EXTENSIONS:
                files.append(child)

    unique = sorted(set(files), key=lambda item: item.relative_to(repo).as_posix())
    return unique, missing


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise AuditFailure(f"failed to read {path}: {exc}") from exc


def find_broken_links(repo: Path, doc_files: list[Path]) -> list[dict[str, Any]]:
    broken: list[dict[str, Any]] = []
    for file_path in doc_files:
        if file_path.suffix.lower() not in {".md", ".mdx"}:
            continue
        text = read_text(file_path)
        for match in LINK_PATTERN.finditer(text):
            target = match.group(1).strip()
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = target.split("#", 1)[0].strip()
            if not target:
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            target_path = (file_path.parent / target).resolve()
            try:
                target_path.relative_to(repo)
            except ValueError:
                continue
            exists = target_path.is_dir() if target.endswith("/") else target_path.exists()
            if not exists:
                line = text[: match.start()].count("\n") + 1
                broken.append(
                    {
                        "file": file_path.relative_to(repo).as_posix(),
                        "line": line,
                        "target": match.group(1),
                    }
                )
    return broken


def find_watch_terms(repo: Path, doc_files: list[Path], terms: list[str]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    if not terms:
        return hits
    for file_path in doc_files:
        text = read_text(file_path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            for term in terms:
                if term and term in line:
                    hits.append(
                        {
                            "file": file_path.relative_to(repo).as_posix(),
                            "line": line_no,
                            "term": term,
                        }
                    )
    return hits


def recent_commits(repo: Path, limit: int) -> list[str]:
    output = run_git(repo, ["log", "--oneline", "--no-decorate", f"-n{limit}"], allow_failure=True)
    return [line for line in output.splitlines() if line.strip()]


def changed_files(repo: Path, recent_limit: int, since_ref: str | None = None) -> tuple[list[str], str]:
    if since_ref:
        output = run_git(repo, ["diff", "--name-only", f"{since_ref}..HEAD"], allow_failure=True)
        return sorted(line for line in output.splitlines() if line.strip()), since_ref

    commits = run_git(repo, ["rev-list", f"--max-count={recent_limit + 1}", "HEAD"], allow_failure=True).splitlines()
    if len(commits) >= 2:
        base = commits[-1]
        output = run_git(repo, ["diff", "--name-only", f"{base}..HEAD"], allow_failure=True)
        return sorted(line for line in output.splitlines() if line.strip()), base
    if len(commits) == 1:
        output = run_git(repo, ["show", "--name-only", "--format=", commits[0]], allow_failure=True)
        return sorted(line for line in output.splitlines() if line.strip()), commits[0]
    return [], "none"


def source_of_truth_status(repo: Path, paths: list[str] | None) -> list[dict[str, Any]]:
    status: list[dict[str, Any]] = []
    for rel in paths or []:
        path = safe_repo_path(repo, rel)
        status.append(
            {
                "path": rel,
                "exists": path.exists(),
                "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
            }
        )
    return status


def build_findings(
    *,
    missing_paths: list[str],
    broken_links: list[dict[str, Any]],
    watch_hits: list[dict[str, Any]],
    changed: list[str],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for rel in missing_paths:
        findings.append(
            {
                "severity": "High",
                "title": "Configured documentation path is missing",
                "evidence": rel,
                "recommendation": "Remove the stale config entry or restore the documented path.",
            }
        )
    for item in broken_links:
        findings.append(
            {
                "severity": "High",
                "title": "Markdown link target does not resolve",
                "evidence": f"{item['file']}:{item['line']} -> {item['target']}",
                "recommendation": "Update the link or move the target into the documented location.",
            }
        )
    for item in watch_hits:
        findings.append(
            {
                "severity": "Medium",
                "title": "Configured watch term still appears in active docs",
                "evidence": f"{item['file']}:{item['line']} contains {item['term']}",
                "recommendation": "Confirm whether this is historical text or stale active terminology.",
            }
        )

    docs_changed = [path for path in changed if is_doc_path(path)]
    code_changed = [path for path in changed if is_code_path(path) and not is_doc_path(path)]
    if code_changed and not docs_changed:
        findings.append(
            {
                "severity": "Medium",
                "title": "Recent code or runtime changes have no matching doc changes",
                "evidence": ", ".join(code_changed[:12]) + (" ..." if len(code_changed) > 12 else ""),
                "recommendation": "Review whether active docs, commands, or architecture notes need alignment.",
            }
        )
    return findings


def audit_repository(
    *,
    repo: Path,
    name: str,
    docs: list[str] | None = None,
    source_of_truth: list[str] | None = None,
    watch_terms: list[str] | None = None,
    recent_limit: int = 5,
    since_ref: str | None = None,
) -> dict[str, Any]:
    root = require_git_repo(repo)
    head = run_git(root, ["rev-parse", "HEAD"])
    branch = run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"], allow_failure=True) or "unknown"
    doc_files, missing_paths = discover_doc_files(root, docs)
    broken = find_broken_links(root, doc_files)
    hits = find_watch_terms(root, doc_files, watch_terms or [])
    changed, diff_base = changed_files(root, recent_limit, since_ref=since_ref)
    findings = build_findings(missing_paths=missing_paths, broken_links=broken, watch_hits=hits, changed=changed)

    return {
        "name": name,
        "repo": str(root),
        "branch": branch,
        "head": head,
        "generated_at": now_local().isoformat(timespec="seconds"),
        "recent_limit": recent_limit,
        "diff_base": diff_base,
        "recent_commits": recent_commits(root, recent_limit),
        "changed_files": changed,
        "doc_files": [path.relative_to(root).as_posix() for path in doc_files],
        "source_of_truth": source_of_truth_status(root, source_of_truth),
        "broken_links": broken,
        "watch_hits": hits,
        "findings": findings,
    }


def render_report(result: dict[str, Any]) -> str:
    findings = result["findings"]
    changed = result["changed_files"]
    doc_changed = [path for path in changed if is_doc_path(path)]
    code_changed = [path for path in changed if is_code_path(path) and not is_doc_path(path)]

    lines = [
        f"# DocWatcher Audit: {result['name']}",
        "",
        f"- Generated: {result['generated_at']}",
        f"- Repo: `{result['repo']}`",
        f"- Branch: `{result['branch']}`",
        f"- Head: `{result['head']}`",
        f"- Diff base: `{result['diff_base']}`",
        "",
        "## Summary",
        "",
        f"- Documentation files scanned: {len(result['doc_files'])}",
        f"- Recent commits listed: {len(result['recent_commits'])}",
        f"- Changed files in audit window: {len(changed)}",
        f"- Changed doc files: {len(doc_changed)}",
        f"- Changed code/runtime files: {len(code_changed)}",
        f"- Broken links: {len(result['broken_links'])}",
        f"- Watch term hits: {len(result['watch_hits'])}",
        f"- Findings: {len(findings)}",
        "",
        "## Source Of Truth",
        "",
    ]

    source = result["source_of_truth"]
    if source:
        for item in source:
            status = "present" if item["exists"] else "missing"
            lines.append(f"- `{item['path']}`: {status} ({item['kind']})")
    else:
        lines.append("- No explicit source-of-truth paths configured.")

    lines.extend(["", "## Recent Commits", ""])
    if result["recent_commits"]:
        lines.extend(f"- {commit}" for commit in result["recent_commits"])
    else:
        lines.append("- No commits found or git log unavailable.")

    lines.extend(["", "## Changed Files", ""])
    if changed:
        lines.extend(f"- `{path}`" for path in changed[:80])
        if len(changed) > 80:
            lines.append(f"- ... {len(changed) - 80} more")
    else:
        lines.append("- No changed files detected in the audit window.")

    lines.extend(["", "## Deterministic Findings", ""])
    if findings:
        for severity in ("High", "Medium", "Low"):
            scoped = [item for item in findings if item["severity"] == severity]
            if not scoped:
                continue
            lines.extend([f"### {severity}", ""])
            for item in scoped:
                lines.append(f"- {item['title']}: {item['evidence']}")
                lines.append(f"  Recommendation: {item['recommendation']}")
            lines.append("")
    else:
        lines.append("- No deterministic findings. A semantic review may still find drift.")

    lines.extend(
        [
            "",
            "## Doc Alignment Focus",
            "",
            "- Confirm active entry points match the current workflow.",
            "- Separate current guidance from historical notes.",
            "- Check whether recent code/runtime changes require documentation updates.",
            "- Verify names, commands, paths, and validation gates use one current vocabulary.",
            "- Decide whether any finding should become a bounded implementation task.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def default_audit_path(state_dir: Path, name: str) -> Path:
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    return state_dir / "audits" / f"{timestamp}-{safe_slug(name)}-audit.md"


def write_report(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(report, encoding="utf-8")
    except OSError as exc:
        raise AuditFailure(f"failed to write audit report {path}: {exc}") from exc


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect read-only documentation drift evidence for one Git repo.")
    parser.add_argument("--repo", required=True, help="Local Git repository path.")
    parser.add_argument("--name", help="Display name. Defaults to repo directory name.")
    parser.add_argument("--docs", nargs="*", help="Docs or directories to scan, relative to repo.")
    parser.add_argument("--source-of-truth", nargs="*", help="Source-of-truth files or directories, relative to repo.")
    parser.add_argument("--watch-term", action="append", default=[], help="Term to flag when found in active docs.")
    parser.add_argument("--recent", type=int, default=5, help="Recent commit window for changed-file evidence.")
    parser.add_argument("--since-ref", help="Git ref to diff against HEAD.")
    parser.add_argument("--state-dir", help="Runtime state directory. Defaults to ~/.codex/doc-watcher.")
    parser.add_argument("--output", help="Audit report output path. Defaults to state audits/.")
    parser.add_argument("--print-report", action="store_true", help="Print the report to stdout.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo = Path(args.repo).expanduser()
    name = args.name or repo.name
    result = audit_repository(
        repo=repo,
        name=name,
        docs=args.docs,
        source_of_truth=args.source_of_truth,
        watch_terms=args.watch_term,
        recent_limit=args.recent,
        since_ref=args.since_ref,
    )
    report = render_report(result)
    output = Path(args.output).expanduser() if args.output else default_audit_path(resolve_state_dir(args.state_dir), name)
    write_report(output, report)
    print(f"audit: {output}")
    print(f"findings: {len(result['findings'])}")
    if args.print_report:
        print()
        print(report, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditFailure as exc:
        raise SystemExit(str(exc)) from exc
