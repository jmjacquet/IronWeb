# -*- coding: utf-8 -*-
from django.conf.urls import  include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from usuarios.views import *
from .views import login,logout,volverHome,alive


urlpatterns = [    
    url(r'^', include('general.urls')),    
    url(r'^felectronica/', include('felectronica.urls')),
    url(r'^usuarios/', include('usuarios.urls')),
    url(r'^entidades/', include('entidades.urls')),  
    url(r'^comprobantes/', include('comprobantes.urls')), 
    url(r'^productos/', include('productos.urls')),  
    url(r'^ingresos/', include('ingresos.urls')),  
    url(r'^egresos/', include('egresos.urls')),  
    url(r'^trabajos/', include('trabajos.urls')),  
    url(r'^reportes/', include('reportes.urls')),      
    url(r'^login/$', login,name="login"),
    url(r'^logout/$', logout,name="logout"),
    url(r'^alive/$', alive,name="alive"),

    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# if settings.DEBUG is False:   #if DEBUG is True it will be served automatically

#     urlpatterns += [
            
#             url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
#             url(r'^staticfiles/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
#     ]

handler500 = volverHome
handler404 = volverHome