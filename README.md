# IronWeb

A multi-tenant Django 1.8 / Python 2.7 accounting and invoicing application.

## Quick Start

```bash
# Local development with Docker
docker-compose -f docker-compose.local.yml up

# Run Django management commands
docker exec -it ironweb python manage.py <command>
docker exec -it ironweb python manage.py migrate
docker exec -it ironweb python manage.py collectstatic --noinput
```

## Architecture

- **Multi-tenant**: Subdomain-based (e.g., `prueba.ironwebgestion.com.ar`). Each tenant has separate MySQL database.
- **TenantMiddleware** (`ggcontable/middleware.py:141`) must be FIRST in MIDDLEWARE_CLASSES - it switches the database per request.
- **Settings**: Use `ggcontable.local` for local dev (via `manage.py`), `ggcontable.settings` for production.
- **Auth**: Custom `UsuarioBackend` (`usuarios/authentication.py`).

## Key Directories

- `ggcontable/` - Project config (settings, urls, middleware)
- `general/` - Core app (views, models, utilities)
- `felectronica/` - AFIP electronic invoicing (pyafipws integration)
- `comprobantes/` - Invoices and vouchers
- `ingresos/egresos/` - Income/expense tracking
- `entidades/` - Client/vendor management
- `productos/` - Product inventory

## Critical Notes

- **Python 2.7 / Django 1.8** - Very old codebase, limited library compatibility
- **M2Crypto**: Installed from system package (`python-m2crypto`), not pip
- **Database**: Set via environment variables `ENTIDAD_DB`, `ENTIDAD_ID`, `ENTIDAD_DIR` per tenant
- **Static files**: Use `staticfiles/` for development, `static/` for collected production assets
- **No formal test suite** - Tests in `modal/tests.py` and `trabajos/tests.py` are minimal
- **Production**: Deployed via Dokploy/Traefik (see `docker-compose.yml`)

## Environment Variables

Required: `DB_HOST`, `DB_USER`, `DB_PASS`, `SECRET_KEY`, `ENTIDAD_DB` (per request by middleware)

## Common Tasks

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Shell access
python manage.py shell

# Create superuser
python manage.py createsuperuser
```

---

For detailed developer instructions, see [AGENTS.md](./AGENTS.md).