# -*- coding: utf-8 -*-
from PIL import Image, ImageFont, ImageDraw
from .utilidades import digVerificador


def GenerarImagen(codigo, archivo="barras.png", 
                      basewidth=3, width=None, height=30, extension = "PNG"):
    "Generar una imágen con el código de barras Interleaved 2 of 5"
    # basado de:
    #  * http://www.fpdf.org/en/script/script67.php
    #  * http://code.activestate.com/recipes/426069/

    wide = basewidth
    narrow = basewidth / 3

    # códigos ancho/angostos (wide/narrow) para los dígitos
    bars = ("nnwwn", "wnnnw", "nwnnw", "wwnnn", "nnwnw", "wnwnn", "nwwnn", 
            "nnnww", "wnnwn", "nwnwn", "nn", "wn")

    # agregar un 0 al principio si el número de dígitos es impar
    if len(codigo) % 2:
        codigo = "0" + codigo

    if not width:
        width = (len(codigo) * 3) * basewidth + (10 * narrow)
        #width = 380
    # crear una nueva imágen
    im = Image.new("1",(width, height))

    # agregar códigos de inicio y final
    codigo = "::" + codigo.lower() + ";:" # A y Z en el original

    # crear un drawer
    draw = ImageDraw.Draw(im)

    # limpiar la imágen
    draw.rectangle(((0, 0), (im.size[0], im.size[1])), fill=256)

    xpos = 0    
    # dibujar los códigos de barras
    for i in range(0,len(codigo),2):
        # obtener el próximo par de dígitos
        bar = ord(codigo[i]) - ord("0")
        space = ord(codigo[i + 1]) - ord("0")
        # crear la sequencia barras (1er dígito=barras, 2do=espacios)
        seq = ""
        for s in range(len(bars[bar])):
            seq = seq + bars[bar][s] + bars[space][s]

        for s in range(len(seq)):
            if seq[s] == "n":
                width = narrow
            else:
                width = wide

            # dibujar barras impares (las pares son espacios)
            if not s % 2:
                draw.rectangle(((xpos,0),(xpos+width-1,height)),fill=0)
            xpos = xpos + width 
   
    # im.save(archivo, extension.upper())
    return im

# def DigitoVerificadorModulo10(self, codigo):
#         "Rutina para el cálculo del dígito verificador 'módulo 10'"
#         # http://www.consejo.org.ar/Bib_elect/diciembre04_CT/documentos/rafip1702.htm
#         # Etapa 1: comenzar desde la izquierda, sumar todos los caracteres ubicados en las posiciones impares.
#         codigo = codigo.strip()
#         if not codigo or not codigo.isdigit():
#             return ''
#         etapa1 = sum([int(c) for i,c in enumerate(codigo) if not i%2])
#         # Etapa 2: multiplicar la suma obtenida en la etapa 1 por el número 3
#         etapa2 = etapa1 * 3
#         # Etapa 3: comenzar desde la izquierda, sumar todos los caracteres que están ubicados en las posiciones pares.
#         etapa3 = sum([int(c) for i,c in enumerate(codigo) if i%2])
#         # Etapa 4: sumar los resultados obtenidos en las etapas 2 y 3.
#         etapa4 = etapa2 + etapa3
#         # Etapa 5: buscar el menor número que sumado al resultado obtenido en la etapa 4 dé un número múltiplo de 10. Este será el valor del dígito verificador del módulo 10.
#         digito = 10 - (etapa4 - (int(etapa4 / 10) * 10))
#         if digito == 10:
#             digito = 0
#         return str(digito)