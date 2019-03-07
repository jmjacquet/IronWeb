# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gral_empresa',
            name='dias_vencimiento_cpbs',
            field=models.IntegerField(default=0, null=True, verbose_name='D\xedas Vencimiento CPBS', blank=True),
        ),
    ]
