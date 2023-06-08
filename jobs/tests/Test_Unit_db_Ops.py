from django.test import TestCase
from datetime import date
from jobs.models import Job
from jobs.modules.DatabaseOperations import DatabaseOperations
dbOps = DatabaseOperations()

#To just run this test file, python manage.py test jobs.tests.Test_Unit_db_Ops

#To get code coverage by tests, coverage run manage.py test
class TestDBOperationsModule(TestCase):
    def test_deadline_passed_set_job_available(self):
        # Create test data
        pass
        #job_in_progress = Job.objects.create(status='In Progress', deadline_date=date.today())
        #job_available = Job.objects.create(status='Available', deadline_date=date.today())

        ## Call the function
        #self.assertEqual(Job.objects.filter(status='In Progress').count(), 1)  # Ensure there is one job in progress before calling the function
        #self.assertEqual(Job.objects.filter(status='Available').count(), 1)  # Ensure there is one available job before calling the function

        #dbOps.deadline_passed_set_job_available()

        ## Check the updated statuses
        #job_in_progress.refresh_from_db()
        #job_available.refresh_from_db()

        #self.assertEqual(job_in_progress.status, 'Available')
        #self.assertIsNone(job_in_progress.user_id)
        #self.assertIsNone(job_in_progress.start_date)
        #self.assertIsNone(job_in_progress.deadline_date)
        #self.assertEqual(job_in_progress.reminder_sent, 'no')

        self.assertEqual(job_available.status, 'Available')  # Ensure the status remains unchanged for already available jobs

        # Check that no job is in progress after the function call
        self.assertEqual(Job.objects.filter(status='In Progress').count(), 0)


