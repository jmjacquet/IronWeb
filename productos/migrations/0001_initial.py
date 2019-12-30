# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import productos.models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='gral_tipo_iva',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('coeficiente', models.DecimalField(default=0, max_digits=5, decimal_places=3)),
                ('id_afip', models.IntegerField(choices=[(1, b'No Gravado'), (2, b'Exento'), (3, b'0%'), (4, b'10,50%'), (5, b'21%'), (6, b'27%'), (9, b'2,50%'), (8, b'5%')])),
            ],
            options={
                'db_table': 'gral_tipo_iva',
            },
        ),
        migrations.CreateModel(
            name='prod_categoria',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('baja', models.BooleanField(default=False)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='empresa', blank=True, to='general.gral_empresa', null=True)),
            ],
            options={
                'ordering': ['nombre'],
                'db_table': 'prod_categoria',
            },
        ),
        migrations.CreateModel(
            name='prod_lista_precios',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('default', models.BooleanField(default=False, verbose_name='Default')),
                ('baja', models.BooleanField(default=False)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='empresa', blank=True, to='general.gral_empresa', null=True)),
            ],
            options={
                'ordering': ['-default', 'nombre'],
                'db_table': 'prod_lista_precios',
            },
        ),
        migrations.CreateModel(
            name='prod_producto_lprecios',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('precio_costo', models.DecimalField(decimal_places=2, default=0, max_digits=15, blank=True, null=True, verbose_name='Precio Costo')),
                ('precio_cimp', models.DecimalField(decimal_places=2, default=0, max_digits=15, blank=True, null=True, verbose_name='Precio c/Imp.')),
                ('coef_ganancia', models.DecimalField(default=1, max_digits=5, decimal_places=3)),
                ('precio_venta', models.DecimalField(decimal_places=2, default=0, max_digits=15, blank=True, null=True, verbose_name='Precio Venta')),
                ('precio_itc', models.DecimalField(decimal_places=3, default=0, max_digits=15, blank=True, null=True, verbose_name='Valor ITC')),
                ('precio_tasa', models.DecimalField(decimal_places=3, default=0, max_digits=15, blank=True, null=True, verbose_name='Valor Tasa')),
                ('lista_precios', models.ForeignKey(related_name='lista_precios', db_column='lista_precios', blank=True, to='productos.prod_lista_precios', null=True)),
            ],
            options={
                'ordering': ['producto__nombre', 'lista_precios'],
                'db_table': 'prod_producto_lprecios',
            },
        ),
        migrations.CreateModel(
            name='prod_producto_ubicac',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('punto_pedido', models.DecimalField(decimal_places=2, default=0, max_digits=15, blank=True, null=True, verbose_name='Punto Pedido')),
            ],
            options={
                'ordering': ['producto__nombre', 'ubicacion'],
                'db_table': 'prod_producto_ubicac',
            },
        ),
        migrations.CreateModel(
            name='prod_productos',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre/Descripci\xf3n')),
                ('codigo', models.CharField(max_length=50, null=True, verbose_name='C\xf3digo', blank=True)),
                ('codigo_barras', models.CharField(max_length=200, null=True, verbose_name='C\xf3digo Barras', blank=True)),
                ('tipo_producto', models.IntegerField(default=1, verbose_name='Tipo', choices=[(1, b'Bienes/Productos/Insumos'), (2, b'Servicios'), (3, b'Trabajos/Pedidos')])),
                ('mostrar_en', models.IntegerField(default=3, verbose_name='Mostrar en', choices=[(1, 'S\xf3lo Ventas'), (2, 'S\xf3lo Compras'), (3, 'Ventas y Compras')])),
                ('unidad', models.IntegerField(default=0, verbose_name='Unidad', choices=[(0, b'u.'), (1, 'm'), (2, 'm2'), (3, 'm3'), (4, 'cm'), (5, 'cm2'), (6, 'cm3'), (7, 'mm'), (8, 'mm2'), (9, 'mm3'), (10, 'gr'), (11, 'Kg'), (12, 'lts'), (13, 'par'), (14, 'doc'), (15, 'km'), (16, 'ton')])),
                ('llevar_stock', models.BooleanField(default=False, verbose_name='Llevar Stock')),
                ('stock_negativo', models.BooleanField(default=True, verbose_name='Stock Negativo')),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('ruta_img', models.ImageField(upload_to=productos.models.get_image_name, db_column='ruta_img', blank=True)),
                ('baja', models.BooleanField(default=False)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modif', models.DateTimeField(auto_now=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='categoria', blank=True, to='productos.prod_categoria', null=True, verbose_name='Categor\xeda')),
                ('cta_egreso', models.ForeignKey(related_name='prod_cta_egreso', on_delete=django.db.models.deletion.SET_NULL, db_column='cta_egreso', blank=True, to='general.gral_plan_cuentas', null=True)),
                ('cta_ingreso', models.ForeignKey(related_name='prod_cta_ingreso', on_delete=django.db.models.deletion.SET_NULL, db_column='cta_ingreso', blank=True, to='general.gral_plan_cuentas', null=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='empresa', blank=True, to='general.gral_empresa', null=True)),
                ('tasa_iva', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='tasa_iva', blank=True, to='productos.gral_tipo_iva', null=True, verbose_name='Tasa IVA')),
            ],
            options={
                'ordering': ['nombre', 'codigo'],
                'db_table': 'prod_productos',
            },
        ),
        migrations.CreateModel(
            name='prod_ubicacion',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('default', models.BooleanField(default=False, verbose_name='Por Defecto')),
                ('baja', models.BooleanField(default=False)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column='empresa', blank=True, to='general.gral_empresa', null=True)),
            ],
            options={
                'ordering': ['-default', 'nombre'],
                'db_table': 'prod_ubicacion',
            },
        ),
        migrations.AddField(
            model_name='prod_producto_ubicac',
            name='producto',
            field=models.ForeignKey(related_name='producto_stock', db_column='producto', blank=True, to='productos.prod_productos', null=True),
        ),
        migrations.AddField(
            model_name='prod_producto_ubicac',
            name='ubicacion',
            field=models.ForeignKey(related_name='ubicacion', db_column='ubicacion', blank=True, to='productos.prod_ubicacion', null=True),
        ),
        migrations.AddField(
            model_name='prod_producto_lprecios',
            name='producto',
            field=models.ForeignKey(related_name='producto_lprecios', db_column='producto', blank=True, to='productos.prod_productos', null=True),
        ),
    ]
