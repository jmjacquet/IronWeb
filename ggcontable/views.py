# -*- coding: utf-8 -*-
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import *
from django.template import RequestContext
from settings import *
from django.core.urlresolvers import reverse
from django.contrib import messages
from general.models import gral_empresa
from usuarios.models import UserProfile
from django.db.models import Q
from django.template.defaulttags import register
from ggcontable.middleware import get_tenant_map

LOGIN_URL = '/login/'
ROOT_URL = '/'

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def login(request):
    error = None
    ROOT_URL='/'
    if not request.user.is_authenticated():
        request.session.clear()
    elif request.method == 'GET':
        return HttpResponseRedirect(ROOT_URL)

    entidad_id = getattr(request, 'tenant_id', None) or os.environ.get('ENTIDAD_ID')
    if entidad_id:
        empresa = gral_empresa.objects.get(id=int(entidad_id))
    else:
        empresa = None
 
    # if empresa.mantenimiento == 1:
    #     return render_to_response('mantenimiento.html', {'dirMuni':MUNI_DIR,'sitio':sitio},context_instance=RequestContext(request))
    
    if request.method == 'POST':               
        usuario = request.POST['username']        
        clave = request.POST['password']
        user =  authenticate(usuario=usuario, clave=clave)        
        if user is not None:
          if user.is_active:
            
            django_login(request, user)
            ROOT_URL = reverse('principal')              
            return HttpResponseRedirect(ROOT_URL)
          else:
          ## invalid login
           error = u"Usuario/Contraseña incorrectos."
        else:
          ## invalid login
           error = u"Usuario/Contraseña incorrectos."
          #return direct_to_template(request, 'invalid_login.html')
    if error:
      messages.add_message(request, messages.ERROR,u'%s' % (error))    
   
    template = 'login.html'      
            
    return render_to_response(template, {'msj':messages,'empresa':empresa},context_instance=RequestContext(request))

def logout(request):
    request.session.clear()
    django_logout(request)
    return HttpResponseRedirect(LOGIN_URL)

def volverHome(request):
    """Used as handler404/handler500 - request.user may not exist if exception occurred before AuthenticationMiddleware."""
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated():
        return HttpResponseRedirect(LOGIN_URL)
    return HttpResponseRedirect(ROOT_URL)



# def volverHome(request):
#     LOGIN_REDIRECT_URL='/login'
#     if not request.user.is_active:
#       return HttpResponseRedirect(LOGIN_URL)
#     return HttpResponseRedirect(LOGIN_REDIRECT_URL)


def alive(request):
  return HttpResponse("Vive", status=200)


@login_required
def tenant_map(request):
    """Show subdomain -> database mapping. Staff only."""
    import os
    tenant_map_data = get_tenant_map()
    current_host = request.get_host().split(':')[0].lower()
    current_db = getattr(request, 'tenant_db', os.environ.get('ENTIDAD_DB', 'ironweb_prueba'))

    rows = []
    for host, cfg in sorted(tenant_map_data.items()):
        rows.append({
            'host': host,
            'db': cfg.get('ENTIDAD_DB', '-'),
            'entidad_id': cfg.get('ENTIDAD_ID', '-'),
            'dir': cfg.get('ENTIDAD_DIR', '-'),
        })

    return render_to_response(
        'tenant_map.html',
        {
            'current_host': current_host,
            'current_db': current_db,
            'rows': rows,
        },
        context_instance=RequestContext(request)
    )