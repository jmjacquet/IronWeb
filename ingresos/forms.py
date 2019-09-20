# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
import datetime
from general.utilidades import *
from django.contrib import admin
from django.utils import *
from django.forms.widgets import TextInput,NumberInput,Select
from django.forms import Widget
from django.db.models import Q
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div,Button,HTML
from comprobantes.models import *
from comprobantes.views import *
from chosen import forms as chosenforms
import math
from general.forms import get_pv_defecto


class EntidadModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
		entidad=u'%s' % obj.apellido_y_nombre.upper()
		cuit='' 
		if obj.fact_cuit=='':    		
			if obj.nro_doc=='':
				cuit = ''
			else:
				cuit = u' - %s'  % obj.nro_doc
		elif obj.fact_cuit:
			cuit = u' - %s'  % obj.fact_cuit
		
		categ_fiscal = ''
		if obj.fact_categFiscal:
			categ_fiscal = ' - %s' % obj.get_categFiscal()
		entidad = u'%s%s%s' % (entidad,cuit,categ_fiscal)
		return entidad.upper()

class CPBVentaForm(forms.ModelForm):
	entidad = EntidadModelChoiceField(label='Cliente',queryset=egr_entidad.objects.filter(tipo_entidad=1,baja=False),empty_label='---',required = False)
	vendedor = EntidadModelChoiceField(label='Vendedor',queryset=egr_entidad.objects.filter(tipo_entidad=3,baja=False),empty_label='---',required = False)
	pto_vta = forms.ChoiceField(label='Pto. Vta.',choices=[(pto.numero, pto.__unicode__()) for pto in cpb_pto_vta.objects.filter(baja=False)],required = False)
	#pto_vta = forms.ModelChoiceField(label='Pto. Vta.',queryset=cpb_pto_vta.objects.filter(baja=False),empty_label=None,required = False)
	fecha_cpb = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=datetime.now())
	fecha_vto = forms.DateField(required = False,widget=forms.DateInput(attrs={'class': 'datepicker'}))	
	observacion = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 5}),required = False)				
	importe_perc_imp = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_subtotal = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_total = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_iva = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_no_gravado = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_cobrado = forms.DecimalField(initial=0.00,decimal_places=2,widget = forms.HiddenInput(), required = False)
	letra = forms.ChoiceField(label='Letra',choices=COMPROB_FISCAL,required=False,initial=1)	
	cpb_tipo = forms.ModelChoiceField(label='Tipo CPB',queryset=cpb_tipo.objects.filter(compra_venta='V',baja=False,tipo__in=[1,2,3,9]),required = True,empty_label=None)
	condic_pago = forms.ChoiceField(label=u'Condición Pago',choices=CONDICION_PAGO,required=False,initial=1)
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)	
	cliente_categ_fiscal = forms.IntegerField(widget = forms.HiddenInput(), required = False,initial=5)		
	cliente_descuento = forms.DecimalField(initial=0.00,decimal_places=2,widget = forms.HiddenInput(), required = False)	
	lista_precios = forms.ModelChoiceField(label='Lista de Precios',queryset=prod_lista_precios.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	origen_destino = forms.ModelChoiceField(label=u'Ubicación',queryset=prod_ubicacion.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	importe_tasa1 = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	importe_tasa2 = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)	
	class Meta:
			model = cpb_comprobante
			exclude = ['id','fecha_creacion','fecha_imputacion','cae','cae_vto','estado','anulacion_motivo','anulacion_fecha','empresa','usuario','presup_tiempo_entrega','presup_forma_pago','presup_aprobacion']

	def clean_entidad(self):		
		entidad = self.cleaned_data['entidad']
		if not entidad:			
				raise forms.ValidationError(u"Debe seleccionar un Cliente.")				
		return entidad

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)		
		super(CPBVentaForm, self).__init__(*args, **kwargs)
		try:			
			empresa = empresa_actual(request)
			letras = tipo_comprob_fiscal(empresa.categ_fiscal)
			self.fields['letra'].choices = letras			
			pto_vta = pto_vta_habilitados(request)
			self.fields['pto_vta'].choices = [(pto.numero, pto.__unicode__()) for pto in pto_vta]						
			self.fields['pto_vta'].initial = get_pv_defecto(request)
			#self.fields['pto_vta'].queryset = pto_vta
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
			self.fields['numero'].initial= ultimoNro(1,pto_vta[0],letras[0][1])
			self.fields['entidad'].queryset = egr_entidad.objects.filter(tipo_entidad=1,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
			self.fields['vendedor'].queryset = egr_entidad.objects.filter(tipo_entidad=3,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
			self.fields['fecha_vto'].initial = datetime.now()+timedelta(days=empresa.get_dias_venc())
			usr = usuario_actual(request)
			if usr.vendedor_defecto:
				self.fields['vendedor'].initial = usr.vendedor_defecto.id
			if usr.cpb_tipo:
				self.fields['cpb_tipo'].initial = usr.cpb_tipo.id
			if usr.condic_pago:
				self.fields['condic_pago'].initial = usr.condic_pago
			if not empresa.usa_impuestos:
				self.fields['importe_tasa1'].widget=forms.HiddenInput()
				self.fields['importe_tasa2'].widget=forms.HiddenInput()
			

		except gral_empresa.DoesNotExist:
			empresa = None
		
	def clean(self):						
		super(forms.ModelForm,self).clean()	
		tipo_form = self.cleaned_data.get('tipo_form')
		entidad = self.cleaned_data.get('entidad')
		importe_cobrado = self.cleaned_data.get('importe_cobrado')
		importe_total = self.cleaned_data.get('importe_total')
		if tipo_form == 'EDICION':							
				if importe_cobrado > importe_total:					
					self._errors['importe_cobrado'] = u'El total del comprobante debe ser igual o mayor al total de sus cobros!($%s)' % (importe_total-importe_cobrado)

		letra = self.cleaned_data.get('letra')
		cpb_tipo = self.cleaned_data.get('cpb_tipo')
		pto_vta = self.cleaned_data.get('pto_vta')
		cliente_categ_fiscal = self.cleaned_data.get('cliente_categ_fiscal')
		numero = self.cleaned_data.get('numero')
		try:
			empresa = self.initial['request'].user.userprofile.id_usuario.empresa						
			if (not facturacion_cliente_letra(letra,cliente_categ_fiscal,empresa.categ_fiscal))and(cpb_tipo.facturable):
				raise forms.ValidationError(u'Letra no válida para el Cliente/CPB seleccionado!')	

		except gral_empresa.DoesNotExist:
			empresa = None
		

		if (importe_total > 1000)and(cliente_categ_fiscal==5)and(entidad.fact_cuit=='')and(entidad.nro_doc=='')and(cpb_tipo.facturable):
			try:
				pv = cpb_pto_vta.objects.get(numero=int(pto_vta),empresa=empresa)  
				if pv.fe_electronica:
					raise forms.ValidationError(u"El total de comprobante no puede superar los $1000.00 para Consumidor Final sin que el mismo posea un Documento ó CUIT válidos!.")			
			except:
				pass	
			
		
		
		id_cpbs=cpb_comprobante.objects.filter(numero=numero,pto_vta=pto_vta,letra=letra,cpb_tipo=cpb_tipo,empresa=empresa).values_list('id',flat=True)
		id_cpbs = [int(x) for x in id_cpbs]  
		cant=len(id_cpbs)
		id_cpb=self.instance.id
		if (cant > 0)and(id_cpb not in id_cpbs):
			raise forms.ValidationError("El Nº de Comprobante ingresado ya existe en el Sistema! Verifique.")	


		return self.cleaned_data
	
class CPBVentaDetalleForm(forms.ModelForm):
	producto = forms.ModelChoiceField(queryset=prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3)),required = True)	
	porc_dcto = forms.DecimalField(initial=0,decimal_places=2)	
	cantidad = forms.DecimalField(initial=1,decimal_places=2)	
	unidad = forms.CharField(required = False,widget=forms.TextInput(attrs={ 'class':'form-control unidades','readonly':'readonly'}),initial='u.')
	importe_unitario = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	importe_costo = forms.DecimalField(widget = forms.HiddenInput(), required = False)
	importe_subtotal = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	pventa = forms.DecimalField(widget = forms.HiddenInput(), required = False)
	coef_iva = forms.DecimalField(widget = forms.HiddenInput(), required = False)
	tasa_iva = forms.ModelChoiceField(queryset=gral_tipo_iva.objects.all(),widget = forms.HiddenInput(),required = False)
	importe_iva = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	importe_total = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)		
	lista_precios = forms.ModelChoiceField(queryset=prod_lista_precios.objects.all(),widget = forms.HiddenInput(),required = False)
	origen_destino = forms.ModelChoiceField(queryset=prod_ubicacion.objects.all(),widget = forms.HiddenInput(),required = False)
	comprobante_original = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	coef_tasa1 = forms.DecimalField(initial=0.000,decimal_places=3,widget = forms.HiddenInput(), required = False)	
	coef_tasa2 = forms.DecimalField(initial=0.000,decimal_places=3,widget = forms.HiddenInput(), required = False)
	importe_tasa1 = forms.DecimalField(initial=0.00,decimal_places=2,widget = forms.HiddenInput(), required = False)	
	importe_tasa2 = forms.DecimalField(initial=0.00,decimal_places=2,widget = forms.HiddenInput(), required = False)	
	importe_no_gravado = forms.DecimalField(initial=0.00,decimal_places=2,widget = forms.HiddenInput(), required = False)	
	class Meta:
			model = cpb_comprobante_detalle
			exclude = ['id','fecha_creacion']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBVentaDetalleForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['producto'].queryset = prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3),empresa__id__in=empresas_habilitadas(request)).order_by('nombre')			
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
		except gral_empresa.DoesNotExist:
			empresa = None			

	def clean(self):		
		super(CPBVentaDetalleForm,self).clean()	
		padre = self.instance.cpb_comprobante
		comprobante_original = self.cleaned_data.get('comprobante_original')
		#Si es ALTA
		if not padre and not comprobante_original:
			producto = self.cleaned_data.get('producto')
			if not producto:
				self._errors['cantidad'] = [u'Stock insuficiente!']
			else:
				cantidad = self.cleaned_data.get('cantidad')
				origen_destino = self.cleaned_data.get('origen_destino')
				comprobante_original = self.cleaned_data.get('comprobante_original')
				if cantidad and producto.llevar_stock:			
					prod_ubi, created = prod_producto_ubicac.objects.get_or_create(producto=producto,ubicacion=origen_destino)
					stock=prod_ubi.get_stock_()		
					if (stock < cantidad) and  not producto.stock_negativo:
						self._errors['cantidad'] = [u'Stock insuficiente!']
			return self.cleaned_data

class CPBVentaPercImpForm(forms.ModelForm):
	perc_imp = forms.ModelChoiceField(label='Perc_Imp',queryset=cpb_perc_imp.objects.all(),empty_label='---',required = False)
	detalle = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control','rows': 3}),required = False)		
	importe_total = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	class Meta:
			model = cpb_comprobante_perc_imp
			exclude = ['id']		
	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)		
		super(CPBVentaPercImpForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['perc_imp'].queryset = cpb_perc_imp.objects.filter(empresa__id__in=empresas_habilitadas(request))			
		except gral_empresa.DoesNotExist:
			empresa = None			

	def clean(self):						
		super(forms.ModelForm,self).clean()	
		importe_total = self.cleaned_data.get('importe_total')				
		perc_imp = self.cleaned_data.get('perc_imp')							
		if perc_imp!=None:
			if not importe_total:
				self._errors['importe_total'] = [u'¡Verificar Fecha!']	
			if not perc_imp:
				self._errors['perc_imp'] = [u'¡Verificar Perc/Imp!']	

		return self.cleaned_data

class CPBFPForm(forms.ModelForm):
	tipo_forma_pago = forms.ModelChoiceField(label='FP',queryset=cpb_tipo_forma_pago.objects.filter(baja=False),empty_label=None,required = False)
	mdcp_fecha = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=datetime.now(),required = False)
	mdcp_banco = forms.ModelChoiceField(label='Banco',queryset=cpb_banco.objects.filter(baja=False),empty_label='---',required = False)
	detalle = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control','rows': 3}),required = False)		
	importe = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	cta_ingreso = forms.ModelChoiceField(label='Cta. Ingreso',queryset=cpb_cuenta.objects.all(),required = True,empty_label=None)
	class Meta:
			model = cpb_comprobante_fp
			exclude = ['id','fecha_creacion','cta_egreso']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)		
		super(CPBFPForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['tipo_forma_pago'].queryset = cpb_tipo_forma_pago.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False)			
			self.fields['mdcp_banco'].queryset = cpb_banco.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False)			
			self.fields['cta_ingreso'].queryset = cpb_cuenta.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False,tipo__in=[0,1,2])			
		except gral_empresa.DoesNotExist:
			empresa = None	

	def clean(self):						
		super(forms.ModelForm,self).clean()	
		tfp = self.cleaned_data.get('tipo_forma_pago')				
		mdcp_fecha = self.cleaned_data.get('mdcp_fecha')				
		cta_ingreso = self.cleaned_data.get('cta_ingreso')	
		mdcp_cheque  = self.cleaned_data.get('mdcp_cheque')
		mdcp_banco = self.cleaned_data.get('mdcp_banco')				
		if not mdcp_fecha:
			self._errors['mdcp_fecha'] = [u'¡Verificar Fecha!']
		if cta_ingreso:
			if ((cta_ingreso.tipo==2) and((not mdcp_fecha)or(not tfp)or(not mdcp_cheque)or(not mdcp_banco))):			
				raise forms.ValidationError("¡Debe completar los datos del medio de Cobro/Pago!")			

		return self.cleaned_data


#*************************************************************************

class CPBRemitoForm(forms.ModelForm):
	entidad = forms.ModelChoiceField(label='Cliente',queryset=egr_entidad.objects.filter(tipo_entidad=1,baja=False),empty_label='---',required = True)		
	fecha_cpb = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'datepicker'}),initial=datetime.now())	
	observacion = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 5}),required = False)						
	letra = forms.ChoiceField(label='Letra',choices=COMPROB_FISCAL_X,required=False,initial=1)	
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)	
	class Meta:
			model = cpb_comprobante
			exclude = ['id','fecha_creacion','cpb_tipo','numero','fecha_imputacion','cae','cae_vto','estado','anulacion_motivo','anulacion_fecha','empresa','usuario','presup_tiempo_entrega','presup_forma_pago','presup_aprobacion','cpb_nro_afip','cpb_tipo']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)		
		super(CPBRemitoForm, self).__init__(*args, **kwargs)
		self.fields['letra'].choices = COMPROB_FISCAL_X
		try:
			empresa = empresa_actual(request)			
			self.fields['entidad'].queryset = egr_entidad.objects.filter(tipo_entidad=1,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')

		except gral_empresa.DoesNotExist:
			empresa = None


class CPBRemitoDetalleForm(forms.ModelForm):
	producto = chosenforms.ChosenModelChoiceField(queryset=prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3)),required = True)
	cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)
	detalle = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control','rows': 1}),required = False)			
	cantidad = forms.DecimalField(initial=1,decimal_places=2)	
	unidad = forms.CharField(required = False,widget=forms.TextInput(attrs={ 'class':'form-control unidades','readonly':'readonly'}),initial='u.')
	lista_precios = forms.ModelChoiceField(queryset=prod_lista_precios.objects.all(),widget = forms.HiddenInput(),required = False)
	origen_destino = forms.ModelChoiceField(queryset=prod_ubicacion.objects.all(),widget = forms.HiddenInput(),required = False)
	class Meta:
			model = cpb_comprobante_detalle
			exclude = ['id','fecha_creacion','coef_iva','tasa_iva']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBRemitoDetalleForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['producto'].queryset = prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3),empresa__id__in=empresas_habilitadas(request)).order_by('nombre')			
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
		except gral_empresa.DoesNotExist:
			empresa = None			

	def clean(self):		
		super(forms.ModelForm,self).clean()	
		producto = self.cleaned_data.get('producto')
		cantidad = self.cleaned_data.get('cantidad')
		if not producto:			
			self._errors['producto'] = [u'Cargar al menos un producto!']

		return self.cleaned_data

#*************************************************************************

class CPBPresupForm(forms.ModelForm):
	entidad = forms.ModelChoiceField(label='Cliente',queryset=egr_entidad.objects.filter(tipo_entidad=1,baja=False),empty_label='---',required = False)
	vendedor = forms.ModelChoiceField(label='Vendedor',queryset=egr_entidad.objects.filter(tipo_entidad=3,baja=False),empty_label='---',required = False)		
	fecha_cpb = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'datepicker'}),initial=datetime.now())							
	fecha_vto = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'datepicker'}))							
	pto_vta = forms.ChoiceField(label='Pto. Vta.',choices=[(pto.numero, pto.__unicode__()) for pto in cpb_pto_vta.objects.filter(baja=False)],required = False)
	id_cpb_padre = forms.IntegerField(widget = forms.HiddenInput(), required = False)			
	observacion = forms.CharField(label='Observaciones',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 4}),required = False)				
	presup_tiempo_entrega = forms.CharField(label='Tiempo estimado de Entrega',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 1}),required = False)				
	presup_forma_pago = forms.CharField(label='Forma de Pago',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 1}),required = False)					
	importe_subtotal = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_total = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_iva = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	letra = forms.ChoiceField(label='Letra',choices=COMPROB_FISCAL_X,required=False,initial=1)
	cliente_categ_fiscal = forms.IntegerField(widget = forms.HiddenInput(), required = False,initial=5)	
	cliente_descuento = forms.DecimalField(initial=0.00,decimal_places=2,widget = forms.HiddenInput(), required = False)	
	lista_precios = forms.ModelChoiceField(label='Lista de Precios',queryset=prod_lista_precios.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	origen_destino = forms.ModelChoiceField(label=u'Ubicación',queryset=prod_ubicacion.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)		
	class Meta:
			model = cpb_comprobante			
			exclude = ['id','fecha_creacion','numero','fecha_imputacion','cae','cae_vto','estado','anulacion_motivo','anulacion_fecha','empresa','usuario','cpb_nro_afip','importe_perc_imp','cpb_tipo']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBPresupForm, self).__init__(*args, **kwargs)		
		try:
			empresa = empresa_actual(request)
			letras = tipo_comprob_fiscal(empresa.categ_fiscal)			
			self.fields['letra'].choices = letras			
			self.fields['letra'].initial = 'X'

			pto_vta = pto_vta_habilitados(request)
			self.fields['pto_vta'].choices = [(pto.numero, pto.__unicode__()) for pto in pto_vta]
			self.fields['pto_vta'].initial = get_pv_defecto(request)
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))			
			self.fields['entidad'].queryset = egr_entidad.objects.filter(tipo_entidad=1,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
			self.fields['fecha_vto'].initial = datetime.now()+timedelta(days=empresa.get_dias_venc())
			usr = usuario_actual(request)
			if usr.vendedor_defecto:
				self.fields['vendedor'].initial = usr.vendedor_defecto.id			

		except gral_empresa.DoesNotExist:
			empresa = None


	def clean_entidad(self):		
		entidad = self.cleaned_data['entidad']
		if not entidad:			
				raise forms.ValidationError(u"Debe seleccionar un Cliente.")				
		return entidad

	def clean(self):						
		super(forms.ModelForm,self).clean()	
		tipo_form = self.cleaned_data.get('tipo_form')		
		letra = self.cleaned_data.get('letra')
		pto_vta = self.cleaned_data.get('pto_vta')		
		numero = self.cleaned_data.get('numero')						
		cliente_categ_fiscal = self.cleaned_data.get('cliente_categ_fiscal')
		numero = self.cleaned_data.get('numero')
		try:
			empresa = self.initial['request'].user.userprofile.id_usuario.empresa			
			if not nofacturac_cliente_letra(letra,cliente_categ_fiscal,empresa.categ_fiscal):
				raise forms.ValidationError(u'Letra no válida para el Cliente/CPB seleccionado!')	

		except gral_empresa.DoesNotExist:
			empresa = None

		cant=cpb_comprobante.objects.filter(numero=numero,pto_vta=pto_vta,letra=letra,cpb_tipo__id=11).count()						
		if (tipo_form == 'ALTA')and(cant > 0):			
			raise forms.ValidationError("¡El Nº de Comprobante ingresado ya existe en el Sistema! Verifique.")			

		return self.cleaned_data

class CPBPresupDetalleForm(forms.ModelForm):
	producto = chosenforms.ChosenModelChoiceField(queryset=prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3)),required = True)		
	importe_unitario = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	porc_dcto = forms.DecimalField(initial=0,decimal_places=2)	
	cantidad = forms.DecimalField(initial=1,decimal_places=2)	
	unidad = forms.CharField(required = False,widget=forms.TextInput(attrs={ 'class':'form-control unidades','readonly':'readonly'}),initial='u.')
	cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	id = forms.IntegerField(widget = forms.HiddenInput(), required = False)
	importe_costo = forms.DecimalField(widget = forms.HiddenInput(), required = False)
	importe_subtotal = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	coef_iva = forms.DecimalField(widget = forms.HiddenInput(), required = False)
	importe_iva = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	importe_total = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0,'readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	tasa_iva = forms.ModelChoiceField(queryset=gral_tipo_iva.objects.all(),widget = forms.HiddenInput(),required = False)
	lista_precios = forms.ModelChoiceField(queryset=prod_lista_precios.objects.all(),widget = forms.HiddenInput(),required = False)
	origen_destino = forms.ModelChoiceField(queryset=prod_ubicacion.objects.all(),widget = forms.HiddenInput(),required = False)
	class Meta:
			model = cpb_comprobante_detalle
			exclude = ['fecha_creacion']	

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBPresupDetalleForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['producto'].queryset = prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3),empresa__id__in=empresas_habilitadas(request)).order_by('nombre')			
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
		except gral_empresa.DoesNotExist:
			empresa = None		

class CPBPresupLiteForm(forms.ModelForm):
	entidad = EntidadModelChoiceField(label='Cliente',queryset=egr_entidad.objects.filter(tipo_entidad=1,baja=False),empty_label='---',required = False)
	vendedor = EntidadModelChoiceField(label='Vendedor',queryset=egr_entidad.objects.filter(tipo_entidad=3,baja=False),empty_label='---',required = False)		
	fecha_cpb = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'datepicker'}),initial=datetime.now())							
	fecha_vto = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'datepicker'}))							
	pto_vta = forms.ChoiceField(label='Pto. Vta.',choices=[(pto.numero, pto.__unicode__()) for pto in cpb_pto_vta.objects.filter(baja=False)],required = False)
	id_cpb_padre = forms.IntegerField(widget = forms.HiddenInput(), required = False)			
	observacion = forms.CharField(label='Observaciones',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 4}),required = False)				
	presup_tiempo_entrega = forms.CharField(label='Tiempo estimado de Entrega',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 1}),required = False)				
	presup_forma_pago = forms.CharField(label='Forma de Pago',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 1}),required = False)					
	importe_subtotal = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_total = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_iva = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	letra = forms.ChoiceField(label='Letra',choices=COMPROB_FISCAL_X,required=False,initial=1)
	cliente_categ_fiscal = forms.IntegerField(widget = forms.HiddenInput(), required = False,initial=5)	
	cliente_descuento = forms.DecimalField(initial=0.00,decimal_places=2,widget = forms.HiddenInput(), required = False)	
	lista_precios = forms.ModelChoiceField(label='Lista de Precios',queryset=prod_lista_precios.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	origen_destino = forms.ModelChoiceField(label=u'Ubicación',queryset=prod_ubicacion.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)		
	class Meta:
			model = cpb_comprobante			
			exclude = ['id','fecha_creacion','numero','fecha_imputacion','cae','cae_vto','estado','anulacion_motivo','anulacion_fecha','empresa','usuario','cpb_nro_afip','importe_perc_imp','cpb_tipo']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBPresupLiteForm, self).__init__(*args, **kwargs)		
		try:
			empresa = empresa_actual(request)
			letras = tipo_comprob_fiscal(empresa.categ_fiscal)			
			self.fields['letra'].choices = letras			
			self.fields['letra'].initial = 'X'

			pto_vta = pto_vta_habilitados(request)
			self.fields['pto_vta'].choices = [(pto.numero, pto.__unicode__()) for pto in pto_vta]
			self.fields['pto_vta'].initial = get_pv_defecto(request)
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
			self.fields['entidad'].queryset = egr_entidad.objects.filter(tipo_entidad=1,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
			self.fields['fecha_vto'].initial = datetime.now()+timedelta(days=empresa.get_dias_venc())
			usr = usuario_actual(request)
			if usr.vendedor_defecto:
				self.fields['vendedor'].initial = usr.vendedor_defecto.id

		except gral_empresa.DoesNotExist:
			empresa = None	


	def clean_entidad(self):		
		entidad = self.cleaned_data['entidad']
		if not entidad:			
				raise forms.ValidationError(u"Debe seleccionar un Cliente.")				
		return entidad

	def clean(self):						
		super(forms.ModelForm,self).clean()	
		tipo_form = self.cleaned_data.get('tipo_form')		
		letra = self.cleaned_data.get('letra')
		pto_vta = self.cleaned_data.get('pto_vta')		
		numero = self.cleaned_data.get('numero')						
		cliente_categ_fiscal = self.cleaned_data.get('cliente_categ_fiscal')
		numero = self.cleaned_data.get('numero')
		try:
			empresa = self.initial['request'].user.userprofile.id_usuario.empresa			
			if not nofacturac_cliente_letra(letra,cliente_categ_fiscal,empresa.categ_fiscal):
				raise forms.ValidationError(u'Letra no válida para el Cliente/CPB seleccionado!')	

		except gral_empresa.DoesNotExist:
			empresa = None

		cant=cpb_comprobante.objects.filter(numero=numero,pto_vta=pto_vta,letra=letra,cpb_tipo__id=11).count()						
		if (tipo_form == 'ALTA')and(cant > 0):			
			raise forms.ValidationError("El Nº de Comprobante ingresado ya existe en el Sistema! Verifique.")			

		return self.cleaned_data

class ProductoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.nombre

class CPBPresupLiteDetalleForm(forms.ModelForm):
	producto = ProductoModelChoiceField(label="Producto/Servicio",queryset=prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3)),required = True)		
	importe_unitario = forms.DecimalField(label="Precio",widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	porc_dcto = forms.DecimalField(initial=0,widget = forms.HiddenInput(),decimal_places=2)	
	cantidad = forms.DecimalField(initial=1,decimal_places=2)	
	unidad = forms.CharField(label=" ",required = False,widget=forms.TextInput(attrs={ 'class':'form-control unidades','readonly':'readonly'}),initial='u.')
	cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	id = forms.IntegerField(widget = forms.HiddenInput(), required = False)
	importe_costo = forms.DecimalField(widget = forms.HiddenInput(), required = False)
	importe_subtotal = forms.DecimalField(widget=forms.HiddenInput(),initial=0.00,decimal_places=2)	
	coef_iva = forms.DecimalField(widget = forms.HiddenInput(), required = False)
	importe_iva = forms.DecimalField(widget=forms.HiddenInput(),initial=0.00,decimal_places=2)	
	importe_total = forms.DecimalField(label="Total",widget=PrependWidget(attrs={'class':'form-control','step':0,'readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	tasa_iva = forms.ModelChoiceField(queryset=gral_tipo_iva.objects.all(),widget = forms.HiddenInput(),required = False)
	lista_precios = forms.ModelChoiceField(queryset=prod_lista_precios.objects.all(),widget = forms.HiddenInput(),required = False)
	origen_destino = forms.ModelChoiceField(queryset=prod_ubicacion.objects.all(),widget = forms.HiddenInput(),required = False)
	detalle = forms.CharField(widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 2}),required = False)				
	class Meta:
			model = cpb_comprobante_detalle
			exclude = ['fecha_creacion']	

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBPresupLiteDetalleForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['producto'].queryset = prod_productos.objects.filter(baja=False,mostrar_en__in=(1,3),empresa__id__in=empresas_habilitadas(request)).order_by('nombre')			
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
		except gral_empresa.DoesNotExist:
			empresa = None		
#############################################################################

class CPBRecCobranzaForm(forms.ModelForm):
	entidad = chosenforms.ChosenModelChoiceField(label='Cliente',queryset=egr_entidad.objects.filter(tipo_entidad=1,baja=False),empty_label='---',required = False)	
	pto_vta = forms.ChoiceField(label='Pto. Vta.',choices=[(pto.numero, pto.__unicode__()) for pto in cpb_pto_vta.objects.filter(baja=False)],required = False)
	fecha_cpb = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=datetime.now())	
	observacion = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 5}),required = False)	
	importe_ret = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	importe_subtotal = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	importe_total = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly',},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)	
	importe_cpbs = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)		
	class Meta:
			model = cpb_comprobante			
			exclude = ['id','fecha_creacion','numero','fecha_imputacion','cae','cae_vto','estado','anulacion_motivo','anulacion_fecha','empresa','usuario','presup_tiempo_entrega','presup_forma_pago','presup_aprobacion','cpb_tipo','letra']

	def clean_entidad(self):		
		entidad = self.cleaned_data['entidad']
		if not entidad:			
				raise forms.ValidationError(u"Debe seleccionar un Cliente.")				
		return entidad

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBRecCobranzaForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)
			pventa = pto_vta_habilitados(request)			
			self.fields['pto_vta'].choices = [(pto.numero, pto.__unicode__()) for pto in pventa]			
			self.fields['pto_vta'].initial = get_pv_defecto(request)			
			self.fields['entidad'].queryset = egr_entidad.objects.filter(tipo_entidad=1,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
			
		except gral_empresa.DoesNotExist:
			empresa = None

class CPBRecCPBForm(forms.ModelForm):	
	detalle_cpb = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','disabled':'disabled'}),required = False)	
	desc_rec = forms.DecimalField(widget=PostPendWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='%',tooltip="Ingese el % de Descuento"),initial=0,decimal_places=2,required = False)	
	importe_total = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2, required = False)	
	id_cpb_factura = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	cpb_factura = forms.ModelChoiceField(queryset=cpb_comprobante.objects.all(),widget = forms.HiddenInput(),empty_label=None, required = False)	
	saldo = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2, required = False)	
	class Meta:
			model = cpb_cobranza
			exclude = ['id','fecha_creacion']	

	def __init__(self, *args, **kwargs):
		super(CPBRecCPBForm, self).__init__(*args, **kwargs)

class CPBRecFPForm(forms.ModelForm):
	tipo_forma_pago = forms.ModelChoiceField(label='FP',queryset=cpb_tipo_forma_pago.objects.filter(baja=False),empty_label='---')
	mdcp_fecha = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=datetime.now(),required = False)
	mdcp_banco = forms.ModelChoiceField(label='Banco',queryset=cpb_banco.objects.filter(baja=False),empty_label='---',required = False)
	detalle = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control','rows': 3}),required = False)		
	importe = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	cta_ingreso = forms.ModelChoiceField(label='Cta. Ingreso',queryset=cpb_cuenta.objects.all(),empty_label='---',required = True)
	class Meta:
			model = cpb_comprobante_fp
			exclude = ['id','fecha_creacion','cta_egreso']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBRecFPForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)			
			self.fields['tipo_forma_pago'].queryset = cpb_tipo_forma_pago.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False)			
			self.fields['mdcp_banco'].queryset = cpb_banco.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False)			
			self.fields['cta_ingreso'].queryset = cpb_cuenta.objects.filter(empresa__id__in=empresas_habilitadas(request),baja=False,tipo__in=[0,1,2])			
		except gral_empresa.DoesNotExist:
			empresa = None	

	def clean(self):						
		super(forms.ModelForm,self).clean()	
		tfp = self.cleaned_data.get('tipo_forma_pago')				
		mdcp_fecha = self.cleaned_data.get('mdcp_fecha')				
		cta_ingreso = self.cleaned_data.get('cta_ingreso')	
		mdcp_cheque  = self.cleaned_data.get('mdcp_cheque')				
		mdcp_banco = self.cleaned_data.get('mdcp_banco')				
		if not mdcp_fecha:
			self._errors['mdcp_fecha'] = [u'¡Verificar Fecha!']
		if cta_ingreso:
			if ((cta_ingreso.tipo==2) and((not mdcp_fecha)or(not tfp)or(not mdcp_cheque)or(not mdcp_banco))):
				raise forms.ValidationError("¡Debe completar los datos del medio de Cobro/Pago!")			

		return self.cleaned_data

class CPBRecRetForm(forms.ModelForm):
	retencion = forms.ModelChoiceField(label='Retenciones',queryset=cpb_retenciones.objects.all(),empty_label='---',required = False)
	detalle = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control','rows': 3}),required = False)		
	importe_total = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	ret_fecha_cpb = forms.DateField(label=u'Fecha Retención',widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),required = False)
	ret_importe_isar = forms.DecimalField(label=u'Importe Sujeto a Retención',widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),decimal_places=2,required = False)
	cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	class Meta:
			model = cpb_comprobante_retenciones
			exclude = ['id']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBRecRetForm, self).__init__(*args, **kwargs)
		try:
			self.fields['retencion'].queryset = cpb_retenciones.objects.filter(empresa__id__in=empresas_habilitadas(request))			
		except:
			pass

#############################################################################

class CPBSeleccionados(forms.Form):
	detalle_cpb = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','disabled':'disabled'}),required = False)
	desc_rec = forms.DecimalField(widget=PostPendWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='%',tooltip="Ingese el % de Descuento"),initial=0,decimal_places=2,required = False)	
	importe_total = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2, required = False)
	# cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	id_cpb_factura = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	saldo = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2, required = False)			

	def __init__(self, *args, **kwargs):
		super(CPBSeleccionados, self).__init__(*args, **kwargs)

	def clean(self):		
		super(forms.Form,self).clean()	
		saldo = self.cleaned_data.get('saldo')
		importe_total = self.cleaned_data.get('importe_total')
		id_cpb_factura = self.cleaned_data.get('id_cpb_factura')
		if id_cpb_factura:
			try:                          				
				cpb = cpb_comprobante.objects.get(id=id_cpb_factura)    
				if cpb.cpb_tipo.signo_ctacte >= 0:
					if (importe_total > saldo):
						self._errors['saldo'] = [u'¡No posee saldo suficiente!']
				else:
					if (math.fabs(importe_total) > math.fabs(saldo) ):
						self._errors['saldo'] = [u'¡No posee crédito suficiente!']
					if (importe_total >= 0 ):
						self._errors['saldo'] = [u'¡Verificar Importe!']
			except:
				self._errors['saldo'] = [u'¡No posee saldo suficiente!']

#############################################################################

	

######################################################
# LIQUIDO PRODUCTO (como un cpb de compra pero va en ventas)

class CPBLiqProdForm(forms.ModelForm):
	entidad = chosenforms.ChosenModelChoiceField(label='Proveedor',queryset=egr_entidad.objects.filter(tipo_entidad=2,baja=False),empty_label='---',required = False)	
	pto_vta = forms.IntegerField(label='Pto. Vta.',required = False)
	fecha_cpb = forms.DateField(required = True,widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=hoy())
	fecha_imputacion = forms.DateField(required = False,widget=forms.DateInput(attrs={'class': 'form-control datepicker'}),initial=hoy())
	fecha_vto = forms.DateField(required = False,widget=forms.DateInput(attrs={'class': 'datepicker'}))	
	observacion = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control2','rows': 5}),required = False)				
	importe_perc_imp = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_subtotal = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_total = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_iva = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	importe_cobrado = forms.DecimalField(label='',widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly'},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	letra = forms.ChoiceField(label='Letra',choices=COMPROB_FISCAL,required=False,initial=1)	
	cpb_tipo = forms.ModelChoiceField(label='Tipo CPB',queryset=cpb_tipo.objects.filter(baja=False,tipo=14),required = True,empty_label=None)
	tipo_form = forms.CharField(widget = forms.HiddenInput(), required = False)	
	cliente_categ_fiscal = forms.IntegerField(widget = forms.HiddenInput(), required = False,initial=5)	
	cliente_descuento = forms.DecimalField(initial=0.00,decimal_places=2,widget = forms.HiddenInput(), required = False)
	lista_precios = forms.ModelChoiceField(label='Lista de Precios',queryset=prod_lista_precios.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	origen_destino = forms.ModelChoiceField(label=u'Ubicación',queryset=prod_ubicacion.objects.filter(baja=False),required = True,empty_label=None,initial=1)
	class Meta:
			model = cpb_comprobante
			exclude = ['id','vendedor','condic_pago','fecha_creacion','cae','cae_vto','estado','anulacion_motivo','anulacion_fecha','empresa','usuario','presup_tiempo_entrega','presup_forma_pago','presup_aprobacion','cpb_nro_afip']


	def clean_entidad(self):		
		entidad = self.cleaned_data['entidad']
		if not entidad:			
				raise forms.ValidationError(u"Debe seleccionar un Cliente/Prov.")				
		return entidad

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBLiqProdForm, self).__init__(*args, **kwargs)
		
		try:
			empresa = empresa_actual(request)
			letras = tipo_comprob_fiscal(empresa.categ_fiscal)
			self.fields['letra'].choices = letras						
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))			
			self.fields['numero'].initial= 1
			self.fields['pto_vta'].initial= 1
			self.fields['entidad'].queryset = egr_entidad.objects.filter(tipo_entidad=2,baja=False,empresa__id__in=empresas_habilitadas(request)).order_by('apellido_y_nombre')
			self.fields['fecha_vto'].initial = hoy()+timedelta(days=empresa.get_dias_venc())
		except:
			empresa = None  

	def clean(self):						
		super(forms.ModelForm,self).clean()	
		entidad = self.cleaned_data.get('entidad')
		tipo_form = self.cleaned_data.get('tipo_form')
		importe_cobrado = self.cleaned_data.get('importe_cobrado')
		importe_total = self.cleaned_data.get('importe_total')
		letra = self.cleaned_data.get('letra')
		cpb_tipo = self.cleaned_data.get('cpb_tipo')
		pto_vta = self.cleaned_data.get('pto_vta')		
		numero = self.cleaned_data.get('numero')
		
		if tipo_form == 'EDICION':							
				if importe_cobrado > importe_total:					
					self._errors['importe_cobrado'] = u'El total del comprobante debe ser igual o mayor al total de sus cobros!($%s)' % (importe_total-importe_cobrado)
		
		id_cpbs=cpb_comprobante.objects.filter(numero=numero,pto_vta=pto_vta,letra=letra,cpb_tipo=cpb_tipo,entidad=entidad).values_list('id',flat=True)
		id_cpbs = [int(x) for x in id_cpbs]  
		cant=len(id_cpbs)
		id_cpb=self.instance.id
		if (cant > 0)and(id_cpb not in id_cpbs):
			raise forms.ValidationError("El Nº de Comprobante ingresado ya existe en el Sistema! Verifique.")			
		
		return self.cleaned_data

class CPBLiqProdDetalleForm(forms.ModelForm):
	producto = chosenforms.ChosenModelChoiceField(queryset=prod_productos.objects.filter(baja=False,mostrar_en__in=(2,3)),required = True)	
	porc_dcto = forms.DecimalField(initial=0,decimal_places=2)	
	cantidad = forms.DecimalField(initial=1,decimal_places=2)	
	unidad = forms.CharField(required = False,widget=forms.TextInput(attrs={ 'class':'form-control unidades','readonly':'readonly'}),initial='u.')
	importe_unitario = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)
	cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	importe_costo = forms.DecimalField(widget = forms.HiddenInput(), required = False)
	importe_subtotal = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	coef_iva = forms.DecimalField(widget = forms.HiddenInput(), required = False)
	tasa_iva = forms.ModelChoiceField(queryset=gral_tipo_iva.objects.all(),widget = forms.HiddenInput(),required = False)
	importe_iva = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','readonly':'readonly','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	importe_total = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2)	
	lista_precios = forms.ModelChoiceField(queryset=prod_lista_precios.objects.all(),widget = forms.HiddenInput(),required = False)
	origen_destino = forms.ModelChoiceField(queryset=prod_ubicacion.objects.all(),widget = forms.HiddenInput(),required = False)
	class Meta:
			model = cpb_comprobante_detalle
			exclude = ['id','fecha_creacion']			

	def __init__(self,*args, **kwargs):				
		request = kwargs.pop('request', None)
		super(CPBLiqProdDetalleForm, self).__init__(*args, **kwargs)					
		self.fields['importe_unitario'].initial = 0
		self.fields['cantidad'].initial = 1	
		try:
			empresa = empresa_actual(request)
			self.fields['producto'].queryset = prod_productos.objects.filter(baja=False,mostrar_en__in=(2,3),empresa__id__in=empresas_habilitadas(request)).order_by('nombre')			
			self.fields['lista_precios'].queryset = prod_lista_precios.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
			self.fields['origen_destino'].queryset = prod_ubicacion.objects.filter(baja=False,empresa__id__in=empresas_habilitadas(request))		
		except:
			empresa = None			

class CPBLiqProdPercImpForm(forms.ModelForm):
	perc_imp = forms.ModelChoiceField(label='Perc_Imp',queryset=cpb_perc_imp.objects.all(),empty_label='---',required = False)
	detalle = forms.CharField(label='Detalle',widget=forms.Textarea(attrs={ 'class':'form-control','rows': 3}),required = False)		
	importe_total = forms.DecimalField(widget=PrependWidget(attrs={'class':'form-control','step':0.00},base_widget=NumberInput, data='$'),initial=0.00,decimal_places=2,required = False)
	cpb_comprobante = forms.IntegerField(widget = forms.HiddenInput(), required = False)	
	class Meta:
			model = cpb_comprobante_perc_imp
			exclude = ['id']

	def __init__(self, *args, **kwargs):
		request = kwargs.pop('request', None)
		super(CPBLiqProdPercImpForm, self).__init__(*args, **kwargs)
		try:
			empresa = empresa_actual(request)
			self.fields['perc_imp'].queryset = cpb_perc_imp.objects.filter(empresa__id__in=empresas_habilitadas(request))			
		except:
			empresa = None			


