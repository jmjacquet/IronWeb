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
from general.models import gral_plan_cuentas,gral_empresa
from comprobantes.models import cpb_cuenta
from general.flavor import ARCUITField,ARDNIField,ARPostalCodeField
from chosen import forms as chosenforms
from .utilidades import *

ESTADO_ = (
 (0,'ACTIVOS'),	
 (1,'TODOS'), 
)

class ConsultaProds(forms.Form):               
	nombre = forms.CharField(label='Nombre',max_length=100,widget=forms.TextInput(attrs={'class':'form-control','text-transform': 'uppercase'}),required=False)    
   	estado = forms.ChoiceField(label='Estado',choices=ESTADO_,required=False,initial=0)	    
				
class ProductosForm(forms.ModelForm):
	descripcion = forms.CharField(label='Observaciones / Datos adicionales',widget=forms.Textarea(attrs={'class':'form-control2', 'rows': 3}),required = False)			
	tasa_iva = forms.ModelChoiceField(queryset=gral_tipo_iva.objects.all(),required = True,initial=5)	
	categoria = forms.ModelChoiceField(queryset=prod_categoria.objects.all(),required = True)	
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)
	cta_ingreso = chosenforms.ChosenModelChoiceField(label='Cuenta Ingreso',queryset=gral_plan_cuentas.objects.filter(baja=False),empty_label='---',required = False)
	cta_egreso = chosenforms.ChosenModelChoiceField(label='Cuenta Egreso',queryset=gral_plan_cuentas.objects.filter(baja=False),empty_label='---',required = False)
	ubicacion = forms.ModelChoiceField(queryset=prod_ubicacion.objects.filter(baja=False),required = False)	
	stock = forms.DecimalField(label='Stock Inicial',initial=1,decimal_places=2,required = False)	
	ppedido = forms.DecimalField(label=popover_html(u'Punto Pedido', u'Stock de Advertencia'),initial=0,decimal_places=2,required = False)	
	coef_iva = forms.DecimalField(widget = forms.HiddenInput(), required = False,decimal_places=3)	
	codigo_barras = forms.CharField(label=u'Código de Barras',required = False,
			widget=PrePendWidgetBoton(attrs={'class':'form-control','type':'number','placeholder':u'Presione para generar un CB a partir del Código',},
			base_widget=TextInput,data='<i class="fa fa-barcode"></i>',tooltip=u"Presione para generar un CB a partir del Código",id="generarCB"))	
	class Meta:
			model = prod_productos
			exclude = ['id','baja','fecha_creacion','fecha_modif','empresa']

	def __init__(self, *args,**kwargs):
		request = kwargs.pop('request', None)
		super(ProductosForm, self).__init__(*args, **kwargs)      
		try:
			empresa = empresa_actual(request)			
			self.fields['cta_ingreso'].queryset = gral_plan_cuentas.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request),tipo=1)
			self.fields['cta_egreso'].queryset = gral_plan_cuentas.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request),tipo=2)			
			self.fields['ubicacion'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))			
			self.fields['categoria'].queryset = prod_categoria.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))			
		except gral_empresa.DoesNotExist:
			empresa = None  

	def clean(self):		
		super(forms.ModelForm,self).clean()	
		ubicacion = self.cleaned_data.get('ubicacion')
		tipo_form = self.cleaned_data.get('tipo_form')
		if (not ubicacion) and (tipo_form=='ALTA'):
			self._errors['ubicacion'] = [u'Debe seleccionar una Ubicación!']

class ProductosFormModal(forms.ModelForm):
	descripcion = forms.CharField(label='Observaciones / Datos adicionales',widget=forms.Textarea(attrs={'class':'form-control2', 'rows': 3}),required = False)			
	tasa_iva = forms.ModelChoiceField(queryset=gral_tipo_iva.objects.all(),required = True,initial=5)	
	categoria = forms.ModelChoiceField(queryset=prod_categoria.objects.all(),required = True)	
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)	
	ubicacion = forms.ModelChoiceField(queryset=prod_ubicacion.objects.filter(baja=False),required = False)	
	stock = forms.DecimalField(label='Stock Inicial',initial=1,decimal_places=2,required = False)	
	ppedido = forms.DecimalField(label=popover_html(u'Punto Pedido', u'Stock de Advertencia'),initial=0,decimal_places=2,required = False)	
	coef_iva = forms.DecimalField(widget = forms.HiddenInput(), required = False,decimal_places=3)	
	codigo_barras = forms.CharField(required = False,label=u'Código de Barras',
			widget=PrePendWidgetBoton(attrs={'class':'form-control','type':'number','placeholder':u'Presione para generar un CB a partir del Código',},
			base_widget=TextInput,data='<i class="fa fa-barcode"></i>',tooltip=u"Presione para generar un CB a partir del Código",id="generarCB"))	
	lista_precios = forms.ModelChoiceField(queryset=prod_lista_precios.objects.filter(baja=False),required = False)	
	precio_costo = forms.DecimalField(label='Precio Costo',widget=PrependWidget(attrs={'class':'form-control','step':0.01},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	precio_cimp = forms.DecimalField(label='Precio c/Imp.',widget=PrependWidget(attrs={'class':'form-control','step':0.01},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	precio_venta = forms.DecimalField(label='Precio Venta',widget=PrependWidget(attrs={'class':'form-control','step':0.01},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	coef_ganancia = forms.DecimalField(label=popover_html(u'Coef.Gan.', u'Coeficiente de Ganancia (1=100%) [0 a 10]'),initial=0,decimal_places=3, required = False)		
	precio_itc = forms.DecimalField(label='Valor ITC',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0,decimal_places=3,required = False)
	precio_tasa = forms.DecimalField(label='Valor TH',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0,decimal_places=3,required = False)	
	class Meta:
			model = prod_productos
			exclude = ['id','baja','fecha_creacion','fecha_modif','empresa']

	def __init__(self, *args,**kwargs):
		request = kwargs.pop('request', None)
		super(ProductosFormModal, self).__init__(*args, **kwargs)      
		try:
			empresa = empresa_actual(request)			
			self.fields['ubicacion'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))			
			self.fields['categoria'].queryset = prod_categoria.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))			
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))			
			if not empresa.usa_impuestos:
				self.fields['precio_itc'].initial = 0
				self.fields['precio_tasa'].initial = 0
			else:				
				self.fields['precio_itc'].label = empresa.nombre_impuesto1	or ''			
				self.fields['precio_tasa'].label = empresa.nombre_impuesto2 or ''
		except gral_empresa.DoesNotExist:
			empresa = None  

	def clean(self):		
		super(forms.ModelForm,self).clean()	
		ubicacion = self.cleaned_data.get('ubicacion')
		tipo_form = self.cleaned_data.get('tipo_form')
		if (not ubicacion) and (tipo_form=='ALTA'):
			self._errors['ubicacion'] = [u'Debe seleccionar una Ubicación!']

		lista_precios = self.cleaned_data.get('lista_precios')
		if not lista_precios:
			self._errors['lista_precios'] = [u'Debe seleccionar una Lista de Precios!']
		coef_ganancia = self.cleaned_data.get('coef_ganancia')
		if coef_ganancia:
			if coef_ganancia>10:
				self._errors['coef_ganancia'] = [u'Valor de 0 a 10!']

class Producto_ListaPreciosForm(forms.ModelForm):
	producto = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	lista_precios = forms.ModelChoiceField(queryset=prod_lista_precios.objects.filter(baja=False),required = False)	
	precio_costo = forms.DecimalField(label='Precio Costo',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	precio_cimp = forms.DecimalField(label='Precio c/Imp.',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	precio_venta = forms.DecimalField(label='Precio Venta',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	precio_itc = forms.DecimalField(label='Valor ITC',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0,decimal_places=3,required = False)
	precio_tasa = forms.DecimalField(label='Valor TH',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0,decimal_places=3,required = False)	
	coef_ganancia = forms.DecimalField(initial=0,decimal_places=3)		

	class Meta:
			model = prod_producto_lprecios
			exclude = ['id']	
	
	def __init__(self, *args,**kwargs):
		request = kwargs.pop('request', None)
		super(Producto_ListaPreciosForm, self).__init__(*args, **kwargs)      
		try:
			empresa = empresa_actual(request)			
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))			
			if not empresa.usa_impuestos:
				self.fields['precio_itc'].initial = 0
				self.fields['precio_tasa'].initial = 0
			else:				
				self.fields['precio_itc'].label = empresa.nombre_impuesto1	or ''			
				self.fields['precio_tasa'].label = empresa.nombre_impuesto2 or ''
		except gral_empresa.DoesNotExist:
			empresa = None  

	def clean(self):		
		super(forms.ModelForm,self).clean()	
		lista_precios = self.cleaned_data.get('lista_precios')
		if not lista_precios:
			self._errors['lista_precios'] = [u'Debe seleccionar una Lista de Precios!']
		coef_ganancia = self.cleaned_data.get('coef_ganancia')
		if coef_ganancia:
			if coef_ganancia>10:
				self._errors['coef_ganancia'] = [u'¡Valor de 0 a 10!']

		

class Producto_StockForm(forms.ModelForm):
	producto = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	ubicacion = forms.ModelChoiceField(queryset=prod_ubicacion.objects.filter(baja=False),required = False)		
	class Meta:
			model = prod_producto_ubicac
			exclude = ['id']

	def __init__(self, *args,**kwargs):
		request = kwargs.pop('request', None)
		super(Producto_StockForm, self).__init__(*args, **kwargs)      
		try:
			empresa = empresa_actual(request)			
			self.fields['ubicacion'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))			
		except gral_empresa.DoesNotExist:
			empresa = None  

	def clean(self):		
		super(forms.ModelForm,self).clean()	
		ubicacion = self.cleaned_data.get('ubicacion')		
		if not ubicacion:
			self._errors['ubicacion'] = [u'Debe cargar al menos una Ubicación!']


class CategoriasForm(forms.ModelForm):
	class Meta:
			model = prod_categoria
			exclude = ['id','baja','empresa']


class UbicacionForm(forms.ModelForm):
	class Meta:
			model = prod_ubicacion
			exclude = ['id','baja','empresa']

class ListaPreciosForm(forms.ModelForm):
	class Meta:
			model = prod_lista_precios
			exclude = ['id','baja','empresa']


class ConsultaLPreciosProd(forms.Form):               
	lista_precios = forms.ModelChoiceField(queryset=prod_lista_precios.objects.filter(baja=False),initial=0)	
	producto = forms.CharField(label='Producto/Servicio',widget=forms.TextInput(attrs={'class':'form-control'}),required = False)
	categoria = forms.ModelChoiceField(queryset=prod_categoria.objects.filter(baja=False),required = False)
	tipo_prod = forms.ChoiceField(label=u'Tipo',choices=TIPO_PRODUCTO_,initial=0)
	mostrar_en = forms.ChoiceField(label=u'Mostrar en',choices=MOSTRAR_PRODUCTO_,required=False,initial=0)

	def __init__(self, *args, **kwargs):		
		request = kwargs.pop('request', None)
		super(ConsultaLPreciosProd, self).__init__(*args, **kwargs)				
		self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
		self.fields['categoria'].queryset = prod_categoria.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
		

class Producto_EditarPrecioForm(forms.ModelForm):	
	precio_costo = forms.DecimalField(label='Precio Costo',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	precio_cimp = forms.DecimalField(label='Precio c/Imp.',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	precio_venta = forms.DecimalField(label='Precio Venta',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	precio_itc = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=vitc,decimal_places=2,required = False)	
	precio_tasa = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=vtasa,decimal_places=2,required = False)		
	coef_ganancia = forms.DecimalField(initial=1,decimal_places=3)		
	class Meta:
			model = prod_producto_lprecios
			exclude = ['id','producto','lista_precios']	

	def __init__(self, *args,**kwargs):
		request = kwargs.pop('request', None)
		super(Producto_EditarPrecioForm, self).__init__(*args, **kwargs)      
		try:
			empresa = empresa_actual(request)			
			if empresa.usa_impuestos:				
				self.fields['precio_itc'].label = empresa.nombre_impuesto1 or ''				
				self.fields['precio_tasa'].label = empresa.nombre_impuesto2 or ''
		except gral_empresa.DoesNotExist:
			empresa = None  



OPERACION_ = (
 (0,'Reemplazar Precio'),	
 (1,'Sumar Monto $'), 
 (2,'Sumar Monto %'), 
 (3,'Reemplazar Coef.Ganancia'),	
)

PRECIO_ = (
 (0,'Precio Venta'),	
 (1,'Precio Costo'), 
 (2,'Precio Costo c/Imp.'), 
 # (3,'Valor ITC'), 
 # (4,'Valor Tasa'), 
)

class ActualizarPrecioForm(forms.Form):	
	tipo_operacion = forms.ChoiceField(label=u'Operación',choices=OPERACION_,required=False,initial=0)	
	tipo_precio = forms.ChoiceField(label=u'Campo',choices=PRECIO_,required=False,initial=0)	
	valor = forms.DecimalField(label='Precio',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	porc = forms.IntegerField(label='Porcentaje',widget=PostPendWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='%',tooltip='[0-100%]'),initial=0)
	coeficiente = forms.DecimalField(initial=1,decimal_places=3)
	recalcular = forms.BooleanField(label='Recalcular Precio Venta',initial=0,required=False)


class ConsultaStockProd(forms.Form):               
	ubicacion = forms.ModelChoiceField(label=u'Ubicación',queryset=prod_ubicacion.objects.filter(baja=False),initial=0)	
	producto = forms.CharField(label='Producto/Servicio',widget=forms.TextInput(attrs={'class':'form-control'}),required = False)
	categoria = forms.ModelChoiceField(queryset=prod_categoria.objects.filter(baja=False),required = False)
	tipo_prod = forms.ChoiceField(label=u'Tipo',choices=TIPO_PRODUCTO_,initial=0)	
	lleva_stock = forms.ChoiceField(label=u'Lleva Stock',required = True,choices=SINO,initial=1)
	stock_pp = forms.ChoiceField(label=u'Bajo P.Pedido',required = False,choices=SINO)

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(ConsultaStockProd, self).__init__(*args, **kwargs)				
		self.fields['ubicacion'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
		self.fields['categoria'].queryset = prod_categoria.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))

OPERACION2_ = (
 (21,'Movimiento Ingreso Stock'),	
 (22,'Movimiento Egreso Stock'), 
 (0,'Actualizar Punto Pedido'), 
)

class ActualizarStockForm(forms.Form):	
	tipo_operacion = forms.ChoiceField(label=u'Operación',choices=OPERACION2_,required=True,initial=21)		
	valor = forms.DecimalField(label='Cantidad',initial=0.00,decimal_places=2)	

class CrearStockForm(forms.Form):		
	ubicacion = forms.ModelChoiceField(label=u'Ubicación',queryset=prod_ubicacion.objects.filter(baja=False),initial=0,required = True)	
	producto = forms.ModelChoiceField(queryset=prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3)),initial=0,required = True)	
	valor = forms.DecimalField(label='Cantidad',initial=0.00,decimal_places=2,required = True)	
	ppedido = forms.DecimalField(label='P.Pedido',initial=0.00,decimal_places=2,required = False)
	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CrearStockForm, self).__init__(*args, **kwargs)				
		self.fields['producto'].queryset = prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3),empresa__id__in=empresas_habilitadas(request)).order_by('nombre')
		self.fields['ubicacion'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))


class StockProdForm(forms.ModelForm):
	class Meta:
			model = prod_producto_ubicac
			exclude = ['id','producto','ubicacion']		

class ImpresionCodbarsForm(forms.Form):	
	detalle = forms.ChoiceField(label=u'Imprimir Detalle',choices=SINO,required=True,initial='S')
	pventa = forms.ChoiceField(label=u'Imprimir Precio Venta',choices=SINO,required=True,initial='S')
	cantidad = forms.IntegerField(label=u'Cantidad de Copias por Producto',required=True,initial=1)
	

class ImportarProductosForm(forms.Form):	
	archivo = forms.FileField(label='Seleccione un archivo',required=True)  
	sobreescribir = forms.ChoiceField(label=u'',choices=SINO,required=True,initial=1)
	lista_precios = forms.ModelChoiceField(queryset=prod_lista_precios.objects.filter(baja=False),initial=0)	
	empresa = forms.ModelChoiceField(queryset=gral_empresa.objects.all(),empty_label=None,required=True)	
	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(ImportarProductosForm, self).__init__(*args, **kwargs)		
		try:
			empresas = empresas_buscador(request)
			self.fields['empresa'].queryset = empresas
			self.fields['empresa'].initial = 1
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
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





from ingresos.forms import ProductoModelChoiceField
class BuscarProdDatos(forms.Form):
	productos_datos = ProductoModelChoiceField(queryset=prod_productos.objects.filter(baja=False),empty_label=None,required=False)	
	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(BuscarProdDatos, self).__init__(*args, **kwargs)				
		self.fields['productos_datos'].queryset = prod_productos.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('nombre')

		