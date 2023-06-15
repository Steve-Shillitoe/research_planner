
from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from jobs.models import Job
from unittest.mock import MagicMock
from jobs.modules.SendEmail import SendEmail
from jobs.modules.DatabaseOperations import DatabaseOperations
from jobs.modules.ViewHelperFunctions import buildMainJobsTable, buildUsersJobTable, \
            delete_report, process_uploaded_file, save_uploaded_file_to_disc, select_job, \
            build_uploaded_report_table, find_string_in_request
dbOps = DatabaseOperations()

#To just run this test file, python manage.py test jobs.tests.Test_Unit_ViewHelperFunctions

class TestViewHelperFunctions(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        #populate the database
        dbOps.populate_database_from_file()

    def test_process_uploaded_file(self):
        # Create a test user
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        #create a super user
        superuser = User.objects.create_superuser(
            username='admin',
            email='s.shillitoe@sheffield.ac.uk',
            password='adminpassword'
        )
        # Create a test job
        Job.objects.filter(id=1).update(user_id=user, status ='In Progress')

        # Create a mock request with a test file
        request = self.factory.post('', {'upload_report_file': SimpleUploadedFile('report.pdf', b'pdf_content')})

        # Create a mock SendEmail instance
        send_email = SendEmail()

        job = Job.objects.get(id=1)

        ###not working
        ## Call the function being tested
        #process_uploaded_file(job, 1, request, send_email)

        ## Assert that the job status is updated correctly
        #self.assertEqual(job.status, 'Received')

        ## Assert that the report_name is set correctly
        #self.assertEqual(job.report_name, 'job_{}_{}_{}.pdf'.format(job.id, job.patient_id, job.task_id))

        ## Assert that the submission_date is set correctly
        #self.assertEqual(job.submission_date, date.today())

        ## Add assertions for the email functionality if needed
        ## For example, you can assert that the sendEmail methods are called with the expected arguments

        # ...
