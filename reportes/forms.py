# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
import datetime
from general.utilidades import *
from general.forms import pto_vta_habilitados
from django.contrib import admin
from django.utils import *
from django.forms.widgets import TextInput,NumberInput,Select
from django.forms import Widget
from django.db.models import Q
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div,Button,HTML
from chosen import forms as chosenforms
from entidades.models import egr_entidad
from comprobantes.models import cpb_pto_vta,cpb_tipo_forma_pago,cpb_cuenta,cpb_tipo
from productos.models import prod_ubicacion
from general.forms import pto_vta_buscador


class ConsultaCtaCteCliente(forms.Form):               
    entidad = chosenforms.ChosenModelChoiceField(label='Cliente',queryset=egr_entidad.objects.filter(tipo_entidad=1,baja=False),empty_label=None,required = True)   
    fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=inicioMes(),required = True)
    fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=hoy(),required = True)
    estado = forms.ChoiceField(label='Estado',choices=ESTADO_,required=False,initial=0)	
    def __init__(self, *args, **kwargs):
		empresa = kwargs.pop('empresa', None)  		
		request = kwargs.pop('request', None) 
		id = kwargs.pop('id', None)
		super(ConsultaCtaCteCliente, self).__init__(*args, **kwargs)
		self.fields['entidad'].queryset = egr_entidad.objects.filter(tipo_entidad=1,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
		if id:
			self.fields['entidad'].initial = id
			self.fields['estado'].initial = 0


class ConsultaSaldosClientes(forms.Form):               
    entidad = chosenforms.ChosenModelChoiceField(label='Cliente',queryset=egr_entidad.objects.filter(tipo_entidad=1,baja=False),empty_label=label_todos,required = False) 
    def __init__(self, *args, **kwargs):
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None) 
		super(ConsultaSaldosClientes, self).__init__(*args, **kwargs)
		self.fields['entidad'].queryset = egr_entidad.objects.filter(tipo_entidad=1,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
		

#############################################################################	

class ConsultaCtaCteProv(forms.Form):               
    entidad = chosenforms.ChosenModelChoiceField(label='Proveedor',queryset=egr_entidad.objects.filter(tipo_entidad=2,baja=False),empty_label=None,required = True)
    fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=inicioMes(),required = True)
    fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=hoy(),required = True)
    estado = forms.ChoiceField(label='Estado',choices=ESTADO_,required=False,initial=0)	
    def __init__(self, *args, **kwargs):
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None) 
		id = kwargs.pop('id', None)
		super(ConsultaCtaCteProv, self).__init__(*args, **kwargs)
		self.fields['entidad'].queryset = egr_entidad.objects.filter(tipo_entidad=2,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
		if id:
			self.fields['entidad'].initial = id
			self.fields['estado'].initial = 0


class ConsultaSaldosProv(forms.Form):               
    entidad = chosenforms.ChosenModelChoiceField(label='Proveedor',queryset=egr_entidad.objects.filter(tipo_entidad=2,baja=False),empty_label=label_todos,required = False) 
    def __init__(self, *args, **kwargs):
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None) 
		super(ConsultaSaldosProv, self).__init__(*args, **kwargs)
		self.fields['entidad'].queryset = egr_entidad.objects.filter(tipo_entidad=2,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
		

#############################################################################	

class ConsultaLibroIVAVentas(forms.Form):               
    entidad = forms.CharField(label='Cliente/Proveedor',max_length=100,widget=forms.TextInput(attrs={'class':'form-control','text-transform': 'uppercase'}),required=False)    
    fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=inicioMes(),required = True)
    fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=finMes(),required = True)
    estado = forms.ChoiceField(label='Estado',choices=ESTADO_,required=False,initial=0)	
    cae = forms.ChoiceField(label='CAE',choices=SINO,required=False,initial=0)	
    pto_vta = forms.IntegerField(label='Pto. Vta.',required = False)
    fact_x = forms.ChoiceField(label='Completo',choices=FACTURAS_X,required=True,initial=1)	
    def __init__(self, *args, **kwargs):		
		request = kwargs.pop('request', None)  
		super(ConsultaLibroIVAVentas, self).__init__(*args, **kwargs)				


class ConsultaLibroIVACompras(forms.Form):               
    entidad = forms.CharField(label='Proveedor',max_length=100,widget=forms.TextInput(attrs={'class':'form-control','text-transform': 'uppercase'}),required=False)    
    fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=inicioMes(),required = True)
    fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=finMes(),required = True)
    estado = forms.ChoiceField(label='Estado',choices=ESTADO_,required=False,initial=0)	    
    pto_vta = forms.IntegerField(label='Pto. Vta.',required = False)    
    fact_x = forms.ChoiceField(label='Completo',choices=FACTURAS_X,required=True,initial=1)	
    def __init__(self, *args, **kwargs):		
		request = kwargs.pop('request', None)   
		super(ConsultaLibroIVACompras, self).__init__(*args, **kwargs)
		


#############################################################################	

class ConsultaCajaDiaria(forms.Form):                   
    cuenta = forms.ModelChoiceField(label='Cuenta Ingreso/Egreso',queryset=cpb_cuenta.objects.all(),empty_label=label_todos,required = True)
    tipo_forma_pago = forms.ModelChoiceField(label='Forma de Pago/Cobro',queryset=cpb_tipo_forma_pago.objects.filter(baja=False),empty_label=label_todos,required = False)
    fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=inicioMes(),required = True)
    fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=finMes(),required = True)    
        
    def __init__(self, *args, **kwargs):
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None) 
		super(ConsultaCajaDiaria, self).__init__(*args, **kwargs)				
		self.fields['cuenta'].queryset = cpb_cuenta.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('codigo')
		self.fields['tipo_forma_pago'].queryset = cpb_tipo_forma_pago.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False)			

class ConsultaIngresosEgresos(forms.Form):               
    tipo_forma_pago = forms.ModelChoiceField(label='Forma de Pago/Cobro',queryset=cpb_tipo_forma_pago.objects.filter(baja=False),empty_label=label_todos,required = False)
    cuenta = forms.ModelChoiceField(label='Cuenta Ingreso/Egreso',queryset=cpb_cuenta.objects.all(),empty_label=label_todos,required = False)
    fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=inicioMes(),required = True)
    fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=finMes(),required = True)    
    pto_vta = forms.IntegerField(label='Pto. Vta.',required = False)
    
    def __init__(self, *args, **kwargs):
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None) 
		super(ConsultaIngresosEgresos, self).__init__(*args, **kwargs)				
		self.fields['cuenta'].queryset = cpb_cuenta.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('codigo')
		self.fields['tipo_forma_pago'].queryset = cpb_tipo_forma_pago.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False)				
#############################################################################	

class ConsultaSaldosCuentas(forms.Form):                   
    cuenta = forms.ModelChoiceField(label='Cuenta Ingreso/Egreso',queryset=cpb_cuenta.objects.all(),empty_label=label_todos,required = False)
    fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=inicioMes(),required = True)
    fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=finMes(),required = True)    
    pto_vta = forms.IntegerField(label='Pto. Vta.',required = False)    
    def __init__(self, *args, **kwargs):
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None) 
		super(ConsultaSaldosCuentas, self).__init__(*args, **kwargs)				
		self.fields['cuenta'].queryset = cpb_cuenta.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('codigo')

#############################################################################	


class ConsultaVencimientos(forms.Form):               
	entidad = forms.CharField(label='Cliente/Proveedor',max_length=100,widget=forms.TextInput(attrs={'class':'form-control','text-transform': 'uppercase'}),required=False)
	fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),required = False,initial=inicioMes())
	fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),required = False,initial=finMes())    	
	pto_vta = forms.IntegerField(label='Pto. Vta.',required = False)
	estado = forms.ChoiceField(label='Estado',choices=ESTADO_,required=False,initial=0)	
	cae = forms.ChoiceField(label='CAE',choices=SINO,required=False,initial=0)	
	tipo_cpb = forms.ModelChoiceField(label='Tipo Comprobante',queryset=cpb_tipo.objects.filter(tipo__in=[1,2,3,6,9],baja=False),empty_label=label_todos,required=False)   
	def __init__(self, *args, **kwargs):
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None) 
		super(ConsultaVencimientos, self).__init__(*args, **kwargs)						
		self.fields['tipo_cpb'].queryset = cpb_tipo.objects.filter(tipo__in=[1,2,3,4,5,6,7,9],baja=False)


###############################################################################

class ConsultaHistStockProd(forms.Form):               	
	producto = forms.CharField(label='Producto/Servicio',widget=forms.TextInput(attrs={'class':'form-control'}),required = False)
	fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),required = True,initial=inicioMes())
	fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),required = True,initial=finMes())    
	

class ConsultaRankings(forms.Form):               	
	fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),required = False,initial=inicioMes())
	fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),required = False,initial=finMes())    	
	pto_vta = forms.IntegerField(label='Pto. Vta.',required = False)
	estado = forms.ChoiceField(label='Estado',choices=ESTADO_,required=False,initial=0)	
	cae = forms.ChoiceField(label='CAE',choices=SINO,required=False,initial=0)	
	tipo_cpb = forms.ModelChoiceField(label='Tipo Comprobante',queryset=cpb_tipo.objects.filter(tipo__in=[1,2,3,6,9],baja=False),empty_label=label_todos,required=False)   
	def __init__(self, *args, **kwargs):
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None) 
		super(ConsultaRankings, self).__init__(*args, **kwargs)							
		self.fields['tipo_cpb'].queryset = cpb_tipo.objects.filter(tipo__in=[1,2,3,4,5,6,7,9],baja=False)		

#################################################################################

class ConsultaRepRetencImp(forms.Form):               
    entidad = forms.CharField(label='Cliente/Proveedor',max_length=100,widget=forms.TextInput(attrs={'class':'form-control','text-transform': 'uppercase'}),required=False)    
    fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=inicioMes(),required = True)
    fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),initial=finMes(),required = True)    
    pto_vta = forms.IntegerField(label='Pto.Vta.',required = False)    
    nro_cpb = forms.IntegerField(label='CPB',required = False)        
    
    def __init__(self, *args, **kwargs):		
		request = kwargs.pop('request', None)   
		super(ConsultaRepRetencImp, self).__init__(*args, **kwargs)

from ingresos.forms import EntidadModelChoiceField

CAMPO = (    
    ('importe_subtotal', u'Importe Bruto'),
    ('importe_total', u'Importe Neto'),    
)

class ConsultaVendedores(forms.Form):               
	vendedor = EntidadModelChoiceField(label='Vendedor',queryset=egr_entidad.objects.filter(tipo_entidad=3,baja=False),empty_label='---',required = True)
	cliente = forms.CharField(label='Cliente',max_length=100,widget=forms.TextInput(attrs={'class':'form-control','text-transform': 'uppercase'}),required=False)    
	campo = forms.ChoiceField(label='Calculado sobre',choices=CAMPO,required=True)	
	fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),required = False,initial=inicioMes())
	fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker','autocomplete':'off'}),required = False,initial=finMes())    	
	pto_vta = forms.IntegerField(label='Pto. Vta.',required = False)		
	comision = forms.DecimalField(label=u'Comisión',required = False,widget=PrependWidget(attrs={'class':'form-control','step':0.01},base_widget=NumberInput, data='%'),initial=5.00,decimal_places=2)
	def __init__(self, *args, **kwargs):
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None) 
		super(ConsultaVendedores, self).__init__(*args, **kwargs)						
		self.fields['vendedor'].queryset = egr_entidad.objects.filter(tipo_entidad=3,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
