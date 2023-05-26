import django
from django.test import LiveServerTestCase, RequestFactory, TestCase, Client
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User, AnonymousUser
from django.urls import resolve, reverse
from django.http import HttpRequest
from jobs.views import home, dbAdmin
from django.contrib.auth import login

class TestUrls(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='s.shillitoe@sheffield.ac.uk',
            password='adminpassword'
        )

    def test_root_url_resolves_to_home(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_home_url_is_resolved(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, home)
