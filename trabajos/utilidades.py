# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.contrib import messages
from django.conf import settings
from django.contrib.messages import constants as message_constants
from django.forms import Widget
from django.utils.safestring import mark_safe
from .models import *
import json
from decimal import *

ESTADO_NP = (
    (0, u'Pendiente'),
    (1, u'Anulada'),
    (2, u'Generó Trabajo'),
)

