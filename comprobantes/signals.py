# -*- coding: utf-8 -*-
# from .models import *
# from django.db.models.signals import post_save,post_delete

# @receiver(post_save, sender=cpb_comprobante,dispatch_uid="actualizar_ultimo_nro")
# def actualizar_ultimo_nro(sender, instance,created, **kwargs):
#    if created:                         
#        letra = instance.letra
#        tipo=instance.cpb_tipo
#        numero=instance.numero       
#        if tipo.usa_pto_vta == True:
#            pventa = cpb_pto_vta.objects.get(numero=instance.pto_vta,empresa=instance.empresa)              
#            pventa_tipoCpb, created = cpb_pto_vta_numero.objects.get_or_create(cpb_tipo=tipo,letra=letra,cpb_pto_vta=pventa,empresa=instance.empresa)
#            pventa_tipoCpb.ultimo_nro+= 1
#            pventa_tipoCpb.save()     
#        else:     
#            if not tipo.facturable:           
#             tipo.ultimo_nro = numero           
#             tipo.save()

# @receiver(post_save, sender=cpb_cobranza,dispatch_uid="actualizar_cobranza")
# @receiver(post_delete, sender=cpb_cobranza,dispatch_uid="actualizar_cobranza")
# def actualizar_cobranza(sender, instance, **kwargs):      
#    if instance:  
#     if instance.cpb_factura:
#         recalcular_saldo_cpb(instance.cpb_factura.pk)            


# @receiver(post_delete, sender=cpb_comprobante_detalle,dispatch_uid="actualizar_comprobante")

#Borro las referencias de un cobro/deposito/pago realizado con un cheque, así me queda liberado
# @receiver(post_delete, sender=cpb_comprobante_fp,dispatch_uid="actualizar_cpbs_fp_cheques")
# def actualizar_cpbs_fp_cheques(sender, instance, **kwargs):      
#    if instance:        
#         fps = cpb_comprobante_fp.objects.filter(mdcp_salida__id=instance.id)
#         for c in fps:
#                 c.mdcp_salida = None
#                 c.save()  
        



