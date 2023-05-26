import django
from django.test import LiveServerTestCase, RequestFactory, TestCase, Client
from django.core.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User, AnonymousUser
from django.urls import resolve, reverse
from django.http import HttpRequest
from jobs import views
from jobs.views import home, dbAdmin
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from django.contrib.admin.sites import AdminSite
from django.contrib.admin import site as admin_site
from django.contrib.admin.views import main as admin_views


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


    def tearDown(self):
        self.browser.quit()

    def test_download_report_url(self):
        url = reverse('download_report')
        self.assertEqual(resolve(url).func, views.download_report)

    def test_download_jobs_url(self):
        url = reverse('download_jobs')
        self.assertEqual(resolve(url).func, views.download_jobs)

    def test_dbAdmin_urls(self):
        url = reverse('dbAdmin')
        self.assertEqual(resolve(url).func, views.dbAdmin)

    def test_root_url_resolves_to_home(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_home_url_is_resolved(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, home)

    def test_register_url(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, views.register_request)
    
    def test_contact_url(self):
        url = reverse('contact')
        self.assertEqual(resolve(url).func, views.contact)
    
    def test_about_url(self):
        url = reverse('about')
        self.assertEqual(resolve(url).func, views.about)


    def test_login_url(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, LoginView)

    def test_logout_url(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func.view_class, auth_views.LogoutView)
    

    def test_admin_url(self):
        url = reverse('admin:index')
        resolver = resolve(url)
        self.assertEqual(resolver.view_name, 'admin:index')

    
    def test_password_reset_done_url(self):
        url = reverse('password_reset_done')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetDoneView)
    
    def test_password_reset_confirm_url(self):
        url = reverse('password_reset_confirm', args=['uidb64', 'token'])
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetConfirmView)
    
    def test_password_reset_complete_url(self):
        url = reverse('password_reset_complete')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetCompleteView)
    
    def test_password_reset_url(self):
        url = reverse('password_reset')
        self.assertEqual(resolve(url).func, views.password_reset_request)