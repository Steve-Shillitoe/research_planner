import django
from django.test import  LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from jobs.models import  Job, Configuration
from django.conf import settings
import time
from datetime import date, timedelta
import os
from jobs.modules.DatabaseOperations import DatabaseOperations
dbOps = DatabaseOperations()

#To just run this test file, python manage.py test jobs.tests.Test_Functional_User_Job_Table

#To get code coverage by tests, coverage run manage.py test


def create_file_in_project_root(file_size_kb, file_name):
    """
    file_name =  file name + extension, e.g., large_file.txt
    """
    full_file_path = os.path.join(settings.BASE_DIR,file_name)

    # Calculate the number of bytes needed for the desired file size
    file_size_bytes = file_size_kb * 1024

    # Create a file and write data to it until the desired file size is reached
    with open(full_file_path, 'w') as file:
        while os.path.getsize(full_file_path) < file_size_bytes:
            file.write('test') 
            
    return full_file_path



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

        #create small & large files to try to upload
        self.large_file=create_file_in_project_root(201, 'large_file.txt')
        self.small_file=create_file_in_project_root(199, 'small_file.txt')

        self.test_files = []

        #Delete files in media\reports self.test_files



    def tearDown(self):
        self.browser.quit()
        if os.path.exists(self.small_file):
            # Delete the file
            os.remove(self.small_file)
        if os.path.exists(self.large_file):
           # Delete the file
           os.remove(self.large_file)


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

        #check for text saying there are no jobs assigned to you at the moment.
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('There are no jobs are assigned to you at the moment.', body.text)

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
        self.assertEqual(Job.objects.filter(status='Available').count(), 197)

        #check user job table
        table_cell = self.browser.find_element(By.NAME, 'status_td_1')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        #check deadline date 
        deadline_date = date.today() + timedelta(Configuration.objects.first().number_days_to_complete)
        table_cell = self.browser.find_element(By.NAME, 'date_td_1')
        self.assertIn(str(deadline_date), table_cell.text)

        #check cancel job
        cancel_button = self.browser.find_element(By.NAME,'cancel_1')
        cancel_button.click()
        #check database
        self.assertEqual(Job.objects.filter(status='In Progress', id=1).count(), 0) #No In Progress job
        self.assertEqual(Job.objects.filter(status='Available').count(), 198) #All jobs Available again
        #In the main table, check that the job is now Available again
        available_button = self.browser.find_element(By.NAME,'select_job_1')
        self.assertEqual(available_button.get_attribute('value'), 'AVAILABLE')

        #Select the first job again
        available_button = self.browser.find_element(By.NAME,'select_job_1')
        available_button.click()
        time.sleep(1)

        
        #try to upload large file
        upload_button = self.browser.find_element(By.ID, 'upload_report_file_1')
        upload_button.send_keys(self.large_file)
        time.sleep(1)
        alert = self.browser.switch_to.alert
        self.assertEquals(alert.text, "The file size must be less than 209KB")
        alert.accept()

        #try to upload file less than 200kb in size
        upload_button.send_keys(self.small_file)
        self.assertRaises(NoAlertPresentException)
        submit_button = self.browser.find_element(By.ID, 'upload_report_1')
        submit_button.click()
        #Do database checks
        #Check file name

        #check file uploaded to media/reports

        #check file name



        

