# -*- coding: utf-8 -*-
# from django.test import TestCase
# from django.test.client import Client
# from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from django.test import LiveServerTestCase

class GeneralTests(TestCase):
	def setUp(self):
		self.c = Client()
		self.user = User.objects.create_user(username="demo", email="test@test.com", password="demo")
		

	def test_homepage(self):
		print self.c.login(username='demo', password='demo')
		response = self.c.get(reverse('principal'))
		self.assertEqual(response.status_code, 200)

	def test_authenticate_inactive(self):
        """
        An inactive user can't authenticate.
        """
        self.assertEqual(authenticate(**self.user_credentials), self.user)
        self.user.is_active = False
        self.user.save()
        self.assertIsNone(authenticate(**self.user_credentials))


class LogInTest(TestCase):
	def setUp(self):
		self.credentials = {
		'username': 'demo',
		'password': 'dem'}
		User.objects.create_user(username="demo", email="test@test.com", password="demo")
	
	def test_login(self):
		# send login data
		response = self.client.post('/login/', self.credentials, follow=True)
		print response.context['user']
		self.assertTrue(response.context['user'].is_authenticated)

class LoginTestCase(LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Chrome()        
        super(LoginTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(LoginTestCase, self).tearDown()

    def test_login(self):
        selenium = self.selenium
        #Opening the link we want to test
        selenium.get('http://127.0.0.1:8000/login')
        

        #find the form element
        username = selenium.find_element_by_name('username')
        password = selenium.find_element_by_name('password')
        

        submit = selenium.find_element_by_name('login')

        #Fill the form with data
        username.send_keys('demo')
        password.send_keys('sarasa')
        
        #submitting the form
        submit.send_keys(Keys.RETURN)

        #check the returned result
        print selenium.page_source
        #assert 'Check your email' in selenium.page_source