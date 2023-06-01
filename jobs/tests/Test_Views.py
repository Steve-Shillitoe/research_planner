import django
from django.test import TestCase, RequestFactory, LiveServerTestCase, Client
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from datetime import datetime
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

        ## Get the sent email object
        #email = mail.outbox[0]

        ## Check email attributes such as subject, sender, recipient, etc.
        #self.assertEqual(email.subject, 'Your Subject')
        #self.assertEqual(email.from_email, 'sender@example.com')
        #self.assertEqual(email.to, ['recipient@example.com'])

        ## Check the email body or text content
        #self.assertIn('Hello,', email.body)
        #self.assertIn('This is the email content.', email.body)


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
        #Create Configuration table with data as 
        #it will be needed to send an email
        Configuration.objects.create(
            main_title="Test Title",
            main_intro="Test Main Intro",
            indiv_intro="Test Individual Intro",
            number_days_to_complete=5,
            max_num_jobs=3
        )
        # Create a POST request with invalid form data
        url = reverse('register')  # 'register' is the  URL name
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword1',
            'password2': 'testpassword2'
        }
        
        client = Client()
        response = client.post(url, form_data)

        # Perform assertions on the response
        self.assertEqual(response.status_code, 200)  # The form is redisplayed with validation errors

        # Check if the form data is retained in the form
        reg_form = response.content.decode('utf-8')
        self.assertIn('name="username" value="testuser"', reg_form)
        self.assertIn('name="email" value="test@example.com"', reg_form)
        self.assertIn('name="first_name" value="Test"', reg_form)
        self.assertIn('name="last_name" value="User"', reg_form)

        # Check if the error message is displayed
        warning = response.context['warning']
        self.assertEqual(warning, 'Unsuccessful registration. Invalid password.')


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
        client = Client()
        # Create a GET request with a non-existing report parameter
        url = reverse('download_report')  # the URL name
        report = 'nonexistent_report.pdf'  # Replace with a non-existing report file
        #request = self.factory.get(url, {'report': report})

        # Call the view function
        #response = download_report(request)
        response = client.get(url, {'report': report})
        # Perform assertions on the response
        self.assertEqual(response.status_code, 200)  # Assuming the 'file_not_found.html' template is rendered
        self.assertTemplateUsed(response, 'jobs/file_not_found.html')


    def test_about_view(self):
        client = Client()
        response = client.get('/about/')  # Replace '/about/' with the actual URL of the 'about' view
        
        self.assertEqual(response.status_code, 200)  # Assert that the response status code is 200 (OK)
        self.assertTemplateUsed(response, 'jobs/about.html')  # Assert that the correct template is used
        
        # Assert the context data passed to the template
        self.assertEqual(response.context['title'], 'About')
        self.assertEqual(response.context['message'], 'Your application description page.')
        self.assertEqual(response.context['year'], datetime.now().year) 


    def test_contact_view(self):
        client = Client()
        response = client.get('/contact/')  # Replace '/contact/' with the actual URL of the 'contact' view
        
        self.assertEqual(response.status_code, 200)  # Assert that the response status code is 200 (OK)
        self.assertTemplateUsed(response, 'jobs/contact.html')  # Assert that the correct template is used
        
        # Assert the context data passed to the template
        self.assertEqual(response.context['title'], 'Contact')
        self.assertEqual(response.context['message'], 'QIB Sheffield')
        self.assertEqual(response.context['year'], datetime.now().year) 



class DbAdminViewTestCase(TestCase):
    def setUp(self):
        #Create Configuration table with data as 
        #it will be needed to send an email
        Configuration.objects.create(
            main_title="Test_Title",
            main_intro="Test Main Intro",
            indiv_intro="Test Individual Intro",
            number_days_to_complete=5,
            max_num_jobs=3
        )
        self.client = Client()
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
        self.client.force_login(self.user)

    def test_get_request(self):
        url = reverse('dbAdmin')  # 'dbadmin' is the URL name associated with the 'dbAdmin' view
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)  # Assert that the response status code is 200 (OK)
        self.assertTemplateUsed(response, 'jobs/dbAdmin.html')  # Assert that the correct template is used

        # Assert the context data passed to the template
        self.assertEqual(response.context['main_title'], 'Test_Title')
        self.assertIsNotNone(response.context['received_reports'])
        self.assertIsNotNone(response.context['approved_reports'])


    #def test_post_request_delete_database(self):
    #    url = reverse('dbAdmin')  # 'dbadmin' is the URL name associated with the 'dbAdmin' view
    #    response = self.client.post(url, {'deleteDatabase': True})

    #    self.assertEqual(response.status_code, 200)  # Assert that the response status code is 200 (OK)
    #    self.assertTemplateUsed(response, 'jobs/dbAdmin.html')  # Assert that the correct template is used

    #    # Assert the context data passed to the template
    #    self.assertEqual(response.context['main_title'], 'Test_Title')
    #    self.assertEqual(response.context['delete_db_message'], 'Database deleted')
    #    self.assertIsNotNone(response.context['received_reports'])
    #    self.assertIsNotNone(response.context['approved_reports'])

    #    # Additional assertions for the expected behavior after deleting the database

    ## Add more test methods to cover other scenarios and form inputs


