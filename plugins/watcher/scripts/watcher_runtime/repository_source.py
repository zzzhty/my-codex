#!/usr/bin/env python3
"""Resolve the canonical repository source used by Watcher runtime commands."""

from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any


REPOSITORY_ROOT_ENV = "MY_CODEX_ROOT"
_CATALOG_MODULES: dict[Path, ModuleType] = {}


@dataclass(frozen=True)
class RepositorySource:
    root: Path
    catalog_module: Path
    watcher_plugin: Path
    watcher_cli: Path


def expand_path(raw: str | Path) -> Path:
    if isinstance(raw, Path):
        return raw.expanduser()
    return Path(os.path.expandvars(str(raw))).expanduser()


def resolve_repository_source(repo_root: str | Path | None = None) -> RepositorySource:
    """Resolve and validate one explicit repository-root contract."""

    raw_root = repo_root if repo_root is not None else os.environ.get(REPOSITORY_ROOT_ENV)
    if raw_root is None or not str(raw_root).strip():
        raise SystemExit(
            "my-codex repository root is required; pass --repo-root or set "
            f"{REPOSITORY_ROOT_ENV}"
        )
    candidate = expand_path(raw_root)
    try:
        root = candidate.resolve(strict=True)
    except OSError as exc:
        raise SystemExit(f"cannot resolve my-codex repository root {candidate}: {exc}") from exc
    if not root.is_dir():
        raise SystemExit(f"my-codex repository root is not a directory: {root}")

    catalog_module = root / "scripts" / "repo_skill_catalog.py"
    watcher_plugin = root / "plugins" / "watcher"
    watcher_cli = watcher_plugin / "scripts" / "watcher"
    required = (
        (catalog_module, "canonical repository skill catalog"),
        (watcher_cli, "Watcher CLI"),
    )
    for path, label in required:
        if not path.is_file():
            raise SystemExit(f"{label} missing under explicit repository root: {path}")
    return RepositorySource(
        root=root,
        catalog_module=catalog_module,
        watcher_plugin=watcher_plugin,
        watcher_cli=watcher_cli,
    )


def _catalog_module(source: RepositorySource) -> ModuleType:
    cached = _CATALOG_MODULES.get(source.catalog_module)
    if cached is not None:
        return cached
    module_name = f"_watcher_repo_skill_catalog_{len(_CATALOG_MODULES)}"
    spec = importlib.util.spec_from_file_location(module_name, source.catalog_module)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load canonical repository skill catalog: {source.catalog_module}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    _CATALOG_MODULES[source.catalog_module] = module
    return module


def load_repository_skill_catalog(source: RepositorySource) -> Any:
    """Load the canonical catalog implementation from the explicit source root."""

    module = _catalog_module(source)
    loader = getattr(module, "load_repo_skill_catalog", None)
    if not callable(loader):
        raise SystemExit(
            "canonical repository skill catalog has no load_repo_skill_catalog entrypoint: "
            f"{source.catalog_module}"
        )
    return loader(source.root)
