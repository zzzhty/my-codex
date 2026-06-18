#!/usr/bin/env python3
"""Refresh the repo-local mattpocock-skills plugin from upstream.

This script is intentionally hard-coded for the my-codex repository and the
https://github.com/mattpocock/skills upstream. It preserves the Codex plugin
wrapper while replacing the packaged skill directories from the upstream
Claude plugin manifest.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable


UPSTREAM_REPO = "https://github.com/mattpocock/skills.git"
TARGET_PLUGIN_NAME = "mattpocock-skills"
UPSTREAM_MANIFEST = ".claude-plugin/plugin.json"
CODEX_ONLY_VERSION_SUFFIX = re.compile(r"\+codex\..*$")
SEMVER_TAG = re.compile(r"^v(?P<version>\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)$")
UNSUPPORTED_FRONTMATTER = {"argument-hint", "disable-model-invocation"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def target_plugin_root() -> Path:
    return repo_root() / "plugins" / TARGET_PLUGIN_NAME


def default_sources_dir() -> Path:
    return Path.home() / ".codex" / "sources"


def run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    print("+ " + subprocess.list2cmdline(command) if os.name == "nt" else "+ " + " ".join(command), flush=True)
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        output = (result.stderr or result.stdout).strip()
        raise SystemExit(f"command failed with exit code {result.returncode}: {output}")
    return result.stdout.strip()


def ensure_inside(path: Path, parent: Path, *, label: str) -> Path:
    resolved = path.resolve()
    resolved_parent = parent.resolve()
    if resolved != resolved_parent and resolved_parent not in resolved.parents:
        raise SystemExit(f"{label} is outside expected parent: {resolved} not under {resolved_parent}")
    return resolved


def latest_semver_tag() -> str:
    output = run(["git", "ls-remote", "--tags", UPSTREAM_REPO])
    versions: list[tuple[tuple[int, int, int], str]] = []
    for line in output.splitlines():
        if line.endswith("^{}"):
            continue
        _, ref = line.split("\t", 1)
        tag = ref.rsplit("/", 1)[-1]
        match = SEMVER_TAG.match(tag)
        if not match:
            continue
        major, minor, patch = match.group("version").split(".", 2)
        patch_number = int(re.match(r"\d+", patch).group(0))  # type: ignore[union-attr]
        versions.append(((int(major), int(minor), patch_number), tag))
    if not versions:
        raise SystemExit(f"no semver tags found in {UPSTREAM_REPO}")
    return sorted(versions)[-1][1]


def clone_upstream(tag: str, sources_dir: Path) -> Path:
    sources_dir.mkdir(parents=True, exist_ok=True)
    base = sources_dir / f"mattpocock-skills-{tag.lstrip('v')}"
    destination = base
    if destination.exists():
        destination = sources_dir / f"{base.name}-{time.strftime('%Y%m%d%H%M%S', time.gmtime())}"
    run(["git", "clone", "--depth", "1", "--branch", tag, UPSTREAM_REPO, str(destination)])
    return destination


def upstream_commit(source_root: Path) -> str:
    return run(["git", "rev-parse", "HEAD"], cwd=source_root)


def version_from_tag(tag: str) -> str:
    match = SEMVER_TAG.match(tag)
    if not match:
        raise SystemExit(f"expected semver tag like v1.0.1, got {tag!r}")
    return match.group("version")


def load_upstream_skill_paths(source_root: Path) -> list[str]:
    manifest_path = source_root / UPSTREAM_MANIFEST
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"upstream manifest missing: {manifest_path}") from exc
    skills = manifest.get("skills")
    if not isinstance(skills, list) or not skills:
        raise SystemExit(f"upstream manifest has no skills list: {manifest_path}")
    paths: list[str] = []
    for item in skills:
        if not isinstance(item, str) or not item.startswith("./skills/"):
            raise SystemExit(f"unexpected upstream skill path in {manifest_path}: {item!r}")
        paths.append(item)
    return paths


def flattened_skill_names(skill_paths: Iterable[str]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for path in skill_paths:
        name = path.rstrip("/").rsplit("/", 1)[-1]
        if name in seen:
            raise SystemExit(f"duplicate flattened skill name: {name}")
        seen.add(name)
        names.append(name)
    return names


def strip_unsupported_frontmatter(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        return text

    filtered = [lines[0]]
    for line in lines[1:end_index]:
        key = line.split(":", 1)[0].strip()
        if key not in UNSUPPORTED_FRONTMATTER:
            filtered.append(line)
    filtered.extend(lines[end_index:])
    return "".join(filtered)


def clean_copied_skills(skills_root: Path) -> None:
    for skill_file in skills_root.glob("*/SKILL.md"):
        original = skill_file.read_text(encoding="utf-8")
        cleaned = strip_unsupported_frontmatter(original)
        if cleaned != original:
            skill_file.write_text(cleaned, encoding="utf-8")


def replace_skill_tree(source_root: Path, skill_paths: list[str], plugin_root: Path) -> list[str]:
    plugin_root = ensure_inside(plugin_root, repo_root(), label="target plugin root")
    skills_root = plugin_root / "skills"
    ensure_inside(skills_root, plugin_root, label="target skills root")

    names = flattened_skill_names(skill_paths)
    if skills_root.exists():
        shutil.rmtree(skills_root)
    skills_root.mkdir(parents=True)

    for upstream_path, name in zip(skill_paths, names):
        source_skill = source_root / upstream_path.removeprefix("./")
        if not (source_skill / "SKILL.md").is_file():
            raise SystemExit(f"upstream skill is missing SKILL.md: {source_skill}")
        shutil.copytree(source_skill, skills_root / name)

    clean_copied_skills(skills_root)
    return names


def update_plugin_manifest(plugin_root: Path, version: str, *, preserve_existing_cachebuster: bool = False) -> None:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current_version = str(manifest.get("version", ""))
    cachebuster = ""
    if preserve_existing_cachebuster:
        match = re.search(r"\+codex\..*$", current_version)
        if match:
            cachebuster = match.group(0)
    manifest.update(
        {
            "name": TARGET_PLUGIN_NAME,
            "version": CODEX_ONLY_VERSION_SUFFIX.sub("", version) + cachebuster,
            "description": "Codex-adapted local copy of Matt Pocock's agent skills.",
            "homepage": "https://github.com/mattpocock/skills",
            "repository": "https://github.com/mattpocock/skills",
            "license": "MIT",
            "keywords": ["skills", "engineering", "productivity", "codex"],
            "skills": "./skills/",
        }
    )
    manifest["author"] = {"name": "Matt Pocock"}
    manifest["interface"] = {
        "displayName": "Matt Pocock Skills",
        "shortDescription": "Use Matt Pocock's agent skills in Codex.",
        "longDescription": (
            f"Matt Pocock Skills packages a local Codex-adapted copy of mattpocock/skills {version}, "
            "including engineering, planning, triage, diagnosis, TDD, architecture, domain-modeling, "
            "teaching, and productivity workflows."
        ),
        "developerName": "Matt Pocock",
        "category": "Productivity",
        "capabilities": ["skills"],
        "defaultPrompt": ["Help me choose the right Matt Pocock skill."],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_readme(plugin_root: Path, tag: str, commit: str, skill_names: list[str]) -> None:
    skills = "\n".join(f"- `{name}`" for name in skill_names)
    text = f"""# Matt Pocock Skills

Skill-only Codex plugin for the local Codex-adapted copy of Matt Pocock's skills.

Upstream: https://github.com/mattpocock/skills

Adapted from: `{tag}` (`{commit}`)

## Skills

{skills}

## Compatibility Notes

This plugin flattens the upstream Claude plugin skill paths into Codex's `skills/<name>/` layout while preserving each published skill directory's contents.

Upstream 1.0.x made these breaking changes:

- `diagnose` was renamed to `diagnosing-bugs`.
- `write-a-skill` was replaced by `writing-great-skills`.
- `caveman` and `zoom-out` were removed upstream and are no longer packaged here.

This plugin is the source of truth for these third-party skills in this Codex setup. Do not maintain separate copies under `$CODEX_HOME/skills`.
"""
    (plugin_root / "README.md").write_text(text, encoding="utf-8")


def copy_license(source_root: Path, plugin_root: Path) -> None:
    shutil.copy2(source_root / "LICENSE", plugin_root / "LICENSE")


def run_cachebuster(plugin_root: Path) -> None:
    script = Path.home() / ".codex" / "skills" / ".system" / "plugin-creator" / "scripts" / "update_plugin_cachebuster.py"
    if not script.is_file():
        raise SystemExit(f"cachebuster helper missing: {script}")
    run([sys.executable, str(script), str(plugin_root)])


def validate(plugin_root: Path) -> None:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    validator = Path(
        os.environ.get(
            "PLUGIN_VALIDATOR",
            str(codex_home / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"),
        )
    )
    quick_validator = codex_home / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    if not validator.is_file():
        raise SystemExit(f"plugin validator missing: {validator}")
    if not quick_validator.is_file():
        raise SystemExit(f"skill validator missing: {quick_validator}")

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    run([sys.executable, str(validator), str(plugin_root)], env=env)
    for skill_dir in sorted((plugin_root / "skills").iterdir()):
        if skill_dir.is_dir():
            run([sys.executable, str(quick_validator), str(skill_dir)], env=env)
    run(["git", "diff", "--check", "--", str(plugin_root.relative_to(repo_root()))], cwd=repo_root())


def sync_from_source(source_root: Path, *, tag: str, commit: str, cachebuster: bool, run_validation: bool) -> list[str]:
    plugin_root = target_plugin_root()
    ensure_inside(plugin_root, repo_root(), label="target plugin root")
    skill_paths = load_upstream_skill_paths(source_root)
    skill_names = replace_skill_tree(source_root, skill_paths, plugin_root)
    copy_license(source_root, plugin_root)
    update_plugin_manifest(plugin_root, version_from_tag(tag), preserve_existing_cachebuster=not cachebuster)
    write_readme(plugin_root, tag, commit, skill_names)
    if cachebuster:
        run_cachebuster(plugin_root)
    if run_validation:
        validate(plugin_root)
    return skill_names


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh plugins/mattpocock-skills from mattpocock/skills.")
    parser.add_argument("--tag", default="latest", help="Upstream tag to install, or `latest` for the newest vX.Y.Z tag.")
    parser.add_argument("--source-dir", help="Use an existing upstream checkout instead of cloning.")
    parser.add_argument("--sources-dir", default=str(default_sources_dir()), help="Directory used for fresh clones.")
    parser.add_argument("--no-cachebuster", action="store_true", help="Do not update the Codex cachebuster suffix.")
    parser.add_argument("--skip-validation", action="store_true", help="Skip plugin and skill validation.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tag = latest_semver_tag() if args.tag == "latest" else args.tag
    source_root = Path(args.source_dir).resolve() if args.source_dir else clone_upstream(tag, Path(args.sources_dir))
    commit = upstream_commit(source_root)
    skills = sync_from_source(
        source_root,
        tag=tag,
        commit=commit,
        cachebuster=not args.no_cachebuster,
        run_validation=not args.skip_validation,
    )
    print(f"updated {TARGET_PLUGIN_NAME} from {tag} ({commit})")
    print("skills: " + ", ".join(skills))


if __name__ == "__main__":
    main()
