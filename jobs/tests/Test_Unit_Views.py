import django
from django.test import TestCase, RequestFactory, LiveServerTestCase, Client
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import xlrd
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.conf import settings
from django.contrib import messages
from jobs.views import password_reset_request, home, register_request, download_report, download_jobs
from jobs.models import Configuration, Job, Task, Patient
from jobs.forms import NewUserForm

#To just run this test file, python manage.py test jobs.tests.Test_Unit_Views
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

        # Get the sent email object
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

        #create a file to download
        folder_path = settings.BASE_DIR + '/media/reports/'
        file_name = 'test.txt'
        file_path = folder_path + '/' + file_name
        # Open the file in write mode ('w') and create it if it doesn't exist
        with open(file_path, 'w') as file:
            file.write('This is a test file.')

        request = self.factory.get(url, {'report': file_name})

        # Call the view function
        response = download_report(request)

        # Perform assertions on the response
        self.assertEqual(response.status_code, 200)  # Assuming the file is found and downloaded
        self.assertEqual(response['Content-Disposition'], 'attachment; filename={}'.format(file_name))
       

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


    def test_access_dbAdmin(self):
        url = reverse('dbAdmin')  # 'dbAdmin' is the URL name associated with the 'dbAdmin' view
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)  # Assert that the response status code is 200 (OK)
        self.assertTemplateUsed(response, 'jobs/dbAdmin.html')  # Assert that the correct template is used

        # Assert the context data passed to the template
        self.assertEqual(response.context['main_title'], 'Test_Title')


    def test_download_jobs(self):
        #May need to populate the database first
       
        # Simulate a GET request to the view function
        client = Client()
        response = client.get(reverse('download_jobs'))  # Replace with the actual download URL

        # Assert that the response has a successful status code
        self.assertEqual(response.status_code, 200)

        # Assert that the content type is set to Excel
        self.assertEqual(response['Content-Type'], 'application/ms-excel')

        # Assert that the content disposition is set correctly
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=jobs.xls')

        # Assert that the response content is not empty
        self.assertTrue(len(response.content) > 0)

        # Read the response content as an Excel file using xlrd
        workbook = xlrd.open_workbook(file_contents=response.content)
        sheet = workbook.sheet_by_name('Jobs')

        # Perform assertions on the sheet data
        self.assertEqual(sheet.nrows, 1)  # Check the row count, should be 1 as there is only a header row
        self.assertIn('job id', sheet.row_values(0))  # Check if 'job id' column exists. It is the first column.

     

