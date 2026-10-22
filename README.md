# Online Chat Quick Start

This project contains the initial quality-gated skeleton for the approved online chat application. The backend uses Flask 3.1.3 with uv-managed dependencies and DuckDB; the frontend uses Vue and Vite.

## Development

Install Python dependencies with `uv sync --frozen` and frontend dependencies with `npm ci`. The DuckDB feasibility gate must pass before startup or quality checks:

```sh
npm run quality:gate
```

The only supported production WSGI entry is the single-worker Gunicorn configuration. It requires `APP_ENV=production`, rejects `APP_WORKERS` values other than `1`, and holds an exclusive lock beside the DuckDB file so a second process using the same file fails:

```sh
npm run serve:production
```

Python checks:

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Frontend checks:

```sh
npm run lint
npm run test:unit
npm run test:e2e
npm run build
```

The approved DuckDB feasibility conclusion is recorded at `../.agents/tasks/online_chat/duckdb-feasibility.md`; startup and the quality gate accept only its exact `## 结论` value `**满足**`. This skeleton does not yet implement room, invitation, media, or signaling behavior.
