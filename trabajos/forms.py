# -*- coding: utf-8 -*-
from django import forms
from .models import *
from django.forms import ModelForm
import datetime
from .utilidades import *
from django.forms.widgets import TextInput,NumberInput
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import TabHolder, Tab
from datetime import datetime,date,timedelta
from django.utils import timezone
from entidades.models import egr_entidad
from productos.models import prod_productos,prod_lista_precios,prod_ubicacion
from general.utilidades import *

def inicioMes():
	hoy=date.today()
	hoy = date(hoy.year,hoy.month,1)
	return hoy



class OPForm(forms.ModelForm):
	cliente = forms.ModelChoiceField(label='Cliente',queryset=egr_entidad.objects.filter(tipo_entidad=1,baja=False),empty_label='---',required = False)
	vendedor = forms.ModelChoiceField(label='Vendedor',queryset=egr_entidad.objects.filter(tipo_entidad=3,baja=False),empty_label='---',required = False)		
	fecha = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'datepicker'}),initial=timezone.now().date())							
	fecha_vto = forms.DateField(label='Fecha',required = False,widget=forms.DateInput(attrs={'class': 'datepicker'}))							
	fecha_entrega = forms.DateField(required = False,widget=forms.DateInput(attrs={'class': 'datepicker'}),initial=timezone.now().date())							
	hora_entrega = forms.TimeField(required = False,widget=forms.TimeInput(format='%H:%M'),initial=timezone.now().time())							
	muestra_enviada = forms.ModelChoiceField(label='Muestra Enviada a',queryset=egr_entidad.objects.filter(tipo_entidad__lte=2,baja=False),empty_label='---',required = False)		
	importe_total = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)	
	detalle = forms.CharField(label='Otros Detalles',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 5}),required = False)				
	lista_precios = forms.ModelChoiceField(label='Lista de Precios',queryset=prod_lista_precios.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	origen_destino = forms.ModelChoiceField(label=u'Ubicación',queryset=prod_ubicacion.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)	
	class Meta:
			model = orden_pedido			
			exclude = ['id','fecha_creacion','empresa','estado']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)		
		usr= request.user     
		super(OPForm, self).__init__(*args, **kwargs)
		try:
			empresa = usr.userprofile.id_usuario.empresa
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
		except gral_empresa.DoesNotExist:
			empresa = None

	def clean_cliente(self):		
		entidad = self.cleaned_data['cliente']
		if not entidad:			
				raise forms.ValidationError(u"Debe seleccionar un Cliente.")				
		return entidad

class OPDetalleForm(forms.ModelForm):
	orden_pedido = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	producto = forms.ModelChoiceField(queryset=prod_productos.objects.filter(baja = False),required = False)		
	cantidad = forms.DecimalField(initial=1,decimal_places=2)	
	unidad = forms.CharField(required = False,widget=forms.TextInput(attrs={ 'class':'form-control unidades','readonly':'readonly'}),initial='u.')
	importe_unitario = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	importe_total = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	lista_precios = forms.ModelChoiceField(queryset=prod_lista_precios.objects.all(),widget = forms.HiddenInput(),required = False)
	origen_destino = forms.ModelChoiceField(queryset=prod_ubicacion.objects.all(),widget = forms.HiddenInput(),required = False)

	class Meta:
			model = orden_pedido_detalle
			exclude = ['id','fecha_creacion']	

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(OPDetalleForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['producto'].queryset = prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3),empresa__id__in=empresas_habilitadas(request)).order_by('nombre')			
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
		except gral_empresa.DoesNotExist:
			empresa = None			


class OPEstadoForm(forms.ModelForm):		
	estado = forms.ModelChoiceField(label='Estado',queryset=cpb_estado.objects.filter(tipo=10).order_by('id'),required = False,empty_label='---',initial=1)	
	class Meta:
			model = orden_pedido			
			fields = ['estado']

	

#################################################################################

class OTForm(forms.ModelForm):	
	responsable = forms.ModelChoiceField(label='Responsable',queryset=egr_entidad.objects.filter(tipo_entidad=3,baja=False),empty_label='---',required = False)		
	fecha = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'datepicker'}),initial=timezone.now().date())							
	fecha_estimada = forms.DateField(label='Fecha Estimada',required = True,widget=forms.DateInput(attrs={'class': 'datepicker'}))								
	detalle = forms.CharField(label='Otros Detalles',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 5}),required = False)				
	origen_destino = forms.ModelChoiceField(label=u'Ubicación',queryset=prod_ubicacion.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)	

	class Meta:
			model = orden_trabajo		
			exclude = ['id','fecha_creacion','empresa','estado','usuario']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)		
		usr= request.user     
		super(OTForm, self).__init__(*args, **kwargs)
		try:
			empresa = usr.userprofile.id_usuario.empresa
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
		except gral_empresa.DoesNotExist:
			empresa = None

	# def clean_responsable(self):		
	# 	entidad = self.cleaned_data['responsable']
	# 	if not entidad:			
	# 			raise forms.ValidationError(u"Debe seleccionar un Responsable.")				
	# 	return entidad

class OTDetalleForm(forms.ModelForm):
	orden_trabajo = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	producto = forms.ModelChoiceField(queryset=prod_productos.objects.filter(tipo_producto=1,baja = False),required = False)		
	cantidad = forms.DecimalField(initial=1,decimal_places=2)		
	unidad = forms.CharField(required = False,widget=forms.TextInput(attrs={ 'class':'form-control unidades','readonly':'readonly'}),initial='u.')

	class Meta:
			model = orden_trabajo_detalle
			exclude = ['id','fecha_creacion']	

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(OTDetalleForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['producto'].queryset = prod_productos.objects.filter(tipo_producto=1,baja=False,mostrar_en__in=(1,3),empresa__id__in=empresas_habilitadas(request)).order_by('nombre')						
		except gral_empresa.DoesNotExist:
			empresa = None		

#################################################################################

class OCForm(forms.ModelForm):	
	vendedor = forms.ModelChoiceField(label='Vendedor',queryset=egr_entidad.objects.filter(tipo_entidad=3,baja=False),empty_label='---',required = False)		
	colocador = forms.ModelChoiceField(label='Colocador',queryset=egr_entidad.objects.filter(tipo_entidad=3,baja=False),empty_label='---',required = False)		
	fecha_colocacion = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'datepicker'}),initial=timezone.now().date())							
	hora_colocacion = forms.TimeField(required = False,widget=forms.TimeInput(format='%H:%M'),initial=timezone.now().time())		
	fecha_vto = forms.DateField(label='Fecha Vencimiento',required = False,widget=forms.DateInput(attrs={'class': 'datepicker'}))								
	detalle = forms.CharField(label='Otros Detalles',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 5}),required = False)					
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)	

	class Meta:
			model = orden_colocacion	
			exclude = ['id','fecha_creacion','empresa','estado','usuario','fecha_colocado']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		usr= request.user     
		super(OCForm, self).__init__(*args, **kwargs)
