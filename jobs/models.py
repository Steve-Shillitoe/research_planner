"""
Definition of models.
Each class represents a database table.  
Each class is 'migrated' to the database 
and a table constructed using the class definition.
"""

from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    """Model representing a dataset."""
    TYPE_OF_DATASET = [
        ('QC', 'QC'),
        ('seg', 'Segmentation'),] 
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    name = models.CharField('Dataset Name',primary_key=True, max_length=30, blank=False)
    type = models.CharField('Dataset Type', max_length=3, blank=False,  choices=TYPE_OF_DATASET)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}' # This always returns string even if self.name is None


class Patient(models.Model):
    """Model representing a patient."""
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    id = models.CharField(primary_key=True, max_length=12, blank=False)
    QC_dataset_name = models.OneToOneField('Dataset', on_delete=models.PROTECT, related_name='+',)
    Seg_dataset_name = models.OneToOneField('Dataset', on_delete=models.PROTECT, related_name='+',)

    def __str__(self):
        """String for representing the Model object."""
        return f'{ self.id}'


class Job(models.Model):
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    TYPE_OF_STATUS = [('Available', 'Available'),
        ('Not Available', 'Not Available'),
        ('In Progress', 'In Progress'),
        ('Received', 'Received'),
        ('Approved', 'Approved'), ]
    YES_NO = [('yes','yes'), ('no','no')]
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    patient_id = models.ForeignKey('Patient', on_delete=models.PROTECT)
    dataset_name = models.ForeignKey('Dataset', on_delete=models.PROTECT)
    status = models.CharField(max_length=13, choices=TYPE_OF_STATUS, default='Available')
    report_name = models.CharField(max_length=52, null=True, blank=True)
    #report_file = models.FileField(upload_to ='reports/', null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    deadline_date = models.DateField(blank=True, null=True)
    submission_date = models.DateField(blank=True, null=True)
    reminder_sent = models.CharField(max_length=3, choices=YES_NO, default='no', blank=False, null=False)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}, {self.patient_id}, {self.dataset_name}'

    class Meta:
        ordering = ['patient_id', 'dataset_name']
        verbose_name_plural = "Jobs"


class Configuration(models.Model):
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    id = models.AutoField(primary_key=True)
    main_title = models.CharField(max_length=50, blank=False, null=False, default="string stored in database")
    main_intro =  models.TextField(blank=True, null=True, default="")
    indiv_intro = models.TextField(blank=True, null=True, default="")
    
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.main_title}'

    class Meta:
        verbose_name_plural = 'Interface Configuration'

     