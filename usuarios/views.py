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
                # permisos = UsuPermiso.objects.filter(grupo=usuario.grupo).values_list('permiso_name', flat=True).distinct()               
                permisos = usuario.permisos.values_list('permiso_name', flat=True).distinct()
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
from general.views import VariablesMixin,getVariablesMixin
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
            usuario = usuario_actual(self.request)
            empresa = empresa_actual(self.request)
            if habilitado_contador(usuario.tipoUsr):
                usuarios = usu_usuario.objects.filter().order_by('nombre')            
            else:
                usuarios = usu_usuario.objects.filter(empresa=empresa).order_by('nombre')            
            context['usuarios'] = usuarios.select_related('grupo','cpb_pto_vta')           
        except:
            context['usuarios'] = None

        return context

@login_required
def UsuarioCreateView(request):    
    if not tiene_permiso(request,'gral_configuracion'):
            return redirect(reverse('usuarios'))
    context = {}
    context = getVariablesMixin(request)    
    try:
        empresa = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        empresa = None 
      
    usuario = usuario_actual(request)
    if request.method == 'POST':
        form = UsuarioForm(request,usuario,request.POST,request.FILES)
        if form.is_valid():
            post = form.save(commit=False)                                    
            post.save()
            form.save_m2m()                            
            messages.success(request, u'Los datos se guardaron con éxito!')
            return HttpResponseRedirect(reverse('usuarios'))  
    else:
        form = UsuarioForm(request,usuario=usuario)

    context['form'] = form
    return render(request, 'usuarios/usuario_form.html',context)

@login_required
def UsuarioEditView(request,id):
    if not tiene_permiso(request,'gral_configuracion'):
            return redirect(reverse('usuarios'))
    context = {}
    context = getVariablesMixin(request)    
    try:
        empresa = empresa_actual(request)
    except gral_empresa.DoesNotExist:
        empresa = None 
    usuario = usuario_actual(request)
    
    usr = get_object_or_404(usu_usuario, id_usuario=id)

    if request.method == 'POST':
        form = UsuarioForm(request,usuario,request.POST,request.FILES,instance=usr)
        if form.is_valid():
            post = form.save(commit=False)                                    
            post.save()
            form.save_m2m()
            messages.success(request, u'Los datos se guardaron con éxito!')
            return HttpResponseRedirect(reverse('usuarios'))                    
    else:
        form = UsuarioForm(request,usuario,instance=usr)

    context['form'] = form
    return render(request, 'usuarios/usuario_form.html',context)


@login_required
def usuarios_baja_reactivar(request,id):
    usr = usu_usuario.objects.get(pk=id) 
    usr.baja = not usr.baja
    usr.save()  
    messages.success(request, u'Los datos se guardaron con éxito!')
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

@login_required
def usuarios_resetear_passwd(request,id):    
    if not tiene_permiso(request,'gral_configuracion'):
            return redirect(reverse('usuarios'))    
    usuario = usu_usuario.objects.get(pk=id) 
    clave = make_password(password=usuario.usuario,salt=None,hasher='unsalted_md5')
    usuario.password = clave
    usuario.save()
    messages.success(request, u'Los datos se guardaron con éxito!')
    return HttpResponseRedirect(reverse('usuarios'))  
