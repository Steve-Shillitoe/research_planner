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

#To just run this test file, python manage.py test jobs.tests.Test_Functional_Forgotten_Password

class TestFunctionalForgottenPassword(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        #create a super user
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='s.shillitoe@sheffield.ac.uk',
            password='adminpassword'
        )

        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

        Configuration.objects.create(
            main_title="Test Title",
            main_intro="Test Main Intro",
            indiv_intro="Test Individual Intro",
            number_days_to_complete=5,
            max_num_jobs=3
        )


    def tearDown(self):
        self.browser.quit()


    def test_forgotten_password(self):
        self.browser.get(self.live_server_url)
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('Log in', body.text)
        time.sleep(1)
        #click Forgot password? link
        forgot_pwd_link = self.browser.find_element(By.LINK_TEXT, "Forgot password?")
        forgot_pwd_link.click()
        time.sleep(2)

        email_txt_box = self.browser.find_element(By.NAME, "email")
        #enter an email that is not in the database
        email_txt_box.send_keys('wrong_email@test.com')
        Send_email_button = self.browser.find_element(By.NAME, "send_email")
        Send_email_button.click()
        time.sleep(2)

        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('No user found who is associated with this email address', body.text)
      
    


