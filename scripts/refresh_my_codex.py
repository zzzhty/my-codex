#!/usr/bin/env python3
"""Refresh the local my-codex marketplace plugins and Watcher skill hooks."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shlex
import shutil
import stat
import subprocess
import sys
import tomllib
from pathlib import Path

from check_skill_discovery import (
    PluginListRow,
    codex_plugin_rows,
    enabled_plugin_names,
    marketplace_plugin_names,
    marketplace_plugin_sources,
    plugin_cache_preflight_issues,
    plugin_installation_issues,
    plugin_package_issues,
    require_profile_closure,
    universal_profile_issues,
)
from discovery_profile_runtime import (
    PluginToUniversalRuntime,
    UniversalToPluginRuntime,
    transition_plugin_to_universal,
    transition_universal_to_plugin,
)
from repo_skill_catalog import SkillCatalog, load_repo_skill_catalog
from skill_discovery_profiles import (
    DISCOVERY_PROFILE_CHOICES,
    DiscoveryProfile,
    RefreshProfileOptions,
    ensure_plugin_profile_covers_catalog,
    parse_discovery_profile,
    validate_refresh_profile,
)
from sync_agents_skills import (
    managed_destination,
    preflight_layer,
    remove_managed_layer,
    sync_layer,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_FILE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
INSTALL_MANIFEST_FILE = REPO_ROOT / ".agents" / "plugins" / "install-manifest.json"
CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
DEFAULT_VENV = CODEX_HOME / "venvs" / "my-codex"
DEFAULT_AGENTS_SKILLS_ROOT = Path.home() / ".agents" / "skills"
MACOS_APPLICATION_DIRS = (Path("/Applications"), Path.home() / "Applications")


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


def latest_files(root: Path, pattern: str) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(root.rglob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)


def macos_app_codex_candidates() -> list[str]:
    if sys.platform != "darwin":
        return []
    candidates = [
        candidate
        for root in MACOS_APPLICATION_DIRS
        if root.is_dir()
        for candidate in root.glob("*.app/Contents/Resources/codex")
        if candidate.is_file()
    ]
    return [str(path) for path in sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)]


def codex_extension_platform_dir() -> str | None:
    machine = platform.machine().lower()
    if machine in {"amd64", "x86_64"}:
        architecture = "x86_64"
    elif machine in {"aarch64", "arm64"}:
        architecture = "aarch64"
    else:
        return None

    if sys.platform == "win32":
        system = "windows"
    elif sys.platform == "darwin":
        system = "macos"
    elif sys.platform.startswith("linux"):
        system = "linux"
    else:
        return None
    return f"{system}-{architecture}"


def codex_extension_candidates(user_home: Path) -> list[str]:
    platform_dir = codex_extension_platform_dir()
    if platform_dir is None:
        return []

    if sys.platform == "win32":
        extension_roots = [
            user_home / ".vscode" / "extensions",
            user_home / ".vscode-insiders" / "extensions",
        ]
        executable_name = "codex.exe"
    else:
        extension_roots = [
            user_home / ".vscode-server" / "extensions",
            user_home / ".vscode-server-insiders" / "extensions",
            user_home / ".vscode" / "extensions",
            user_home / ".vscode-insiders" / "extensions",
        ]
        executable_name = "codex"

    candidates: list[Path] = []
    for extension_root in extension_roots:
        if not extension_root.is_dir():
            continue
        for extension in extension_root.glob("openai.chatgpt-*"):
            candidate = extension / "bin" / platform_dir / executable_name
            if candidate.is_file():
                candidates.append(candidate)
    return [str(path) for path in sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)]


def codex_fallback_candidates(codex_home: Path) -> list[str]:
    is_windows = sys.platform == "win32"
    executable_name = "codex.exe" if is_windows else "codex"

    if is_windows:
        user_home = expand_path(os.environ.get("USERPROFILE") or Path.home())
        local_app_data = os.environ.get("LOCALAPPDATA")
        default_install_dir = (
            expand_path(local_app_data) / "Programs" / "OpenAI" / "Codex" / "bin"
            if local_app_data
            else None
        )
    else:
        user_home = expand_path(os.environ.get("HOME") or Path.home())
        local_app_data = None
        default_install_dir = user_home / ".local" / "bin"

    install_dir_raw = os.environ.get("CODEX_INSTALL_DIR")
    install_dir = expand_path(install_dir_raw) if install_dir_raw else default_install_dir

    candidates: list[str] = []
    if install_dir is not None:
        candidates.append(str(install_dir / executable_name))

    standalone_current = codex_home / "packages" / "standalone" / "current"
    candidates.extend(
        [
            str(standalone_current / "bin" / executable_name),
            str(standalone_current / executable_name),
        ]
    )

    if local_app_data:
        desktop_bin_root = expand_path(local_app_data) / "OpenAI" / "Codex" / "bin"
        candidates.extend(str(path) for path in latest_files(desktop_bin_root, executable_name))

    candidates.extend(macos_app_codex_candidates())
    candidates.extend(codex_extension_candidates(user_home))
    return list(dict.fromkeys(candidates))


def resolve_first_executable(candidates: list[str]) -> str:
    checked: list[str] = []
    for candidate in candidates:
        if not candidate:
            continue
        expanded = os.path.expandvars(os.path.expanduser(candidate))
        checked.append(candidate)
        if any(separator in expanded for separator in (os.sep, os.altsep) if separator):
            path = Path(expanded)
            if path.is_file():
                return str(path)
            continue
        resolved = shutil.which(expanded)
        if resolved is not None:
            return resolved
    raise SystemExit("executable not found. Checked:\n" + "\n".join(checked))


def resolve_executable(raw: str) -> str:
    return resolve_first_executable([raw])


def resolve_codex_executable(raw: str | None, *, codex_home: Path) -> str:
    if raw is not None:
        return resolve_executable(raw)

    configured = os.environ.get("CODEX_BIN")
    if configured:
        return resolve_executable(configured)

    path_codex = shutil.which("codex")
    if path_codex is not None:
        return path_codex

    fallbacks = codex_fallback_candidates(codex_home)
    try:
        return resolve_first_executable(fallbacks)
    except SystemExit:
        raise SystemExit(
            "executable not found. Checked:\n"
            "codex on PATH\n"
            + "\n".join(fallbacks)
        ) from None


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
    except PermissionError as exc:
        raise SystemExit(f"command not executable: {command[0]}: {exc}") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"command failed with exit code {exc.returncode}: {command_text(command)}") from exc
    return result.returncode


def codex_version(codex: str, *, env: dict[str, str]) -> str:
    try:
        result = subprocess.run([codex, "--version"], env=env, capture_output=True, text=True)
    except (FileNotFoundError, PermissionError):
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    return (result.stdout or result.stderr).strip() or "unknown"


def read_codex_plugin_rows(
    codex: str,
    *,
    env: dict[str, str],
) -> dict[tuple[str, str], PluginListRow]:
    command = [codex, "plugin", "list"]
    try:
        result = subprocess.run(command, env=env, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise SystemExit(f"command not found: {command[0]}") from exc
    except PermissionError as exc:
        raise SystemExit(f"command not executable: {command[0]}: {exc}") from exc
    if result.returncode != 0:
        output = (result.stderr or result.stdout).strip()
        raise SystemExit(
            f"failed to inspect active discovery state with `{command_text(command)}`: {output}"
        )
    try:
        return codex_plugin_rows(result.stdout)
    except ValueError as exc:
        raise SystemExit(f"failed to parse `{command_text(command)}` output: {exc}") from exc


def require_codex_subcommand(codex: str, label: str, args: list[str], *, env: dict[str, str]) -> None:
    command = [codex, *args, "--help"]
    try:
        result = subprocess.run(command, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError as exc:
        raise SystemExit(f"command not found: {command[0]}") from exc
    except PermissionError as exc:
        raise SystemExit(f"command not executable: {command[0]}: {exc}") from exc
    if result.returncode == 0:
        return

    raise SystemExit(
        "\n".join(
            [
                f"required Codex CLI command is unavailable: codex {label}",
                f"CodexPath={codex}",
                f"CodexVersion={codex_version(codex, env=env)}",
                f"FailedCommand={command_text(command)}",
                "Breakpoint=before marketplace refresh in scripts/refresh_my_codex.py",
                "Upgrade Codex CLI; this refresh flow requires non-interactive plugin marketplace/add/list commands and pruning also requires plugin remove.",
            ]
        )
    )


def require_codex_plugin_commands(
    codex: str,
    *,
    env: dict[str, str],
    require_marketplace: bool = True,
    require_add: bool = True,
    require_list: bool = True,
    require_remove: bool = False,
) -> None:
    if require_marketplace:
        require_codex_subcommand(codex, "plugin marketplace add", ["plugin", "marketplace", "add"], env=env)
    if require_add:
        require_codex_subcommand(codex, "plugin add", ["plugin", "add"], env=env)
    if require_list:
        require_codex_subcommand(codex, "plugin list", ["plugin", "list"], env=env)
    if require_remove:
        require_codex_subcommand(codex, "plugin remove", ["plugin", "remove"], env=env)


def run_agent_sync(*, codex_home: Path, env: dict[str, str], dry_run: bool) -> None:
    sync_script = REPO_ROOT / "scripts" / "sync_codex_agents.py"
    if not sync_script.is_file():
        raise SystemExit(f"agent sync script does not exist: {sync_script}")
    command = [sys.executable, str(sync_script), "--codex-home", str(codex_home), "--prune"]
    if dry_run:
        command.append("--dry-run")
    run(command, env=env, dry_run=False)


def run_tooling_bootstrap(*, venv_path: Path, env: dict[str, str], dry_run: bool) -> None:
    bootstrap_script = REPO_ROOT / "scripts" / "bootstrap_tooling_env.py"
    if not bootstrap_script.is_file():
        raise SystemExit(f"tooling bootstrap script does not exist: {bootstrap_script}")
    command = [sys.executable, str(bootstrap_script), "--venv", str(venv_path)]
    if dry_run:
        command.append("--dry-run")
    run(command, env=env, dry_run=False)


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


def load_install_manifest(manifest_file: Path = INSTALL_MANIFEST_FILE) -> dict:
    data = load_json_object(manifest_file, label="install manifest")
    if data.get("schemaVersion") != 2:
        raise SystemExit(f"install manifest schemaVersion must be 2: {manifest_file}")
    if data.get("discoveryProfile") != "plugin":
        raise SystemExit(
            f"install manifest discoveryProfile must be 'plugin': {manifest_file}"
        )

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
    try:
        present = marketplace_plugin_names(marketplace_file)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
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


def configured_plugin_settings(
    codex_home: Path,
) -> dict[tuple[str, str], dict[str, object]]:
    config_path = codex_home / "config.toml"
    if not config_path.is_file():
        return {}
    try:
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(f"Codex config is not valid readable TOML: {config_path}: {exc}") from exc
    plugins = payload.get("plugins", {})
    if not isinstance(plugins, dict):
        raise SystemExit(f"Codex config plugins table must be a mapping: {config_path}")
    selectors: dict[tuple[str, str], dict[str, object]] = {}
    for raw_selector, settings in plugins.items():
        if not isinstance(raw_selector, str) or not isinstance(settings, dict):
            raise SystemExit(f"Codex config plugin entry is malformed: {raw_selector!r}: {config_path}")
        plugin_name, separator, marketplace = raw_selector.rpartition("@")
        if not separator or not plugin_name or not marketplace:
            raise SystemExit(f"Codex config plugin selector is malformed: {raw_selector!r}: {config_path}")
        selectors[(marketplace, plugin_name)] = settings
    return selectors


def configured_plugin_selectors(codex_home: Path) -> set[tuple[str, str]]:
    return set(configured_plugin_settings(codex_home))


def enabled_configured_plugin_selectors(codex_home: Path) -> set[tuple[str, str]]:
    """Return plugin selectors explicitly enabled in Codex config."""

    selectors: set[tuple[str, str]] = set()
    for selector, settings in configured_plugin_settings(codex_home).items():
        enabled = settings.get("enabled", False)
        if not isinstance(enabled, bool):
            marketplace, plugin_name = selector
            raise SystemExit(
                "Codex config plugin enabled field must be boolean: "
                f"{plugin_name}@{marketplace}"
            )
        if enabled:
            selectors.add(selector)
    return selectors


def configured_plugin_names(codex_home: Path, marketplace_name: str) -> set[str]:
    return {
        plugin_name
        for marketplace, plugin_name in configured_plugin_selectors(codex_home)
        if marketplace == marketplace_name
    }


def universal_layer_active(catalog: SkillCatalog, *, target_root: Path) -> bool:
    if not target_root.is_dir():
        return False
    return any(
        target.is_symlink() and managed_destination(target, catalog) is not None
        for target in target_root.iterdir()
    )


def _enabled_profile_plugins(
    catalog: SkillCatalog,
    *,
    codex: str,
    marketplace_name: str,
    env: dict[str, str],
) -> set[str]:
    selectors = _enabled_skill_plugin_selectors(
        catalog,
        codex=codex,
        marketplace_name=marketplace_name,
        env=env,
    )
    alternate = sorted(
        f"{plugin_name}@{marketplace}"
        for marketplace, plugin_name in selectors
        if marketplace != marketplace_name
    )
    if alternate:
        raise SystemExit(
            "canonical skill plugins are enabled through another marketplace: "
            + ", ".join(alternate)
        )
    return {
        plugin_name
        for marketplace, plugin_name in selectors
        if marketplace == marketplace_name
    }


def _enabled_skill_plugin_selectors(
    catalog: SkillCatalog,
    *,
    codex: str,
    marketplace_name: str,
    env: dict[str, str],
) -> set[tuple[str, str]]:
    rows = read_codex_plugin_rows(codex, env=env)
    expected = set(catalog.plugin_names)
    enabled = {
        (marketplace, plugin_name)
        for (marketplace, plugin_name), row in rows.items()
        if row.status == "installed, enabled"
    }
    unclassified = sorted(
        plugin_name
        for marketplace, plugin_name in enabled
        if marketplace == marketplace_name and plugin_name not in expected
    )
    if unclassified:
        raise SystemExit(
            "unclassified enabled my-codex plugins are outside the frozen discovery profile: "
            + ", ".join(unclassified)
        )
    return {
        (marketplace, plugin_name)
        for marketplace, plugin_name in enabled
        if plugin_name in expected
    }


def apply_universal_discovery_profile(
    catalog: SkillCatalog,
    *,
    codex: str | None,
    codex_home: Path,
    marketplace_name: str,
    target_root: Path,
    env: dict[str, str],
    dry_run: bool,
) -> None:
    expected = set(catalog.plugin_names)
    configured = enabled_configured_plugin_selectors(codex_home)
    discovery_configured = {
        (marketplace, plugin_name)
        for marketplace, plugin_name in configured
        if plugin_name in expected or marketplace == marketplace_name
    }
    enabled_before: set[tuple[str, str]]
    if discovery_configured:
        if codex is None:
            raise SystemExit("Codex CLI is required to inspect configured skills-bearing plugins")
        enabled_before = _enabled_skill_plugin_selectors(
            catalog,
            codex=codex,
            marketplace_name=marketplace_name,
            env=env,
        )
        missing_from_cli = sorted(discovery_configured - enabled_before)
        if missing_from_cli:
            raise SystemExit(
                "Codex config and `codex plugin list` disagree about enabled discovery plugins: "
                + ", ".join(
                    f"{plugin_name}@{marketplace}"
                    for marketplace, plugin_name in missing_from_cli
                )
            )
    else:
        enabled_before = set()
    selectors = [
        f"{plugin_name}@{marketplace}"
        for marketplace, plugin_name in sorted(enabled_before)
    ]
    if selectors and codex is None:  # defensive; configured state above already resolves this
        raise SystemExit("Codex CLI is required to deactivate configured skills-bearing plugins")

    def current_enabled() -> set[tuple[str, str]]:
        if codex is None:
            return set()
        return _enabled_skill_plugin_selectors(
            catalog,
            codex=codex,
            marketplace_name=marketplace_name,
            env=env,
        )

    def verify_plugins_inactive() -> None:
        if dry_run:
            return
        remaining = current_enabled()
        if remaining:
            raise SystemExit(
                "skills-bearing plugin path remains enabled after deactivation: "
                + ", ".join(
                    f"{plugin_name}@{marketplace}"
                    for marketplace, plugin_name in sorted(remaining)
                )
            )

    def verify_universal() -> None:
        if dry_run:
            return
        require_profile_closure(
            "universal",
            universal_profile_issues(
                catalog,
                target_root=target_root,
                enabled_plugin_names={name for _, name in current_enabled()},
            ),
        )

    def verify_plugin() -> None:
        if dry_run:
            return
        restored = current_enabled()
        if restored != enabled_before or universal_layer_active(catalog, target_root=target_root):
            raise SystemExit(
                "plugin rollback did not restore the prior active path: "
                f"expected enabled {sorted(enabled_before)}, found {sorted(restored)}"
            )

    def restore_plugin(selector: str) -> None:
        plugin_name, _, marketplace = selector.partition("@")
        if not dry_run and (marketplace, plugin_name) in current_enabled():
            return
        run(
            [str(codex), "plugin", "add", selector],
            env=env,
            dry_run=dry_run,
        )

    runtime = PluginToUniversalRuntime(
        preflight_universal=lambda: preflight_layer(catalog, target_root=target_root),
        activate_universal=lambda: sync_layer(
            catalog,
            target_root=target_root,
            dry_run=dry_run,
            prune=True,
        ),
        deactivate_universal=lambda: remove_managed_layer(
            catalog,
            target_root=target_root,
            dry_run=dry_run,
        ),
        verify_universal=verify_universal,
        activate_plugin=restore_plugin,
        deactivate_plugin=lambda selector: run(
            [str(codex), "plugin", "remove", selector],
            env=env,
            dry_run=dry_run,
        ),
        verify_plugin=verify_plugin,
        verify_plugins_inactive=verify_plugins_inactive,
    )
    transition_plugin_to_universal(runtime, selectors)


def apply_plugin_discovery_profile(
    catalog: SkillCatalog,
    *,
    codex: str,
    codex_home: Path,
    marketplace_name: str,
    target_root: Path,
    requested_plugins: list[str] | None,
    env: dict[str, str],
    dry_run: bool,
) -> None:
    marketplace_file = catalog.repo_root / ".agents" / "plugins" / "marketplace.json"
    manifest_file = catalog.repo_root / ".agents" / "plugins" / "install-manifest.json"
    all_selectors = selected_plugins(
        None,
        marketplace_name,
        action="install",
        manifest_file=manifest_file,
        marketplace_file=marketplace_file,
    )
    ensure_plugin_profile_covers_catalog(
        catalog,
        all_selectors,
        marketplace_name=marketplace_name,
    )
    try:
        marketplace_identity, plugin_sources = marketplace_plugin_sources(catalog.repo_root)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if marketplace_identity != marketplace_name:
        raise SystemExit(
            f"marketplace identity mismatch: expected {marketplace_name!r}, found {marketplace_identity!r}"
        )
    require_profile_closure(
        "plugin package preflight",
        [
            *plugin_package_issues(catalog, plugin_sources=plugin_sources),
            *plugin_cache_preflight_issues(
                catalog,
                codex_home=codex_home,
                marketplace_name=marketplace_name,
            ),
        ],
    )

    selected = selected_plugins(
        requested_plugins,
        marketplace_name,
        action="install",
        manifest_file=manifest_file,
        marketplace_file=marketplace_file,
    )
    expected_names = set(catalog.plugin_names)
    invalid_selected = sorted(
        selector
        for selector in selected
        if selector.partition("@")[2] != marketplace_name
        or selector.partition("@")[0] not in expected_names
    )
    if invalid_selected:
        raise SystemExit(
            "--plugin selectors must name canonical skills-bearing packages in the selected marketplace: "
            + ", ".join(invalid_selected)
        )
    preflight_layer(catalog, target_root=target_root)
    enabled_before = _enabled_profile_plugins(
        catalog,
        codex=codex,
        marketplace_name=marketplace_name,
        env=env,
    )
    universal_active = universal_layer_active(catalog, target_root=target_root)
    if universal_active and enabled_before:
        raise SystemExit("universal and plugin discovery are already active together; refusing transition")
    if universal_active and requested_plugins is not None:
        raise SystemExit("--plugin cannot narrow a universal-to-plugin profile transition")
    if not universal_active and requested_plugins is not None and enabled_before != expected_names:
        raise SystemExit(
            "--plugin cannot repair an incomplete plugin profile; rerun without package narrowing"
        )
    transition_selectors = all_selectors if universal_active else selected

    def current_rows() -> dict[tuple[str, str], PluginListRow]:
        return read_codex_plugin_rows(codex, env=env)

    def current_enabled() -> set[str]:
        rows = current_rows()
        enabled = enabled_plugin_names(rows, marketplace_name=marketplace_name)
        unclassified = sorted(enabled - expected_names)
        if unclassified:
            raise SystemExit(
                "unclassified enabled my-codex plugins are outside the frozen discovery profile: "
                + ", ".join(unclassified)
            )
        return enabled

    def preflight_plugin() -> None:
        preflight_layer(catalog, target_root=target_root)
        require_profile_closure(
            "plugin package preflight",
            [
                *plugin_package_issues(catalog, plugin_sources=plugin_sources),
                *plugin_cache_preflight_issues(
                    catalog,
                    codex_home=codex_home,
                    marketplace_name=marketplace_name,
                ),
            ],
        )

    def verify_plugin() -> None:
        if dry_run:
            return
        require_profile_closure(
            "plugin",
            plugin_installation_issues(
                catalog,
                marketplace_name=marketplace_name,
                target_root=target_root,
                codex_home=codex_home,
                rows=current_rows(),
                plugin_sources=plugin_sources,
            ),
        )

    def verify_universal() -> None:
        if dry_run:
            return
        require_profile_closure(
            "universal rollback",
            universal_profile_issues(
                catalog,
                target_root=target_root,
                enabled_plugin_names=current_enabled(),
            ),
        )

    def deactivate_plugin(selector: str) -> None:
        plugin_name, _, selector_marketplace = selector.partition("@")
        if not dry_run:
            row = current_rows().get((selector_marketplace, plugin_name))
            configured = (
                selector_marketplace,
                plugin_name,
            ) in configured_plugin_selectors(codex_home)
            if (row is None or row.status == "not installed") and not configured:
                return
        run(
            [codex, "plugin", "remove", selector],
            env=env,
            dry_run=dry_run,
        )

    runtime = UniversalToPluginRuntime(
        activate_universal=lambda: sync_layer(
            catalog,
            target_root=target_root,
            dry_run=dry_run,
            prune=True,
        ),
        deactivate_universal=lambda: remove_managed_layer(
            catalog,
            target_root=target_root,
            dry_run=dry_run,
        ),
        verify_universal=verify_universal,
        preflight_plugin=preflight_plugin,
        activate_plugin=lambda selector: run(
            [codex, "plugin", "add", selector],
            env=env,
            dry_run=dry_run,
        ),
        deactivate_plugin=deactivate_plugin,
        verify_plugin=verify_plugin,
    )
    if universal_active:
        transition_universal_to_plugin(runtime, transition_selectors)
        return

    attempted_new: list[str] = []
    try:
        for selector in transition_selectors:
            if selector.partition("@")[0] not in enabled_before:
                attempted_new.append(selector)
            runtime.activate_plugin(selector)
        verify_plugin()
    except (Exception, SystemExit) as exc:
        try:
            for selector in reversed(attempted_new):
                deactivate_plugin(selector)
            restored = current_enabled()
            if restored != enabled_before:
                raise SystemExit(
                    "plugin refresh rollback did not restore the prior enabled set: "
                    f"expected {sorted(enabled_before)}, found {sorted(restored)}"
                )
        except (Exception, SystemExit) as rollback_exc:
            raise SystemExit(
                f"plugin profile activation failed: {exc}; rollback failed: {rollback_exc}"
            ) from exc
        raise


def cached_plugin_names(codex_home: Path, marketplace_name: str) -> set[str]:
    cache_root = codex_home / "plugins" / "cache" / marketplace_name
    if not cache_root.is_dir():
        return set()
    return {path.name for path in cache_root.iterdir() if path.is_dir()}


def plugin_cache_dir(codex_home: Path, marketplace_name: str, plugin_name: str) -> Path:
    return codex_home / "plugins" / "cache" / marketplace_name / plugin_name


def stale_plugin_names(
    *,
    codex_home: Path,
    marketplace_name: str,
    desired_plugin_names: list[str],
) -> list[str]:
    discovered = configured_plugin_names(codex_home, marketplace_name) | cached_plugin_names(codex_home, marketplace_name)
    desired = set(desired_plugin_names)
    return sorted(discovered - desired)


def remove_cached_plugin_dir(
    *,
    codex_home: Path,
    marketplace_name: str,
    plugin_name: str,
    dry_run: bool,
) -> None:
    cache_root = codex_home / "plugins" / "cache" / marketplace_name
    plugin_dir = plugin_cache_dir(codex_home, marketplace_name, plugin_name)
    if not plugin_dir.exists():
        return
    try:
        plugin_dir.resolve().relative_to(cache_root.resolve())
    except ValueError as exc:
        raise SystemExit(f"refusing to remove plugin cache outside marketplace cache root: {plugin_dir}") from exc
    print(f"+ remove plugin cache {plugin_dir}", flush=True)
    if dry_run:
        return
    clear_readonly_attributes(plugin_dir)
    try:
        shutil.rmtree(plugin_dir)
    except OSError as exc:
        raise SystemExit(f"failed to remove plugin cache {plugin_dir}: {exc}") from exc


def prune_stale_plugins(
    codex: str,
    *,
    codex_home: Path,
    marketplace_name: str,
    desired_plugin_names: list[str],
    env: dict[str, str],
    dry_run: bool,
) -> None:
    stale = stale_plugin_names(
        codex_home=codex_home,
        marketplace_name=marketplace_name,
        desired_plugin_names=desired_plugin_names,
    )
    if not stale:
        print(f"No stale plugins to prune for marketplace `{marketplace_name}`.")
        return

    configured = configured_plugin_names(codex_home, marketplace_name)
    cached = cached_plugin_names(codex_home, marketplace_name)
    print("Stale plugins selected for pruning:")
    for name in stale:
        print(f"- {name}@{marketplace_name}")
    for name in stale:
        if name in configured:
            run([codex, "plugin", "remove", f"{name}@{marketplace_name}"], env=env, dry_run=dry_run)
        if name in cached:
            remove_cached_plugin_dir(
                codex_home=codex_home,
                marketplace_name=marketplace_name,
                plugin_name=name,
                dry_run=dry_run,
            )


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
    env["PYTHONDONTWRITEBYTECODE"] = "1"
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
        description="Refresh my-codex plugin installs and user-level Watcher skill hooks."
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them.")
    parser.add_argument(
        "--discovery-profile",
        required=True,
        choices=DISCOVERY_PROFILE_CHOICES,
        help="Required skill discovery profile: universal or plugin.",
    )
    parser.add_argument(
        "--codex",
        help="Explicit Codex CLI executable. Defaults to CODEX_BIN, PATH, then managed install fallbacks.",
    )
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
    parser.add_argument("--skip-marketplace", action="store_true", help="Deprecated profile bypass; rejected.")
    parser.add_argument("--skip-plugins", action="store_true", help="Deprecated profile bypass; rejected.")
    parser.add_argument(
        "--prune-plugins",
        action="store_true",
        help="Remove installed or cached marketplace plugins that are not selected for install by the manifest.",
    )
    parser.add_argument("--skip-agents", action="store_true", help="Do not sync the subagent support file into $CODEX_HOME/agents.")
    parser.add_argument("--skip-agents-skills", action="store_true", help="Deprecated profile bypass; rejected.")
    parser.add_argument(
        "--agents-skills-root",
        default=str(DEFAULT_AGENTS_SKILLS_ROOT),
        help="Universal skill projection root (default: ~/.agents/skills).",
    )
    parser.add_argument("--skip-hooks", action="store_true", help="Do not refresh Watcher skill hooks.")
    parser.add_argument("--skip-doctor", action="store_true", help="Do not run Watcher skill doctor after refresh.")
    args = parser.parse_args()

    profile = parse_discovery_profile(args.discovery_profile)
    validate_refresh_profile(
        RefreshProfileOptions(
            profile=profile,
            skip_marketplace=args.skip_marketplace,
            skip_plugins=args.skip_plugins,
            skip_agents_skills=args.skip_agents_skills,
            prune_plugins=args.prune_plugins,
            selected_plugins=tuple(args.plugin or ()),
        )
    )
    catalog = load_repo_skill_catalog()

    codex_home = expand_path(args.codex_home)
    agents_skills_root = expand_path(args.agents_skills_root)
    venv_path = expand_path(args.venv)
    tooling_python = tooling_python_from_args(args, venv_path)
    env = build_env(codex_home=codex_home, tooling_python=tooling_python)
    codex: str | None = None
    configured_profile_plugins = {
        (marketplace, plugin_name)
        for marketplace, plugin_name in enabled_configured_plugin_selectors(codex_home)
        if plugin_name in set(catalog.plugin_names) or marketplace == args.marketplace_name
    }
    if profile is DiscoveryProfile.PLUGIN:
        codex = resolve_codex_executable(args.codex, codex_home=codex_home)
        require_codex_plugin_commands(
            codex,
            env=env,
            require_marketplace=True,
            require_add=True,
            require_list=True,
            require_remove=args.prune_plugins or universal_layer_active(
                catalog,
                target_root=agents_skills_root,
            ),
        )
    elif configured_profile_plugins:
        codex = resolve_codex_executable(args.codex, codex_home=codex_home)
        require_codex_plugin_commands(
            codex,
            env=env,
            require_marketplace=False,
            require_add=True,
            require_list=True,
            require_remove=True,
        )

    if not args.skip_bootstrap:
        run_tooling_bootstrap(venv_path=venv_path, env=env, dry_run=args.dry_run)

    if profile is DiscoveryProfile.PLUGIN:
        assert codex is not None
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
        if args.prune_plugins:
            _enabled_profile_plugins(
                catalog,
                codex=codex,
                marketplace_name=args.marketplace_name,
                env=env,
            )
            prune_stale_plugins(
                codex,
                codex_home=codex_home,
                marketplace_name=args.marketplace_name,
                desired_plugin_names=default_plugin_names(
                    "install",
                    marketplace_name=args.marketplace_name,
                ),
                env=env,
                dry_run=args.dry_run,
            )
        apply_plugin_discovery_profile(
            catalog,
            codex=codex,
            codex_home=codex_home,
            marketplace_name=args.marketplace_name,
            target_root=agents_skills_root,
            requested_plugins=args.plugin,
            env=env,
            dry_run=args.dry_run,
        )
    else:
        apply_universal_discovery_profile(
            catalog,
            codex=codex,
            codex_home=codex_home,
            marketplace_name=args.marketplace_name,
            target_root=agents_skills_root,
            env=env,
            dry_run=args.dry_run,
        )

    if not args.skip_agents:
        run_agent_sync(codex_home=codex_home, env=env, dry_run=args.dry_run)

    watcher_cli = REPO_ROOT / "plugins" / "watcher" / "scripts" / "watcher"
    if not args.skip_hooks:
        if not args.dry_run and not tooling_python.is_file():
            raise SystemExit(f"tooling Python does not exist: {tooling_python}")
        if not watcher_cli.is_file():
            raise SystemExit(f"Watcher CLI does not exist: {watcher_cli}")
        run(
            [
                str(tooling_python),
                str(watcher_cli),
                "skill",
                "install-hook",
                "--apply",
                "--python",
                str(tooling_python),
                "--repo-root",
                str(REPO_ROOT),
            ],
            env=env,
            dry_run=args.dry_run,
        )

    if not args.skip_doctor:
        if not args.dry_run and not tooling_python.is_file():
            raise SystemExit(f"tooling Python does not exist: {tooling_python}")
        if not watcher_cli.is_file():
            raise SystemExit(f"Watcher CLI does not exist: {watcher_cli}")
        run(
            [
                str(tooling_python),
                str(watcher_cli),
                "skill",
                "doctor",
                "--repo-root",
                str(REPO_ROOT),
            ],
            env=env,
            dry_run=args.dry_run,
        )

    if args.dry_run:
        print(f"dry-run only; no changes written (discovery profile: {profile.value})")
    else:
        print(f"refresh complete (discovery profile: {profile.value})")
        if not args.skip_hooks:
            print("open /hooks in Codex to review and trust refreshed Watcher skill command hooks")


if __name__ == "__main__":
    main()
