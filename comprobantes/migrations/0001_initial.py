# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0002_auto_20180507_1523'),
        ('entidades', '__first__'),
        ('general', '0002_gral_empresa_dias_vencimiento_cpbs'),
        ('usuarios', '__first__'),
    ]

    operations = [
              
        migrations.AddField(
            model_name='cpb_comprobante_fp',
            name='mdcp_origen',
            field=models.ForeignKey(related_name='fp_mov_origen', on_delete=django.db.models.deletion.SET_NULL, db_column='mdcp_origen', blank=True, to='comprobantes.cpb_comprobante_fp', null=True),
        ),
        migrations.AddField(
            model_name='cpb_comprobante_fp',
            name='mdcp_salida',
            field=models.ForeignKey(related_name='fp_mov_salida', on_delete=django.db.models.deletion.SET_NULL, db_column='mdcp_salida', blank=True, to='comprobantes.cpb_comprobante_fp', null=True),
        ),
      
     
    ]
