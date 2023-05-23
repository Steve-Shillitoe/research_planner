"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""
import django
from django.test import LiveServerTestCase, RequestFactory, TestCase
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User, AnonymousUser
from django.urls import resolve, reverse
from django.http import HttpRequest
from jobs.views import home
from django.contrib.auth import login

# TODO: Configure your database in settings.py and sync before running tests.

class FunctionalTestCases(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='s.shillitoe@sheffield.ac.uk',
            password='adminpassword'
        )

    def test_root_url_resolves_to_home(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_home_view_with_authenticated_user(self):
        # Create a GET request to the home view with an authenticated user
        url = reverse('home')
        request = self.factory.get(url)
        request.user = self.user

        # Use the `home` view function to handle the request
        response = home(request)

        # Add your assertions to check the response, status code, etc.
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "initial value")

    def test_homepage_Redirect_To_Login(self):
        # Browse to the home page as an unauthenticated user
        # Should redirect to the login page
        self.browser.get(self.live_server_url)
        self.assertIn('Log in', self.browser.page_source)
        
    def test_home_view_with_unauthenticated_user(self):
        # Create a GET request to the home view with an unauthenticated user
        url = reverse('home')
        request = self.factory.get(url)
        request.user = AnonymousUser()

        # Use the `home` view function to handle the request
        response = home(request)

        # status code = 302 means temporary redirect to another page.
        self.assertEqual(response.status_code, 302)
        # Get the redirect location
        redirect_location = response.url
        # Assert that the redirect location matches the expected URL
        self.assertEqual(redirect_location, '/login/?next=/')  
        
        
      

    #def test_home_page_returns_correct_html(self):
    #    request = HttpRequest()
    #    response = home(request)
    #    html = response.content.decode('utf8')
    #    #print(html)
    #    #self.assertTrue(html.startswith('<!DOCTYPE html>'))
    #    self.assertTrue(html.endswith('</html>'))


    #def test_homepage_JobTable(self):
    #    self.browser.get(self.live_server_url)
    #    self.assertIn('{{ JobTable }}', self.browser.page_source)


    #def test_homepage_UsersJobTable(self):
    #    self.browser.get(self.live_server_url)
    #    self.assertIn('{{UsersJobTable}}', self.browser.page_source)

    #def test_hash_of_hello(self):
    #    self.browser.get(self.live_server_url) #'http://localhost:8000'
    #    text = self.browser.find_element(By.ID, "id_text")
    #    text.send_keys("hello")
    #    self.browser.find_element(By.NAME,"submit").click()
    #    self.assertIn('2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824', self.browser.page_source)
    
    #def test_hash_ajax(self):
    #    self.browser.get(self.live_server_url)
    #    self.browser.find_element(By.ID, 'id_text').send_keys('hello')
    #    time.sleep(5)
    #    self.assertIn('2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824',self.browser.page_source)

    def tearDown(self):
        self.browser.quit()


#class UnitTestCase(TestCase):
#    def test_homepage_Go_To_Login_First(self):
#        response = self.client.get('/')
#        print('response=',response)
#        self.assertTemplateUsed(response, 'jobs/login.html')

#class ViewTest(TestCase):
#    """Tests for the application views."""

#    if django.VERSION[:2] >= (1, 7):
#        # Django 1.7 requires an explicit setup() when running tests in PTVS
#        @classmethod
#        def setUpClass(cls):
#            super(ViewTest, cls).setUpClass()
#            django.setup()

#    #def test_home(self):
#    #    """Tests the home page."""
#    #    response = self.client.get('/')
#    #    self.assertContains(response, 'iBeat', 1, 200)

#    def test_contact(self):
#        """Tests the contact page."""
#        response = self.client.get('/contact')
#        self.assertContains(response, 'Contact', 3, 200)

#    def test_about(self):
#        """Tests the about page."""
#        response = self.client.get('/about')
#        self.assertContains(response, 'About', 3, 200)


