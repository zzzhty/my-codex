#!/usr/bin/env python3
"""Run final closure checks for the local my-codex installation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from check_skill_discovery import (
    PluginListRow,
    codex_plugin_rows,
    enabled_plugin_names,
    plugin_installation_issues,
    plugin_package_issues,
    universal_profile_issues,
)
from refresh_my_codex import (
    CODEX_HOME,
    DEFAULT_AGENTS_SKILLS_ROOT,
    DEFAULT_VENV,
    INSTALL_MANIFEST_FILE,
    MARKETPLACE_FILE,
    REPO_ROOT,
    build_env,
    cached_plugin_names,
    command_text,
    configured_plugin_names,
    expand_path,
    resolve_codex_executable,
    selected_plugins,
    stale_plugin_names,
    tooling_python_from_args,
)
from repo_skill_catalog import SkillCatalog, load_repo_skill_catalog
from skill_discovery_profiles import (
    DISCOVERY_PROFILE_CHOICES,
    CheckProfileOptions,
    DiscoveryProfile,
    parse_discovery_profile,
    validate_check_profile,
)


WATCHER_SCRIPTS = REPO_ROOT / "plugins" / "watcher" / "scripts"
sys.path.insert(0, str(WATCHER_SCRIPTS))

from watcher_runtime.skill.codex_hook_config import HOOK_EVENTS, adapter_path, load_config  # noqa: E402
from watcher_runtime.skill.doctor import find_managed_hook_issues  # noqa: E402


def configure_output_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")


def plugin_check_scopes(
    raw_plugins: list[str] | None,
    marketplace_name: str,
    *,
    manifest_file: Path = INSTALL_MANIFEST_FILE,
    marketplace_file: Path = MARKETPLACE_FILE,
) -> tuple[list[str], list[str]]:
    plugins_to_check = selected_plugins(
        raw_plugins,
        marketplace_name,
        action="check",
        manifest_file=manifest_file,
        marketplace_file=marketplace_file,
    )
    desired_plugins = selected_plugins(
        None,
        marketplace_name,
        action="check",
        manifest_file=manifest_file,
        marketplace_file=marketplace_file,
    )
    return plugins_to_check, desired_plugins


def decode_subprocess_output(raw: bytes | str | None) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    return raw.decode("utf-8", errors="replace")


def print_text(message: str) -> None:
    try:
        print(message)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        safe = message.encode(encoding, errors="backslashreplace").decode(encoding, errors="replace")
        print(safe)


def plugin_manifest_identity(manifest: Path, *, label: str) -> tuple[str, str]:
    if not manifest.is_file():
        raise ValueError(f"{label} manifest missing: {manifest}")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{label} manifest is not valid JSON: {manifest}: line {exc.lineno}, column {exc.colno}"
        ) from exc
    except OSError as exc:
        raise ValueError(f"{label} manifest cannot be read: {manifest}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} manifest must be an object: {manifest}")
    identity = []
    for field in ("name", "version"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} manifest {field} must be a non-empty string: {manifest}")
        identity.append(value.strip())
    return identity[0], identity[1]


def marketplace_plugin_sources(source_root: Path) -> tuple[str, dict[str, Path]]:
    marketplace = source_root / ".agents" / "plugins" / "marketplace.json"
    if not marketplace.is_file():
        raise ValueError(f"marketplace file missing: {marketplace}")
    try:
        data = json.loads(marketplace.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"marketplace file is not valid JSON: {marketplace}: line {exc.lineno}, column {exc.colno}"
        ) from exc
    except OSError as exc:
        raise ValueError(f"marketplace file cannot be read: {marketplace}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"marketplace must be an object: {marketplace}")
    marketplace_name = data.get("name")
    if not isinstance(marketplace_name, str) or not marketplace_name.strip():
        raise ValueError(f"marketplace name must be a non-empty string: {marketplace}")
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        raise ValueError(f"marketplace plugins field is not a list: {marketplace}")

    sources: dict[str, Path] = {}
    for index, entry in enumerate(plugins, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"marketplace plugin entry #{index} must be an object: {marketplace}")
        plugin_name = entry.get("name")
        if not isinstance(plugin_name, str) or not plugin_name.strip():
            raise ValueError(f"marketplace plugin entry #{index} name missing: {marketplace}")
        plugin_name = plugin_name.strip()
        if plugin_name in sources:
            raise ValueError(f"duplicate marketplace plugin name {plugin_name!r}: {marketplace}")
        source = entry.get("source")
        if not isinstance(source, dict):
            raise ValueError(f"marketplace plugin entry #{index} source must be an object: {marketplace}")
        source_kind = source.get("source")
        if source_kind != "local":
            raise ValueError(
                f"unsupported marketplace source kind {source_kind!r} for {plugin_name!r}: {marketplace}"
            )
        raw_path = source.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError(f"marketplace local plugin entry #{index} path missing: {marketplace}")
        plugin_dir = expand_path(raw_path.strip())
        if not plugin_dir.is_absolute():
            plugin_dir = source_root / plugin_dir
        plugin_dir = plugin_dir.resolve()
        if not plugin_dir.is_dir():
            raise ValueError(f"marketplace local plugin path missing: {plugin_dir}")
        manifest = plugin_dir / ".codex-plugin" / "plugin.json"
        manifest_name, _ = plugin_manifest_identity(manifest, label="source")
        if manifest_name != plugin_name:
            raise ValueError(
                f"marketplace/source manifest name mismatch for entry #{index}; "
                f"catalog has {plugin_name!r}, manifest has {manifest_name!r} at {manifest}"
            )
        sources[plugin_name] = plugin_dir
    return marketplace_name.strip(), sources


class CheckRunner:
    def __init__(self) -> None:
        self.failures = 0
        self.warnings = 0

    def ok(self, message: str) -> None:
        print_text(f"OK   {message}")

    def warn(self, message: str) -> None:
        self.warnings += 1
        print_text(f"WARN {message}")

    def fail(self, message: str) -> None:
        self.failures += 1
        print_text(f"FAIL {message}")

    def run_command(self, command: list[str], *, env: dict[str, str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        print("+ " + command_text(command), flush=True)
        try:
            result = subprocess.run(command, cwd=str(cwd) if cwd else None, env=env, capture_output=True)
            return subprocess.CompletedProcess(
                command,
                result.returncode,
                decode_subprocess_output(result.stdout),
                decode_subprocess_output(result.stderr),
            )
        except FileNotFoundError as exc:
            return subprocess.CompletedProcess(command, 127, "", f"command not found: {exc.filename}")
        except PermissionError as exc:
            return subprocess.CompletedProcess(command, 126, "", f"command not executable: {command[0]}: {exc}")

    def check_marketplace_file(
        self,
        expected_plugins: list[str],
        *,
        source_root: Path = REPO_ROOT,
    ) -> dict[str, Path] | None:
        try:
            marketplace_name, sources = marketplace_plugin_sources(source_root)
        except ValueError as exc:
            self.fail(str(exc))
            return None
        selector_marketplaces = {selector.partition("@")[2] for selector in expected_plugins if "@" in selector}
        if selector_marketplaces != {marketplace_name}:
            self.fail(
                f"marketplace name mismatch: catalog has {marketplace_name!r}, "
                f"selectors require {', '.join(sorted(selector_marketplaces)) or 'none'}"
            )
            return None
        present = set(sources)
        expected = {selector.split("@", 1)[0] for selector in expected_plugins}
        missing = sorted(expected - present)
        if missing:
            self.fail(f"marketplace is missing plugins: {', '.join(missing)}")
            return None
        marketplace = source_root / ".agents" / "plugins" / "marketplace.json"
        self.ok(f"marketplace file includes exact local plugin identities: {marketplace}")
        return sources

    def check_plugin_packages(
        self,
        catalog: SkillCatalog,
        *,
        plugin_sources: dict[str, Path],
    ) -> None:
        issues = plugin_package_issues(catalog, plugin_sources=plugin_sources)
        if issues:
            for issue in issues:
                self.fail(issue)
            return
        self.ok("marketplace package sources match the repository callable catalog")

    def check_tooling_python(self, tooling_python: Path, *, env: dict[str, str]) -> None:
        if not tooling_python.is_file():
            self.fail(f"tooling Python missing: {tooling_python}")
            return
        result = self.run_command([str(tooling_python), "-c", "import yaml; print(yaml.__version__)"], env=env)
        if result.returncode == 0:
            self.ok(f"tooling Python imports PyYAML: {tooling_python} ({result.stdout.strip()})")
        else:
            output = (result.stderr or result.stdout).strip()
            self.fail(f"tooling Python cannot import PyYAML: {tooling_python}: {output}")

    def read_plugin_rows(
        self,
        codex: str,
        *,
        env: dict[str, str],
    ) -> dict[tuple[str, str], PluginListRow] | None:
        result = self.run_command([codex, "plugin", "list"], env=env)
        if result.returncode != 0:
            output = (result.stderr or result.stdout).strip()
            self.fail(f"`codex plugin list` failed: {output}")
            return None
        return codex_plugin_rows(result.stdout)

    def check_codex_plugin_list(
        self,
        codex: str,
        plugins: list[str],
        *,
        env: dict[str, str],
        plugin_sources: dict[str, Path],
    ) -> dict[tuple[str, str], PluginListRow] | None:
        rows = self.read_plugin_rows(codex, env=env)
        if rows is None:
            return None
        failures: list[str] = []
        for selector in plugins:
            plugin_name, separator, marketplace_name = selector.partition("@")
            if not separator or not plugin_name or not marketplace_name:
                failures.append(f"invalid plugin selector: {selector!r}")
                continue
            plugin_dir = plugin_sources.get(plugin_name)
            if plugin_dir is None:
                failures.append(f"{selector}: no source path from marketplace catalog")
                continue
            source_manifest = plugin_dir / ".codex-plugin" / "plugin.json"
            try:
                source_name, source_version = plugin_manifest_identity(source_manifest, label="source")
            except ValueError as exc:
                failures.append(f"{selector}: {exc}")
                continue
            if source_name != plugin_name:
                failures.append(
                    f"{selector}: source manifest name mismatch at {source_manifest}; "
                    f"expected {plugin_name!r}, found {source_name!r}"
                )
                continue
            installed = rows.get((marketplace_name, plugin_name))
            if installed is None:
                failures.append(f"{selector}: missing from `codex plugin list`")
                continue
            if installed.status != "installed, enabled":
                failures.append(
                    f"{selector}: expected status 'installed, enabled', found {installed.status!r}"
                )
            if installed.version != source_version:
                failures.append(
                    f"{selector}: installed version mismatch; expected source version {source_version!r}, "
                    f"found {installed.version!r}"
                )
        if failures:
            self.fail("plugin source/installed identity check failed: " + "; ".join(failures))
            return rows
        self.ok("codex plugin list matches source plugin name/version identities and enabled status")
        return rows

    def check_universal_discovery_profile(
        self,
        catalog: SkillCatalog,
        *,
        target_root: Path,
        marketplace_name: str,
        rows: dict[tuple[str, str], PluginListRow],
    ) -> None:
        enabled = enabled_plugin_names(rows, marketplace_name=marketplace_name)
        unclassified = sorted(enabled - set(catalog.plugin_names))
        issues = universal_profile_issues(
            catalog,
            target_root=target_root,
            enabled_plugin_names=enabled,
        )
        if unclassified:
            issues.append(
                "unclassified enabled my-codex plugins are outside the frozen discovery profile: "
                + ", ".join(unclassified)
            )
        if issues:
            for issue in issues:
                self.fail(issue)
            return
        self.ok(f"universal discovery profile is closed under {target_root}")

    def check_plugin_discovery_profile(
        self,
        catalog: SkillCatalog,
        *,
        target_root: Path,
        codex_home: Path,
        marketplace_name: str,
        rows: dict[tuple[str, str], PluginListRow],
        plugin_sources: dict[str, Path],
    ) -> None:
        issues = plugin_installation_issues(
            catalog,
            marketplace_name=marketplace_name,
            target_root=target_root,
            codex_home=codex_home,
            rows=rows,
            plugin_sources=plugin_sources,
        )
        if issues:
            for issue in issues:
                self.fail(issue)
            return
        self.ok("plugin discovery profile matches repository, CLI, cache, and inactive universal layer")

    def check_plugin_cache(
        self,
        plugins: list[str],
        *,
        codex_home: Path,
        plugin_sources: dict[str, Path],
    ) -> None:
        failures: list[str] = []
        cache_root = codex_home / "plugins" / "cache"
        for selector in plugins:
            plugin_name, separator, marketplace_name = selector.partition("@")
            if not separator or not plugin_name or not marketplace_name:
                failures.append(f"invalid plugin selector: {selector!r}")
                continue
            plugin_dir = plugin_sources.get(plugin_name)
            if plugin_dir is None:
                failures.append(f"{selector}: no source path from marketplace catalog")
                continue
            source_manifest = plugin_dir / ".codex-plugin" / "plugin.json"
            try:
                source_name, source_version = plugin_manifest_identity(source_manifest, label="source")
            except ValueError as exc:
                failures.append(f"{selector}: {exc}")
                continue
            if source_name != plugin_name:
                failures.append(
                    f"{selector}: source manifest name mismatch at {source_manifest}; "
                    f"expected {plugin_name!r}, found {source_name!r}"
                )
                continue
            plugin_root = cache_root / marketplace_name / plugin_name
            version_roots = (
                sorted(path for path in plugin_root.iterdir() if path.is_dir())
                if plugin_root.is_dir()
                else []
            )
            if len(version_roots) != 1:
                found_text = ", ".join(path.name for path in version_roots) or "none"
                failures.append(
                    f"{selector}: expected exactly one cache version {source_version!r}; "
                    f"found versions: {found_text}"
                )
                continue
            version_root = version_roots[0]
            if version_root.is_symlink() or version_root.name != source_version:
                failures.append(
                    f"{selector}: exact cache version mismatch; expected {source_version!r}, "
                    f"found {version_root.name!r}"
                )
                continue
            cache_manifest = version_root / ".codex-plugin" / "plugin.json"
            try:
                cache_name, cache_version = plugin_manifest_identity(cache_manifest, label="cache")
            except ValueError as exc:
                failures.append(f"{selector}: {exc}")
                continue
            if cache_name != source_name:
                failures.append(
                    f"{selector}: cache manifest name mismatch at {cache_manifest}; "
                    f"expected {source_name!r}, found {cache_name!r}"
                )
            if cache_version != source_version:
                failures.append(
                    f"{selector}: cache manifest version mismatch at {cache_manifest}; "
                    f"expected {source_version!r}, found {cache_version!r}"
                )
        if failures:
            self.fail("plugin source/cache identity check failed: " + "; ".join(failures))
            return
        self.ok(f"plugin source/cache manifest identity matches under {cache_root}")

    def check_no_stale_my_codex_plugins(
        self,
        plugins: list[str],
        *,
        codex_home: Path,
        marketplace_name: str,
    ) -> None:
        desired = [selector.split("@", 1)[0] for selector in plugins]
        stale = stale_plugin_names(
            codex_home=codex_home,
            marketplace_name=marketplace_name,
            desired_plugin_names=desired,
        )
        if stale:
            configured = configured_plugin_names(codex_home, marketplace_name)
            cached = cached_plugin_names(codex_home, marketplace_name)
            details = []
            for name in stale:
                locations = []
                if name in configured:
                    locations.append("config")
                if name in cached:
                    locations.append("cache")
                details.append(f"{name} ({'+'.join(locations) or 'unknown'})")
            self.fail(
                "stale my-codex plugins remain. "
                "Run scripts/refresh_my_codex.py --discovery-profile plugin --prune-plugins. "
                f"Stale={', '.join(details)}"
            )
            return
        self.ok("no stale my-codex plugin config or cache entries remain")

    def check_hook_config(self, tooling_python: Path, *, hook_config: Path) -> None:
        if not hook_config.is_file():
            self.fail(f"Watcher skill hook config missing: {hook_config}")
            return
        try:
            config = load_config(hook_config)
        except SystemExit as exc:
            self.fail(str(exc))
            return
        matched_events, issues = find_managed_hook_issues(
            config,
            python_path=tooling_python,
            adapter=adapter_path(),
        )
        if issues:
            self.fail(
                "Watcher skill hook config has stale managed handlers. "
                "Run scripts/refresh_my_codex.py with the same explicit discovery profile. "
                f"Issues: {issues}"
            )
            return
        expected = set(HOOK_EVENTS)
        if matched_events != expected:
            self.fail(
                "Watcher skill hook config event coverage mismatch: "
                f"expected {sorted(expected)}, found {sorted(matched_events)}"
            )
            return
        self.ok(f"Watcher skill hooks match current schema: {hook_config}")

    def check_plugin_validation(
        self,
        tooling_python: Path,
        plugins: list[str],
        *,
        env: dict[str, str],
        validator: Path,
    ) -> None:
        plugin_names = [selector.split("@", 1)[0] for selector in plugins]
        bundled_plugin_names = [
            plugin_name
            for plugin_name in plugin_names
            if plugin_name != "mattpocock-skills"
        ]
        if bundled_plugin_names and not validator.is_file():
            self.fail(f"plugin validator missing: {validator}")
            return
        for plugin_name in plugin_names:
            if plugin_name == "mattpocock-skills":
                command = [
                    str(tooling_python),
                    str(REPO_ROOT / "scripts" / "update_mattpocock_skills.py"),
                    "--validate-only",
                ]
            else:
                command = [
                    str(tooling_python),
                    str(validator),
                    str(REPO_ROOT / "plugins" / plugin_name),
                ]
            result = self.run_command(command, env=env)
            if result.returncode == 0:
                self.ok(f"plugin validation passed: {plugin_name}")
            else:
                output = (result.stderr or result.stdout).strip()
                self.fail(f"plugin validation failed for {plugin_name}: {output}")

    def check_doctor(self, tooling_python: Path, *, env: dict[str, str]) -> None:
        watcher = REPO_ROOT / "plugins" / "watcher" / "scripts" / "watcher"
        result = self.run_command([str(tooling_python), str(watcher), "skill", "doctor"], env=env)
        if result.returncode == 0:
            self.ok("Watcher skill doctor passed")
        else:
            output = (result.stderr or result.stdout).strip()
            self.fail(f"Watcher skill doctor failed: {output}")

    def check_agent_sync(self, *, codex_home: Path, env: dict[str, str]) -> None:
        sync_script = REPO_ROOT / "scripts" / "sync_codex_agents.py"
        if not sync_script.is_file():
            self.fail(f"agent sync script missing: {sync_script}")
            return
        result = self.run_command(
            [sys.executable, str(sync_script), "--check", "--prune", "--codex-home", str(codex_home)],
            env=env,
        )
        if result.returncode == 0:
            self.ok(f"subagent support file is synced: {codex_home / 'agents'}")
        else:
            output = (result.stderr or result.stdout).strip()
            self.fail(f"subagent support file is not synced: {output}")

    def check_agents_skills_layer(
        self,
        tooling_python: Path,
        *,
        target_root: Path,
        env: dict[str, str],
    ) -> None:
        sync_script = REPO_ROOT / "scripts" / "sync_agents_skills.py"
        if not sync_script.is_file():
            self.fail(f"agents skills sync script missing: {sync_script}")
            return
        result = self.run_command(
            [
                str(tooling_python),
                str(sync_script),
                "--repo-root",
                str(REPO_ROOT),
                "--target-root",
                str(target_root),
                "--check",
                "--prune",
            ],
            env=env,
        )
        if result.returncode == 0:
            self.ok("agents skills exposure layer is synced")
        else:
            output = (result.stderr or result.stdout).strip()
            self.fail(f"agents skills exposure layer is not synced: {output}")

    def check_watcher_runtime_cutover(self, *, codex_home: Path) -> None:
        legacy_roots = [codex_home / "skill-watcher", codex_home / "doc-watcher"]
        existing = [path for path in legacy_roots if path.exists()]
        if existing:
            self.fail(
                "legacy Watcher runtime roots still exist. "
                "Run plugins/watcher/scripts/watcher migrate-state --apply. "
                f"Existing={'; '.join(str(path) for path in existing)}"
            )
            return
        self.ok("legacy Watcher runtime roots are absent")

    def finish(self, *, strict_warnings: bool) -> None:
        if strict_warnings and self.warnings:
            self.failures += self.warnings
        if self.failures:
            raise SystemExit(f"check failed with {self.failures} failure(s), {self.warnings} warning(s)")
        print(f"check passed with {self.warnings} warning(s)")


def main() -> None:
    configure_output_streams()

    parser = argparse.ArgumentParser(description="Final checks for my-codex plugin and hook state.")
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
    parser.add_argument("--python", help="Explicit tooling Python expected in hooks and diagnostics.")
    parser.add_argument("--marketplace-name", default="my-codex", help="Configured marketplace name.")
    parser.add_argument("--plugin", action="append", help="Plugin name or selector to check. May be repeated.")
    parser.add_argument("--skip-plugins", action="store_true", help="Deprecated profile bypass; rejected.")
    parser.add_argument("--skip-hooks", action="store_true", help="Skip Watcher skill hook config checks.")
    parser.add_argument("--skip-agents", action="store_true", help="Skip subagent support-file sync checks.")
    parser.add_argument("--skip-agents-skills", action="store_true", help="Deprecated profile bypass; rejected.")
    parser.add_argument(
        "--agents-skills-root",
        default=str(DEFAULT_AGENTS_SKILLS_ROOT),
        help="Universal skill projection root (default: ~/.agents/skills).",
    )
    parser.add_argument("--skip-plugin-validation", action="store_true", help="Skip plugin validator checks.")
    parser.add_argument("--skip-doctor", action="store_true", help="Skip Watcher skill doctor.")
    parser.add_argument("--strict-warnings", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args()

    profile = parse_discovery_profile(args.discovery_profile)
    validate_check_profile(
        CheckProfileOptions(
            profile=profile,
            skip_plugins=args.skip_plugins,
            skip_agents_skills=args.skip_agents_skills,
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
    if profile is DiscoveryProfile.PLUGIN or configured_plugin_names(
        codex_home,
        args.marketplace_name,
    ):
        codex = resolve_codex_executable(args.codex, codex_home=codex_home)

    source_plugins = [
        f"{plugin_name}@{args.marketplace_name}"
        for plugin_name in catalog.plugin_names
    ]
    validator = Path(env["PLUGIN_VALIDATOR"])

    runner = CheckRunner()
    runner.check_tooling_python(tooling_python, env=env)
    if profile is DiscoveryProfile.PLUGIN:
        assert codex is not None
        plugins_to_check, desired_plugins = plugin_check_scopes(
            None,
            args.marketplace_name,
        )
        plugin_sources = runner.check_marketplace_file(plugins_to_check)
        rows = runner.read_plugin_rows(codex, env=env)
        if plugin_sources is not None:
            runner.check_plugin_packages(catalog, plugin_sources=plugin_sources)
        if plugin_sources is not None and rows is not None:
            runner.check_plugin_discovery_profile(
                catalog,
                target_root=agents_skills_root,
                codex_home=codex_home,
                marketplace_name=args.marketplace_name,
                rows=rows,
                plugin_sources=plugin_sources,
            )
        runner.check_no_stale_my_codex_plugins(
            desired_plugins,
            codex_home=codex_home,
            marketplace_name=args.marketplace_name,
        )
    else:
        rows: dict[tuple[str, str], PluginListRow] = {}
        if codex is not None:
            inspected = runner.read_plugin_rows(codex, env=env)
            if inspected is not None:
                rows = inspected
        runner.check_universal_discovery_profile(
            catalog,
            target_root=agents_skills_root,
            marketplace_name=args.marketplace_name,
            rows=rows,
        )
    if not args.skip_hooks:
        runner.check_hook_config(tooling_python, hook_config=codex_home / "hooks.json")
    runner.check_watcher_runtime_cutover(codex_home=codex_home)
    if not args.skip_agents:
        runner.check_agent_sync(codex_home=codex_home, env=env)
    if profile is DiscoveryProfile.UNIVERSAL:
        runner.check_agents_skills_layer(
            tooling_python,
            target_root=agents_skills_root,
            env=env,
        )
    if not args.skip_plugin_validation:
        runner.check_plugin_validation(
            tooling_python,
            source_plugins,
            env=env,
            validator=validator,
        )
    if not args.skip_doctor:
        runner.check_doctor(tooling_python, env=env)
    runner.finish(strict_warnings=args.strict_warnings)


if __name__ == "__main__":
    main()
