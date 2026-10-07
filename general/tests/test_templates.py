# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
from django import forms
from django.conf import settings
settings.CERTIFICADOS_PATH = '/tmp'

PLANTILLAS = ['comprobantes/importar_arca.html',
              'productos/importar_productos.html',
              'entidades/importar_entidades.html']


class FormStub(forms.Form):
    archivo = forms.FileField(required=False)
    compra_venta = forms.ChoiceField(choices=(('C', 'C'), ('V', 'V')), required=False)
    empresa = forms.CharField(required=False)
    lista_precios = forms.CharField(required=False)
    sobreescribir = forms.ChoiceField(choices=(('S', 'S'), ('N', 'N')), required=False)
    tipo_entidad = forms.ChoiceField(choices=((1, 'Cliente'),), required=False)


@pytest.mark.django_db
@pytest.mark.parametrize('plantilla', PLANTILLAS)
def test_importadores_renderizan_el_header(plantilla):
    from django.template.loader import render_to_string
    html = render_to_string(plantilla, {
        'form': FormStub(), 'permisos_grupo': [], 'tipo_usr': 0})
    assert 'page-header-fixed' in html, 'falta el <body> de index.html'
    assert 'page-content-wrapper' in html, 'falta el wrapper de contenido'
    assert 'Manual de Usuario' in html, 'falta header.html'
    assert 'id="cargando"' in html, 'el spinner no se renderiza'
