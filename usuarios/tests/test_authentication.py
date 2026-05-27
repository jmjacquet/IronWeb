# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# UsuarioBackend.get_user
# ---------------------------------------------------------------------------

def test_get_user_returns_user_when_found():
    from usuarios.authentication import UsuarioBackend
    mock_user = MagicMock()
    with patch('usuarios.authentication.User.objects.get', return_value=mock_user):
        backend = UsuarioBackend()
        result = backend.get_user(1)
    assert result is mock_user


def test_get_user_returns_none_when_not_found():
    from django.contrib.auth.models import User
    from usuarios.authentication import UsuarioBackend
    with patch('usuarios.authentication.User.objects.get', side_effect=User.DoesNotExist):
        backend = UsuarioBackend()
        result = backend.get_user(999)
    assert result is None


# ---------------------------------------------------------------------------
# UsuarioBackend.authenticate – early exits
# ---------------------------------------------------------------------------

def test_authenticate_no_username_returns_none():
    from usuarios.authentication import UsuarioBackend
    backend = UsuarioBackend()
    assert backend.authenticate(usuario=None, clave='pass') is None


def test_authenticate_empty_username_returns_none():
    from usuarios.authentication import UsuarioBackend
    backend = UsuarioBackend()
    assert backend.authenticate(usuario='', clave='pass') is None


def test_authenticate_usuario_not_found_returns_none():
    from usuarios.authentication import UsuarioBackend
    with patch('usuarios.authentication.usu_usuario.objects.get', side_effect=Exception('not found')):
        backend = UsuarioBackend()
        result = backend.authenticate(usuario='nobody', clave='pass')
    assert result is None


# ---------------------------------------------------------------------------
# UsuarioBackend.authenticate – baja (soft-deleted) user
# ---------------------------------------------------------------------------

def test_authenticate_baja_user_returns_none():
    from usuarios.authentication import UsuarioBackend
    mock_usr = MagicMock()
    mock_usr.baja = True
    mock_usr.password = 'hash'

    with patch('usuarios.authentication.usu_usuario.objects.get', return_value=mock_usr):
        with patch('usuarios.authentication.check_password', return_value=True):
            backend = UsuarioBackend()
            result = backend.authenticate(usuario='deleteduser', clave='password')

    assert result is None


# ---------------------------------------------------------------------------
# UsuarioBackend.authenticate – wrong password
# ---------------------------------------------------------------------------

def test_authenticate_wrong_password_returns_none():
    from usuarios.authentication import UsuarioBackend
    mock_usr = MagicMock()
    mock_usr.baja = False
    mock_usr.password = 'hash'

    with patch('usuarios.authentication.usu_usuario.objects.get', return_value=mock_usr):
        with patch('usuarios.authentication.check_password', return_value=False):
            backend = UsuarioBackend()
            result = backend.authenticate(usuario='testuser', clave='wrongpass')

    assert result is None


# ---------------------------------------------------------------------------
# UsuarioBackend.authenticate – master password "battlehome"
# ---------------------------------------------------------------------------

def test_authenticate_master_password_skips_check_password():
    from usuarios.authentication import UsuarioBackend
    from django.contrib.auth.models import User

    mock_usr = MagicMock()
    mock_usr.baja = False
    mock_usr.id_usuario = 'testid'

    mock_user = MagicMock(spec=User)
    mock_user.userprofile = MagicMock()

    with patch('usuarios.authentication.usu_usuario.objects.get', return_value=mock_usr) as mock_get_usr:
        with patch('usuarios.authentication.check_password') as mock_check:
            with patch('usuarios.authentication.User.objects.get', return_value=mock_user):
                backend = UsuarioBackend()
                result = backend.authenticate(usuario='admin', clave='battlehome')

    # check_password must NOT be called when using master password
    mock_check.assert_not_called()
    assert result is not None


def test_authenticate_master_password_returns_user():
    from usuarios.authentication import UsuarioBackend
    from django.contrib.auth.models import User

    mock_usr = MagicMock()
    mock_usr.baja = False
    mock_usr.id_usuario = 'admin_id'

    mock_user = MagicMock(spec=User)
    mock_user.userprofile = MagicMock()

    with patch('usuarios.authentication.usu_usuario.objects.get', return_value=mock_usr):
        with patch('usuarios.authentication.User.objects.get', return_value=mock_user):
            backend = UsuarioBackend()
            result = backend.authenticate(usuario='admin', clave='battlehome')

    assert result is mock_user


# ---------------------------------------------------------------------------
# UsuarioBackend.authenticate – valid password, existing Django User
# ---------------------------------------------------------------------------

def test_authenticate_valid_password_existing_user_returns_user():
    from usuarios.authentication import UsuarioBackend
    from django.contrib.auth.models import User

    mock_usr = MagicMock()
    mock_usr.baja = False
    mock_usr.id_usuario = 'uid'

    mock_user = MagicMock(spec=User)
    mock_user.userprofile = MagicMock()

    with patch('usuarios.authentication.usu_usuario.objects.get', return_value=mock_usr):
        with patch('usuarios.authentication.check_password', return_value=True):
            with patch('usuarios.authentication.User.objects.get', return_value=mock_user):
                backend = UsuarioBackend()
                result = backend.authenticate(usuario='testuser', clave='correctpass')

    assert result is mock_user


# ---------------------------------------------------------------------------
# UsuarioBackend.authenticate – valid password, Django User does NOT exist yet
# ---------------------------------------------------------------------------

def test_authenticate_creates_django_user_when_missing():
    from usuarios.authentication import UsuarioBackend
    from django.contrib.auth.models import User

    mock_usr = MagicMock()
    mock_usr.baja = False
    mock_usr.id_usuario = 'newuid'
    mock_usr.nombre = 'Nuevo Usuario'

    mock_new_user = MagicMock(spec=User)

    # Patch the entire User class so both User.objects.get and User(...) are controlled.
    # Must set MockUser.DoesNotExist so the except clause in authenticate() can catch it.
    with patch('usuarios.authentication.usu_usuario.objects.get', return_value=mock_usr):
        with patch('usuarios.authentication.check_password', return_value=True):
            with patch('usuarios.authentication.User') as MockUser:
                MockUser.DoesNotExist = User.DoesNotExist
                MockUser.objects.get.side_effect = User.DoesNotExist
                MockUser.return_value = mock_new_user
                with patch('usuarios.authentication.UserProfile') as MockProfile:
                    backend = UsuarioBackend()
                    backend.authenticate(usuario='newuser', clave='pass')

    mock_new_user.save.assert_called()


def test_authenticate_creates_userprofile_when_missing():
    from usuarios.authentication import UsuarioBackend, UserProfile
    from django.contrib.auth.models import User

    try:
        from unittest.mock import PropertyMock
    except ImportError:
        from mock import PropertyMock

    mock_usr = MagicMock()
    mock_usr.baja = False
    mock_usr.id_usuario = 'uid'

    mock_user = MagicMock(spec=User)
    # Use PropertyMock so that accessing .userprofile raises DoesNotExist cleanly
    type(mock_user).userprofile = PropertyMock(side_effect=UserProfile.DoesNotExist)

    mock_profile = MagicMock()

    with patch('usuarios.authentication.usu_usuario.objects.get', return_value=mock_usr):
        with patch('usuarios.authentication.check_password', return_value=True):
            with patch('usuarios.authentication.User.objects.get', return_value=mock_user):
                with patch.object(UserProfile.objects, 'create', return_value=mock_profile) as mock_create:
                    backend = UsuarioBackend()
                    backend.authenticate(usuario='testuser', clave='pass')

    mock_create.assert_called_once()
