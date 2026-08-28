# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

TIPO_PRODUCTO = (    
    (1, 'Bienes/Productos/Insumos'),
    (2, 'Servicios'),
    (3, 'Trabajos/Pedidos'),
)

MOSTRAR_PRODUCTO = (    
    (1, u'Sólo Ventas'),
    (2, u'Sólo Compras'),
    (3, u'Ventas y Compras'),    
)

TIPO_PRODUCTO_ = (    
    (0, 'Todos'),
    (1, 'Bienes/Productos/Insumos'),
    (2, 'Servicios'),
    (3, 'Trabajos/Pedidos'),
)


MOSTRAR_PRODUCTO_ = (    
    (0, u'Todos'),
    (1, u'Sólo Ventas'),
    (2, u'Sólo Compras'),
    (3, u'Ventas y Compras'),    
)

BAJA_ = (    
    (0, 'Todos'),
    (1, 'Activos'),
    (2, 'Baja'),
)

#Valor ITC default
vitc = 5.733
#Valor TASA default
vtasa = 0.704