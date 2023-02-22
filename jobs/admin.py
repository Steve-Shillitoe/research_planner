from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from .models import Job, Dataset, Patient,  Configuration

# Register your models here.
@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    list_filter = ('type', )
    #exclude = ('field name', )
    
    #def show_type(self, obj):
    #    from django.utils.html import format_html
    #    return format_html("<b><i>{}</i></b>", Dataset.type.value_to_string(obj))

    #show_type.short_description = "Dataset Type"

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "QC_dataset_name", "Seg_dataset_name")

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id","patient_id", "dataset_name", "status")
    ordering =("id","patient_id", "dataset_name")


@admin.register(Configuration)
class AdminConfiguration(admin.ModelAdmin):
       formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'50'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    } 
#Unregister models here
#admin.site.unregister(Group)