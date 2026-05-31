#!/usr/bin/env python3
"""Bootstrap the shared my-codex tooling Python environment."""

from __future__ import annotations

import argparse
import subprocess
import venv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VENV = Path.home() / ".codex" / "venvs" / "my-codex"
DEFAULT_REQUIREMENTS = REPO_ROOT / "requirements-tools.txt"


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or refresh the shared my-codex tooling venv.")
    parser.add_argument("--venv", default=str(DEFAULT_VENV), help="Target venv path. Defaults to ~/.codex/venvs/my-codex.")
    parser.add_argument(
        "--requirements",
        default=str(DEFAULT_REQUIREMENTS),
        help="Requirements file for my-codex tooling dependencies.",
    )
    args = parser.parse_args()

    venv_path = Path(args.venv).expanduser()
    requirements = Path(args.requirements).expanduser()
    if not requirements.is_file():
        raise SystemExit(f"requirements file does not exist: {requirements}")

    venv_path.parent.mkdir(parents=True, exist_ok=True)
    venv.EnvBuilder(with_pip=True, clear=False).create(venv_path)

    python = venv_path / "bin" / "python"
    if not python.is_file():
        raise SystemExit(f"venv Python was not created: {python}")

    run([str(python), "-m", "pip", "install", "-r", str(requirements)])
    run([str(python), "-c", "import yaml; print('PyYAML', yaml.__version__)"])
    print(f"my-codex tooling Python: {python}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
