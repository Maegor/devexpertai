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
Usa los credenciales del fichero .env para conectarte a la base de datos `dxpromoter` cuando sea necesario. 
- No pidas permiso para ejecutar comandos que interactúen con la base de datos, como correr scripts de seed o ejecutar SQL directo. 
- Sin embargo, ten cuidado al modificar datos en la base de datos, especialmente en un entorno de desarrollo compartido. Asegúrate de no eliminar o alterar datos importantes accidentalmente.

## Tests

Tests use `httpx.AsyncClient` with `ASGITransport` (no real HTTP server). The `conftest.py` fixture overrides `get_db` with a test session that hits the real `dxpromoter` database and deletes test data after each test via `DELETE FROM <table>`. Tests are not isolated with a separate test database.


## Tabla de base de datos

```
CREATE TABLE public.internal_users (
	id uuid NOT NULL,
	name varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
	password_hash varchar(255) NOT NULL,
	totp_secret varchar(255) NULL,
	mfa_enabled bool NOT NULL,
	"role" public.internal_role NOT NULL,
	is_active bool NOT NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	updated_at timestamp DEFAULT now() NOT NULL,
	CONSTRAINT internal_users_email_key UNIQUE (email),
	CONSTRAINT internal_users_pkey PRIMARY KEY (id)
);
```

```
CREATE TABLE public.invoices (
	id uuid NOT NULL,
	partner_id uuid NOT NULL,
	billing_entity_id uuid NULL,
	"type" public."invoice_type" NOT NULL,
	invoice_reference varchar(100) NOT NULL,
	currency varchar(10) NOT NULL,
	net_amount numeric(15, 2) NOT NULL,
	vat_amount numeric(15, 2) NULL,
	gross_total numeric(15, 2) NOT NULL,
	tax_rate varchar(50) NULL,
	pdf_path varchar(500) NOT NULL,
	status public."invoice_status" NOT NULL,
	rejection_reason text NULL,
	scheduled_payment_date date NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	updated_at timestamp DEFAULT now() NOT NULL,
	period_from date NOT NULL,
	period_to date NOT NULL,
	CONSTRAINT invoices_invoice_reference_key UNIQUE (invoice_reference),
	CONSTRAINT invoices_pkey PRIMARY KEY (id),
	CONSTRAINT invoices_billing_entity_id_fkey FOREIGN KEY (billing_entity_id) REFERENCES public.billing_entities(id),
	CONSTRAINT invoices_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE CASCADE
);
```

```
CREATE TABLE public.partner_deals (
	id uuid NOT NULL,
	partner_id uuid NOT NULL,
	description varchar(255) NOT NULL,
	currency varchar(3) NOT NULL,
	status public."partner_deal_status" NOT NULL,
	start_month date NOT NULL,
	end_month date NOT NULL,
	total_cost numeric(15, 2) NOT NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	updated_at timestamp DEFAULT now() NOT NULL,
	CONSTRAINT partner_deals_pkey PRIMARY KEY (id),
	CONSTRAINT partner_deals_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE CASCADE
);
```

```
CREATE TABLE public.partners (
	id uuid NOT NULL,
	fp_promoter_id varchar(255) NULL,
	parent_partner_id uuid NULL,
	"name" varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
	company_name varchar(255) NULL,
	website varchar(255) NULL,
	country varchar(100) NULL,
	collaboration_reason text NULL,
	assigned_sales_rep_id uuid NULL,
	language_preference varchar(10) NOT NULL,
	referral_enabled bool NOT NULL,
	deals_enabled bool NOT NULL,
	status public."partner_status" NOT NULL,
	tc_version_accepted varchar(50) NULL,
	tc_acceptance_date timestamp NULL,
	tc_acceptance_ip varchar(45) NULL,
	tc_accepted_by varchar(255) NULL,
	qb_account_referral varchar(255) NULL,
	qb_account_fixed varchar(255) NULL,
	self_billing_enabled bool NOT NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	updated_at timestamp DEFAULT now() NOT NULL,
	password_hash varchar(255) NULL,
	CONSTRAINT partners_email_key UNIQUE (email),
	CONSTRAINT partners_pkey PRIMARY KEY (id),
	CONSTRAINT partners_assigned_sales_rep_id_fkey FOREIGN KEY (assigned_sales_rep_id) REFERENCES public.internal_users(id),
	CONSTRAINT partners_parent_partner_id_fkey FOREIGN KEY (parent_partner_id) REFERENCES public.partners(id)
);
```

```
CREATE TABLE public.rewards (
	id uuid NOT NULL,
	partner_id uuid NOT NULL,
	transaction_date timestamp NOT NULL,
	product_code varchar(100) NOT NULL,
	customer_id uuid NULL,
	customer_email varchar(255) NULL,
	amount numeric(15, 2) NOT NULL,
	currency varchar(10) NOT NULL,
	reward_type varchar(100) NOT NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	updated_at timestamp DEFAULT now() NOT NULL,
	status public."reward_status" DEFAULT 'Pending'::reward_status NOT NULL,
	invoice_id uuid NULL,
	CONSTRAINT rewards_pkey PRIMARY KEY (id),
	CONSTRAINT rewards_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id) ON DELETE SET NULL,
	CONSTRAINT rewards_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE CASCADE
);
```