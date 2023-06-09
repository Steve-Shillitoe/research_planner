import django
from django.test import  LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from jobs.models import  Job
from django.conf import settings
import time
import os
from jobs.modules.DatabaseOperations import DatabaseOperations
dbOps = DatabaseOperations()

#To just run this test file, python manage.py test jobs.tests.Test_Functional_User_Job_Table

#To get code coverage by tests, coverage run manage.py test

class FunctionalTestUserJobTable(LiveServerTestCase):
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


    def test_user_job_table(self):
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

        #select one job
        available_button = self.browser.find_element(By.NAME,'select_job_1')
        available_button.click()
        time.sleep(1)
        table_cell = self.browser.find_element(By.NAME, 'td_1')
        self.assertIn('In Progress', table_cell.text)
        #test table cell background colour is yellow
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        #check database
        self.assertEqual(Job.objects.filter(status='In Progress', id=1).count(), 1)