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

- **Multi-tenant**: Subdomain-based. Each tenant has separate MySQL database.
- **TenantMiddleware** (`ggcontable/middleware.py:141`) must be FIRST in MIDDLEWARE_CLASSES.
- **Auth**: Custom `UsuarioBackend` (`usuarios/authentication.py`).

## Key Directories

- `ggcontable/` - Project config (settings, urls, middleware)
- `general/` - Core app
- `felectronica/` - AFIP electronic invoicing
- `comprobantes/` - Invoices
- `ingresos/egresos/` - Income/expense
- `entidades/` - Client/vendor management
- `productos/` - Product inventory

## Critical Notes

- **Python 2.7 / Django 1.8** - Very old codebase, limited library compatibility
- **M2Crypto**: Installed from system package (`python-m2crypto`), not pip
- **Database**: Set via environment variables `ENTIDAD_DB`, `ENTIDAD_ID`, `ENTIDAD_DIR` per tenant
- **Statics**: Use `staticfiles/` for dev, `static/` for collected production assets

## Environment Variables

Required: `DB_HOST`, `DB_USER`, `DB_PASS`, `SECRET_KEY`, `ENTIDAD_DB`

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