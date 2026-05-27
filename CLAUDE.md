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

## Testing

**Stack**: `pytest 4.6.x` + `pytest-django 3.4.x` + `mock 2.0` — all Python 2.7 compatible.

**Run all tests** (inside Docker):
```bash
docker exec -it ironweb_local pytest
```

**Run with coverage** (target ≥ 80%):
```bash
docker exec -it ironweb_local pytest --cov=. --cov-report=term-missing
```

**Run a specific file**:
```bash
docker exec -it ironweb_local pytest general/tests/test_utilidades.py -v
```

**Config files**:
- `pytest.ini` — test discovery, `DJANGO_SETTINGS_MODULE = ggcontable.settings_test`
- `ggcontable/settings_test.py` — SQLite in-memory, no env vars required
- `conftest.py` — shared fixtures (`mock_request`, `mock_empresa`, `mock_usuario`)

**Test locations**:
| Module | Test file |
|---|---|
| `general/utilidades.py` | `general/tests/test_utilidades.py` |
| `ggcontable/middleware.py` | `ggcontable/tests/test_middleware.py` |
| `entidades/models.py` | `entidades/tests/test_models.py` |
| `comprobantes/models.py` | `comprobantes/tests/test_models.py` |
| `usuarios/authentication.py` | `usuarios/tests/test_authentication.py` |

**Patterns used**:
- Pure functions (utilidades): plain `def test_*` with `pytest.mark.parametrize`
- Model methods without DB: `Model.__new__(Model)` to create instances in-memory
- Middleware / auth backend: `monkeypatch` for env vars, `patch` for DB calls
- DB tests: `@pytest.mark.django_db` only where strictly needed

**Mocking import**:
```python
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch  # Python 2.7 backport
```

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