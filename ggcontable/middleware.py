# -*- coding: utf-8 -*-
"""
Tenant Middleware for Multi-tenant Django Application
Detects tenant from subdomain (Host header) and switches DB connection per request.

Works with Traefik/Nginx: all subdomains hit the same app; Host header determines tenant.
Only closes connection when tenant changes (same-tenant requests reuse connection).
"""
import os
import json
import threading

# Track last tenant per thread - avoid closing when same tenant gets consecutive requests
_last_tenant = threading.local()

# Tenant configuration map (fallback if env vars not set)
# Maps subdomain to tenant database and settings
TENANT_MAP = {
    'prueba.ironwebgestion.com.ar': {
        'ENTIDAD_ID': '1',
        'ENTIDAD_DB': 'ironweb_prueba',
        'ENTIDAD_DIR': 'prueba',
    },
    'www.prueba.ironwebgestion.com.ar': {
        'ENTIDAD_ID': '1',
        'ENTIDAD_DB': 'ironweb_prueba',
        'ENTIDAD_DIR': 'prueba',
    },
    'mullertma.ironwebgestion.com.ar': {
        'ENTIDAD_ID': '10',
        'ENTIDAD_DB': 'ironweb_mullertma',
        'ENTIDAD_DIR': 'mullertma',
    },
    'www.mullertma.ironwebgestion.com.ar': {
        'ENTIDAD_ID': '10',
        'ENTIDAD_DB': 'ironweb_mullertma',
        'ENTIDAD_DIR': 'mullertma',
    },
    # 'sucec.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '2',
    #     'ENTIDAD_DB': 'ironweb_sucec',
    #     'ENTIDAD_DIR': 'sucec',
    # },
    # 'www.sucec.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '2',
    #     'ENTIDAD_DB': 'ironweb_sucec',
    #     'ENTIDAD_DIR': 'sucec',
    # },
    # 'digra.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '3',
    #     'ENTIDAD_DB': 'ironweb_digra',
    #     'ENTIDAD_DIR': 'digra',
    # },
    # 'www.digra.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '3',
    #     'ENTIDAD_DB': 'ironweb_digra',
    #     'ENTIDAD_DIR': 'digra',
    # },
    # # 'brolcazsrl.ironwebgestion.com.ar': {
    # #     'ENTIDAD_ID': '4',
    # #     'ENTIDAD_DB': 'ironweb_brolcazsrl',
    # #     'ENTIDAD_DIR': 'brolcazsrl',
    # # },
    # # 'www.brolcazsrl.ironwebgestion.com.ar': {
    # #     'ENTIDAD_ID': '4',
    # #     'ENTIDAD_DB': 'ironweb_brolcazsrl',
    # #     'ENTIDAD_DIR': 'brolcazsrl',
    # # },
    # 'cornercorto.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '5',
    #     'ENTIDAD_DB': 'ironweb_cornercorto',
    #     'ENTIDAD_DIR': 'cornercorto',
    # },
    # 'www.cornercorto.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '5',
    #     'ENTIDAD_DB': 'ironweb_cornercorto',
    #     'ENTIDAD_DIR': 'cornercorto',
    # },
    # 'laboralsaludsf.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '6',
    #     'ENTIDAD_DB': 'ironweb_laboralsaludsf',
    #     'ENTIDAD_DIR': 'laboralsaludsf',
    # },
    # 'www.laboralsaludsf.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '6',
    #     'ENTIDAD_DB': 'ironweb_laboralsaludsf',
    #     'ENTIDAD_DIR': 'laboralsaludsf',
    # },
    # 'labartoladeco.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '7',
    #     'ENTIDAD_DB': 'ironweb_labartoladeco',
    #     'ENTIDAD_DIR': 'labartoladeco',
    # },
    # 'www.labartoladeco.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '7',
    #     'ENTIDAD_DB': 'ironweb_labartoladeco',
    #     'ENTIDAD_DIR': 'labartoladeco',
    # },
    # 'cirugiamf.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '8',
    #     'ENTIDAD_DB': 'ironweb_cirugiamf',
    #     'ENTIDAD_DIR': 'cirugiamf',
    # },
    # 'www.cirugiamf.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '8',
    #     'ENTIDAD_DB': 'ironweb_cirugiamf',
    #     'ENTIDAD_DIR': 'cirugiamf',
    # },
    # 'development.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '9',
    #     'ENTIDAD_DB': 'ironweb_development',
    #     'ENTIDAD_DIR': 'development',
    # },
    # 'www.development.ironwebgestion.com.ar': {
    #     'ENTIDAD_ID': '9',
    #     'ENTIDAD_DB': 'ironweb_development',
    #     'ENTIDAD_DIR': 'development',
    # },
}


def get_tenant_map():
    """
    Get tenant configuration map from environment variable or use hardcoded map.
    Environment variable TENANT_MAP should be a JSON string.
    Example: TENANT_MAP='{"subdomain.example.com": {"ENTIDAD_ID": "1", "ENTIDAD_DB": "db1", "ENTIDAD_DIR": "dir1"}}'
    """
    tenant_map_env = os.environ.get('TENANT_MAP')
    if tenant_map_env:
        try:
            return json.loads(tenant_map_env)
        except (json.JSONDecodeError, ValueError):
            # If JSON parsing fails, fall back to hardcoded map
            pass
    return TENANT_MAP


class TenantMiddleware(object):
    """
    Middleware to detect tenant from request host and set environment variables.
    This must be the FIRST middleware in MIDDLEWARE_CLASSES.

    Configuration priority:
    1. Environment variable TENANT_MAP (JSON string)
    2. Hardcoded TENANT_MAP in this file
    3. Default fallback values
    """

    def __init__(self, get_response=None):
        # Django 1.8 compatibility
        self.get_response = get_response
        # Load tenant map once at initialization
        self.tenant_map = get_tenant_map()

    def process_request(self, request):
        """Process request and set tenant environment variables"""
        # Get host - use X-Forwarded-Host when behind Traefik/Nginx (original client host)
        host = request.META.get('HTTP_X_FORWARDED_HOST') or request.get_host()
        host = host.split(',')[0].strip().split(':')[0].lower()

        # Look up tenant configuration
        tenant_config = self.tenant_map.get(host)

        if tenant_config:
            # Set environment variables for this request
            os.environ['ENTIDAD_ID'] = tenant_config['ENTIDAD_ID']
            os.environ['ENTIDAD_DB'] = tenant_config['ENTIDAD_DB']
            os.environ['ENTIDAD_DIR'] = tenant_config['ENTIDAD_DIR']

            # Store in request for easy access in views
            request.tenant_id = tenant_config['ENTIDAD_ID']
            request.tenant_db = tenant_config['ENTIDAD_DB']
            request.tenant_dir = tenant_config['ENTIDAD_DIR']
        else:
            # Host not in TENANT_MAP - return 404 (like Apache: no VirtualHost = no response)
            from django.http import HttpResponseNotFound
            return HttpResponseNotFound('Subdomain not configured')

        # Switch DB connection for this request (only close when tenant changed)
        self._switch_db(request.tenant_db)

        return None

    def _switch_db(self, db_name):
        """Switch default connection to tenant DB. Only close when tenant changed."""
        last = getattr(_last_tenant, 'db', None)
        if last == db_name:
            return  # Same tenant, reuse connection
        try:
            from django.db import connection
            connection.settings_dict['NAME'] = db_name
            connection.close()
            _last_tenant.db = db_name
        except Exception:
            pass  # Next request will retry

    def __call__(self, request):
        """Django 1.8+ compatibility"""
        self.process_request(request)
        response = self.get_response(request)
        return response