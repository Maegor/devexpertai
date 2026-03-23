# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the dev server
.venv/bin/uvicorn main:app --reload

# Run all tests
.venv/bin/pytest

# Run a single test file
.venv/bin/pytest tests/test_internal_users.py

# Run a single test by name
.venv/bin/pytest tests/test_internal_users.py::test_crear_usuario

# Install a new dependency
uv add <package>
```

## Environment

Requires a `.env` file with:
```
DB_HOST=localhost
DB_NAME=dxpromoter
DB_USER=admin
DB_PASSWORD=...
```

Database tables are created automatically on startup via `Base.metadata.create_all` in the `lifespan` handler in `main.py`. There are no Alembic migrations yet.

## Architecture

The stack is **FastAPI + SQLAlchemy 2.0 async + asyncpg + PostgreSQL 16**. The project follows a strict three-layer separation:

```
router → repository → database
```

- **`models.py`** — All SQLAlchemy ORM models (`InternalUser`, `Partner`, `BillingEntity`). PostgreSQL ENUMs (`InternalRole`, `PartnerStatus`) are defined here as `PgEnum` objects. UUIDs use `sqlalchemy.dialects.postgresql.UUID(as_uuid=True)`.
- **`schemas/`** — Pydantic models per entity (`*Create`, `*Update`, `*Response`). `InternalUserResponse` intentionally omits `password_hash`.
- **`repositories/`** — Async DB access functions. All receive an `AsyncSession` and return ORM objects. No business logic here.
- **`routers/`** — FastAPI `APIRouter` instances. JSON API routers (`internal_user`, `partner`, `billing_entity`) use `response_model` with Pydantic schemas. The `web` router renders Jinja2 HTML templates for the public `/register` flow.
- **`routers/admin.py`** — HTML-first admin panel at `/admin`. Uses `SessionMiddleware` (cookie-based sessions via `itsdangerous`) and `passlib[bcrypt]` to authenticate `InternalUser` records. Sidebar navigation loads content fragments via htmx into `#content-area`.
- **`database.py`** — Single async engine, `SessionLocal` session factory, `get_db` dependency.
- **`config.py`** — `pydantic-settings` reads from `.env`.

## Templates

`templates/` uses Jinja2 with htmx 2.0 + Bootstrap 5.3. The design system uses CSS variables defined in `base.html` (dark theme: `--bg-primary: #1a1b2e`, `--accent: #e8651a`).

- `base.html` — Public pages layout (header + footer)
- `admin/login.html` — Standalone login page (no base inheritance)
- `admin/dashboard.html` — Full admin shell with fixed topbar + sidebar; content area loaded via htmx
- `admin/partials/` — Bare HTML fragments returned to htmx requests (no `<html>` wrapper)

## Permisos pre-aprobados

Las siguientes operaciones están pre-aprobadas en `.claude/settings.json` y no requieren confirmación:

- `uv add <paquete>` — instalar dependencias
- `.venv/bin/python -c <código>` — ejecutar Python inline (verificaciones de imports, etc.)
- `.venv/bin/python -m <módulo>` — ejecutar módulos Python
- `.venv/bin/python seeds/<script>` — ejecutar scripts de seed
- `.venv/bin/pytest <args>` — ejecutar tests
- `PGPASSWORD=... psql -U admin -d dxpromoter -h localhost -c <sql>` — ejecutar SQL directo en BD (migraciones manuales, limpieza de datos)
- Escribir en la ruta del proyecto /home/jomolero/devexpertai/devexpertai sin restricciones (para crear nuevos archivos, editar código, etc.)
## Tests

Tests use `httpx.AsyncClient` with `ASGITransport` (no real HTTP server). The `conftest.py` fixture overrides `get_db` with a test session that hits the real `dxpromoter` database and deletes test data after each test via `DELETE FROM <table>`. Tests are not isolated with a separate test database.
