from jobs.modules.SendEmail import SendEmail
sendEmail = SendEmail()
from jobs.modules.DatabaseOperations import DatabaseOperations
dbOps = DatabaseOperations()
from django.core import mail
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from jobs.models import Job, Configuration
from datetime import date, timedelta

#To just run this test file, python manage.py test jobs.tests.Test_Unit_SendEmail

class SendEmailTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        #populate the database
        dbOps.populate_database_from_file()
        # Create a test user
        self.user1 = User.objects.create_user(username='testuser', email='test@sheffield.ac.uk', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', email='test2@sheffield.ac.uk', password='testpassword2')
        
        Configuration.objects.create(
            main_title="Test Title",
            main_intro="Test Main Intro",
            indiv_intro="Test Individual Intro",
            number_days_to_complete=5,
            max_num_jobs=3
        )

    def test_deadline_reminder_email(self):
        # Create a test job with a deadline tomorrow
        tomorrow = date.today() + timedelta(days=1)
        Job.objects.filter(id=1).update(deadline_date=tomorrow, user_id=self.user1, status ='In Progress')
        job = Job.objects.get(id=1)
        self.assertEqual(job.reminder_sent, 'no')

        # Create a mock request
        request = self.factory.get('') #home url

        # Call the view function that handles the request
        sendEmail.deadline_reminder_email(request)

        # Assert that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        # Assert the email content
        self.assertEqual(email.subject, 'Test Title Job report deadline reminder')
        self.assertEqual(email.to, ['test@sheffield.ac.uk'])
        self.assertIn('The report for job 1', email.body)
        self.assertIn('is due to be submitted tomorrow.', email.body)

        # Assert that the reminder_sent field is updated
        job = Job.objects.get(id=1)
        self.assertEqual(job.reminder_sent, 'yes')


    def test_deadline_reminder_emails(self):
        # Create a test job with a deadline tomorrow
        tomorrow = date.today() + timedelta(days=1)
        print (Job.objects.count())
        #Job.objects.filter(id=2).update(deadline_date=tomorrow, user_id=self.user1, status ='In Progress')
        #job2 = Job.objects.get(id=2)
        #self.assertEqual(job2.reminder_sent, 'no')
        #Job.objects.filter(id=4).update(deadline_date=tomorrow, user_id=self.user2, status ='In Progress')
        #job4 = Job.objects.get(id=4)
        #self.assertEqual(job4.reminder_sent, 'no')