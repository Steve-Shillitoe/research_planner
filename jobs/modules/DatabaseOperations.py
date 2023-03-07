from ..models import Job, Task, Patient, Configuration
from .SendEmail import SendEmail
from django.contrib.auth.models import User
from datetime import date
from django.conf import settings
from django.db import connection
import os

class DatabaseOperations:
    """Functions that directly operate on the database"""

    def populate_Configuration_table(self):
        if Configuration.objects.filter(id=1).first() is None:
           #empty table, so populate it
           first_table_row = Configuration(main_title = 'initial value',
            main_intro = 'initial value',
            indiv_intro = 'initial value')
           first_table_row.save()


    def deadline_passed_set_job_available(self):
        """Database function"""
        jobs = Job.objects.filter(deadline_date__lt=date.today())
        jobs.update(status ='Available',
                    user_id = None,
                    start_date = None,
                    deadline_date = None,
                    reminder_sent= 'no')


    def clear_database(self):
        """Delete all data in the database to create empty tables"""
        Job.objects.all().delete()
        Patient.objects.all().delete()
        Task.objects.all().delete()
        #Reset the auto-increment primary key id field back to an initial value of 1
        cursor = connection.cursor()
        cursor.execute("ALTER Sequence jobs_job_id_seq RESTART with 1;")
        cursor.execute("ALTER Sequence jobs_task_task_id_seq RESTART with 1;")
        connection.commit()
        connection.close()


    def populate_task_table(self, wb):
        """Populate the Task table using the data in an Excel spreadsheet"""
        wsTask = wb["Tasks"]
        # iterating over the rows and
        # getting value from each cell in row
        for row_num, row in enumerate(wsTask.iter_rows()):
            #Ignore header row
            if row_num > 0:
                new_task_name =row[0].value
                if row[1].value is None:
                    new_repetitions= 1
                else:
                    new_repetitions=row[1].value

                task, _ = Task.objects.update_or_create(task_name=new_task_name, repetitions=new_repetitions)
                task.save()


    def populate_patient_table(self, wb):
        """Populate the Patient table using the data in an Excel spreadsheet"""
        wsPatient = wb["Patients"]
        # iterating over the rows and
        # getting value from each cell in row
        for row_num, row in enumerate(wsPatient.iter_rows()):
            #Ignore header row
            if row_num > 0:
                patient, _ = Patient.objects.update_or_create(patient_id =row[0].value)
                patient.save()


    def populate_job_table(self):
        """Populate the Job table using the data in the Task & Patient tables"""
        patient_list = Patient.objects.all()
        task_list = Task.objects.all()
        task_counter = 1
        for patient in patient_list:
            for task in task_list:
                num_repetions = task.repetitions
                for i in range(num_repetions):
                    job = Job(patient_id=patient, task_id=task, repetition_num=i+1)
                    job.save()

    