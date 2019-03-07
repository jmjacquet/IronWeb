# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import datetime
import general.models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='gral_empresa',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('categ_fiscal', models.IntegerField(blank=True, null=True, verbose_name='Categor\xeda Fiscal', choices=[(1, b'IVA Responsable Inscripto'), (2, b'Responsable No Inscripto'), (3, b'IVA No Responsable'), (4, b'IVA Sujeto Exento'), (5, b'Consumidor Final'), (6, b'Monotributista'), (7, b'No Categorizado'), (8, b'Proveedor Exterior'), (9, b'Consumidor Exterior'), (10, b'IVA Liberado-Ley19.640'), (11, 'IVA RI \u2013 Ag. Percepci\xf3n'), (12, b'Eventual'), (13, b'Monotributista Social'), (14, b'Eventual Social')])),
                ('cuit', models.CharField(max_length=50, null=True, verbose_name='CUIT', blank=True)),
                ('iibb', models.CharField(max_length=50, null=True, verbose_name='IIBB', blank=True)),
                ('fecha_inicio_activ', models.DateTimeField(null=True, verbose_name='Fecha Inicio Actividades')),
                ('domicilio', models.CharField(max_length=200, null=True, verbose_name='Domicilio', blank=True)),
                ('provincia', models.IntegerField(default=12, null=True, verbose_name='Provincia', blank=True, choices=[(0, 'CABA'), (1, b'Buenos Aires'), (2, b'Catamarca'), (3, 'C\xf3rdoba'), (4, b'Corrientes'), (5, 'Entre R\xedos'), (6, b'Jujuy'), (7, b'Mendoza'), (8, b'La Rioja'), (9, b'Salta'), (10, b'San Juan'), (11, b'San Luis'), (12, b'Santa Fe'), (13, b'Santiago del Estero'), (14, 'Tucum\xe1n'), (16, b'Chaco'), (17, b'Chubut'), (18, b'Formosa'), (19, b'Misiones'), (20, 'Neuqu\xe9n'), (21, b'La Pampa'), (22, b'R\xc3\xado Negro'), (23, b'Santa Cruz'), (24, b'Tierra del Fuego/Ant\xc3\xa1rtida/Islas Malvinas')])),
                ('localidad', models.CharField(max_length=100, null=True, verbose_name='Localidad', blank=True)),
                ('cod_postal', models.CharField(max_length=50, null=True, verbose_name='CP', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Email', blank=True)),
                ('telefono', models.CharField(max_length=50, null=True, verbose_name='Tel\xe9fono', blank=True)),
                ('celular', models.CharField(max_length=50, null=True, verbose_name='Celular', blank=True)),
                ('baja', models.BooleanField(default=False)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('ruta_logo', models.ImageField(upload_to=general.models.get_image_name, db_column='ruta_logo', blank=True)),
            ],
            options={
                'db_table': 'gral_empresa',
            },
        ),
        migrations.CreateModel(
            name='gral_plan_cuentas',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('codigo', models.CharField(max_length=100)),
                ('nombre', models.CharField(max_length=100)),
                ('tipo', models.IntegerField(blank=True, null=True, choices=[(0, 'Padre'), (1, 'Ingreso'), (2, 'Egreso')])),
                ('baja', models.BooleanField(default=False)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='empresa', blank=True, to='general.gral_empresa', null=True)),
                ('padre', models.ForeignKey(related_name='plan_ctas_padre', on_delete=django.db.models.deletion.SET_NULL, db_column='padre', blank=True, to='general.gral_plan_cuentas', null=True)),
            ],
            options={
                'ordering': ['codigo', 'nombre'],
                'db_table': 'gral_plan_cuentas',
            },
        ),
        migrations.CreateModel(
            name='gral_tareas',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('estado', models.CharField(max_length=50, null=True, verbose_name='Estado', blank=True)),
                ('title', models.CharField(max_length=200, null=True, verbose_name='T\xedtulo', blank=True)),
                ('detalle', models.TextField(null=True, verbose_name='Detalle', blank=True)),
                ('respuesta', models.CharField(max_length=500, null=True, verbose_name='Respuesta', blank=True)),
                ('color', models.CharField(max_length=200, null=True, verbose_name='Color', blank=True)),
                ('fecha', models.DateTimeField(default=datetime.datetime.now)),
                ('fecha_creacion', models.DateField(auto_now=True)),
                ('usuario_asignado', models.ForeignKey(related_name='usuario_asignado', on_delete=django.db.models.deletion.SET_NULL, db_column='usuario_asignado', blank=True, to='usuarios.usu_usuario', null=True)),
                ('usuario_creador', models.ForeignKey(related_name='usuario_creador', on_delete=django.db.models.deletion.SET_NULL, db_column='usuario_creador', blank=True, to='usuarios.usu_usuario', null=True)),
            ],
            options={
                'db_table': 'gral_tareas',
            },
        ),
    ]
