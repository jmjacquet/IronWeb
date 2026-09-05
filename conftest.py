# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import django
import pytest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ggcontable.settings_test')
django.setup()

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


@pytest.fixture
def mock_request():
    """Minimal request object for tests that need one."""
    request = MagicMock()
    request.session = {}
    request.META = {}
    request.get_host.return_value = 'prueba.ironwebgestion.com.ar'
    return request


@pytest.fixture
def mock_empresa():
    """Mock empresa (company) object."""
    empresa = MagicMock()
    empresa.id = 1
    empresa.usa_impuestos = False
    return empresa


@pytest.fixture
def mock_usuario(mock_empresa):
    """Mock usu_usuario object."""
    usuario = MagicMock()
    usuario.baja = False
    usuario.tipoUsr = 0
    usuario.empresa = mock_empresa
    return usuario
