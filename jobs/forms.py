"""
This module defines structured and validated forms for collecting user input.
Forms in Django come with built-in validation capabilities. 
You can specify validation rules for each field, such as required fields, 
maximum length, numeric constraints, and custom validations. 
When a user submits a form, Django automatically validates the input based 
on these rules and provides error messages if the data is invalid.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .modules.SendEmail import SendEmail

#Log in form
class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))


#Form for user self-registration
class NewUserForm(UserCreationForm):
	#This class inherits from UserCreationForm, adds an email field and 
	#sends a welcome email to the new user when they are added to the database.
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "first_name", "last_name", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
			#send the new user a welcome email
			sendEmail = SendEmail()
			sendEmail.new_user_email(self.cleaned_data['first_name'], 
							self.cleaned_data["username"], 
							self.cleaned_data['email'])
		return user