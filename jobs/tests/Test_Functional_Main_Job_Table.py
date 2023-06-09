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

#To just run this test file, python manage.py test jobs.tests.Test_Functional_Main_Job_Table

#To get code coverage by tests, coverage run manage.py test

class FunctionalTestSelectJob(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        
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
        #time.sleep(1)

        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('198 jobs', body.text)
        self.assertIn("You can have a maximum of 4 'In Progress' jobs at one time.", body.text)
        self.assertIn("There are no jobs are assigned to you at the moment.", body.text)
        self.assertEquals(Job.objects.count(), 198)
        #time.sleep(1)

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

        #select second job
        available_button = self.browser.find_element(By.NAME,'select_job_2')
        available_button.click()
        time.sleep(1)
        table_cell = self.browser.find_element(By.NAME, 'td_1')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        table_cell = self.browser.find_element(By.NAME, 'td_2')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        #check database
        self.assertEqual(Job.objects.filter(status='In Progress', id=2).count(), 1)
        self.assertEqual(Job.objects.filter(status='In Progress').count(), 2)

        #check that the user cannot select the same task twice
        available_button = self.browser.find_element(By.NAME,'select_job_3')
        available_button.click()
        time.sleep(1)
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('You may only select the same subject-task combination once.', body.text)
        #check database, status of job 3 is unchanged
        self.assertEqual(Job.objects.filter(status='In Progress', id=3).count(), 0)
        self.assertEqual(Job.objects.filter(status='Available', id=3).count(), 1)
        #check total number of jobs is not changed
        self.assertEqual(Job.objects.filter(status='In Progress').count(), 2)

        #select third job
        available_button = self.browser.find_element(By.NAME,'select_job_4')
        available_button.click()
        time.sleep(1)
        table_cell = self.browser.find_element(By.NAME, 'td_1')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        table_cell = self.browser.find_element(By.NAME, 'td_2')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        table_cell = self.browser.find_element(By.NAME, 'td_4')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        #check database
        self.assertEqual(Job.objects.filter(status='In Progress', id=4).count(), 1)
        self.assertEqual(Job.objects.filter(status='In Progress').count(), 3)

        #select forth job
        available_button = self.browser.find_element(By.NAME,'select_job_7')
        available_button.click()
        time.sleep(1)
        table_cell = self.browser.find_element(By.NAME, 'td_1')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        table_cell = self.browser.find_element(By.NAME, 'td_2')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        table_cell = self.browser.find_element(By.NAME, 'td_4')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        table_cell = self.browser.find_element(By.NAME, 'td_7')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        #check database
        self.assertEqual(Job.objects.filter(status='In Progress', id=7).count(), 1)
        #now there should be 4 In Progress jobs in the database
        self.assertEqual(Job.objects.filter(status='In Progress').count(), 4)

        #test the user can only have 4 'In Progress' jobs at one time
        available_button = self.browser.find_element(By.NAME,'select_job_8')
        available_button.click()
        time.sleep(1)
        table_cell = self.browser.find_element(By.NAME, 'td_8')
        self.assertNotIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertNotEqual(background_color, 'rgba(255, 255, 0, 1)')  #it not fully opaque yellow
        #check max number jobs warning displayed
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn("You may only have a maximum of 4 jobs in progress.", body.text)
        #there should still be 4 In Progress jobs in the database
        self.assertEqual(Job.objects.filter(status='In Progress').count(), 4)

        



