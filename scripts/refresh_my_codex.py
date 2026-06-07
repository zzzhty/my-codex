#!/usr/bin/env python3
"""Refresh the local my-codex marketplace plugins and Skill Watcher hooks."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_FILE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
INSTALL_MANIFEST_FILE = REPO_ROOT / ".agents" / "plugins" / "install-manifest.json"
CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
DEFAULT_VENV = CODEX_HOME / "venvs" / "my-codex"


def expand_path(raw: str | Path) -> Path:
    return Path(os.path.expandvars(str(raw))).expanduser()


def venv_python(venv_path: Path) -> Path:
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def command_text(command: list[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def resolve_executable(raw: str) -> str:
    expanded = os.path.expandvars(os.path.expanduser(raw))
    if any(separator in expanded for separator in (os.sep, os.altsep) if separator):
        path = Path(expanded)
        if path.is_file():
            return str(path)
        raise SystemExit(f"executable does not exist: {path}")
    resolved = shutil.which(expanded)
    if resolved is None:
        raise SystemExit(f"executable not found on PATH: {raw}")
    return resolved


def marketplace_source_arg(raw: str) -> str:
    if "://" in raw or raw.startswith("git@"):
        return raw
    expanded = os.path.expandvars(os.path.expanduser(raw))
    path_like = (
        raw.startswith((".", "~", "/", "\\"))
        or (len(raw) >= 3 and raw[1] == ":" and raw[2] in {"\\", "/"})
        or Path(expanded).exists()
    )
    if path_like:
        return str(Path(expanded))
    return raw


def run(command: list[str], *, env: dict[str, str], dry_run: bool, check: bool = True) -> int:
    print("+ " + command_text(command), flush=True)
    if dry_run:
        return 0
    try:
        result = subprocess.run(command, check=check, env=env)
    except FileNotFoundError as exc:
        raise SystemExit(f"command not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"command failed with exit code {exc.returncode}: {command_text(command)}") from exc
    return result.returncode


def load_json_object(path: Path, *, label: str) -> dict:
    if not path.is_file():
        raise SystemExit(f"{label} file missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{label} file is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"{label} file must contain a JSON object: {path}")
    return data


def marketplace_plugin_names(marketplace_file: Path = MARKETPLACE_FILE) -> set[str]:
    data = load_json_object(marketplace_file, label="marketplace")
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        raise SystemExit(f"marketplace plugins field is not a list: {marketplace_file}")

    names: set[str] = set()
    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            raise SystemExit(f"marketplace plugin entry #{index + 1} is not an object: {marketplace_file}")
        name = plugin.get("name")
        if not isinstance(name, str) or not name.strip():
            raise SystemExit(f"marketplace plugin entry #{index + 1} has no valid name: {marketplace_file}")
        names.add(name)
    return names


def load_install_manifest(manifest_file: Path = INSTALL_MANIFEST_FILE) -> dict:
    data = load_json_object(manifest_file, label="install manifest")
    if data.get("schemaVersion") != 1:
        raise SystemExit(f"install manifest schemaVersion must be 1: {manifest_file}")

    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        raise SystemExit(f"install manifest plugins field is not a list: {manifest_file}")

    seen: set[str] = set()
    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            raise SystemExit(f"install manifest plugin entry #{index + 1} is not an object: {manifest_file}")
        name = plugin.get("name")
        if not isinstance(name, str) or not name.strip():
            raise SystemExit(f"install manifest plugin entry #{index + 1} has no valid name: {manifest_file}")
        if name in seen:
            raise SystemExit(f"install manifest contains duplicate plugin: {name}")
        seen.add(name)
        for flag in ("install", "check"):
            if not isinstance(plugin.get(flag), bool):
                raise SystemExit(f"install manifest plugin `{name}` has non-boolean `{flag}`")
    return data


def ensure_plugins_in_marketplace(plugin_names: list[str], *, marketplace_file: Path = MARKETPLACE_FILE) -> None:
    present = marketplace_plugin_names(marketplace_file)
    missing = sorted(set(plugin_names) - present)
    if missing:
        raise SystemExit(
            "install manifest selected plugins are missing from marketplace: " + ", ".join(missing)
        )


def default_plugin_names(
    action: str,
    *,
    marketplace_name: str,
    manifest_file: Path = INSTALL_MANIFEST_FILE,
    marketplace_file: Path = MARKETPLACE_FILE,
) -> list[str]:
    if action not in {"install", "check"}:
        raise ValueError(f"unsupported plugin selection action: {action}")

    manifest = load_install_manifest(manifest_file)
    configured_marketplace = manifest.get("marketplace")
    if configured_marketplace != marketplace_name:
        raise SystemExit(
            f"install manifest marketplace mismatch: expected {marketplace_name!r}, "
            f"found {configured_marketplace!r}"
        )

    plugins = manifest["plugins"]
    names = [plugin["name"] for plugin in plugins if plugin[action]]
    if not names:
        raise SystemExit(f"install manifest selects no plugins for `{action}`")
    ensure_plugins_in_marketplace(names, marketplace_file=marketplace_file)
    return names


def selected_plugins(
    raw_plugins: list[str] | None,
    marketplace_name: str,
    *,
    action: str,
    manifest_file: Path = INSTALL_MANIFEST_FILE,
    marketplace_file: Path = MARKETPLACE_FILE,
) -> list[str]:
    if raw_plugins is None:
        plugin_names = default_plugin_names(
            action,
            marketplace_name=marketplace_name,
            manifest_file=manifest_file,
            marketplace_file=marketplace_file,
        )
    else:
        plugin_names = raw_plugins

    selectors: list[str] = []
    names_to_validate: list[str] = []
    for raw_plugin in plugin_names:
        plugin = raw_plugin.strip()
        if not plugin:
            raise SystemExit("plugin selector cannot be empty")
        name, separator, selector_marketplace = plugin.partition("@")
        if not name:
            raise SystemExit(f"plugin selector has no plugin name: {plugin}")
        if separator:
            selectors.append(plugin)
            if selector_marketplace == marketplace_name:
                names_to_validate.append(name)
        else:
            selectors.append(f"{name}@{marketplace_name}")
            names_to_validate.append(name)

    if names_to_validate:
        ensure_plugins_in_marketplace(names_to_validate, marketplace_file=marketplace_file)
    return selectors


def tooling_python_from_args(args: argparse.Namespace, venv_path: Path) -> Path:
    override = args.python or os.environ.get("MY_CODEX_TOOLING_PYTHON") or os.environ.get("MY_CODEX_PYTHON")
    if override:
        return expand_path(override)
    return venv_python(venv_path)


def build_env(*, codex_home: Path, tooling_python: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    env["MY_CODEX_ROOT"] = str(REPO_ROOT)
    env["MY_CODEX_PYTHON"] = str(tooling_python)
    env["MY_CODEX_TOOLING_PYTHON"] = str(tooling_python)
    env.setdefault(
        "PLUGIN_VALIDATOR",
        str(codex_home / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"),
    )
    return env


def decode_text(raw: bytes | str | None) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    return raw.decode("utf-8", errors="replace")


def git_remote_source(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "config", "--get", "remote.origin.url"],
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    source = decode_text(result.stdout).strip()
    return source or None


def git_remote_ref_status(repo_root: Path, ref: str) -> tuple[bool, str]:
    worktree = subprocess.run(
        ["git", "-C", str(repo_root), "status", "--porcelain"],
        capture_output=True,
    )
    if worktree.returncode != 0:
        return False, "local worktree status is unavailable"
    if decode_text(worktree.stdout).strip():
        return False, "local worktree has uncommitted changes"

    remote_ref = f"refs/remotes/origin/{ref}"
    head = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--verify", "HEAD"],
        capture_output=True,
    )
    if head.returncode != 0:
        return False, "local HEAD is unavailable"

    remote = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--verify", remote_ref],
        capture_output=True,
    )
    if remote.returncode != 0:
        return False, f"remote tracking ref {remote_ref} is unavailable"

    head_sha = decode_text(head.stdout).strip()
    remote_sha = decode_text(remote.stdout).strip()
    if head_sha != remote_sha:
        return False, f"local HEAD {head_sha[:12]} differs from {remote_ref} {remote_sha[:12]}"

    return True, f"local HEAD matches {remote_ref}"


def toml_string_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def configured_marketplace(codex_home: Path, marketplace_name: str) -> dict[str, str] | None:
    config_path = codex_home / "config.toml"
    if not config_path.is_file():
        return None

    section = f"[marketplaces.{marketplace_name}]"
    in_section = False
    values: dict[str, str] = {}
    for line in config_path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped == section:
            in_section = True
            continue
        if in_section and stripped.startswith("[") and stripped.endswith("]"):
            break
        if not in_section or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if key in {"source_type", "source", "ref"}:
            values[key] = toml_string_value(value)

    return values or None


def clear_readonly_attributes(root: Path) -> None:
    if not root.exists():
        return
    items = [root, *root.rglob("*")]
    for item in items:
        try:
            mode = item.stat().st_mode
            item.chmod(mode | stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            continue


def remove_marketplace_source(
    codex: str,
    *,
    codex_home: Path,
    marketplace_name: str,
    env: dict[str, str],
    dry_run: bool,
) -> None:
    config = configured_marketplace(codex_home, marketplace_name)
    if config is None:
        return

    if dry_run:
        print(f"Would clear read-only attributes before removing marketplace `{marketplace_name}`.")
    else:
        source = config.get("source")
        if config.get("source_type") == "local" and source:
            clear_readonly_attributes(expand_path(source))
        clear_readonly_attributes(codex_home / ".tmp" / "marketplaces" / marketplace_name)

    run([codex, "plugin", "marketplace", "remove", marketplace_name], env=env, dry_run=dry_run)


def same_path(left: str | Path, right: str | Path) -> bool:
    try:
        return expand_path(left).resolve() == expand_path(right).resolve()
    except OSError:
        return str(expand_path(left)).rstrip("/\\").lower() == str(expand_path(right)).rstrip("/\\").lower()


def source_is_path_like(raw: str) -> bool:
    if "://" in raw or raw.startswith("git@"):
        return False
    expanded = os.path.expandvars(os.path.expanduser(raw))
    return (
        raw.startswith((".", "~", "/", "\\"))
        or (len(raw) >= 3 and raw[1] == ":" and raw[2] in {"\\", "/"})
        or Path(expanded).exists()
    )


def same_marketplace_source(left: str, right: str) -> bool:
    if source_is_path_like(left) and source_is_path_like(right):
        return same_path(left, right)
    left_source = marketplace_source_arg(left).strip().rstrip("/\\")
    right_source = marketplace_source_arg(right).strip().rstrip("/\\")
    return left_source == right_source


def same_marketplace_ref(left: str | None, right: str) -> bool:
    return (left or "").strip() == (right or "").strip()


def ensure_git_marketplace_source(
    codex: str,
    *,
    codex_home: Path,
    marketplace_name: str,
    source: str,
    ref: str,
    env: dict[str, str],
    dry_run: bool,
) -> int:
    config = configured_marketplace(codex_home, marketplace_name)
    if config and config.get("source_type") == "git":
        configured_source = config.get("source")
        if (
            configured_source
            and same_marketplace_source(configured_source, source)
            and same_marketplace_ref(config.get("ref"), ref)
        ):
            return run(
                [codex, "plugin", "marketplace", "upgrade", marketplace_name],
                env=env,
                dry_run=dry_run,
                check=False,
            )

        print("Configured Git marketplace differs from requested source/ref; re-adding marketplace.")
        print(f"ConfiguredSource={configured_source or '<missing>'}")
        print(f"RequestedSource={source}")
        print(f"ConfiguredRef={config.get('ref') or '<missing>'}")
        print(f"RequestedRef={ref or '<none>'}")

    if config:
        remove_marketplace_source(
            codex,
            codex_home=codex_home,
            marketplace_name=marketplace_name,
            env=env,
            dry_run=dry_run,
        )

    command = [codex, "plugin", "marketplace", "add", marketplace_source_arg(source)]
    if ref:
        command += ["--ref", ref]
    return run(command, env=env, dry_run=dry_run, check=False)


def ensure_local_marketplace_source(
    codex: str,
    *,
    codex_home: Path,
    marketplace_name: str,
    source: str,
    env: dict[str, str],
    dry_run: bool,
) -> None:
    config = configured_marketplace(codex_home, marketplace_name)
    if config and config.get("source_type") == "local" and config.get("source"):
        if same_path(config["source"], source):
            return

    if config:
        remove_marketplace_source(
            codex,
            codex_home=codex_home,
            marketplace_name=marketplace_name,
            env=env,
            dry_run=dry_run,
        )

    run([codex, "plugin", "marketplace", "add", marketplace_source_arg(source)], env=env, dry_run=dry_run)


def ensure_marketplace_source(
    codex: str,
    *,
    codex_home: Path,
    marketplace_name: str,
    git_source: str | None,
    git_ref: str,
    git_source_explicit: bool,
    local_source: str,
    env: dict[str, str],
    dry_run: bool,
) -> None:
    skipped_stale_git_source = False
    if git_source:
        if not git_source_explicit:
            current, reason = git_remote_ref_status(REPO_ROOT, git_ref)
            if not current:
                print(f"Local checkout is ahead of or not aligned with Git marketplace ref `{git_ref}`; using local source.")
                print(f"Reason: {reason}")
                git_source = None
                skipped_stale_git_source = True
            else:
                print(f"Git marketplace freshness check passed: {reason}")

    if git_source:
        print(f"Trying Git marketplace source first: {git_source}")
        git_exit = ensure_git_marketplace_source(
            codex,
            codex_home=codex_home,
            marketplace_name=marketplace_name,
            source=git_source,
            ref=git_ref,
            env=env,
            dry_run=dry_run,
        )
        if git_exit == 0:
            print("Marketplace source mode: git")
            return
        print(f"Git marketplace source failed with exit code {git_exit}; falling back to local source.")
    elif not skipped_stale_git_source:
        print("Git marketplace source was not found; falling back to local source.")

    ensure_local_marketplace_source(
        codex,
        codex_home=codex_home,
        marketplace_name=marketplace_name,
        source=local_source,
        env=env,
        dry_run=dry_run,
    )
    print("Marketplace source mode: local")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refresh my-codex plugin installs and user-level Skill Watcher hooks."
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them.")
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"), help="Codex CLI executable.")
    parser.add_argument("--codex-home", default=str(CODEX_HOME), help="Codex home directory.")
    parser.add_argument("--venv", default=str(DEFAULT_VENV), help="Shared my-codex tooling venv path.")
    parser.add_argument("--python", help="Explicit tooling Python for hooks and diagnostics.")
    parser.add_argument("--marketplace-name", default="my-codex", help="Configured marketplace name.")
    parser.add_argument(
        "--marketplace-source",
        default=str(REPO_ROOT),
        help="Local marketplace source used when Git marketplace update is unavailable.",
    )
    parser.add_argument(
        "--git-marketplace-source",
        help="Git marketplace source to try first. Defaults to this checkout's remote.origin.url.",
    )
    parser.add_argument("--git-ref", default="main", help="Git ref for first-time Git marketplace add.")
    parser.add_argument(
        "--plugin",
        action="append",
        help="Plugin name or PLUGIN@MARKETPLACE selector to refresh. May be repeated.",
    )
    parser.add_argument("--skip-bootstrap", action="store_true", help="Do not refresh the shared tooling venv.")
    parser.add_argument("--skip-marketplace", action="store_true", help="Do not refresh marketplace config/snapshot.")
    parser.add_argument("--skip-plugins", action="store_true", help="Do not run `codex plugin add`.")
    parser.add_argument("--skip-hooks", action="store_true", help="Do not refresh Skill Watcher hooks.")
    parser.add_argument("--skip-doctor", action="store_true", help="Do not run Skill Watcher doctor after refresh.")
    args = parser.parse_args()

    if not MARKETPLACE_FILE.is_file():
        raise SystemExit(f"marketplace file does not exist: {MARKETPLACE_FILE}")

    codex_home = expand_path(args.codex_home)
    venv_path = expand_path(args.venv)
    tooling_python = tooling_python_from_args(args, venv_path)
    env = build_env(codex_home=codex_home, tooling_python=tooling_python)
    codex = resolve_executable(args.codex)

    if not args.skip_bootstrap:
        run(
            [sys.executable, str(REPO_ROOT / "scripts" / "bootstrap_tooling_env.py"), "--venv", str(venv_path)],
            env=env,
            dry_run=args.dry_run,
        )

    if not args.skip_marketplace:
        ensure_marketplace_source(
            codex,
            codex_home=codex_home,
            marketplace_name=args.marketplace_name,
            git_source=args.git_marketplace_source or git_remote_source(REPO_ROOT),
            git_ref=args.git_ref,
            git_source_explicit=args.git_marketplace_source is not None,
            local_source=args.marketplace_source,
            env=env,
            dry_run=args.dry_run,
        )

    if not args.skip_plugins:
        for plugin in selected_plugins(args.plugin, args.marketplace_name, action="install"):
            run([codex, "plugin", "add", plugin], env=env, dry_run=args.dry_run)

    hook_installer = REPO_ROOT / "plugins" / "skill-watcher" / "scripts" / "install_codex_hook.py"
    if not args.skip_hooks:
        if not args.dry_run and not tooling_python.is_file():
            raise SystemExit(f"tooling Python does not exist: {tooling_python}")
        if not hook_installer.is_file():
            raise SystemExit(f"Skill Watcher hook installer does not exist: {hook_installer}")
        run(
            [str(tooling_python), str(hook_installer), "--apply", "--python", str(tooling_python)],
            env=env,
            dry_run=args.dry_run,
        )

    doctor = REPO_ROOT / "plugins" / "skill-watcher" / "scripts" / "doctor.py"
    if not args.skip_doctor:
        if not args.dry_run and not tooling_python.is_file():
            raise SystemExit(f"tooling Python does not exist: {tooling_python}")
        run([str(tooling_python), str(doctor)], env=env, dry_run=args.dry_run)

    if args.dry_run:
        print("dry-run only; no changes written")
    else:
        print("refresh complete")
        if not args.skip_hooks:
            print("open /hooks in Codex to review and trust refreshed Skill Watcher command hooks")


if __name__ == "__main__":
    main()
