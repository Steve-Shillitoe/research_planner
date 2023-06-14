from jobs.modules.SendEmail import SendEmail
sendEmail = SendEmail()
from django.core import mail
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from jobs.models import Job
from jobs.views import home 

class DeadlineReminderEmailTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_deadline_reminder_email(self):
        # Create a test user
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

        # Create a test job with tomorrow's deadline
        tomorrow = date.today() + timedelta(days=1)
        job = Job.objects.create(deadline_date=tomorrow, user=user, patient_id=1, task_id=1)

        # Create a mock request
        request = self.factory.get('/dummy-url')

        # Call the view function that handles the request
        response = MyView.as_view()(request)

        # Assert that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        # Assert the email content
        self.assertEqual(email.subject, 'Your Job report deadline reminder')
        self.assertEqual(email.to, ['test@example.com'])
        self.assertIn('The report for job', email.body)
        self.assertIn('is due to be submitted tomorrow.', email.body)

        # Assert that the reminder_sent field is updated
        job.refresh_from_db()
        self.assertEqual(job.reminder_sent, 'yes')
