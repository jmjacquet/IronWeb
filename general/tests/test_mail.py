# -*- coding: utf-8 -*-
from email.utils import parseaddr

from django.test import override_settings

from general.models import gral_empresa


def test_get_datos_mail_falls_back_to_settings_when_port_is_none():
    d = gral_empresa(nombre='Emp', mail_puerto=None, mail_servidor='', email='x@y.com').get_datos_mail()
    assert d['mail_puerto'] == 587
    assert d['mail_servidor'] == 'localhost'


def test_own_relay_sends_from_its_own_user():
    d = gral_empresa(nombre='Emp, S.A.', mail_puerto=465, mail_servidor='smtp.x',
                     mail_usuario='u@x.com', email='x@y.com').get_datos_mail()
    assert d['mail_puerto'] == 465
    assert parseaddr(d['mail_origen']) == ('Emp, S.A.', 'u@x.com')
    assert d['mail_respuesta'] == 'x@y.com'


@override_settings(DEFAULT_FROM_EMAIL='noreply@ironwebgestion.com.ar')
def test_shared_relay_sends_from_default_from_email():
    d = gral_empresa(nombre='Emp', mail_servidor='', email='x@y.com').get_datos_mail()
    assert parseaddr(d['mail_origen']) == ('Emp', 'noreply@ironwebgestion.com.ar')
    assert d['mail_respuesta'] == 'x@y.com'


def test_shared_relay_without_default_keeps_company_email():
    d = gral_empresa(nombre='Emp', mail_servidor='', email='x@y.com').get_datos_mail()
    assert parseaddr(d['mail_origen']) == ('Emp', 'x@y.com')
