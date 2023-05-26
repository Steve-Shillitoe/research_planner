"""
"""
import django
from django.test import LiveServerTestCase, RequestFactory, TestCase, Client
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User, AnonymousUser
from django.urls import resolve, reverse
from django.http import HttpRequest
from jobs.views import home, dbAdmin
from django.contrib.auth import login
import time
from jobs.modules.DatabaseOperations import DatabaseOperations


class TestUserAccess(LiveServerTestCase):

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


    def tearDown(self):
        self.browser.quit()


    def test_home_view_with_super_user(self):
         # Simulate logging in as a superuser
        self.client.login(username='admin', password='adminpassword')
        
        # Make another GET request to the root URL
        response = self.client.get(self.live_server_url)

        # Add your assertions to check the response, status code, etc.
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "initial value")
        #The following 2 links should be visible to a super user
        self.assertContains(response, 'Admin')
        self.assertContains(response, 'Database Administration')


    def test_home_view_with_authenticated_user(self):
        # Create a GET request to the home view with an authenticated user
        #print('test_home_view_with_authenticated_user')
       
        url = reverse('home')
        request = self.factory.get(url)
        request.user = self.user

        # Use the `home` view function to handle the request
        response = home(request)

        # Add your assertions to check the response, status code, etc.
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "initial value")
        #The following 2 links should not be visible to an ordinary user
        self.assertNotContains(response, 'Admin')
        self.assertNotContains(response, 'Database Administration')


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
         
    
    def test_dbAdmin_view_with_unauthenticated_user(self):
        # Create a GET request to the dbAdmin view with an unauthenticated user
        url = reverse('dbAdmin')
        request = self.factory.get(url)
        request.user = AnonymousUser()

        # Use the `dbAdmin' view function to handle the request
        response = dbAdmin(request)

        # status code = 302 means temporary redirect to another page.
        self.assertEqual(response.status_code, 302)
        # Get the redirect location
        redirect_location = response.url
        # Assert that the redirect location matches the expected URL
        self.assertEqual(redirect_location, '/login/?next=/dbAdmin/')  


    def test_dbAdmin_view_with_authenticated_user(self):
        #This user does not have superuser status, so should not be
        #able to access this view.
        # Create a GET request to the dbAdmin view with an unauthenticated user
        url = reverse('dbAdmin')
        request = self.factory.get(url)
        request.user = self.user

        # Use the `dbAdmin` view function to handle the request
        response = dbAdmin(request)

        # status code = 302 means temporary redirect to another page.
        self.assertEqual(response.status_code, 302)
        # Get the redirect location
        redirect_location = response.url
        # Assert that the redirect location matches the expected URL
        self.assertEqual(redirect_location, '/login/?next=/dbAdmin/')  

    
    def test_admin_access(self):
        # Simulate logging in as a regular user
        self.client.login(username='testuser', password='testpassword')
        
        # Make a GET request to the admin URL
        response = self.client.get(self.live_server_url + '/admin/')
        
        # Assert that the regular user is redirected
        self.assertRedirects(response, '/admin/login/?next=/admin/')
        
        # Simulate logging in as a superuser
        self.client.login(username='admin', password='adminpassword')
        
        # Make another GET request to the admin URL
        response = self.client.get(self.live_server_url + '/admin/')
        
        # Assert that the superuser is allowed access
        self.assertEqual(response.status_code, 200)


    


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


#class TestSuperUserAccess(LiveServerTestCase):

#    def setUp(self):
#        self.browser = webdriver.Chrome()
#        self.factory = RequestFactory()
#        self.user = User.objects.create_user(
#            username='testuser',
#            email='testuser@example.com',
#            password='testpassword'
#        )
#        self.superuser = User.objects.create_superuser(
#            username='admin',
#            email='s.shillitoe@sheffield.ac.uk',
#            password='adminpassword'
#        )


#    def tearDown(self):
#        self.browser.quit()


    