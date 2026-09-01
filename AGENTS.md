# IronWeb - Django 1.8 / Python 2.7 Legacy Project

> Full architecture, deployment, and config detail: [docs/architecture.md](docs/architecture.md)

## Quick Start

```bash
cd ~/Repo/IronWeb

# Local development with Docker
docker-compose -f docker-compose.local.yml up

# Run Django management commands
docker exec -it ironweb python manage.py <command>
```

## Architecture

- **Multi-tenant**: Subdomain-based. Each tenant has a separate MySQL database, but they all run through **one** app instance.
- **TenantMiddleware** (`ggcontable/middleware.py`) must be FIRST in `MIDDLEWARE_CLASSES` — it switches the DB connection per request based on the `Host` header.
- **Auth**: Custom `UsuarioBackend` (`usuarios/authentication.py`).
- Deployed via Docker/Dokploy/Traefik. See [docs/architecture.md](docs/architecture.md) for the tenant-switching internals, settings/WSGI module map, AFIP/`felectronica` integration, and full deploy layout.

## Key Directories

- `ggcontable/` - Project config (settings per environment, urls, `TenantMiddleware`, WSGI entry points)
- `general/` - Core app (shared views/utilities used across other apps)
- `usuarios/` - Users, auth backend, permissions
- `entidades/` - Client/vendor management
- `productos/` - Product inventory
- `comprobantes/` - Invoices/vouchers (comprobantes)
- `ingresos/`, `egresos/` - Income/expense tracking (separate apps despite the similar name)
- `felectronica/` - AFIP electronic invoicing; wraps `pyafipws/` (vendored third-party AFIP web-service client). See [docs/architecture.md](docs/architecture.md) for how it works and known issues.
- `pyafipws/` - Vendored AFIP SOAP client library, not our code — avoid "fixing" its style, patch minimally.
- `trabajos/`, `reportes/`, `modal/` - Jobs/tasks, reporting, and shared modal/dialog helpers respectively.

## Critical Notes

- **Python 2.7 / Django 1.8** - very old codebase, limited library compatibility. `reqs.txt` is what's actually installed; `requirements.txt` is an unused draft for a future migration (see [docs/architecture.md](docs/architecture.md)).
- **M2Crypto**: Installed from system package (`python-m2crypto`) in the Dockerfile, not pip.
- **Statics**: `staticfiles/` is the source tree for dev; `collectstatic` writes to `static/`.
- **Tests**: pytest (`pytest.ini` → `ggcontable.settings_test`, SQLite in-memory, no live MySQL required).

## Environment Variables

Required: `DB_HOST`, `DB_USER`, `DB_PASS`, `SECRET_KEY`. See `.env.example` for the full list and [docs/architecture.md](docs/architecture.md) for how tenant DB selection and `TENANT_MAP` work.

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