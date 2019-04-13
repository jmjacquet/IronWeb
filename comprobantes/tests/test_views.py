from django.test import TestCase
from django.core.urlresolvers import reverse
from usuarios.models import usu_usuario,UserProfile,User
from django.test.client import Client

class MovInternosTest(TestCase):
	def setUp(self):		
		self.credentials = {
		'username': 'demo',
		'password': 'dem'}
		self.c = Client()
		self.user = User.objects.create_user(username="demo", email="test@test.com", password="demo")
		print self.c.login(username='demo', password='demo')
		response = self.c.post('/login/', self.credentials, follow=True)
		print response.context['user']
        

	def test_MovInternosCreateView(self):
		
		response = self.client.get(reverse('principal'))		
		self.assertEqual(response.status_code, 200)
		self.assertIn("form", response.context)
		self.assertIn("cpb_fp", response.context)

	
		