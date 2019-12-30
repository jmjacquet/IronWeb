# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
        ('usuarios', '__first__'),
        ('general', '0001_initial'),
        ('entidades', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='egr_entidad',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='empresa', blank=True, to='general.gral_empresa', null=True),
        ),
        migrations.AddField(
            model_name='egr_entidad',
            name='lista_precios_defecto',
            field=models.ForeignKey(db_column='lista_precios_defecto', blank=True, to='productos.prod_lista_precios', null=True),
        ),
        migrations.AddField(
            model_name='egr_entidad',
            name='usuario',
            field=models.ForeignKey(related_name='usu_usuario_entidad', on_delete=django.db.models.deletion.SET_NULL, db_column='usuario', blank=True, to='usuarios.usu_usuario', null=True),
        ),
    ]
