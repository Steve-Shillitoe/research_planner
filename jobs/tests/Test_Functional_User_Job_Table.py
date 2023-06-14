import django
from django.test import  LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import Select
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
from .Helper_Functions import create_file_in_project_root
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
        #create 2 ordinary users
        self.user1 = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='testuser2@example.com',
            password='testpassword2'
        )


        #populate the database
        dbOps.populate_database_from_file()

        #create small & large files to try to upload
        self.large_file=create_file_in_project_root(201, 'large_file.txt')
        self.small_file=create_file_in_project_root(190, 'small_file.txt')

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
        for test_file in self.test_files:
            folder_path = settings.BASE_DIR + '/media/reports/'
            full_file_path = os.path.join(folder_path, test_file)
            if os.path.exists(full_file_path):
                os.remove(full_file_path)


    def log_in(self, username, pwd):
        username_field = self.browser.find_element(By.NAME,'username')
        username_field.send_keys(username)
        password_field = self.browser.find_element(By.NAME,'password')
        password_field.send_keys(pwd)
        password_field.send_keys(Keys.RETURN)

    def log_off(self):
        log_off_link = self.browser.find_element(By.LINK_TEXT, "Log off")
        log_off_link.click()

    def check_main_job_table_In_Progress(self):
        table_cell = self.browser.find_element(By.NAME, 'td_1')
        self.assertIn('In Progress', table_cell.text)
        #test table cell background colour is yellow
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')

    def check_user_job_table_In_Progress(self):
        table_cell = self.browser.find_element(By.NAME, 'status_td_1')
        self.assertIn('In Progress', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 255, 0, 1)')  #fully opaque yellow
        #check deadline date 
        deadline_date = date.today() + timedelta(Configuration.objects.first().number_days_to_complete)
        table_cell = self.browser.find_element(By.NAME, 'date_td_1')
        self.assertIn(str(deadline_date), table_cell.text)

    def check_text_no_jobs_assigned_to_you(self):
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('There are no jobs are assigned to you at the moment.', body.text)

    def check_report_uploaded(self, report_name):
        folder_path = settings.BASE_DIR + '/media/reports/'
        full_file_path = os.path.join(folder_path, report_name)
        self.assertTrue(os.path.exists(full_file_path))

    def check_report_not_uploaded(self, report_name):
        folder_path = settings.BASE_DIR + '/media/reports/'
        full_file_path = os.path.join(folder_path, report_name)
        self.assertFalse(os.path.exists(full_file_path))

    def test_user_job_table(self):
        self.browser.get(self.live_server_url)
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('Log in', body.text)

        #log in as an ordinary user
        self.log_in('testuser', 'testpassword')
        time.sleep(1)

        #check for text saying there are no jobs assigned to you at the moment.
        self.check_text_no_jobs_assigned_to_you()

        #select one job
        available_button = self.browser.find_element(By.NAME,'select_job_1')
        available_button.click()
        time.sleep(1)
        self.check_main_job_table_In_Progress()
        #check database
        self.assertEqual(Job.objects.filter(status='In Progress', id=1).count(), 1)
        self.assertEqual(Job.objects.filter(status='Available').count(), 197)

        #check user job table
        self.check_user_job_table_In_Progress()

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
        #check user job table
        table_cell = self.browser.find_element(By.NAME, 'status_td_1')
        self.assertIn('Received', table_cell.text)
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 0, 255, 1)')  #magenta

        #check main table
        table_cell = self.browser.find_element(By.NAME, 'td_1')
        self.assertIn('Received', table_cell.text)
        #test table cell background colour is yellow
        background_color = table_cell.value_of_css_property("background-color")
        self.assertEqual(background_color, 'rgba(255, 0, 255, 1)')  #magenta

        #Do database checks
        #check status
        self.assertEqual(Job.objects.filter(status='Received', id=1).count(), 1) #One Received job
        self.assertEqual(Job.objects.filter(status='Available').count(), 197) #197 jobs Available now
        #Check submission date
        submission_date = date.today()
        job = Job.objects.get(id=1) 
        self.assertEqual(job.submission_date, submission_date ) 
        #Check file name
        report_name = "job_1"  + "_" + str(job.patient_id) + "_" + str(job.task_id) + ".txt"
        report_name = report_name.replace(" ", "")
        self.test_files.append(report_name)
        self.assertEqual(job.report_name, report_name)
        #check file uploaded to media/reports
        self.check_report_uploaded(report_name)

        #Let's check the uploaded report on the Database Administration page
        #Log off as an ordinary user 
        self.log_off()
        #Log in as a super user
        self.log_in('admin', 'adminpassword')
        time.sleep(1)
        #go to 'Database Administration' page
        db_admin_link = self.browser.find_element(By.LINK_TEXT, 'Database Administration')
        db_admin_link.click()
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('There are no reports uploaded to the database with status Approved.', body.text)
        
        #check dropdown list displays the Received option
        dropdown_element = self.browser.find_element(By.ID, '1dropdown')
        dropdown = Select(dropdown_element)
         # Get the currently selected option
        selected_option = dropdown.first_selected_option
        # Assert the selected option value 'Received'
        self.assertEqual(selected_option.get_attribute('value'), 'Received')
        
        #change status from Received to Approved
        dropdown.select_by_value('Approved')
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('There are no reports uploaded to the database with status Received.', body.text)
        #check database
        job = Job.objects.get(id=1)
        report_name = job.report_name
        self.assertEquals(job.status, 'Approved')

        #Now click Delete (a report) button
        delete_button = self.browser.find_element(By.ID, 'delete_1')
        delete_button.click()
        #click Cancel on the javascript alert
        alert = self.browser.switch_to.alert
        self.assertEquals(alert.text, "Are you sure you want to delete this report?")
        alert.dismiss()
        self.check_report_uploaded(report_name)
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('There are no reports uploaded to the database with status Received.', body.text)
        self.assertNotIn('There are no reports uploaded to the database with status Approved.', body.text)
        #check database
        job = Job.objects.get(id=1)
        self.assertEquals(job.status, 'Approved')
        time.sleep(1)
        #Now click Delete (a report) button again
        report_name = Job.objects.get(id=1).report_name
        delete_button.click()
        #click OK on the javascript alert
        alert = self.browser.switch_to.alert
        self.assertEquals(alert.text, "Are you sure you want to delete this report?")
        alert.accept()
        time.sleep(1)
        self.check_report_not_uploaded(report_name)
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('There are no reports uploaded to the database with status Received.', body.text)
        self.assertIn('There are no reports uploaded to the database with status Approved.', body.text)
        self.assertIn('Report ' + report_name + ' deleted', body.text)
        #check database
        job = Job.objects.get(id=1)
        self.assertEquals(job.status, 'In Progress')
        self.assertEquals(job.report_name, '') 
        self.assertEquals(job.submission_date, None) 
        self.assertEquals(job.start_date, date.today())
        deadline_date = date.today() + timedelta(Configuration.objects.first().number_days_to_complete)
        self.assertEquals(job.deadline_date,  deadline_date)
        self.assertEquals(Job.objects.filter(status='Available').count(), 197)

        #Go to Home page
        home_link = self.browser.find_element(By.LINK_TEXT, "Home")
        home_link.click()
        time.sleep(5)
        #Check Home page appears OK to the super user
        #main job table
        self.check_main_job_table_In_Progress()  
        self.check_text_no_jobs_assigned_to_you()

        #Log out as super user
        self.log_off()
        #log in as user1 to check their view of the Home page
        self.log_in('testuser', 'testpassword')
        #main job table
        self.check_main_job_table_In_Progress() 
        #Check user job table
        self.check_user_job_table_In_Progress()

        #Log out as user1
        self.log_off()
        #log in as user1 to check their view of the Home page
        self.log_in('testuser2', 'testpassword2')
        #main job table
        self.check_main_job_table_In_Progress() 
        self.check_text_no_jobs_assigned_to_you()


        
        



                                              
       







        

