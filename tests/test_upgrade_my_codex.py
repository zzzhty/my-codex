from __future__ import annotations

import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
UPGRADE_SCRIPT = REPO_ROOT / "scripts" / "upgrade_my_codex.sh"
POWERSHELL_UPGRADE_SCRIPT = REPO_ROOT / "scripts" / "upgrade_my_codex.ps1"


def extension_platform_dir() -> str | None:
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Linux":
        platform_name = "linux"
    elif system == "Darwin":
        platform_name = "macos"
    else:
        return None

    if machine in {"amd64", "x86_64"}:
        architecture = "x86_64"
    elif machine in {"aarch64", "arm64"}:
        architecture = "aarch64"
    else:
        return None
    return f"{platform_name}-{architecture}"


def write_fake_codex(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "#!/usr/bin/env sh\n"
        "if [ \"${1-}\" = \"--version\" ]; then\n"
        "    echo 'codex-cli 999.0.0-test'\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_python_proxy(path: Path, *, reject_profile_helpers: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rejection = (
        'case "${1-}" in\n'
        '    *refresh_my_codex.py|*check_my_codex.py)\n'
        '        echo "bootstrap Python has no PyYAML" >&2\n'
        '        exit 91\n'
        '        ;;\n'
        'esac\n'
        if reject_profile_helpers
        else ""
    )
    path.write_text(
        "#!/usr/bin/env sh\n"
        + rejection
        + f"exec {shlex.quote(sys.executable)} \"$@\"\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


@unittest.skipIf(os.name == "nt", "Unix wrapper test")
class UnixUpgradeWrapperTests(unittest.TestCase):
    def run_upgrade(
        self,
        *,
        env: dict[str, str],
        codex_home: Path,
        profile: str = "plugin",
        bootstrap_python: Path | str = sys.executable,
        tooling_python: Path | str | None = sys.executable,
        extra_args: list[str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            str(UPGRADE_SCRIPT),
            "--discovery-profile",
            profile,
            "--bootstrap-python",
            str(bootstrap_python),
            "--codex-home",
            str(codex_home),
            "--dry-run",
            "--skip-check",
        ]
        if tooling_python is not None:
            command.extend(["--tooling-python", str(tooling_python)])
        command.extend(extra_args or [])
        return subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

    def test_bootstrap_python_without_yaml_never_runs_profile_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            user_home = root / "home"
            codex_home = user_home / ".codex"
            bootstrap_python = root / "bin" / "bootstrap-python"
            tooling_python = codex_home / "venvs" / "my-codex" / "bin" / "python"
            write_python_proxy(bootstrap_python, reject_profile_helpers=True)
            write_python_proxy(tooling_python, reject_profile_helpers=False)
            env = os.environ.copy()
            env.update({"HOME": str(user_home), "PATH": "/usr/bin:/bin"})
            env.pop("CODEX_BIN", None)

            result = self.run_upgrade(
                env=env,
                codex_home=codex_home,
                profile="universal",
                bootstrap_python=bootstrap_python,
                tooling_python=None,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"+ {bootstrap_python} {REPO_ROOT / 'scripts' / 'bootstrap_tooling_env.py'}",
            result.stdout,
        )
        self.assertIn(
            f"+ {tooling_python} {REPO_ROOT / 'scripts' / 'refresh_my_codex.py'}",
            result.stdout,
        )
        self.assertNotIn("bootstrap Python has no PyYAML", result.stderr)

    def test_wrapper_delegates_codex_resolution_and_keeps_codex_bin_strict(self) -> None:
        platform_dir = extension_platform_dir()
        if platform_dir is None:
            self.skipTest("unsupported Codex extension platform")
        system_path = "/usr/bin:/bin"
        if shutil.which("codex", path=system_path):
            self.skipTest("test PATH unexpectedly contains codex")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            user_home = root / "home"
            codex_home = user_home / ".codex"
            standalone_cli = codex_home / "packages" / "standalone" / "current" / "bin" / "codex"
            extension_cli = (
                user_home
                / ".vscode-server"
                / "extensions"
                / "openai.chatgpt-1.2.3"
                / "bin"
                / platform_dir
                / "codex"
            )
            write_fake_codex(standalone_cli)
            write_fake_codex(extension_cli)

            env = os.environ.copy()
            env.update({"HOME": str(user_home), "PATH": system_path})
            env.pop("CODEX_BIN", None)
            env.pop("CODEX_HOME", None)
            env.pop("CODEX_INSTALL_DIR", None)

            standalone_result = self.run_upgrade(env=env, codex_home=codex_home)
            self.assertEqual(standalone_result.returncode, 0, standalone_result.stderr)
            self.assertIn("CodexPath=auto-if-plugin-removal-is-required", standalone_result.stdout)
            self.assertIn(str(standalone_cli), standalone_result.stdout)
            self.assertIn("--discovery-profile plugin", standalone_result.stdout)

            standalone_cli.unlink()
            extension_result = self.run_upgrade(
                env=env,
                codex_home=codex_home,
                extra_args=["--codex", str(extension_cli)],
            )
            self.assertEqual(extension_result.returncode, 0, extension_result.stderr)
            self.assertIn(str(extension_cli), extension_result.stdout)

            env["CODEX_BIN"] = str(root / "missing-configured-codex")
            strict_result = self.run_upgrade(env=env, codex_home=codex_home)
            self.assertNotEqual(strict_result.returncode, 0)
            self.assertIn("executable not found. Checked:", strict_result.stderr)
            self.assertIn(env["CODEX_BIN"], strict_result.stderr)

    def test_invalid_distribution_fails_before_codex_resolution_in_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            shutil.copytree(
                REPO_ROOT,
                repo,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            marketplace = repo / ".agents" / "plugins" / "marketplace.json"
            payload = json.loads(marketplace.read_text(encoding="utf-8"))
            payload["plugins"][0]["policy"]["installation"] = "INSTALLED_BY_DEFAULT"
            marketplace.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

            user_home = root / "home"
            codex_home = user_home / ".codex"
            missing_codex = root / "missing-codex"
            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(user_home),
                    "PATH": "/usr/bin:/bin",
                    "CODEX_BIN": str(missing_codex),
                }
            )
            result = subprocess.run(
                [
                    str(repo / "scripts" / "upgrade_my_codex.sh"),
                    "--discovery-profile",
                    "plugin",
                    "--bootstrap-python",
                    sys.executable,
                    "--codex-home",
                    str(codex_home),
                    "--tooling-python",
                    sys.executable,
                    "--dry-run",
                    "--skip-check",
                ],
                cwd=repo,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("installation policy must be 'AVAILABLE'", result.stderr)
        self.assertNotIn("executable not found", result.stderr)
        self.assertNotIn(str(missing_codex), result.stderr)

    def test_missing_profile_fails_before_executable_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = os.environ.copy()
            env.update({"HOME": str(root / "home"), "PATH": "/usr/bin:/bin"})
            env["CODEX_BIN"] = str(root / "missing-codex")
            result = subprocess.run(
                [str(UPGRADE_SCRIPT), "--dry-run", "--skip-check"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("missing required --discovery-profile", result.stderr)
        self.assertNotIn("Codex CLI", result.stderr)

    def test_universal_profile_does_not_require_codex_when_no_plugin_is_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            user_home = root / "home"
            codex_home = user_home / ".codex"
            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(user_home),
                    "PATH": "/usr/bin:/bin",
                    "CODEX_BIN": str(root / "missing-codex"),
                }
            )
            result = self.run_upgrade(
                env=env,
                codex_home=codex_home,
                profile="universal",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CodexPath=auto-if-plugin-removal-is-required", result.stdout)
        self.assertIn("--discovery-profile universal", result.stdout)

    def test_wrapper_only_forwards_git_ref_when_the_user_supplies_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            user_home = root / "home"
            codex_home = user_home / ".codex"
            env = os.environ.copy()
            env.update({"HOME": str(user_home), "PATH": "/usr/bin:/bin"})

            default_result = self.run_upgrade(
                env=env,
                codex_home=codex_home,
                profile="universal",
            )
            explicit_result = self.run_upgrade(
                env=env,
                codex_home=codex_home,
                profile="universal",
                extra_args=["--git-ref", "release"],
            )

        self.assertEqual(default_result.returncode, 0, default_result.stderr)
        self.assertNotIn("--git-ref", default_result.stdout)
        self.assertEqual(explicit_result.returncode, 0, explicit_result.stderr)
        self.assertIn("--git-ref release", explicit_result.stdout)


class PowerShellUpgradeWrapperContractTests(unittest.TestCase):
    def test_required_profile_is_forwarded_to_refresh_and_check(self) -> None:
        script = POWERSHELL_UPGRADE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('[ValidateSet("universal", "plugin")]', script)
        self.assertIn('throw "missing required -DiscoveryProfile universal|plugin"', script)
        self.assertGreaterEqual(script.count('"--discovery-profile", $DiscoveryProfile'), 2)
        self.assertIn('$GitRefWasProvided = $PSBoundParameters.ContainsKey("GitRef")', script)
        self.assertIn('if ($GitRefWasProvided)', script)
        self.assertIn('$CodexPathWasProvided = $PSBoundParameters.ContainsKey("CodexPath")', script)
        self.assertNotIn("Resolve-CodexCli", script)
        self.assertNotIn("Get-CodexCliFallbackCandidates", script)
        self.assertIn('"scripts\\bootstrap_tooling_env.py"', script)
        self.assertIn('"--skip-bootstrap"', script)
        self.assertLess(
            script.index('-Exe $BootstrapPython', script.index('$bootstrapArgs')),
            script.index('-Exe $env:MY_CODEX_PYTHON', script.index('$refreshArgs')),
        )


if __name__ == "__main__":
    unittest.main()
