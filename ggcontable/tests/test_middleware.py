# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

import pytest

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch

from ggcontable.middleware import TenantMiddleware, get_tenant_map, TENANT_MAP


# ---------------------------------------------------------------------------
# get_tenant_map
# ---------------------------------------------------------------------------

def test_get_tenant_map_includes_hardcoded_defaults(monkeypatch):
    monkeypatch.delenv('TENANT_MAP', raising=False)
    result = get_tenant_map()
    assert 'prueba.ironwebgestion.com.ar' in result
    assert 'mullertma.ironwebgestion.com.ar' in result


def test_get_tenant_map_merges_env_var(monkeypatch):
    extra = json.dumps({
        'localhost': {
            'ENTIDAD_ID': '1',
            'ENTIDAD_DB': 'ironweb_prueba',
            'ENTIDAD_DIR': 'prueba',
        }
    })
    monkeypatch.setenv('TENANT_MAP', extra)
    result = get_tenant_map()
    assert 'localhost' in result
    assert 'prueba.ironwebgestion.com.ar' in result


def test_get_tenant_map_env_var_overrides_defaults(monkeypatch):
    override = json.dumps({
        'prueba.ironwebgestion.com.ar': {
            'ENTIDAD_ID': '99',
            'ENTIDAD_DB': 'overridden_db',
            'ENTIDAD_DIR': 'overridden',
        }
    })
    monkeypatch.setenv('TENANT_MAP', override)
    result = get_tenant_map()
    assert result['prueba.ironwebgestion.com.ar']['ENTIDAD_DB'] == 'overridden_db'


def test_get_tenant_map_invalid_json_silently_ignored(monkeypatch):
    monkeypatch.setenv('TENANT_MAP', 'not-valid-json')
    result = get_tenant_map()
    assert 'prueba.ironwebgestion.com.ar' in result


def test_get_tenant_map_non_dict_json_ignored(monkeypatch):
    monkeypatch.setenv('TENANT_MAP', '["list", "not", "dict"]')
    result = get_tenant_map()
    assert 'prueba.ironwebgestion.com.ar' in result


def test_get_tenant_map_returns_copy_not_mutating_original(monkeypatch):
    monkeypatch.delenv('TENANT_MAP', raising=False)
    result = get_tenant_map()
    result['injected'] = {}
    assert 'injected' not in TENANT_MAP


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def middleware():
    get_response = MagicMock(return_value=MagicMock())
    return TenantMiddleware(get_response)


def _req(host, forwarded_host=None):
    """Build a minimal mock request."""
    request = MagicMock()
    request.get_host.return_value = host
    meta = {}
    if forwarded_host:
        meta['HTTP_X_FORWARDED_HOST'] = forwarded_host
    request.META = meta
    return request


# ---------------------------------------------------------------------------
# TenantMiddleware.process_request – known tenant
# ---------------------------------------------------------------------------

def test_process_request_known_host_returns_none(middleware, monkeypatch):
    monkeypatch.delenv('TENANT_MAP', raising=False)
    req = _req('prueba.ironwebgestion.com.ar')
    result = middleware.process_request(req)
    assert result is None


def test_process_request_sets_env_vars(middleware, monkeypatch):
    monkeypatch.delenv('TENANT_MAP', raising=False)
    req = _req('prueba.ironwebgestion.com.ar')
    middleware.process_request(req)
    assert os.environ.get('ENTIDAD_DB') == 'ironweb_prueba'
    assert os.environ.get('ENTIDAD_ID') == '1'
    assert os.environ.get('ENTIDAD_DIR') == 'prueba'


def test_process_request_sets_request_attributes(middleware, monkeypatch):
    monkeypatch.delenv('TENANT_MAP', raising=False)
    req = _req('prueba.ironwebgestion.com.ar')
    middleware.process_request(req)
    assert req.tenant_id == '1'
    assert req.tenant_db == 'ironweb_prueba'
    assert req.tenant_dir == 'prueba'


def test_process_request_mullertma_tenant(middleware, monkeypatch):
    monkeypatch.delenv('TENANT_MAP', raising=False)
    req = _req('mullertma.ironwebgestion.com.ar')
    middleware.process_request(req)
    assert req.tenant_db == 'ironweb_mullertma'
    assert req.tenant_id == '10'


# ---------------------------------------------------------------------------
# TenantMiddleware.process_request – unknown tenant → 404
# ---------------------------------------------------------------------------

def test_process_request_unknown_host_returns_404(middleware):
    from django.http import HttpResponseNotFound
    req = _req('unknown.example.com')
    response = middleware.process_request(req)
    assert isinstance(response, HttpResponseNotFound)


def test_process_request_unknown_host_404_contains_message(middleware):
    req = _req('notregistered.com')
    response = middleware.process_request(req)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Host normalisation
# ---------------------------------------------------------------------------

def test_process_request_strips_port(middleware, monkeypatch):
    monkeypatch.delenv('TENANT_MAP', raising=False)
    req = _req('prueba.ironwebgestion.com.ar:8000')
    result = middleware.process_request(req)
    assert result is None


def test_process_request_normalises_uppercase(middleware, monkeypatch):
    monkeypatch.delenv('TENANT_MAP', raising=False)
    req = _req('PRUEBA.IRONWEBGESTION.COM.AR')
    result = middleware.process_request(req)
    assert result is None


def test_process_request_x_forwarded_host_used(middleware, monkeypatch):
    monkeypatch.delenv('TENANT_MAP', raising=False)
    req = _req('internal.cluster', forwarded_host='prueba.ironwebgestion.com.ar')
    result = middleware.process_request(req)
    assert result is None


def test_process_request_x_forwarded_host_comma_list_uses_first(middleware, monkeypatch):
    monkeypatch.delenv('TENANT_MAP', raising=False)
    req = _req('internal.cluster', forwarded_host='prueba.ironwebgestion.com.ar, other.host')
    result = middleware.process_request(req)
    assert result is None


def test_process_request_env_tenant_works(middleware, monkeypatch):
    extra = json.dumps({
        'testenv.local': {
            'ENTIDAD_ID': '5',
            'ENTIDAD_DB': 'ironweb_test',
            'ENTIDAD_DIR': 'testdir',
        }
    })
    monkeypatch.setenv('TENANT_MAP', extra)
    # Re-init so middleware picks up new tenant map
    mw = TenantMiddleware(MagicMock())
    req = _req('testenv.local')
    mw.process_request(req)
    assert req.tenant_db == 'ironweb_test'


# ---------------------------------------------------------------------------
# TenantMiddleware._switch_db
# ---------------------------------------------------------------------------

def test_switch_db_same_tenant_does_not_close(middleware):
    import ggcontable.middleware as mw_module
    mw_module._last_tenant.db = 'ironweb_prueba'
    from django.db import connection
    with patch.object(connection, 'close') as mock_close:
        middleware._switch_db('ironweb_prueba')
        mock_close.assert_not_called()
    assert mw_module._last_tenant.db == 'ironweb_prueba'


def test_switch_db_different_tenant_closes_connection(middleware):
    import ggcontable.middleware as mw_module
    mw_module._last_tenant.db = 'old_db'
    from django.db import connection
    with patch.object(connection, 'close') as mock_close:
        with patch.dict(connection.settings_dict, {'NAME': 'old_db'}):
            middleware._switch_db('new_db')
            mock_close.assert_called_once()
