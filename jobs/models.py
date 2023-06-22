"""
Definition of models using Django's ORM (Object-Relational Mapping) to interact with the database.
Each class represents a database table.  
Each class is 'migrated' to the database and a table constructed using the class definition.

Whenever one of the model classes is changed, open a command prompt in the root of this project and
run,
        python manage.py makemigration

This command analyzes your models and creates migration files in the migrations directory 
of each app involved in the changes. 
The migration files contain Python code that represents the changes to be made 
in the database schema.

If the above command ran without generating errors, then run,
        python manage.py migrate

It will create new tables, modify existing tables, and apply any necessary data transformations 
to keep the database schema in sync with your models.
"""

from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    """Model representing a task performed on a dataset. It defines the Task table in the database"""
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=50, blank=False, null=False)
    repetitions = models.IntegerField(default=1)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.task_name}' # This always returns string even if self.task_name is None


class Patient(models.Model):
    """Model representing a patient. It defines the Patient table in the database."""
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    patient_id = models.CharField(primary_key=True, max_length=30, default="patient_1")

    def __str__(self):
        """String for representing the Model object."""
        return f'{ self.patient_id}'


class Job(models.Model):
    """
    Model representing a job, the action of a task on a patient's data. 
    It defines the Job table in the database.
    """
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    TYPE_OF_STATUS = [('Available', 'Available'),
        ('Not Available', 'Not Available'),
        ('In Progress', 'In Progress'),
        ('Received', 'Received'),
        ('Approved', 'Approved')]
    YES_NO = [('yes','yes'), ('no','no')]
    id = models.AutoField(primary_key=True)
    #the link to the user in the User table
    user_id = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    #the link to the patient in the Patient table 
    patient_id = models.ForeignKey('Patient', on_delete=models.PROTECT)
    #the link to the task in the Task table
    task_id = models.ForeignKey('Task', on_delete=models.PROTECT, null=True, blank=True)
    repetition_num = models.IntegerField(default=1) #Number of times a task should be performed
    status = models.CharField(max_length=13, choices=TYPE_OF_STATUS, default='Available')
    report_name = models.CharField(max_length=52, null=True, blank=True)
    start_date = models.DateField(blank=True, null=True) 
    deadline_date = models.DateField(blank=True, null=True)
    submission_date = models.DateField(blank=True, null=True)
    reminder_sent = models.CharField(max_length=3, choices=YES_NO, default='no', blank=False, null=False)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}, {self.patient_id}, {self.task_id}, {self.repetition_num}'

    class Meta:
        ordering = ['patient_id', 'task_id']
        verbose_name_plural = "Jobs"  #text forming link on the Admin page

class Configuration(models.Model):
    """
    Model defining the Configuration table, which allows the application user to configure 
        text on the home page,
        number of days to complete a task,
        maximum number of 'In Progress' task a user may have at one time.
    """
    objects = models.Manager() #Not necessary but without it this function fails PyLint
    id = models.AutoField(primary_key=True)
    main_title = models.CharField(max_length=50, blank=False, null=False, default="string stored in database", verbose_name="Project title")
    main_intro =  models.TextField(blank=True, null=True, default="", verbose_name="Main table text")
    indiv_intro = models.TextField(blank=True, null=True, default="", verbose_name="Individual user table text")
    number_days_to_complete = models.IntegerField(default=7, verbose_name="Number of days to complete a job")
    max_num_jobs = models.IntegerField(default=4, verbose_name="Maximum number of active jobs per user")
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.main_title}'

    class Meta:
        verbose_name_plural = 'Configuration'

     