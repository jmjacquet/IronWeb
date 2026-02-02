# -*- coding: utf-8 -*-
"""
Database router for multi-tenant Django application.
Routes all reads/writes to the tenant database set by TenantMiddleware via thread-local.
Each tenant gets its own connection pool (CONN_MAX_AGE) - no connection churn.
"""
import threading

# Thread-local: current request's tenant DB alias (set by middleware)
_tenant_db = threading.local()


def set_tenant_db(alias):
    """Set the database alias for the current thread/request."""
    _tenant_db.alias = alias


def get_tenant_db():
    """Get the database alias for the current thread. Returns None if not set (e.g. mgmt commands)."""
    return getattr(_tenant_db, 'alias', None)


class TenantRouter(object):
    """
    Routes all DB operations to the tenant database for the current request.
    When no tenant is set (migrations, shell, mgmt commands), uses 'default'.
    """

    def db_for_read(self, model, **hints):
        return get_tenant_db() or 'default'

    def db_for_write(self, model, **hints):
        return get_tenant_db() or 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, **hints):
        # Only migrate 'default' to avoid creating tables in all tenant DBs
        return db == 'default'
