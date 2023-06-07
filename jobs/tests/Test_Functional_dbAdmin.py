import django
from django.test import TestCase, RequestFactory, LiveServerTestCase, Client
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from jobs.models import Patient, Job, Configuration, Task
from django.conf import settings
import time
import os

#To just run this test file, python manage.py test jobs.tests.Test_Functional_dbAdmin

#To get code coverage by tests, coverage run manage.py test

class FunctionalTestsdbAdmin(LiveServerTestCase):
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


    def return_num_files_in_folder(self, file, folder_path):
        files = os.listdir(folder_path)
        # Filter out directories from the list
        files = [file for file in files if os.path.isfile(os.path.join(folder_path, file))]
        # Count the number of files
        file_count = len(files)
        return file_count


    def test_database_administration(self):
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

        #test delete database
        delete_database_button = self.browser.find_element(By.NAME, "deleteDatabase")
        delete_database_button.click()
        time.sleep(1)
        #handle javascript confirm pop-up
        alert = self.browser.switch_to.alert
        self.assertEquals(alert.text, "Are you sure you want to delete all the data in the database?")
        alert.accept()
        time.sleep(1)
        #test for data successful deletion of database
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('Database deleted', body.text)
        #test database table Jobs is empty
        self.assertFalse(Job.objects.exists())

        #test delete reports
        #first add a report to '/media/reports/'
        folder_path = settings.BASE_DIR + '/media/reports/'
        file_name = 'test.txt'
        file_path = folder_path + '/' + file_name
        # Open the file in write mode ('w') and create it if it doesn't exist
        with open(file_path, 'w') as file:
            file.write('This is a test file.')
        #check there is one file in this directory
        file_count = self.return_num_files_in_folder(file, folder_path)
        self.assertEquals(file_count, 1)
        delete_reports_button = self.browser.find_element(By.NAME, "deleteAllReports")
        delete_reports_button.click()
        time.sleep(1)
        #handle javascript confirm pop-up
        alert = self.browser.switch_to.alert
        self.assertEquals(alert.text, "Are you sure you want to delete all the reports? You should only do this after you have deleted the database.")
        alert.accept()
        time.sleep(1)
        #test for data successful deletion of report
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('All reports deleted', body.text)
        #The reports folder should now contain zero reports
        file_count = self.return_num_files_in_folder(file, folder_path)
        self.assertEquals(file_count, 0)


        #Upload excel spreadsheet to populate the database
        choose_file_button = self.browser.find_element(By.NAME, "excel_file")
        file_path = os.path.join(settings.BASE_DIR, 'researchPlannerData.xlsx')
        time.sleep(1)
        choose_file_button.send_keys(file_path)
        submit_button = self.browser.find_element(By.NAME, "uploadFile")
        submit_button.click()
        time.sleep(1)
        #handle javascript confirm pop-up
        alert = self.browser.switch_to.alert
        self.assertEquals(alert.text, "This action will delete all the existing data in the database. Do you wish to continue?")
        alert.accept()

        #test for data successfully added to database
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('Data successfully uploaded to database', body.text)
        #test the actual database by
        #testing Jobs table is not empty
        self.assertTrue(Job.objects.exists())
        
        #test download jobs spreadsheet link
        download_jobs_link = self.browser.find_element(By.LINK_TEXT, "Download Jobs Spreadsheet")
        download_jobs_link.click()
        time.sleep(5)
        #downloads_folder = os.path.expanduser("~/Downloads")
        #to further test this we'd have to open the downloaded excel file which would
        #mean this test would not be generic. Also, this has been covered in the views unit tests



     
        


