# -*- coding: utf-8 -*-
from django.template import RequestContext,Context
from django.shortcuts import *
from .models import *
from django.views.generic import TemplateView,ListView,CreateView,UpdateView,FormView
from django.conf import settings
from django.db.models import Q,Sum,Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,redirect
from django.contrib import messages
import json
import urllib
from general.views import VariablesMixin
from .facturacion import facturarAFIP,consultar_cae
from comprobantes.models import *
from django.core.serializers.json import DjangoJSONEncoder
from .forms import ConsultaCAE

class CAEView(VariablesMixin,TemplateView):
    template_name = 'felectronica.html'
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CAEView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CAEView, self).get_context_data(**kwargs)        
        try:
            empresa = empresa_actual(self.request)
        except gral_empresa.DoesNotExist:
            empresa = None 
        form = ConsultaCAE(self.request.POST or None,empresa=empresa,request=self.request)           
        facturacion=None
        cpb = None  
        if form.is_valid():                                
            idcpb = form.cleaned_data['idcpb']            
            facturacion=consultar_cae(self.request,idcpb)                       
            
            try:
                cpb=cpb_comprobante.objects.get(id=idcpb)       
            except:
                cpb = None    
        context['facturacion'] =   facturacion        
        context['cpb'] =   cpb     
        context['form'] = form
        return context

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

def felectronica_json(request,id):      
   facturacion=consultar_cae(id)
   return HttpResponse( json.dumps(facturacion,cls=DjangoJSONEncoder), content_type='application/json' ) 
