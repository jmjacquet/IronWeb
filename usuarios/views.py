# -*- coding: utf-8 -*-
from django.template import RequestContext,Context
from django.shortcuts import *
from .models import *
from django.contrib.auth.decorators import login_required
from fm.views import AjaxDeleteView
from django.views.generic import TemplateView,ListView,CreateView,UpdateView
from .forms import *


# def ver_permisos(id_app,id_usuario=None):
#     if id_usuario:
#         permisos = UsuUsuario.objects.filter(permisos__app__id_app=id_app,id_usuario=id_usuario.pk).values_list('permisos__permiso_name', flat=True).distinct()
#     else:
#         permisos = UsuUsuario.objects.filter(permisos__permiso_name__id_app=id_app).values_list('permisos__permiso_name', flat=True).distinct()
#     return permisos


#####################
@login_required 
def ver_permisos(request):
    try:
        if request:
            usuario=request.user.userprofile.id_usuario           
            if usuario.grupo.pk == 0:
                permisos = UsuPermiso.objects.all().values_list('permiso_name', flat=True).distinct()
            else:
                permisos = UsuPermiso.objects.filter(grupo=usuario.grupo).values_list('permiso_name', flat=True).distinct()               
        else:
            permisos = []
    except:
        permisos = []
    
    return permisos  

@login_required 
def tiene_permiso(request,permiso):
    permisos = ver_permisos(request)        
    return (permiso in permisos)


from django.contrib.auth.hashers import make_password

@login_required 
def password(request):
  if request.method == 'GET':
    clave = request.GET.get('clave','')
    if clave:
      clave = make_password(password=clave,salt=None,hasher='unsalted_md5')

  return HttpResponse( clave, content_type='application/json' ) 


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

# @login_required 
# def cambiar_password(request):
#     form = UsuarioCambiarPasswdForm(request.POST or None)
#     if request.method == 'POST':        
#         if form.is_valid():            
#             new_password = form.cleaned_data['new_password']
#             usuario=request.user.userprofile.id_usuario
#             clave = make_password(password=new_password,salt=None,hasher='unsalted_md5')
#             usuario.password = clave
#             usuario.save()
#             update_session_auth_hash(request, usuario)
#             messages.success(request, _(u'Su contraseña fué actualizada!'))
#             return redirect('principal')
#         else:
#             messages.error(request, _(u'Ingrese los datos correctamente.'))    
#     return render(request, 'general/varios/cambiar_password.html', {
#         'form': form
#     })

@login_required 
def cambiar_password(request):            
    form = UsuarioCambiarPasswdForm(request.POST or None)
    if request.method == 'POST' and request.is_ajax():                                       
        if form.is_valid():                                   
            new_password = form.cleaned_data['new_password']
            usuario=request.user.userprofile.id_usuario
            clave = make_password(password=new_password,salt=None,hasher='unsalted_md5')
            usuario.password = clave
            usuario.save()
            update_session_auth_hash(request, usuario)            
            response = {'status': 1, 'message': "Ok"} # for ok        
        else:
            errors = form.errors            
            response = {'status': 0, 'message': json.dumps(errors)} 
            
        return HttpResponse(json.dumps(response,default=default), content_type='application/json')
    else:                
        variables = RequestContext(request, {'form':form})        
        return render_to_response("general/varios/cambiar_password.html", variables)

from django.views.generic import TemplateView,ListView
from general.views import VariablesMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

class UsuarioList(VariablesMixin,ListView):
    template_name = 'usuarios/lista_usuarios.html'
    model = usu_usuario
    context_object_name = 'usuarios'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):                
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('principal'))
        return super(UsuarioList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UsuarioList, self).get_context_data(**kwargs)        
        try:             
            empresa = empresa_actual(self.request)
            usuarios = usu_usuario.objects.filter(empresa=empresa).order_by('nombre')            
            context['usuarios'] = usuarios.select_related('grupo','cpb_pto_vta')           
        except:
            context['usuarios'] = None

        return context

class UsuarioCreateView(VariablesMixin,CreateView):
    form_class = UsuarioForm
    model = usu_usuario
    template_name = 'usuarios/usuario_form.html'


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('usuarios'))
        return super(UsuarioCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):                       
        form.instance.empresa = empresa_actual(self.request)
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('usuarios'))

    def get_initial(self):    
        initial = super(UsuarioCreateView, self).get_initial()               
        return initial    

    def get_form_kwargs(self):
        kwargs = super(UsuarioCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class UsuarioEditView(VariablesMixin,UpdateView):
    form_class = UsuarioForm
    model = usu_usuario
    template_name = 'usuarios/usuario_form.html'
    pk_url_kwarg = 'id'
    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):        
        if not tiene_permiso(self.request,'gral_configuracion'):
            return redirect(reverse('usuarios'))
        return super(UsuarioEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):        
        messages.success(self.request, u'Los datos se guardaron con éxito!')
        return HttpResponseRedirect(reverse('usuarios'))

    def get_initial(self):    
        initial = super(UsuarioEditView, self).get_initial()                      
        return initial    

    def get_form_kwargs(self):
        kwargs = super(UsuarioEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

@login_required
def usuarios_baja_reactivar(request,id):
    usr = usu_usuario.objects.get(pk=id) 
    usr.baja = not usr.baja
    usr.save()  
    messages.success(self.request, u'Los datos se eliminaron con éxito!')
    return HttpResponseRedirect(reverse('usuarios'))                



from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json

@login_required 
def get_usuarios_conectados(request):
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_id_list = []
    for session in active_sessions:
        data = session.get_decoded()
        user_id_list.append(data.get('_auth_user_id', None))
    # Query all logged in users based on id list
    conectados = []
    usuarios = UserProfile.objects.filter(user__id__in=user_id_list)    
    for u in usuarios:
        if u.user.is_authenticated():
            conectados.append(u.id_usuario.usuario)

    return HttpResponse( json.dumps(conectados), content_type='application/json' ) 

