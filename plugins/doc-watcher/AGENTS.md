# Repository Guidelines

## Project Structure & Module Organization

DocWatcher is now an audit-first Codex plugin for personal documentation drift checks. `README.md` is the source of truth for the audit-first product model.

Plugin files live at the repository root: `.codex-plugin/plugin.json` defines the plugin, `skills/doc-alignment` contains the agent workflow, `scripts` contains local audit/report utilities, and `config` contains example repo configuration.

The existing Python backend and Vite/React frontend remain in place as reusable legacy surfaces. Backend application code lives in `backend/app`: API routes are under `api/v1`, business logic under `services`, LLM adapters under `llm`, Git integrations under `git_providers`, database code under `database`, and Pydantic contracts under `schemas`. Backend tests belong in `backend/tests`.

Frontend code lives in `frontend/src`: shared API clients in `api`, reusable UI in `components`, hooks in `hooks`, route views in `pages`, shared types in `types`, and static assets in `assets`.

## Build, Test, and Development Commands

- `python3 scripts/audit_repo.py --repo <path> --name <name> --print-report`: run one read-only repo audit.
- `python3 scripts/generate_report.py --config config/repos.example.json --print-report`: generate a report from configured repos.
- `python3 scripts/generate_report.py --config config/repos.example.json --mode commit-dependent --mark-audited --digest`: generate an incremental digest and advance audit state only after successful audits.
- `python3 scripts/commit_counter.py --config config/repos.example.json`: inspect commit-threshold trigger state.
- `python3 scripts/doctor.py --config config/repos.example.json`: check plugin/runtime/config basics.
- `PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py}" && cd backend && uv run python "$PLUGIN_VALIDATOR" ..`: validate plugin metadata with a Python environment that includes PyYAML.
- `cd backend && uv sync`: install backend dependencies.
- `cd backend && uv run python -m uvicorn app.main:app --reload`: run the legacy FastAPI API on port `8000`.
- `cd backend && uv run --all-groups python -m pytest`: run backend tests.
- `cd backend && uv run ruff check app tests`: lint backend Python.
- `cd frontend && pnpm install`: install frontend dependencies.
- `cd frontend && pnpm dev`: run Vite on port `5173`; `/api` proxies to `localhost:8000`.
- `cd frontend && pnpm build`: type-check and build the frontend.
- `cd frontend && pnpm lint`: run ESLint.

## Coding Style & Naming Conventions

Use 4-space indentation, type hints, `snake_case` modules/functions, and `PascalCase` classes for Python. Prefer Pydantic models for backend contracts and keep route handlers thin by moving workflow logic into `services`.

Plugin scripts should use only the Python standard library unless a dependency is explicitly added and documented. Keep target repo operations read-only by default, and write runtime artifacts only under `$CODEX_HOME/doc-watcher/` unless the user passes an explicit output path.

Use TypeScript and React function components in the frontend. Name components and page files in `PascalCase`, hooks as `useSomething`, and API helpers with clear verb-based names. Keep styling consistent with the Tailwind CSS setup.

## Testing Guidelines

Backend tests use `pytest`; name files `test_*.py` and place them in `backend/tests`, mirroring the app area being tested. Add focused unit tests for services and regression tests for API behavior when changing routes.

For plugin scripts, validate with `python3 -m py_compile scripts/*.py`, `scripts/doctor.py`, and representative dry-run/report commands. Frontend test tooling is not configured yet; if adding it, include scripts in `frontend/package.json`.

## Commit Guidelines

The current history uses short, imperative summaries such as `Init DocWatcher: ...`. Keep commit subjects concise and describe one logical change. Include purpose, main changes, validation results, and screenshots for visible UI changes when handing work over for review.

## Security & Configuration Tips

Backend settings load from `.env`; keep secrets such as `LLM_API_KEY`, provider tokens, and custom base URLs out of git. Do not commit generated folders or local run state such as `.venv`, `node_modules`, `dist`, `__pycache__`, local SQLite databases, or private `config/repos.json` files.
