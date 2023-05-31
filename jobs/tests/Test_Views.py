import django
from django.test import TestCase, RequestFactory
from django.test import LiveServerTestCase
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from jobs.views import password_reset_request, home


class PasswordResetRequestViewTest(TestCase):
    def setUp(self):
        # Set up the request factory
        self.factory = RequestFactory()

    def test_password_reset_request(self):
        # Create a POST request with valid email
        url = reverse('password_reset')  #URL name
        request = self.factory.post(url, {'email': 'user@example.com'})

        # Create associated user in the database
        User.objects.create_user(username='user', email='user@example.com', password='password')

        # Call the view function
        response = password_reset_request(request)

        # Perform assertions on the response
        self.assertEqual(response.status_code, 302)  # Assuming redirect status code is expected
        self.assertEqual(response.url, '/password_reset/done/')  # Assuming the redirect URL is '/password_reset/done/'

        # Check if the email was sent
        self.assertEqual(len(mail.outbox), 1)  # Assuming one email was sent
        self.assertEqual(mail.outbox[0].subject, 'Password Reset Requested')
        self.assertEqual(mail.outbox[0].to, ['user@example.com'])

        # Add more assertions as needed for different scenarios and edge cases



#class FunctionalTestCases(LiveServerTestCase):

#    def setUp(self):
#        self.browser = webdriver.Chrome()

#    def test_homepage_Go_To_Login_First(self):
#        self.browser.get(self.live_server_url)
#        self.assertIn('Log in', self.browser.page_source)


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

    #def tearDown(self):
    #    self.browser.quit()


#class UnitTestCase(TestCase):
#    def test_homepage_Go_To_Login_First(self):
#        response = self.client.get('/')
#        print('response=',response)
#        self.assertTemplateUsed(response, 'jobs/login.html')
       

    #def test_hash_form(self):
    #    form = HashForm(data={'text':'hello'})
    #    self.assertTrue(form.is_valid())

    #def test_hash_func_works(self):
    #    text_hash = hashlib.sha256('hello'.encode('utf-8')).hexdigest()
    #    self.assertEqual('2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824', text_hash)
    
    #def save_hash(self):
    #    hash = Hash()
    #    hash.text = 'hello'
    #    hash.hash = '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
    #    hash.save()
    #    return hash

    #def test_hash_object(self):
    #    hash = self.save_hash()
    #    pulled_hash = Hash.objects.get(hash='2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824')
    #    self.assertEqual(hash.text, pulled_hash.text)

    #def test_viewing_hash(self):
    #    hash = self.save_hash()
    #    response = self.client.get('/hash/2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824')
    #    self.assertContains(response, 'hello')

    #def test_bad_data(self):
    #    def badHash():
    #        hash = Hash()
    #        hash.text = 'hello'
    #        hash.hash = '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362aaaaaaa'
    #        hash.full_clean()
    #    self.assertRaises(ValidationError, badHash())

    
#class ViewTest(TestCase):
#    """Tests for the application views."""

#    if django.VERSION[:2] >= (1, 7):
#        # Django 1.7 requires an explicit setup() when running tests in PTVS
#        @classmethod
#        def setUpClass(cls):
#            super(ViewTest, cls).setUpClass()
#            django.setup()


#    def test_home(self):
#        """Tests the home page."""
#        response = self.client.get('/')
#        self.assertContains(response, 'Django', 1, 200)

#    def test_contact(self):
#        """Tests the contact page."""
#        response = self.client.get('/contact')
#        self.assertContains(response, 'Microsoft', 3, 200)

#    def test_about(self):
#        """Tests the about page."""
#        response = self.client.get('/about')
#        self.assertContains(response, 'About', 3, 200)
