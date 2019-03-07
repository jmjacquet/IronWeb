from django.test import TestCase
from comprobantes.models import cpb_estado,cpb_tipo,cpb_nro_afip, cpb_pto_vta,cpb_comprobante
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

#python manage.py dumpdata --format=json comprobantes.cpb_estado comprobantes.cpb_tipo comprobantes.cpb_nro_afip comprobantes.cpb_pto_vta > initial_data.json
#>python manage.py dumpdata comprobantes.cpb_tipo --indent 2 > cpb_tipo.json

class cpb_estado_ModelTest(TestCase):
	

	def test_representacion(self):
	    estado = mommy.make(cpb_estado)
	    self.assertEqual(estado.__unicode__(), estado.nombre)


class cpb_tipo_ModelTest(TestCase):	

	def test_representacion(self):
	    tipo = mommy.make(cpb_tipo)
	    self.assertEqual(tipo.__unicode__(), tipo.nombre)


class cpb_nro_afip_ModelTest(TestCase):
	
	def test_representacion(self):
	    tipo = mommy.make(cpb_tipo)
	    na = mommy.make(cpb_nro_afip)
	    self.assertEqual(na.__unicode__(), u'%s - %s --> %s' % (na.cpb_tipo,na.letra,na.numero_afip) )


class cpb_comprobante_ModelTest(TestCase):	

	def setUp(self):
		tipo = mommy.make(cpb_tipo,id=1)
		entidad = mommy.make('entidades.egr_entidad')		
		self.cpb = mommy.make(cpb_comprobante,id=1,cpb_tipo=tipo)
		
		
	def test_get_pto_vta(self):
		pv = mommy.make(cpb_pto_vta,numero=1)
		self.cpb.pto_vta = pv.numero
		self.assertNotEqual(self.cpb.get_pto_vta(), None)

	def test_get_listado(self):
		response = self.client.get(self.cpb.get_listado())
		self.assertEqual(response.status_code, 302)
