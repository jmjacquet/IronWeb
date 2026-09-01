# IronWeb Architecture

Django 1.8 / Python 2.7 multi-tenant accounting & invoicing app. This doc consolidates what's been learned across sessions about the deployment, architecture, and config — beyond what's in `AGENTS.md`.

## Multi-tenancy

- Subdomain-based (`<tenant>.ironwebgestion.com.ar`). Each tenant has its own MySQL database, but **all tenants share one app process**.
- `TenantMiddleware` (`ggcontable/middleware.py`) must be first in `MIDDLEWARE_CLASSES`. Per request it:
  1. Reads `Host` (or `X-Forwarded-Host` behind Traefik).
  2. Looks it up in `TENANT_MAP` — a dict hardcoded in `middleware.py`, overlaid by a `TENANT_MAP` JSON env var (used in `docker-compose.local.yml` to map `localhost`/`127.0.0.1` to the `prueba` tenant).
  3. Mutates `connection.settings_dict['NAME']` directly on the shared `default` DB connection, only closing/reopening it when the tenant actually changes between consecutive requests.
- `ggcontable/db_router.py` is **dead code**: it implements an alternate thread-local `TenantRouter`, but it's never wired into `DATABASE_ROUTERS` in any settings module. Ignore it — the middleware above is the only thing that actually switches tenants.
- In application code, the canonical way to resolve "which company/tenant-config row applies to the current user" is `empresa_actual(request)` in `general/utilidades.py`, which resolves to `request.user.userprofile.id_usuario.empresa`.
- Not every tenant necessarily lives inside this shared multi-tenant deploy: Dokploy also hosts a fully separate `laboralsalud` / `laboralsalud_dev` / `laboralsalud-static` project alongside `ironweb` / `ironweb_dev` / `ironweb-static` / `ironweb-ftp`. That suggests `laboralsalud` may run as its own standalone deploy rather than just a database row in the shared setup — unconfirmed, worth checking before assuming all tenants are interchangeable.

## Auth

- Custom `UsuarioBackend` (`usuarios/authentication.py`), chained after `ModelBackend` in `AUTHENTICATION_BACKENDS`.
- Authenticates against the legacy `usu_usuario` table (per-tenant), then lazily creates/links a Django `User` + `UserProfile` on first login.

## AFIP electronic invoicing (`felectronica/`)

- Wraps `pyafipws/`, a vendored third-party AFIP SOAP client (WSAA auth + WSFEv1 invoicing). Treat `pyafipws/` as third-party: patch minimally, don't refactor its style.
- Core entry point: `facturarAFIP(request, idCpb)` in `felectronica/facturacion.py`, triggered by the `/comprobantes/cpb_facturar_afip/` GET view (`comprobantes/views.py`), called from the browser via `facturar(id)` in `staticfiles/js/scripts/scripts_listado_ventas.js`.
- Transport is `pysimplesoap` (pip-installed). WSAA CMS signing normally uses M2Crypto, but falls back to shelling out to system `openssl smime -sign` when `import M2Crypto` fails — which is actually the active path in the running containers today: `python-m2crypto` is apt-installed in the Dockerfile, but for the wrong Python interpreter, so the import fails at runtime and the openssl fallback is what's really in use.
- Certs/keys: homologación (test) mode uses `empresa.fe_crt`/`fe_key` (company-level); producción mode uses `cpb.get_pto_vta().fe_crt`/`fe_key` (per punto-de-venta). Files live under `MEDIA_ROOT/certificados/<filename>` (i.e. `CERTIFICADOS_PATH`, see Config below).
- WSAA ticket (TA) is cached to `CERTIFICADOS_PATH/TA-<cuit>-<service>.xml`, **unencrypted**, with a hardcoded ~5h TTL — the function's `ttl` parameter exists but is overwritten internally and effectively ignored.
- Homologación vs producción AFIP endpoint URLs (WSDL/WSAA) are hardcoded inline and duplicated across ~6-7 functions in `facturacion.py` — there's no settings variable for this. Which environment a tenant hits is a per-tenant DB flag (`empresa.homologacion`), not a deploy-time setting.
- A commented-out `afip-service` container block in `docker-compose.yml` suggests this was at some point split into (or planned as) a separate microservice; currently it runs in-process.
- No test coverage exists for the `facturarAFIP`/WSAA/WSFEv1 flow — no mocks of `pyafipws.wsfev1.WSFEv1` or `pyafipws.wsaa` in the suite.

### Known AFIP issues

- **Fixed (not yet deployed)**: AFIP's legacy WSFEv1 producción server (`servicios1.afip.gov.ar`) offers a weak DH key, which OpenSSL 1.1.1's default `SECLEVEL=2` rejects (`SSL: DH_KEY_TOO_SMALL`). Fix: a `RUN sed` line in the `Dockerfile` lowering `/etc/ssl/openssl.cnf`'s `CipherString` to `SECLEVEL=1`. Verified against real AFIP producción (`AppServer/DbServer/AuthServer: OK`), but only applied on image rebuild — not yet live anywhere.
- **Open, unresolved**: intermittent `ns1:cms.bad.base64` AFIP WSAA fault seen on the dev deploy for a specific comprobante/tenant. Not the classic passphrase-prompt-corrupts-stdin issue (that tenant's key is an unencrypted PKCS#8 key). Root cause not yet identified.

## Deployment

- One `Dockerfile` (`python:2.7-slim` base) builds a single image used by all three compose files — `docker-compose.local.yml`, `docker-compose.dev.yml`, `docker-compose.yml` (prod). Same image; environment and `GUNICORN_WSGI` target differ per environment.
- Orchestrated by **Dokploy** on a remote host; containers join the `dokploy-network`. **Traefik** handles TLS (Let's Encrypt) and HTTP→HTTPS redirects via compose labels on the prod/dev services.
- Dokploy stacks (confirmed via its API): `ironweb`, `ironweb_dev` (appName `ironwebdev-zaogqj`, repo `IronWeb`/`master`, compose path `./docker-compose.dev.yml`), `ironweb-static`, `ironweb-ftp` — plus the separate `laboralsalud`/`laboralsalud_dev`/`laboralsalud-static` project noted above.
- `docker-compose.static.yml` runs a standalone nginx container serving `/static` and `/media` straight from shared Docker volumes, bypassing Gunicorn entirely — matched by Traefik path-prefix rules with higher priority than the app router.
- `docker-entrypoint.sh`: waits for the DB port to be reachable, optionally runs `collectstatic` (`COLLECT_STATIC=true`), then `exec`s `gunicorn` against `$GUNICORN_WSGI`.
- **Media volume gotcha**: `/app/media` (including AFIP certs under `media/certificados/`) is a named Docker volume, decoupled from the git working tree. Adding files to `media/certificados/` in the repo on the host does **not** put them in a running container — the volume has to be repopulated via rebuild/redeploy or a manual copy.
- `.github/workflows/main.yml` ("Deploy via Git Pull...OpalStack") is a **stale leftover** from the pre-Docker deployment path (SSH into OpalStack, `git pull`, `collectstatic`). It is not how the app deploys today — there is no active CI/CD pipeline for the Docker/Dokploy setup; deploys go through Dokploy directly.
- `opalstack/` at the repo root is unrelated tooling (an Apache memory-check script) from that same legacy era, not part of the Django app.

### Settings / WSGI map

| Environment | Settings module | WSGI entry point | Compose file |
|---|---|---|---|
| Local dev | `ggcontable.local` | `wsgi_local.py` | `docker-compose.local.yml` |
| Dokploy "dev" | `ggcontable.development` | `wsgi_dev.py` | `docker-compose.dev.yml` |
| Production | `ggcontable.prod` | `wsgi.py` | `docker-compose.yml` |
| Tests | `ggcontable.settings_test` | — (pytest) | — |
| Legacy (OpalStack era, unused) | `ggcontable.docker`, `ggcontable.opal` | `wsgi_sucec.py` | — |

All non-test/non-legacy settings modules import everything from `ggcontable/settings.py` as their base.

## Config / environment variables

- Required: `DB_HOST`, `DB_USER`, `DB_PASS`, `SECRET_KEY`.
- `ENTIDAD_DB` / `ENTIDAD_ID` / `ENTIDAD_DIR` — legacy OpalStack-era carryover (one process per tenant, back then). Now set dynamically by `TenantMiddleware` on every request; not meant to be hand-set, except as the `TENANT_MAP` JSON overlay for local/dev hosts.
- `CERTIFICADOS_PATH` (`ggcontable/settings.py`) = `MEDIA_ROOT/certificados/` — where AFIP certs and cached WSAA tickets live.
- `COLLECT_STATIC`, `RUN_MIGRATIONS`, `GUNICORN_*` — deploy-time toggles read by `docker-entrypoint.sh` / compose files. See `.env.example` for the full list (email, Gunicorn tuning, session cookie name, etc).
- `reqs.txt` is what's actually pinned and installed (py2.7 / Django 1.8) — this is the real dependency list the Dockerfile uses. `requirements.txt` is a **draft for a hypothetical future Django 5 / Python 3.11 migration**; it is not used by the current Dockerfile and shouldn't be treated as authoritative.

## Tests

- pytest, config in `pytest.ini`: `DJANGO_SETTINGS_MODULE=ggcontable.settings_test`, SQLite in-memory (no live MySQL needed).
- Test dirs: `general/tests`, `ggcontable/tests`, `entidades/tests`, `comprobantes/tests`, `usuarios/tests`.
- Shared fixtures (`mock_request`, `mock_empresa`, `mock_usuario`) live in root `conftest.py` — but as of this writing nothing actually imports them, and `mock_request` doesn't set `.user`/`.userprofile`/`.id_usuario`, so they aren't wired together yet.
- No coverage exists for the AFIP/WSAA/WSFEv1 flow (see above).

## Legacy vs. current — quick reference

Everything below is pre-Docker OpalStack-era (Apache + mod_wsgi, one process per tenant) and is **not** part of the current deploy path; kept for reference only:

- `ggcontable.docker`, `ggcontable.opal` settings modules
- `wsgi_sucec.py`
- `opalstack/` directory at repo root
- `.github/workflows/main.yml`
- `ggcontable/db_router.py` (dead code, separate issue from the OpalStack legacy — never wired up, of unclear origin)
