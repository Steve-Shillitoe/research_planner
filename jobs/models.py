"""
Definition of models.
Each class represents a database table.  
Each class is 'migrated' to the database 
and a table constructed using the class definition.
"""

from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    """Model representing a task performed on a dataset."""
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=50, blank=False, null=False)
    repetitions = models.IntegerField(default=1)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.task_name}' # This always returns string even if self.name is None


class Patient(models.Model):
    """Model representing a patient."""
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    patient_id = models.CharField(primary_key=True, max_length=30, default="patient_1")

    def __str__(self):
        """String for representing the Model object."""
        return f'{ self.patient_id}'


class Job(models.Model):
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    TYPE_OF_STATUS = [('Available', 'Available'),
        ('Not Available', 'Not Available'),
        ('In Progress', 'In Progress'),
        ('Received', 'Received'),
        ('Approved', 'Approved')]
    YES_NO = [('yes','yes'), ('no','no')]
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    patient_id = models.ForeignKey('Patient', on_delete=models.PROTECT)
    task_id = models.ForeignKey('Task', on_delete=models.PROTECT, null=True, blank=True)
    repetition_num = models.IntegerField(default=1)
    status = models.CharField(max_length=13, choices=TYPE_OF_STATUS, default='Available')
    report_name = models.CharField(max_length=52, null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    deadline_date = models.DateField(blank=True, null=True)
    submission_date = models.DateField(blank=True, null=True)
    reminder_sent = models.CharField(max_length=3, choices=YES_NO, default='no', blank=False, null=False)

    def __str__(self):
        """String for representing the Model object."""
        #task = Task.objects.get(task_id=self.task_id)
        return f'{self.id}, {self.patient_id}, {self.task_id}, {self.repetition_num}'

    class Meta:
        ordering = ['patient_id', 'task_id']
        verbose_name_plural = "Jobs"


class Configuration(models.Model):
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    id = models.AutoField(primary_key=True)
    main_title = models.CharField(max_length=50, blank=False, null=False, default="string stored in database")
    main_intro =  models.TextField(blank=True, null=True, default="")
    indiv_intro = models.TextField(blank=True, null=True, default="")
    number_days_to_complete = models.IntegerField(default=7, verbose_name="Number of days to complete a job")
    max_num_jobs = models.IntegerField(default=4, verbose_name="Maximum number of active jobs per user")
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.main_title}'

    class Meta:
        verbose_name_plural = 'Configuration'

     