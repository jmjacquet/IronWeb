from django import forms

# place form definition here
from comprobantes.models import cpb_pto_vta,cpb_tipo_forma_pago,cpb_cuenta,cpb_tipo
from general.utilidades import *
from general.forms import pto_vta_habilitados


class ConsultaCAE(forms.Form):               
	# cpb_tipo = forms.ModelChoiceField(label='Tipo CPB',queryset=cpb_tipo.objects.filter(compra_venta='V',baja=False),required = True,empty_label=None)
	# pto_vta = forms.ModelChoiceField(label='Pto. Vta.',queryset=cpb_pto_vta.objects.filter(baja=False),empty_label=label_todos,required = False)	
	# numero = forms.IntegerField(label=u'Numero CPB',required = False)	
	# letra = forms.ChoiceField(label='Letra',choices=COMPROB_FISCAL,required=False,initial=1)	
	idcpb = forms.IntegerField(label=u'Id CPB',required = False)	
	def __init__(self, *args, **kwargs):		
		empresa = kwargs.pop('empresa', None)  
		request = kwargs.pop('request', None)  
		super(ConsultaCAE, self).__init__(*args, **kwargs)						
		# self.fields['pto_vta'].queryset = pto_vta_habilitados(request)

