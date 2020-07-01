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
from general.models import gral_empresa
from general.forms import empresas_buscador
from general.flavor import ARCUITField,ARDNIField,ARPostalCodeField
from productos.models import prod_lista_precios
				

class EntidadesForm(forms.ModelForm):
	observaciones = forms.CharField(label='Observaciones / Datos adicionales',widget=forms.Textarea(attrs={'class':'form-control2', 'rows': 5}),required = False)	
	fact_cuit = ARCUITField(label='CUIT',required = False,widget=PostPendWidgetBuscar(attrs={'class':'form-control','autofocus':'autofocus'},
			base_widget=TextInput,data='<i class="fa fa-search" aria-hidden="true"></i>',tooltip=u"Buscar datos y validar CUIT en AFIP"))		
	fact_categFiscal = forms.ChoiceField(label=u'Categoría Fiscal',required = True,choices=CATEG_FISCAL,initial=5)	
	fact_nro_doc = ARDNIField(label=u'Número',required = False)	
	tipo_doc = forms.ChoiceField(label=u'Tipo Documento',required = True,choices=TIPO_DOC)
	cod_postal = ARPostalCodeField(label='CP',required = False)		
	tipo_entidad = forms.IntegerField(widget = forms.HiddenInput(), required = False)
	empresa = forms.ModelChoiceField(queryset=gral_empresa.objects.all(),empty_label=None)
	dcto_general = forms.DecimalField(label=u'% Dcto.General',initial=0,decimal_places=2,required = False)	
	tope_cta_cte = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	lista_precios_defecto = forms.ModelChoiceField(label=u'Lista Precios x Defecto',queryset=prod_lista_precios.objects.all(),required = False)
	class Meta:
			model = egr_entidad
			exclude = ['id','fecha_creacion','fecha_modif','usuario']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(EntidadesForm, self).__init__(*args, **kwargs)
		self.fields['lista_precios_defecto'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
		try:
			empresas = empresas_buscador(request)			
			self.fields['empresa'].queryset = empresas
			self.fields['empresa'].initial = 1
		except:
			empresas = empresa_actual(request)  
			self.fields['empresa'].queryset = empresas		
			

	def clean(self):		
		fact_cuit = self.cleaned_data.get('fact_cuit')
		tipo_entidad = self.cleaned_data.get('tipo_entidad')
		fact_categFiscal = self.cleaned_data.get('fact_categFiscal')
		tipo_doc = self.cleaned_data.get('tipo_doc')
		if fact_cuit: 
			try:
				entidad=egr_entidad.objects.filter(fact_cuit=fact_cuit,tipo_entidad=tipo_entidad,baja=False)				
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
	empresa = forms.ModelChoiceField(queryset=gral_empresa.objects.all(),empty_label=None)
	dcto_general = forms.DecimalField(label=u'% Dcto.General',initial=0,decimal_places=2,required = False)	
	tope_cta_cte = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	lista_precios_defecto = forms.ModelChoiceField(label=u'Lista Precios x Defecto',queryset=prod_lista_precios.objects.all(),required = False)
	class Meta:
			model = egr_entidad
			exclude = ['id','fecha_creacion','fecha_modif','usuario']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(EntidadesEditForm, self).__init__(*args, **kwargs)
		self.fields['lista_precios_defecto'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
		try:
			empresas = empresas_buscador(request)			
			self.fields['empresa'].queryset = empresas			
		except:
			empresas = empresa_actual(request)  
			self.fields['empresa'].queryset = empresas


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
	empresa = forms.ModelChoiceField(queryset=gral_empresa.objects.all(),empty_label=None)
	class Meta:
			model = egr_entidad
			exclude = ['id','fecha_creacion','fecha_modif','usuario']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(VendedoresForm, self).__init__(*args, **kwargs)
		
		try:
			empresas = empresas_buscador(request)
			self.fields['empresa'].queryset = empresas
			self.fields['empresa'].initial = 1
		except:
			empresa = empresa_actual(request)  
	

class ImportarEntidadesForm(forms.Form):	
	archivo = forms.FileField(label='Seleccione un archivo',required=True)  
	sobreescribir = forms.ChoiceField(label=u'¿Sobreescribir Existentes?',choices=SINO,required=True,initial='S')
	empresa = forms.ModelChoiceField(queryset=gral_empresa.objects.all(),empty_label=None,required=True)
	tipo_entidad = forms.ChoiceField(label=u'Tipo Entidad',choices=TIPO_ENTIDAD,required=True,initial=1)	
	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(ImportarEntidadesForm, self).__init__(*args, **kwargs)
		
		try:
			empresas = empresas_buscador(request)
			self.fields['empresa'].queryset = empresas
			self.fields['empresa'].initial = 1
		except:
			empresa = empresa_actual(request)  

	def clean(self):
		archivo = self.cleaned_data.get('archivo')        
		if archivo:
			if not archivo.name.endswith('.csv'):
				self.add_error("archivo",u'¡El archivo debe tener extensión .CSV!')            
			#if file is too large, return
			if archivo.multiple_chunks():
				self.add_error("archivo",u"El archivo es demasiado grande (%.2f MB)." % (archivo.size/(1000*1000),))
		return self.cleaned_data
	    