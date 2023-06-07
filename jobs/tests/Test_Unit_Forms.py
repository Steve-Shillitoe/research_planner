from django.test import TestCase
from django.contrib.auth.models import User
from jobs.models import Configuration
from jobs.forms import NewUserForm

class NewUserFormTest(TestCase):

    def test_save(self):
        Configuration.objects.create(
            main_title="Test Title",
            main_intro="Test Main Intro",
            indiv_intro="Test Individual Intro",
            number_days_to_complete=5,
            max_num_jobs=3
        )
        form_data = {
            'username': 'testuser',
            'email': 's.shillitoe@sheffield.ac.uk',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword1234',
            'password2': 'testpassword1234'
        }
        
        form = NewUserForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Call the save method
        user = form.save()

        # Perform assertions on the saved user
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 's.shillitoe@sheffield.ac.uk')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')


    def test_save_no_data(self):
        form_data = {}
        
        form = NewUserForm(data=form_data)
        self.assertFalse(form.is_valid())


    def test_save_invalid_email(self):
        form_data = {
            'username': 'testuser',
            'email': 'testexample.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword1234',
            'password2': 'testpassword1234'
        }
        
        form = NewUserForm(data=form_data)
        self.assertFalse(form.is_valid())  
        

    def test_save_invalid_password(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'password',
            'password2': 'password'
        }
        
        form = NewUserForm(data=form_data)
        self.assertFalse(form.is_valid())  


