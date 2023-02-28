from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from .models import Job, Patient, Task, Configuration

# Register your models here.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("task_name", "repetitions")
    list_filter = ('task_name', )
    #exclude = ('field name', )
    
    #def show_type(self, obj):
    #    from django.utils.html import format_html
    #    return format_html("<b><i>{}</i></b>", Dataset.type.value_to_string(obj))

    #show_type.short_description = "Dataset Type"

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass
    #list_display = ("patient_id")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id","patient_id", "task_name", "repetition_num", "status")
    ordering =("id","patient_id", "task_name", "repetition_num")


@admin.register(Configuration)
class AdminConfiguration(admin.ModelAdmin):
       formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'50'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    } 
#Unregister models here
#admin.site.unregister(Group)