# -*- coding: utf-8 -*-
from django.conf.urls import *
from django.conf import settings
import os
from .views import *
from django.views.generic import RedirectView,TemplateView

# Uncomment the next two lines to enable the admin:


urlpatterns = patterns('felectronica.views',
	
    # url(r'^estudios/$', EstudiosView.as_view(),name="padrones_estudio"),
    
    url(r'^felectronica/$', CAEView.as_view(),name="felectronica"),
    url(r'^felectronica_json/(?P<id>\d+)/$', felectronica_json,name="felectronica_json"),
    
    )