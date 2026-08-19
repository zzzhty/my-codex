from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
UPGRADE_SCRIPT = REPO_ROOT / "scripts" / "upgrade_my_codex.sh"


def extension_platform_dir() -> str | None:
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Linux":
        platform_name = "linux"
    elif system == "Darwin":
        platform_name = "darwin"
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


@unittest.skipIf(os.name == "nt", "Unix wrapper test")
class UnixUpgradeWrapperTests(unittest.TestCase):
    def run_upgrade(self, *, env: dict[str, str], codex_home: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                str(UPGRADE_SCRIPT),
                "--bootstrap-python",
                sys.executable,
                "--codex-home",
                str(codex_home),
                "--dry-run",
                "--skip-check",
            ],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

    def test_wrapper_uses_standalone_then_vscode_and_keeps_codex_bin_strict(self) -> None:
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
            self.assertIn(f"CodexPath={standalone_cli}", standalone_result.stdout)

            standalone_cli.unlink()
            extension_result = self.run_upgrade(env=env, codex_home=codex_home)
            self.assertEqual(extension_result.returncode, 0, extension_result.stderr)
            self.assertIn(f"CodexPath={extension_cli}", extension_result.stdout)

            env["CODEX_BIN"] = str(root / "missing-configured-codex")
            strict_result = self.run_upgrade(env=env, codex_home=codex_home)
            self.assertNotEqual(strict_result.returncode, 0)
            self.assertIn("Codex CLI from CODEX_BIN not found", strict_result.stderr)


if __name__ == "__main__":
    unittest.main()
