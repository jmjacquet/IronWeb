# -*- coding: utf-8 -*-
from django import forms

from comprobantes.models import cpb_pto_vta,cpb_tipo_forma_pago,cpb_cuenta,cpb_tipo,cpb_nro_afip
from general.utilidades import *
from general.forms import pto_vta_habilitados

from general.models import gral_empresa

class ImportarCPBSForm(forms.Form):		
	archivo = forms.FileField(label='Seleccione un archivo',required=True)  
	migra = forms.ChoiceField(label=u'¿Crear CPBs Faltantes?',choices=SINO,required=True,initial=2)
	empresa = forms.ModelChoiceField(queryset=gral_empresa.objects.all(),empty_label=None,required=True)
	# tipo_entidad = forms.ChoiceField(label=u'Tipo Entidad',choices=TIPO_ENTIDAD,required=True,initial=1)	
	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(ImportarCPBSForm, self).__init__(*args, **kwargs)
		
		try:
			empresas = empresas_buscador(request)			
			self.fields['empresa'].queryset = empresas			
		except:
			pass

	def clean(self):
		archivo = self.cleaned_data.get('archivo')        
		if archivo:
			if not archivo.name.endswith('.csv'):
				self.add_error("archivo",u'¡El archivo debe tener extensión .CSV!')            
			#if file is too large, return
			if archivo.multiple_chunks():
				self.add_error("archivo",u"El archivo es demasiado grande (%.2f MB)." % (archivo.size/(1000*1000),))
		return self.cleaned_data

class RecuperarCPBS(forms.Form):               
	cpb_tipo = forms.ModelChoiceField(label='Tipo CPB',queryset=cpb_nro_afip.objects.all(),required = True,empty_label=None)
	pto_vta = forms.IntegerField(label='Pto. Vta.',required = True)		
	generar = forms.ChoiceField(label=u'¿Crear CPBs Faltantes?',choices=SINO,required=True,initial=2)
	def __init__(self, *args, **kwargs):		
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None)  
		super(RecuperarCPBS, self).__init__(*args, **kwargs)						
		# self.fields['pto_vta'].queryset = pto_vta_habilitados(request)

class ConsultaCPB(forms.Form):               
	cpb_tipo = forms.ModelChoiceField(label='Tipo CPB',queryset=cpb_nro_afip.objects.all(),required = True,empty_label=None)
	pto_vta = forms.IntegerField(label='Pto. Vta.',required = True)	
	numero = forms.IntegerField(label=u'Numero CPB',required = True)	

	def __init__(self, *args, **kwargs):		
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None)  
		super(ConsultaCPB, self).__init__(*args, **kwargs)						
		# self.fields['pto_vta'].queryset = pto_vta_habilitados(request)
