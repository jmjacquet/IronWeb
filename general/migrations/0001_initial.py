# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '__first__'),
        ('comprobantes', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='gral_afip_categorias',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('letra', models.CharField(blank=True, max_length=1, null=True, verbose_name='Letra', choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'M', b'M'), (b'E', b'E'), (b'X', b'X')])),
                ('importe', models.DecimalField(default=0, null=True, max_digits=15, decimal_places=2, blank=True)),
            ],
            options={
                'db_table': 'gral_afip_categorias',
            },
        ),
        migrations.CreateModel(
            name='gral_empresa',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('categ_fiscal', models.IntegerField(blank=True, null=True, verbose_name='Categor\xeda Fiscal', choices=[(1, b'IVA Responsable Inscripto'), (2, b'Responsable No Inscripto'), (3, b'IVA No Responsable'), (4, b'IVA Sujeto Exento'), (5, b'Consumidor Final'), (6, b'Monotributista'), (7, b'No Categorizado'), (8, b'Proveedor Exterior'), (9, b'Consumidor Exterior'), (10, b'IVA Liberado-Ley19.640'), (11, 'IVA RI \u2013 Ag. Percepci\xf3n'), (12, b'Eventual'), (13, b'Monotributista Social'), (14, b'Eventual Social')])),
                ('cuit', models.CharField(max_length=50, verbose_name='CUIT')),
                ('iibb', models.CharField(max_length=50, null=True, verbose_name='N\xba IIBB', blank=True)),
                ('fecha_inicio_activ', models.DateTimeField(null=True, verbose_name='Fecha Inicio Actividades')),
                ('domicilio', models.CharField(max_length=200, null=True, verbose_name='Domicilio', blank=True)),
                ('provincia', models.IntegerField(default=12, null=True, verbose_name='Provincia', blank=True, choices=[(0, 'CABA'), (1, b'Buenos Aires'), (2, b'Catamarca'), (3, 'C\xf3rdoba'), (4, b'Corrientes'), (5, 'Entre R\xedos'), (6, b'Jujuy'), (7, b'Mendoza'), (8, b'La Rioja'), (9, b'Salta'), (10, b'San Juan'), (11, b'San Luis'), (12, b'Santa Fe'), (13, b'Santiago del Estero'), (14, 'Tucum\xe1n'), (16, b'Chaco'), (17, b'Chubut'), (18, b'Formosa'), (19, b'Misiones'), (20, 'Neuqu\xe9n'), (21, b'La Pampa'), (22, b'R\xc3\xado Negro'), (23, b'Santa Cruz'), (24, b'Tierra del Fuego/Ant\xc3\xa1rtida/Islas Malvinas')])),
                ('localidad', models.CharField(max_length=100, null=True, verbose_name='Localidad', blank=True)),
                ('cod_postal', models.CharField(max_length=50, null=True, verbose_name='CP', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('telefono', models.CharField(max_length=50, null=True, verbose_name='Tel\xe9fono', blank=True)),
                ('celular', models.CharField(max_length=50, null=True, verbose_name='Celular', blank=True)),
                ('baja', models.BooleanField(default=False)),
                ('fecha_creacion', models.DateField(auto_now_add=True)),
                ('nombre_fantasia', models.CharField(max_length=200, verbose_name='Nombre Fantas\xeda')),
                ('dias_vencimiento_cpbs', models.IntegerField(default=0, null=True, verbose_name='D\xedas Vencimiento CPBS', blank=True)),
                ('pprincipal_aviso_tareas', models.BooleanField(default=False, verbose_name='Tareas Pendientes al inicio')),
                ('pprincipal_panel_cpbs', models.BooleanField(default=False, verbose_name='Panel \xdaltimos CPBs')),
                ('pprincipal_estadisticas', models.BooleanField(default=False, verbose_name='Panel Estad\xedsticas')),
                ('fp_facturas', models.BooleanField(default=True, verbose_name='Mostrar FP en Facturas')),
                ('barra_busq_meses_atras', models.IntegerField(default=2, null=True, blank=True)),
                ('fe_crt', models.CharField(max_length=50, null=True, verbose_name='Nombre Archivo CRT', blank=True)),
                ('fe_key', models.CharField(max_length=50, null=True, verbose_name='Nombre Archivo Key', blank=True)),
                ('homologacion', models.BooleanField(default=True, verbose_name='Modo HOMOLOGACI\xd3N')),
                ('mail_cuerpo', models.CharField(max_length=500, null=True, verbose_name='Cuerpo del Email (env\xedo de Comprobantes)', blank=True)),
                ('mail_servidor', models.CharField(max_length=100, verbose_name='Servidor SMTP', blank=True)),
                ('mail_puerto', models.IntegerField(default=587, null=True, verbose_name='Puerto', blank=True)),
                ('mail_usuario', models.CharField(max_length=100, verbose_name='Usuario', blank=True)),
                ('mail_password', models.CharField(max_length=100, verbose_name='Password', blank=True)),
                ('ruta_logo', models.CharField(max_length=100, null=True, db_column='ruta_logo', blank=True)),
                ('tipo_logo_factura', models.IntegerField(blank=True, null=True, verbose_name='Tipo Logotipo', choices=[(1, b'Sin LOGOTIPO'), (2, b'Con LOGOTIPO total'), (3, b'Con LOGOTIPO y detalles')])),
                ('afip_categoria', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='afip_categoria', blank=True, to='general.gral_afip_categorias', null=True, verbose_name='Categor\xeda AFIP (si corresponde)')),
                ('pto_vta_defecto', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='pto_vta_defecto', blank=True, to='comprobantes.cpb_pto_vta', null=True, verbose_name='Pto. Venta x Defecto')),
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
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='empresa', blank=True, to='general.gral_empresa', null=True)),
                ('usuario_asignado', models.ForeignKey(related_name='usuario_asignado', on_delete=django.db.models.deletion.SET_NULL, db_column='usuario_asignado', blank=True, to='usuarios.usu_usuario', null=True)),
                ('usuario_creador', models.ForeignKey(related_name='usuario_creador', on_delete=django.db.models.deletion.SET_NULL, db_column='usuario_creador', blank=True, to='usuarios.usu_usuario', null=True)),
            ],
            options={
                'db_table': 'gral_tareas',
            },
        ),
    ]
