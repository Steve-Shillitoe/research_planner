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



class CustomUserCreationForm(UserCreationForm):
    #This class inherits from UserCreationForm, adds an email field and 
	#sends a welcome email to the new user when they are added to the database.
	
    # Customize the username field
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'class': 'custom-class'})
    )

    # Customize the email field
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'custom-class'})
    )
    first_name = forms.CharField(label="First Name",  
			      widget=forms.TextInput(attrs={'class': 'custom-class'}))
				       
    last_name = forms.CharField(label="Last Name",  
			      widget=forms.TextInput(attrs={'class': 'custom-class'}))

    # Customize the password fields (password1 and password2)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'custom-class'}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'custom-class'}),
    )

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
