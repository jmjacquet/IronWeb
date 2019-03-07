# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prod_productos',
            name='cta_egreso',
            field=models.ForeignKey(related_name='prod_cta_egreso', on_delete=django.db.models.deletion.SET_NULL, db_column='cta_egreso', blank=True, to='general.gral_plan_cuentas', null=True),
        ),
        migrations.AddField(
            model_name='prod_productos',
            name='cta_ingreso',
            field=models.ForeignKey(related_name='prod_cta_ingreso', on_delete=django.db.models.deletion.SET_NULL, db_column='cta_ingreso', blank=True, to='general.gral_plan_cuentas', null=True),
        ),
    ]
