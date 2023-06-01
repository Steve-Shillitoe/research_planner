import django
from django.test import TestCase, RequestFactory, LiveServerTestCase, Client
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from django.conf import settings
import time
import os

#To just run this test file, python manage.py test jobs.tests.Test_Functional_Views

class FunctionalTestsViews(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        #create a super user
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='s.shillitoe@sheffield.ac.uk',
            password='adminpassword'
        )


    def tearDown(self):
        self.browser.quit()


    def test_create_database(self):
        self.browser.get(self.live_server_url)
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('Research Planner', body.text)

        #log in as admin
        username_field = self.browser.find_element(By.NAME,'username')
        username_field.send_keys('admin')
        password_field = self.browser.find_element(By.NAME,'password')
        password_field.send_keys('adminpassword')
        password_field.send_keys(Keys.RETURN)
        time.sleep(1)
        # admin user clicks on the Database Administration link
        dbAdmin_link = self.browser.find_element(By.LINK_TEXT, "Database Administration")
        dbAdmin_link.click()
        time.sleep(1)
        # verify that Populate Database header is present.
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('Populate Database', body.text)

        #Upload excel spreadsheet to populate the database with
        choose_file_button = self.browser.find_element(By.NAME, "excel_file")
        file_path = os.path.join(settings.BASE_DIR, 'researchPlannerData.xlsx')
        choose_file_button.send_keys(file_path)
        submit_button = self.browser.find_element(By.NAME, "uploadFile")
        submit_button.click()
       
        #handle javascript confirm pop-up
        alert = self.browser.switch_to.alert
        self.assertEquals(alert.text, "This action will delete all the existing data in the database. Do you wish to continue?")
        alert.accept()

        #test for data successfully added to database
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('Data successfully uploaded to database', body.text)

        #test the actual database
        


     
        


