# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models
from datetime import datetime,date
from dateutil.relativedelta import *
from django.conf import settings
import os 
from general.utilidades import *
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone

