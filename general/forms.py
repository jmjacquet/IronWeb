# -*- coding: utf-8 -*-
from django import forms
from .models import *
from django.forms import ModelForm
import datetime
from .utilidades import *
from django.contrib import admin
from django.forms.widgets import TextInput,NumberInput
from django.contrib.auth.models import User   # fill in custom user info then save it 
from django.contrib.auth.forms import UserCreationForm   
from django.utils.safestring import mark_safe
from .flavor import ARCUITField,ARDNIField,ARPostalCodeField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import TabHolder, Tab
from datetime import datetime,date,timedelta
from django.utils import timezone
from chosen import forms as chosenforms
from productos.models import prod_productos,prod_producto_lprecios,prod_lista_precios
from comprobantes.models import cpb_comprobante,cpb_pto_vta
from entidades.models import egr_entidad


def empresas_buscador(request):        
    empresas = gral_empresa.objects.filter(id__in=empresas_habilitadas(request)).order_by('id')        
    return empresas

def pto_vta_habilitados(request):    
    empresa = empresa_actual(request)  
    usuario = usuario_actual(request) 
    pv = cpb_pto_vta.objects.filter(baja=False).order_by('numero')
    if empresa:
    	pv = pv.filter(empresa=empresa)        
    try:
    	if usuario.cpb_pto_vta:
        	pv = pv.filter(id=usuario.cpb_pto_vta.id)        
    except:    	
    	return pv
    return pv

def pto_vta_habilitados_list(request):    
    pvs = pto_vta_habilitados(request)
    pvs = [pto.numero for pto in pvs]
   
    return pvs

def pto_vta_buscador(request):    
    empresa = empresa_actual(request)  
    usuario = usuario_actual(request) 
    pv = cpb_pto_vta.objects.filter(baja=False).order_by('numero')
    pvs = []
    if empresa:
    	pv = pv.filter(empresa=empresa)        
    try:
    	if usuario.cpb_pto_vta:
        	pv = pv.filter(id=usuario.cpb_pto_vta.id)

        pvs = [(pto.numero, pto.__unicode__()) for pto in pv]        
        pvs.insert(0,{'',label_todos})
    except:
    	pvs = [(pto.numero, pto.__unicode__()) for pto in pv]
    	pvs.insert(0,{'',label_todos})
    	return pvs
    return pvs

def get_pv_defecto(request):
        pvs = pto_vta_habilitados_list(request)
        num_pv=empresa_actual(request).pto_vta_defecto.numero
        usuario = usuario_actual(request)
        pvusr = usuario.cpb_pto_vta
        if pvusr:
        	return pvusr.numero
        elif num_pv in pvs:
            return num_pv
        else:
            return 1

            
class ConsultaCpbs(forms.Form):               
	entidad = forms.CharField(label='Cliente',max_length=100,widget=forms.TextInput(attrs={'class':'form-control','text-transform': 'uppercase'}),required=False)
	fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=inicioMesAnt(),required = False)
	fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=finMes(),required = False)    
	vendedor = forms.CharField(label='Vendedor',max_length=100,widget=forms.TextInput(attrs={'class':'form-control','text-transform': 'uppercase'}),required=False)
	pto_vta = forms.IntegerField(label='Pto. Vta.',required = False)
	letra = forms.ChoiceField(label='Letra',choices=COMPROB_FISCAL_,required=False,initial='')	
	estado = forms.ChoiceField(label='Estado',choices=ESTADO_,required=False,initial=0)	
	cae = forms.ChoiceField(label='CAE',choices=SINO,required=False,initial=0)
	
	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)  
		empresa = kwargs.pop('empresa', None)  
		super(ConsultaCpbs, self).__init__(*args, **kwargs)				

class ConsultaCpbsCompras(forms.Form):               
	entidad = forms.CharField(label='Proveedor',max_length=100,widget=forms.TextInput(attrs={'class':'form-control','text-transform': 'uppercase'}),required=False)
	fdesde =  forms.DateField(label='Fecha Desde',widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=inicioMesAnt(),required = False)
	fhasta =  forms.DateField(label='Fecha Hasta',widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=finMes(),required = False)    
	vendedor = forms.CharField(label='Vendedor',max_length=100,widget=forms.TextInput(attrs={'class':'form-control','text-transform': 'uppercase'}),required=False)
	pto_vta = forms.IntegerField(label='Pto. Vta.',required = False)
	letra = forms.ChoiceField(label='Letra',choices=COMPROB_FISCAL_,required=False,initial='')	
	estado = forms.ChoiceField(label='Estado',choices=ESTADO_,required=False,initial=0)	
	
	
	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)  
		empresa = kwargs.pop('empresa', None)  
		super(ConsultaCpbsCompras, self).__init__(*args, **kwargs)				


TIPO_CODBAR_QR_CHOICE = (
	('CODBAR', 'Código Barras'),
	('URL_DETALLE_PROD', 'URL Detalle')
)

class EmpresaForm(forms.ModelForm):
	# observaciones = forms.CharField(label='Observaciones / Datos adicionales',widget=forms.Textarea(attrs={ 'rows': 3}),required = False)		
	cuit = ARCUITField(label='CUIT',required = False,widget=PostPendWidgetBuscar(attrs={'class':'form-control','autofocus':'autofocus'},
			base_widget=TextInput,data='<i class="fa fa-search" aria-hidden="true"></i>',tooltip=u"Buscar datos y validar CUIT en AFIP"))		
	categ_fiscal = forms.ChoiceField(label=u'Categoría Fiscal',required = True,choices=CATEG_FISCAL)	
	# fact_nro_doc = ARDNIField(label=u'Número',required = False)	
	# cod_postal = ARPostalCodeField(label='CP',required = False)	
	fecha_inicio_activ = forms.DateField(label='Inicio Actividades',required = True,widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=inicioMes())	
	dias_vencimiento_cpbs =  forms.IntegerField(label=u'Días Vencimiento CPBS',required = True,initial=20)
	barra_busq_meses_atras =  forms.IntegerField(label=u'Meses Búsquedas atrás',required = True,initial=2)
	pto_vta_defecto = forms.ModelChoiceField(label='Pto.Vta. por Defecto',queryset=cpb_pto_vta.objects.filter(baja=False),empty_label=None,required = True)
	mail_cuerpo = forms.CharField(label=u'Cuerpo Email (envío de Comprobantes)',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 3}),required = False)				
	mail_password = forms.CharField(widget=forms.PasswordInput(render_value = True),max_length=20,label=u'Contraseña')
	codbar_tipo = forms.ChoiceField(label=u'Contenido del QR',required=False,choices=TIPO_CODBAR_QR_CHOICE)
	qr_size = forms.IntegerField(label=u'Tamaño QR (mm)', required=True, initial=40)
	class Meta:
			model = gral_empresa
			exclude = ['id','baja','fecha_creacion',]	

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(EmpresaForm, self).__init__(*args, **kwargs)		
		pto_vta = pto_vta_habilitados(request)
		self.fields['pto_vta_defecto'].queryset = pto_vta					

	# def clean(self):
	# 	super(forms.ModelForm,self).clean()
	# 	ruta_logo = self.cleaned_data.get('ruta_logo', False)
	# 	try:
	# 		if ruta_logo:			
	# 			if ruta_logo.file.size > 1024*1024:
	# 				raise forms.ValidationError(u"El tamaño de la Imágen no debe superar los 1024 KB (<=1MB)")            
	# 		else:
	# 			raise forms.ValidationError(u"No se pudo leer la Imágen")
	# 	except:
	# 		raise forms.ValidationError(u"No se pudo leer la Imágen")

	# 	return self.cleaned_data

class TareasForm(forms.ModelForm):
	title = forms.CharField(label=u'Título',widget=forms.Textarea(attrs={ 'rows': 1,'class':'form-control2'}),required = False)		
	detalle = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'rows': 5,'class':'form-control2 editables'}),required = False)		
	fecha = forms.DateField(label='Fecha',required = True,widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=timezone.now)	

	class Meta:
			model = gral_tareas
			exclude = ['id','fecha_creacion','color','usuario_creador','respuesta']			


class ConsultaLPreciosProductos(forms.Form):               
    lista = chosenforms.ChosenModelChoiceField(label='Lista',queryset=prod_lista_precios.objects.filter(baja=False),empty_label=label_todos,required = False)

    def __init__(self, *args, **kwargs):		
		empresa = kwargs.pop('empresa', None)     
		super(ConsultaLPreciosProductos, self).__init__(*args, **kwargs)
		self.fields['lista'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('nombre')			
		

# class UserForm(UserCreationForm):
#     username = forms.CharField(label=u'Usuario',required = True)
#     password1 = forms.CharField(widget=forms.PasswordInput(render_value = True),max_length=10,label='Contraseña') 
#     password2 = forms.CharField(widget=forms.PasswordInput(render_value = True),max_length=10,label='Confirmar Contraseña') 
#     class Meta:
#         model = User
#         fields = ('username', 'password1', 'password2')