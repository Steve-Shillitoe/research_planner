from django.test import TestCase
from datetime import date, timedelta
from jobs.models import Job
from django.contrib.auth.models import User
from jobs.modules.DatabaseOperations import DatabaseOperations
dbOps = DatabaseOperations()
from .Helper_Functions import flush_database
#To just run this test file, python manage.py test jobs.tests.Test_Unit_db_Ops

#To get code coverage by tests, coverage run manage.py test
class TestDBOperationsModule(TestCase):
    def test_deadline_passed_set_job_available(self):
        #start with an empty database, with id's reset to 1
        flush_database()

        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

        #populate the database
        dbOps.populate_database_from_file()

        job_in_progress_due_today = Job.objects.filter(id=1).update(status ='In Progress', 
                                            user_id = self.user,
                                            start_date = date.today()- timedelta(days=6),
                                            deadline_date = date.today())

        job_in_progress_due_yesterday = Job.objects.filter(id=2).update(status ='In Progress', 
                                            user_id = self.user,
                                            start_date = date.today()- timedelta(days=7),
                                            deadline_date = date.today() - timedelta(days=1))
        

        # Ensure there are jobs in progress before calling the function
        self.assertEqual(Job.objects.filter(status='In Progress').count(), 2) 
        # Ensure there is one job available before calling the function
        self.assertEqual(Job.objects.filter(status='Available').count(), 196) 
        
         # Call the function
        dbOps.deadline_passed_set_job_available()

        # Check the updated statuses
        job_in_progress_due_today = Job.objects.get(id=1)
        job_in_progress_due_yesterday = Job.objects.get(id=2)

        self.assertEqual(job_in_progress_due_yesterday.status, 'Available')
        self.assertIsNone(job_in_progress_due_yesterday.user_id)
        self.assertIsNone(job_in_progress_due_yesterday.start_date)
        self.assertIsNone(job_in_progress_due_yesterday.deadline_date)
        self.assertEqual(job_in_progress_due_yesterday.reminder_sent, 'no')

        self.assertEqual(job_in_progress_due_today.status, 'In Progress')  # Ensure the status remains unchanged for already available jobs

        # Check that there is one job is in progress after the function call
        self.assertEqual(Job.objects.filter(status='In Progress').count(), 1)
        #and 197 Available jobs
        self.assertEqual(Job.objects.filter(status='Available').count(), 197)


