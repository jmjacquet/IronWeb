# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet
import datetime
from general.utilidades import *
from django.contrib import admin
from django.utils import *
from django.forms.widgets import TextInput,NumberInput
from django.forms import Widget
from django.db.models import Q
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div,Button,HTML
from .models import *
from general.utilidades import *
from general.flavor import ARCUITField,ARDNIField,ARPostalCodeField
				

class EntidadesForm(forms.ModelForm):
	observaciones = forms.CharField(label='Observaciones / Datos adicionales',widget=forms.Textarea(attrs={'class':'form-control2', 'rows': 5}),required = False)	
	fact_cuit = ARCUITField(label='CUIT',required = False,widget=PostPendWidgetBuscar(attrs={'class':'form-control','autofocus':'autofocus'},
			base_widget=TextInput,data='<i class="fa fa-search" aria-hidden="true"></i>',tooltip=u"Buscar datos y validar CUIT en AFIP"))		
	fact_categFiscal = forms.ChoiceField(label=u'Categoría Fiscal',required = True,choices=CATEG_FISCAL,initial=5)	
	fact_nro_doc = ARDNIField(label=u'Número',required = False)	
	tipo_doc = forms.ChoiceField(label=u'Tipo Documento',required = True,choices=TIPO_DOC)
	cod_postal = ARPostalCodeField(label='CP',required = False)		
	tipo_entidad = forms.IntegerField(widget = forms.HiddenInput(), required = False)

	class Meta:
			model = egr_entidad
			exclude = ['id','fecha_creacion','fecha_modif','usuario','empresa']

	def clean(self):		
		fact_cuit = self.cleaned_data.get('fact_cuit')
		tipo_entidad = self.cleaned_data.get('tipo_entidad')
		fact_categFiscal = self.cleaned_data.get('fact_categFiscal')
		tipo_doc = self.cleaned_data.get('tipo_doc')
		if fact_cuit: 
			try:
				entidad=egr_entidad.objects.get(fact_cuit=fact_cuit,tipo_entidad=tipo_entidad,baja=False)				
				if entidad:
					raise forms.ValidationError("El Nº de CUIT ingresado ya existe en el Sistema! Verifique.")
			except egr_entidad.DoesNotExist:
			#because we didn't get a match
				pass

		if fact_categFiscal and tipo_doc:
			if (int(fact_categFiscal)==1)and(int(tipo_doc)==80)and(not validar_cuit(fact_cuit)):
				raise forms.ValidationError(u'Debe cargar un CUIT válido! Verifique.')

			if (int(fact_categFiscal)==1)and(int(tipo_doc)!=80):
				raise forms.ValidationError(u'Si es IVA R.I. debe seleccionar CUIT como tipo de Documento! Verifique.')				


		return self.cleaned_data

class EntidadesEditForm(forms.ModelForm):
	observaciones = forms.CharField(label='Observaciones / Datos adicionales',widget=forms.Textarea(attrs={'class':'form-control2', 'rows': 5}),required = False)	
	fact_cuit = ARCUITField(label='CUIT',required = False,widget=PostPendWidgetBuscar(attrs={'class':'form-control','autofocus':'autofocus'},
			base_widget=TextInput,data='<i class="fa fa-search" aria-hidden="true"></i>',tooltip=u"Buscar datos y validar CUIT en AFIP"))		
	fact_categFiscal = forms.ChoiceField(label=u'Categoría Fiscal',required = True,choices=CATEG_FISCAL,initial=5)	
	fact_nro_doc = ARDNIField(label=u'Número',required = False)	
	cod_postal = ARPostalCodeField(label='CP',required = False)		
	tipo_entidad = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	tipo_doc = forms.ChoiceField(label=u'Tipo Documento',required = True,choices=TIPO_DOC,initial=80)

	class Meta:
			model = egr_entidad
			exclude = ['id','fecha_creacion','fecha_modif','usuario','empresa']

	def clean(self):				
		fact_categFiscal = self.cleaned_data.get('fact_categFiscal')
		tipo_doc = self.cleaned_data.get('tipo_doc')
		fact_cuit = self.cleaned_data.get('fact_cuit')
		
		if fact_categFiscal and tipo_doc:
			if (int(fact_categFiscal)==1)and(int(tipo_doc)==80)and(not validar_cuit(fact_cuit)):
				self._errors['fact_cuit'] = ''				
				raise forms.ValidationError(u'Debe cargar un CUIT válido! Verifique.')

			if (int(fact_categFiscal)==1)and(int(tipo_doc)!=80):
				self._errors['tipo_doc'] = u''		
				raise forms.ValidationError(u'Si es IVA R.I. debe seleccionar CUIT como tipo de Documento! Verifique.')				


		return self.cleaned_data

	


class VendedoresForm(forms.ModelForm):
	observaciones = forms.CharField(label='Observaciones / Datos adicionales',widget=forms.Textarea(attrs={'class':'form-control2', 'rows': 5}),required = False)	
	fact_nro_doc = ARDNIField(label=u'Número',required = False)	
	cod_postal = ARPostalCodeField(label='CP',required = False)		
	tipo_entidad = forms.IntegerField(widget = forms.HiddenInput(), required = False)
	

	class Meta:
			model = egr_entidad
			exclude = ['id','fecha_creacion','fecha_modif','usuario','empresa']
	

