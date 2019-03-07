# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='egr_entidad',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('apellido_y_nombre', models.CharField(max_length=200, verbose_name='Apellido y Nombre')),
                ('codigo', models.CharField(max_length=50, null=True, verbose_name='C\xf3digo', blank=True)),
                ('tipo_doc', models.IntegerField(default=99, null=True, verbose_name='Tipo Documento', blank=True, choices=[(80, b'CUIT'), (86, b'CUIL'), (87, b'CDI'), (89, b'LE'), (90, b'LC'), (91, b'CI extranjera'), (92, b'En tr\xc3\xa1mite'), (93, b'Acta nacimiento'), (94, b'Pasaporte'), (95, b'CI Bs. As. RNP'), (96, b'DNI'), (99, b'Sin Identificar'), (30, b'Certificado Migraci\xc3\xb3n'), (88, b'Usado por Anses')])),
                ('nro_doc', models.CharField(max_length=50, null=True, verbose_name='N\xfamero', blank=True)),
                ('domicilio', models.CharField(max_length=200, null=True, verbose_name='Domicilio', blank=True)),
                ('provincia', models.IntegerField(default=12, null=True, verbose_name='Provincia', blank=True, choices=[(0, 'CABA'), (1, b'Buenos Aires'), (2, b'Catamarca'), (3, 'C\xf3rdoba'), (4, b'Corrientes'), (5, 'Entre R\xedos'), (6, b'Jujuy'), (7, b'Mendoza'), (8, b'La Rioja'), (9, b'Salta'), (10, b'San Juan'), (11, b'San Luis'), (12, b'Santa Fe'), (13, b'Santiago del Estero'), (14, 'Tucum\xe1n'), (16, b'Chaco'), (17, b'Chubut'), (18, b'Formosa'), (19, b'Misiones'), (20, 'Neuqu\xe9n'), (21, b'La Pampa'), (22, b'R\xc3\xado Negro'), (23, b'Santa Cruz'), (24, b'Tierra del Fuego/Ant\xc3\xa1rtida/Islas Malvinas')])),
                ('localidad', models.CharField(max_length=100, null=True, verbose_name='Localidad', blank=True)),
                ('cod_postal', models.CharField(max_length=50, null=True, verbose_name='CP', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Email', blank=True)),
                ('telefono', models.CharField(max_length=50, null=True, verbose_name='Tel\xe9fono', blank=True)),
                ('celular', models.CharField(max_length=50, null=True, verbose_name='Celular', blank=True)),
                ('tipo_entidad', models.IntegerField(default=1, null=True, blank=True, choices=[(1, b'Cliente'), (2, b'Proveedor'), (3, b'Empleado')])),
                ('dcto_general', models.DecimalField(decimal_places=3, default=0, max_digits=15, blank=True, null=True, verbose_name='Dcto.Gral')),
                ('fact_razon_social', models.CharField(max_length=200, null=True, verbose_name='Raz\xf3n Social', blank=True)),
                ('fact_cuit', models.CharField(max_length=50, null=True, verbose_name='CUIT', blank=True)),
                ('fact_direccion', models.CharField(max_length=200, null=True, verbose_name='Direcci\xf3n', blank=True)),
                ('fact_telefono', models.CharField(max_length=50, null=True, verbose_name='Tel\xe9fono', blank=True)),
                ('fact_categFiscal', models.IntegerField(blank=True, null=True, verbose_name='Categor\xeda Fiscal', choices=[(1, b'Responsable Inscripto'), (2, b'Responsable No Inscripto'), (3, b'IVA No Responsable'), (4, b'IVA Sujeto Exento'), (5, b'Consumidor Final'), (6, b'Monotributista'), (7, b'No Categorizado'), (8, b'Proveedor Exterior'), (9, b'Consumidor Exterior'), (10, b'IVA Liberado-Ley19.640'), (11, 'IVA RI \u2013 Ag. Percepci\xf3n'), (12, b'Eventual'), (13, b'Monotributista Social'), (14, b'Eventual Social')])),
                ('cbu', models.CharField(max_length=100, null=True, verbose_name='CBU', blank=True)),
                ('contacto', models.CharField(max_length=200, null=True, verbose_name='Contacto', blank=True)),
                ('observaciones', models.TextField(null=True, verbose_name='Observaciones', blank=True)),
                ('baja', models.BooleanField(default=False)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modif', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'egr_entidad',
            },
        ),
    ]
