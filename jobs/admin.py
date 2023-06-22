"""
This module allows you to configure and customise the Django admin interface, 
which is available to superusers only via the Admin link at the top of the home page. 

The Django admin is a powerful built-in feature that allows you to manage and
manipulate data stored in your models via an intuitive web-based interface.

Below it is used for model registration.
Once the required modules are imported, they are registered using the admin.site.register() method. 
By registering a model, it becomes accessible and editable through the Django admin interface.
"""

from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from .models import Job, Patient, Task, Configuration

# Register your models here.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("task_name", "repetitions")
    #list_filter = ('task_name', )
    #exclude = ('field name', )
    #def show_type(self, obj):
    #    from django.utils.html import format_html
    #    return format_html("<b><i>{}</i></b>", Dataset.type.value_to_string(obj))
    #show_type.short_description = "Dataset Type"

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass
    #use default setup


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    #When the Jobs link is clicked, field labels in list_display are displayed
    #ordered by the values of the fields in ordering
    list_display = ("id","patient_id", "task_id", "repetition_num", "status")
    ordering =("id","patient_id", "task_id", "repetition_num")


@admin.register(Configuration)
class AdminConfiguration(admin.ModelAdmin):
       #Rather than use the default widgets, 
       #override the main_title field with a textinput widget and
       #override the main_intro & indiv_intro fields with textarea widgets.
       #All other fields will use the defaults.
       formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'50'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})}
    }