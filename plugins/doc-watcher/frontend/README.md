# DocWatcher Frontend

React + TypeScript + Vite frontend for the DocWatcher audit cockpit.

The frontend is a presentation adapter for DocWatcher plugin state. It reads the backend `/api/v1/audit/*` endpoints, shows configured repositories, due status, report history, finding backlog, and recent manual runs, then offers handoff prompts for explicit `doc-alignment` implementation mode.

Current routes:

- `/audit`: audit cockpit dashboard.
- `/audit/reports/:reportId`: Markdown report detail plus copyable handoff prompt.
- `/audit/repos/:repoName/findings/:findingId`: finding evidence detail plus copyable handoff prompt.
- `/dashboard`: redirects to `/audit`.

Legacy Projects, Changes, Patches, and Doc PR page files are not mounted as current product navigation.

## Commands

- `pnpm install`: install dependencies from `pnpm-lock.yaml`.
- `pnpm dev`: start Vite on port `5173`; `/api` proxies to the backend at `localhost:8000`.
- `pnpm build`: run TypeScript project build and produce `dist/`.
- `pnpm lint`: run ESLint.
- `pnpm preview`: preview the production build locally.

Run with the backend:

```bash
cd ..
./scripts/doc-watcher up
```

Or run services separately:

```bash
cd ../backend
uv run python -m uvicorn app.main:app --reload

cd ../frontend
pnpm dev
```

## Structure

- `src/api`: typed API clients.
- `src/hooks`: React Query hooks.
- `src/components`: reusable UI components.
- `src/pages`: route-level views.
- `src/types`: shared TypeScript types.
- `src/assets` and `public`: static assets.

The root `README.md` is the source of truth for product direction and MVP scope.

## Validation

- `pnpm build`
- `pnpm lint`
- Browser smoke check `/audit` at desktop and mobile widths when route, layout, or interaction behavior changes.
- Confirm mounted audit routes do not reintroduce legacy current-product labels such as `Patch Generated`, `Open PRs`, or `Doc PRs`.
