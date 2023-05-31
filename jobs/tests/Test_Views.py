import django
from django.test import TestCase, RequestFactory, LiveServerTestCase
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.conf import settings
from django.contrib import messages
from jobs.views import password_reset_request, home, register_request, download_report
from jobs.models import Configuration
from jobs.forms import NewUserForm


class UnitTestCases(TestCase):
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


    def test_register_request_valid_form(self):
        #Create Configuration table with data as 
        #it will be needed to send an email
        Configuration.objects.create(
            main_title="Test Title",
            main_intro="Test Main Intro",
            indiv_intro="Test Individual Intro",
            number_days_to_complete=5,
            max_num_jobs=3
        )
        # Create a POST request with valid form data
        url = reverse('register')  # 'register' is the  URL name
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }
        request = self.factory.post(url, form_data)

        # Call the view function
        response = register_request(request)

        # Perform assertions on the response
        self.assertEqual(response.status_code, 302)  # Redirect status code is expected
        self.assertEqual(response.url, '/login/')  # The redirect URL is '/login/'

        # Check if the user was created in the database
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')


    def test_register_request_invalid_form(self):
        # Create a POST request with invalid form data
        url = reverse('register')  # Replace 'register' with the actual URL name
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword1',
            'password2': 'testpassword2'
        }
        request = self.factory.post(url, form_data)

        # Call the view function
        response = register_request(request)

        # Perform assertions on the response
        self.assertEqual(response.status_code, 200)  # Assuming the form is redisplayed with validation errors

        # Check if the form data is retained in the form
        form = response.context_data['register_form']
        self.assertEqual(form.initial['username'], 'testuser')
        self.assertEqual(form.initial['email'], 'test@example.com')
        self.assertEqual(form.initial['first_name'], 'Test')
        self.assertEqual(form.initial['last_name'], 'User')

        # Check if the error message is displayed
        messages = list(response.context.get('messages'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Unsuccessful registration. Invalid password.')


    def test_download_report_existing_file(self):
        # Create a GET request with a valid report parameter
        url = reverse('download_report')  #the  URL name
        #path_to_report = settings.BASE_DIR + '/media/reports/' + report
        report = 'Test.pdf'  # Replace with an existing report file in your media/reports directory
        request = self.factory.get(url, {'report': report})

        # Call the view function
        response = download_report(request)

        # Perform assertions on the response
        self.assertEqual(response.status_code, 200)  # Assuming the file is found and downloaded
        self.assertEqual(response['Content-Disposition'], 'attachment; filename={}'.format(report))

       

    def test_download_report_nonexistent_file(self):
        # Create a GET request with a non-existing report parameter
        url = reverse('download_report')  # the URL name
        report = 'nonexistent_report.pdf'  # Replace with a non-existing report file
        request = self.factory.get(url, {'report': report})

        # Call the view function
        response = download_report(request)

        # Perform assertions on the response
        self.assertEqual(response.status_code, 200)  # Assuming the 'file_not_found.html' template is rendered
        self.assertTemplateUsed(response, 'file_not_found.html')


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
