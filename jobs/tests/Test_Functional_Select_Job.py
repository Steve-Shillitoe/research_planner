import django
from django.test import TestCase, RequestFactory, LiveServerTestCase, Client
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from jobs.models import Patient, Job, Configuration, Task
from django.conf import settings
import time
import os
from jobs.modules.DatabaseOperations import DatabaseOperations
dbOps = DatabaseOperations()

#To just run this test file, python manage.py test jobs.tests.Test_Functional_Select_Job

#To get code coverage by tests, coverage run manage.py test

class FunctionalTestsSelectJob(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        #create a super user
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='s.shillitoe@sheffield.ac.uk',
            password='adminpassword'
        )
        #create an ordinary user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

        #populate the database
        dbOps.populate_database_from_file()


    def tearDown(self):
        self.browser.quit()


    def test_select_job(self):
        self.browser.get(self.live_server_url)
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('Log in', body.text)
        time.sleep(1)

        #log in as an ordinary user
        username_field = self.browser.find_element(By.NAME,'username')
        username_field.send_keys('testuser')
        password_field = self.browser.find_element(By.NAME,'password')
        password_field.send_keys('testpassword')
        password_field.send_keys(Keys.RETURN)
        time.sleep(1)

        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('198 jobs', body.text)
        time.sleep(1)


