from ..models import Job, Task, Patient, Configuration
from .SendEmail import SendEmail
from django.contrib.auth.models import User
from datetime import date
from django.conf import settings
#import sqlite3
import os

class DatabaseOperations:
    """description of class"""

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
        """Build Database function"""
        Job.objects.all().delete()
        Patient.objects.all().delete()
        Task.objects.all().delete()


    def populate_task_table(self, wb):
        """Populate the Task table using the data in an Excel spreadsheet"""
        wsTask = wb["Tasks"]
        # iterating over the rows and
        # getting value from each cell in row
        for row_num, row in enumerate(wsTask.iter_rows()):
            #Ignore header row
            if row_num > 0:
                task, _ = Task.objects.update_or_create(task_name =row[0].value, repetitions=row[1].value)
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


    #def _reset_job_id_in_jobs_table(self):
    #    """Build Database function"""
    #    con = sqlite3.connect(os.path.join(settings.BASE_DIR, 'db.sqlite3'))
    #    cur = con.cursor()
    #    cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE sqlite_sequence.name = 'app_job'")
    #    con.commit()
    #    con.close()


    def populate_job_table(self):
        """Populate the Job table using the data in the Task & Patient tables"""
        #self._reset_job_id_in_jobs_table()
        patient_list = Patient.objects.all()
        task_list = Task.objects.all()
        task_counter = 1
        for patient in patient_list:
            for task in task_list:
                num_repetions = task.repetitions
                for i in range(num_repetions):
                    job = Job(patient_id=patient, task_name=task, repetition_num=i+1)
                    job.save()

    