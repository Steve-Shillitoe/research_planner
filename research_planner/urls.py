"""
Definition of urls for iBeatStudyWebApp.
"""

from datetime import datetime
from django.urls import path, re_path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from jobs import forms, views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve 
# Use include() to add URLS from the  authentication system
from django.urls import include

admin.site.site_header = "Research Planner Administration"
admin.site.site_title = "Research Planner Admin"
admin.site.index_title = "Welcome to the Research Planner Administration Page"

      
urlpatterns = [
    path('download_report/', views.download_report, name='download_report'),
    path('download_jobs', views.download_jobs, name='download_jobs'),
    path('dbAdmin/', views.dbAdmin, name='dbAdmin'),
    path('', views.home, name='home'),
    path("register", views.register_request, name="register"),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='jobs/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    #path('accounts/', include('django.contrib.auth.urls')),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='jobs/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="jobs/password/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='jobs/password/password_reset_complete.html'), name='password_reset_complete'),      
    path("password_reset", views.password_reset_request, name="password_reset"),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT})
]
#Add Django site authentication urls (for login, logout, password management)
#urlpatterns += [
 #   path('accounts/', include('django.contrib.auth.urls')),]

#if settings.DEBUG:

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
