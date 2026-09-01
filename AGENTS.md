# IronWeb - Django 1.8 / Python 2.7 Legacy Project


## Quick Start

```bash
cd ~/Repo/IronWeb

# Local development with Docker
docker-compose -f docker-compose.local.yml up

# Run Django management commands
docker exec -it ironweb python manage.py <command>
```

## Architecture

- **Multi-tenant**: Subdomain-based (`<tenant>.ironwebgestion.com.ar`). Each tenant has a separate MySQL database, but they all run through **one** app instance.
- **TenantMiddleware** (`ggcontable/middleware.py`) must be FIRST in `MIDDLEWARE_CLASSES`. It reads the `Host` header (or `X-Forwarded-Host` behind Traefik), looks the tenant up in `TENANT_MAP`, and mutates `connection.settings_dict['NAME']` directly on the shared `default` connection — it only closes/reopens the connection when the tenant actually changes between consecutive requests.
- `TENANT_MAP` is hardcoded in `middleware.py` and can be overlaid with a `TENANT_MAP` env var (JSON) — used by `docker-compose.local.yml` to map `localhost`/`127.0.0.1` to the `prueba` tenant.
- **`ggcontable/db_router.py` is dead code** — it implements an alternative thread-local `TenantRouter`, but it's never wired up via `DATABASE_ROUTERS` in any settings file. Don't assume it does anything; the middleware above is the only tenant-switching mechanism that runs.
- **Auth**: Custom `UsuarioBackend` (`usuarios/authentication.py`), chained after `ModelBackend` in `AUTHENTICATION_BACKENDS`. It authenticates against the legacy `usu_usuario` table (per-tenant) and lazily creates/links a Django `User` + `UserProfile` on first login.
- **Settings module map** (all import from `ggcontable/settings.py`):
  - `ggcontable.prod` — current production (Docker/Dokploy), used by `wsgi.py`. Adds `TenantMiddleware`, trusts `X-Forwarded-Proto`.
  - `ggcontable.local` — local Docker dev, used by `wsgi_local.py` / `docker-compose.local.yml`.
  - `ggcontable.development` — Dokploy "development" environment, used by `wsgi_dev.py` / `docker-compose.dev.yml`.
  - `ggcontable.settings_test` — pytest only, SQLite in-memory, no MySQL needed.
  - `ggcontable.docker` / `ggcontable.opal` / `wsgi_sucec.py` — **legacy**, from the pre-Docker OpalStack (Apache+mod_wsgi) era where each tenant got its own hardcoded WSGI file/settings module instead of the shared `TenantMiddleware`. Left for reference; not part of the current deploy path.

## Deployment

- **Current**: Docker containers behind **Traefik**, orchestrated by **Dokploy**, network `dokploy-network`. `docker-compose.yml` (prod) and `docker-compose.dev.yml` (dev) define the app service; Traefik labels handle TLS (Let's Encrypt) and HTTP→HTTPS redirects. `docker-compose.static.yml` runs a separate nginx container serving `/static` and `/media` directly from shared Docker volumes (bypasses Gunicorn for static assets, matched by Traefik path-prefix rules with high priority).
- Entry point is `docker-entrypoint.sh`: waits for the DB port, optionally runs `collectstatic` (`COLLECT_STATIC=true`), then execs `gunicorn` against `$GUNICORN_WSGI`.
- `.github/workflows/main.yml` ("Deploy via Git Pull...OpalStack") is a **stale leftover from the pre-Docker deployment** (SSH into OpalStack, `git pull`, `collectstatic`) — it is not how the app is deployed today. There is no active CI/CD pipeline for the Docker/Dokploy setup; deploys are presumably triggered through Dokploy itself.
- `opalstack/` at the repo root is unrelated tooling (Apache memory-check script), not part of the Django app.

## Key Directories

- `ggcontable/` - Project config (settings per environment, urls, `TenantMiddleware`, WSGI entry points)
- `general/` - Core app (shared views/utilities used across other apps)
- `usuarios/` - Users, auth backend, permissions
- `entidades/` - Client/vendor management
- `productos/` - Product inventory
- `comprobantes/` - Invoices/vouchers (comprobantes)
- `ingresos/`, `egresos/` - Income/expense tracking (separate apps despite the similar name)
- `felectronica/` - AFIP electronic invoicing; wraps `pyafipws/` (vendored third-party AFIP web-service client — WSAA auth, WSFEv1 invoicing). A commented-out `afip-service` container in `docker-compose.yml` suggests this was at some point split into (or planned as) a separate microservice; currently it runs in-process.
- `pyafipws/` - Vendored AFIP SOAP client library, not our code — avoid "fixing" its style, patch minimally.
- `trabajos/`, `reportes/`, `modal/` - Jobs/tasks, reporting, and shared modal/dialog helpers respectively.

## Critical Notes

- **Python 2.7 / Django 1.8** - very old codebase, limited library compatibility. `reqs.txt` is what's actually installed (pinned to py2.7/Django 1.8). `requirements.txt` is a **draft for a future Django 5 / Python 3.11 migration** — not used by the current Dockerfile, don't treat it as the real dependency list.
- **M2Crypto**: Installed from system package (`python-m2crypto`) in the Dockerfile, not pip — `reqs.txt`'s `GRR-M2Crypto` line is explicitly stripped out before `pip install`.
- **Database**: Tenant DB is selected per-request by `TenantMiddleware`, not per-process. `ENTIDAD_DB`/`ENTIDAD_ID`/`ENTIDAD_DIR` env vars are a legacy carry-over from the OpalStack era (one process per tenant) and are now set dynamically by the middleware each request rather than read once at startup.
- **Statics**: `staticfiles/` is the source tree for dev; `collectstatic` writes to `static/`, which in production is served by the separate nginx container in `docker-compose.static.yml`, not by Gunicorn.
- **Tests**: pytest, config in `pytest.ini` (`DJANGO_SETTINGS_MODULE=ggcontable.settings_test`, SQLite in-memory). Test dirs: `general/tests`, `ggcontable/tests`, `entidades/tests`, `comprobantes/tests`, `usuarios/tests`. Shared fixtures (`mock_request`, `mock_empresa`, `mock_usuario`) live in root `conftest.py`. Run with `pytest` (needs `ggcontable.settings_test`, no live MySQL required).

## Environment Variables

Required: `DB_HOST`, `DB_USER`, `DB_PASS`, `SECRET_KEY`. Per-tenant (`ENTIDAD_DB`/`ENTIDAD_ID`/`ENTIDAD_DIR`) are set by `TenantMiddleware`, not meant to be set manually except as a `TENANT_MAP` JSON overlay for local/dev hosts. See `.env.example` for the full list (email, Gunicorn tuning, `COLLECT_STATIC`, `RUN_MIGRATIONS`).

## Skills

- `~/Repo/IronWeb/.claude/skills/django-expert`
- `~/Repo/IronWeb/.claude/skills/django-patterns`
- `~/Repo/IronWeb/.claude/skills/django-security`
- `~/Repo/IronWeb/.claude/skills/python-design-patterns`
- `~/Repo/IronWeb/.claude/skills/python-testing-patterns`
- `~/Repo/IronWeb/.claude/skills/frontend-design`
- `~/Repo/IronWeb/.claude/skills/accessibility`
- `~/Repo/IronWeb/.claude/skills/seo`
- `~/Repo/IronWeb/.claude/skills/python-executor`