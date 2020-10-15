# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
import datetime
from general.utilidades import *
from general.views import ultimoNroId
from general.forms import pto_vta_habilitados
from django.contrib import admin
from django.utils import *
from django.forms.widgets import TextInput,NumberInput
from django.forms import Widget
from django.db.models import Q
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div,Button,HTML
from .models import *
from general.flavor import ARCUITField,ARDNIField,ARPostalCodeField
from chosen import forms as chosenforms

####################################################################################################

class BancosForm(forms.ModelForm):
    class Meta:
            model = cpb_banco
            exclude = ['id','baja','empresa']

class PercImpForm(forms.ModelForm):
    class Meta:
            model = cpb_perc_imp
            exclude = ['id','baja','empresa']      

class RetencForm(forms.ModelForm):
    class Meta:
            model = cpb_retenciones
            exclude = ['id','empresa'] 

class FormaPagoForm(forms.ModelForm):
    signo = forms.ChoiceField(label='Signo',choices=SIGNO,required=False,initial=1)
    cuenta = forms.ModelChoiceField(label='Cuenta x Defecto',queryset=cpb_cuenta.objects.all(),empty_label='---')
    class Meta:
            model = cpb_tipo_forma_pago
            exclude = ['id','baja','empresa'] 

    def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(FormaPagoForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)						
			self.fields['cuenta'].queryset = cpb_cuenta.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False,tipo__in=[0,1,2])			
		except gral_empresa.DoesNotExist:
			empresa = None	


####################################################################################################

class MovimCuentasForm(forms.ModelForm):
	fecha_cpb = forms.DateField(label='Fecha',widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=hoy(),required = True)
	observacion = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 3}),required = False)			
	importe_total = forms.DecimalField(label='Total Comprobante',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly',},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)					
	class Meta:
			model = cpb_comprobante			
			fields = ['observacion','importe_total','fecha_cpb']


	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(MovimCuentasForm, self).__init__(*args, **kwargs)		
	
class MovimCuentasFPForm(forms.ModelForm):
	tipo_forma_pago = forms.ModelChoiceField(label='Medio de Pago',queryset=cpb_tipo_forma_pago.objects.filter(baja=False),empty_label='---')
	mdcp_fecha = forms.DateField(label='Fecha',widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=hoy(),required = False)
	mdcp_banco = forms.ModelChoiceField(label='Banco',queryset=cpb_banco.objects.filter(baja=False),empty_label='---',required = False)
	detalle = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control','rows': 3}),required = False)		
	importe = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	cta_egreso = forms.ModelChoiceField(label='Cuenta Origen/Egreso',queryset=cpb_cuenta.objects.all(),empty_label='---')
	cta_ingreso = forms.ModelChoiceField(label='Cuenta Destino/Ingreso',queryset=cpb_cuenta.objects.all(),empty_label='---')
	class Meta:
			model = cpb_comprobante_fp
			exclude = ['id','fecha_creacion']			

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(MovimCuentasFPForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['tipo_forma_pago'].queryset = cpb_tipo_forma_pago.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False,cuenta__tipo__in=[0,1,3])			
			self.fields['mdcp_banco'].queryset = cpb_banco.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False)			
			self.fields['cta_egreso'].queryset = cpb_cuenta.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False,tipo__in=[0,1,3])			
			self.fields['cta_ingreso'].queryset = cpb_cuenta.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False,tipo__in=[0,1,3])			
		except gral_empresa.DoesNotExist:
			empresa = None		


	def clean(self):						
		super(forms.ModelForm,self).clean()	
		egreso = self.cleaned_data.get('cta_egreso')
		ingreso = self.cleaned_data.get('cta_ingreso')
		if egreso == ingreso:
			self._errors['cta_egreso'] = [u'Las cuentas deben ser distintas.']
			self._errors['cta_ingreso'] = [u'Las cuentas deben ser distintas.']

		return self.cleaned_data

####################################################################################################

class SeguimientoForm(forms.ModelForm):
	seguimiento = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 8}),required = False)			

	class Meta:
			model = cpb_comprobante
			fields = ['seguimiento']

class PtoVtaForm(forms.ModelForm):
	# observaciones = forms.CharField(label='Observaciones / Datos adicionales',widget=forms.Textarea(attrs={ 'rows': 3}),required = False)		
	cuit = ARCUITField(label='CUIT',required = True,widget=PostPendWidgetBuscar(attrs={'class':'form-control','autofocus':'autofocus'},
			base_widget=TextInput,data='<i class="fa fa-search" aria-hidden="true"></i>',tooltip=u"Buscar datos y validar CUIT en AFIP"))		
	categ_fiscal = forms.ChoiceField(label=u'Categoría Fiscal',required = True,choices=CATEG_FISCAL)	
	
	fecha_inicio_activ = forms.DateField(label='Inicio Actividades',required = True,widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=inicioMes())		

	class Meta:
			model = cpb_pto_vta
			exclude = ['id','baja','empresa','fecha_creacion','fecha_modif',]	

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(PtoVtaForm, self).__init__(*args, **kwargs)
		id = ultimoNroId(cpb_pto_vta)+1
		self.fields['numero'].initial = id 
		self.fields['nombre'].initial = 'PV'+str(id)

	def clean(self):								
		super(forms.ModelForm,self).clean()	
		cuit = self.cleaned_data.get('cuit')
		fe_electronica = self.cleaned_data.get('fe_electronica')
		categ_fiscal = self.cleaned_data.get('categ_fiscal')
		fe_crt = self.cleaned_data.get('fe_crt')
		fe_key = self.cleaned_data.get('fe_key')
		numero = self.cleaned_data.get('numero')
		if fe_electronica:
			if not cuit:
				self._errors['cuit'] = [u'Debe cargar un CUIT válido!']
			if not categ_fiscal:
				self._errors['categ_fiscal'] = [u'Categ. Fiscal no válida!']
			if not fe_crt:
				self._errors['fe_crt'] = [u'Debe cargar el nombre del archivo CRT!']
			if not fe_key:
				self._errors['fe_key'] = [u'Debe cargar el nombre del archivo KEY!']

		ids=cpb_pto_vta.objects.filter(empresa=empresa_actual( self.initial['request']),numero=numero).values_list('id',flat=True)		
		cant=len(ids)		
		if (cant > 0):
			raise forms.ValidationError("El Nº de Pto. de Venta ya existe para la empresa actual! Verifique.")	

		return self.cleaned_data

class PtoVtaEditForm(forms.ModelForm):
	# observaciones = forms.CharField(label='Observaciones / Datos adicionales',widget=forms.Textarea(attrs={ 'rows': 3}),required = False)		
	cuit = ARCUITField(label='CUIT',required = False,widget=PostPendWidgetBuscar(attrs={'class':'form-control','autofocus':'autofocus'},
			base_widget=TextInput,data='<i class="fa fa-search" aria-hidden="true"></i>',tooltip=u"Buscar datos y validar CUIT en AFIP"))		
	categ_fiscal = forms.ChoiceField(label=u'Categoría Fiscal',required = True,choices=CATEG_FISCAL)		
	fecha_inicio_activ = forms.DateField(label='Inicio Actividades',required = True,widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=inicioMes())		
	
	class Meta:
			model = cpb_pto_vta
			exclude = ['id','baja','empresa','fecha_creacion','fecha_modif','numero']				

	def clean(self):						
		super(forms.ModelForm,self).clean()	
		cuit = self.cleaned_data.get('cuit')
		fe_electronica = self.cleaned_data.get('fe_electronica')
		categ_fiscal = self.cleaned_data.get('categ_fiscal')
		fe_crt = self.cleaned_data.get('fe_crt')
		fe_key = self.cleaned_data.get('fe_key')
		if fe_electronica:
			if not cuit:
				self._errors['cuit'] = [u'Debe cargar un CUIT válido!']
			if not categ_fiscal:
				self._errors['categ_fiscal'] = [u'Categ.Fiscal no válida!']
			if not fe_crt:
				self._errors['fe_crt'] = [u'Debe cargar el nombre del archivo CRT!']
			if not fe_key:
				self._errors['fe_key'] = [u'Debe cargar el nombre del archivo KEY!']
		return self.cleaned_data    

class DispoForm(forms.ModelForm):    
    tipo_forma_pago = forms.ModelChoiceField(label='FP x Defecto',queryset=cpb_tipo_forma_pago.objects.all(),empty_label='---')
    tipo = forms.ChoiceField(label=u'Tipo Cuenta',required = True,choices=TIPO_CTA_DISPO)		
    class Meta:
            model = cpb_cuenta
            exclude = ['id','baja','empresa','modificable'] 

    def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(DispoForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)
			self.fields['tipo_forma_pago'].queryset = cpb_tipo_forma_pago.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False)			
			self.fields['banco'].queryset = cpb_banco.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False)			
		except gral_empresa.DoesNotExist:
			empresa = None	

####################################################################################################

class ChequesModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.get_selCheque()

class FormCheques(forms.Form):
	cheques = ChequesModelChoiceField(label='Seleccione el Cheque a utilizar:',queryset=cpb_comprobante_fp.objects.none(),empty_label='---',required = True)	

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		id_cheques = kwargs.pop('id_cheques', None)		
		super(FormCheques, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)	
			if id_cheques:
				self.fields['cheques'].queryset = cpb_comprobante_fp.objects.filter(cpb_comprobante__empresa=empresa,cta_ingreso__isnull=False,cta_ingreso__tipo=2,mdcp_salida__isnull=True).exclude(id__in=id_cheques).order_by('-mdcp_fecha','-fecha_creacion')			
			else:
				self.fields['cheques'].queryset = cpb_comprobante_fp.objects.filter(cpb_comprobante__empresa=empresa,cta_ingreso__isnull=False,cta_ingreso__tipo=2,mdcp_salida__isnull=True).order_by('-mdcp_fecha','-fecha_creacion')									
		except gral_empresa.DoesNotExist:
			empresa = None  

class FormChequesCobro(forms.Form):
	fecha_cpb = forms.DateField(label='Fecha Movimiento',required = True,widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=hoy())		
	observacion = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 3}),required = False)					
	cuenta = forms.ModelChoiceField(label='Cuenta:',queryset=cpb_cuenta.objects.all(),required=True,initial='0')    	
	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)				
		super(FormChequesCobro, self).__init__(*args, **kwargs)
		try:			
			empresa = empresa_actual(request)					
			self.fields['cuenta'].queryset = cpb_cuenta.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False,tipo__in=[0,1])			
		except gral_empresa.DoesNotExist:
			empresa = None


# def unique_field_formset(field_name):
#     from django.forms.models import BaseInlineFormSet
#     class UniqueFieldFormSet (BaseInlineFormSet):
#         def clean(self):
#             if any(self.errors):
#                 # Don't bother validating the formset unless each form is valid on its own
#                 return
#             values = set()
#             for form in self.forms:
#                 value = form.cleaned_data[field_name]
#                 if value in values:
#                     raise forms.ValidationError('No deben repetirse productos!')
#                 values.add(value)
#     return UniqueFieldFormSet

class SaldoInicialForm(forms.ModelForm):
	tipo_forma_pago = forms.ModelChoiceField(label='Medio de Pago',queryset=cpb_tipo_forma_pago.objects.filter(baja=False),empty_label='---')
	mdcp_fecha = forms.DateField(label='Fecha',widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=hoy(),required = False)
	mdcp_banco = forms.ModelChoiceField(label='Banco',queryset=cpb_banco.objects.filter(baja=False),empty_label='---',required = False)
	detalle = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control','rows': 3}),required = False)		
	importe = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	cta_ingreso = forms.ModelChoiceField(label='Cuenta Destino/Ingreso',queryset=cpb_cuenta.objects.all(),empty_label='---')
	class Meta:
			model = cpb_comprobante_fp
			exclude = ['id','fecha_creacion']			

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(SaldoInicialForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['tipo_forma_pago'].queryset = cpb_tipo_forma_pago.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False,cuenta__tipo__in=[0,1,3])			
			self.fields['mdcp_banco'].queryset = cpb_banco.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False)			
			self.fields['cta_ingreso'].queryset = cpb_cuenta.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False,tipo__in=[0,1,3])			
		except gral_empresa.DoesNotExist:
			empresa = None		
	