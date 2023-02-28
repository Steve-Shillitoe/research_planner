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
        Dataset.objects.all().delete()


    def populate_user_table(self, wb):
        """Build Database function"""
        sendEmail = SendEmail()
        wsDataset = wb["User"]
        # iterating over the rows and
        # getting value from each cell in row
        for row_num, row in enumerate(wsDataset.iter_rows()):
            #ignore header row
            if row_num > 0:
                user_name = row[0].value
                #Only create a User if they do not already exist
                if  User.objects.filter(username=user_name).count() == 0:
                    first_name = row[1].value
                    last_name = row[2].value
                    password = row[3].value
                    email = row[4].value
                    email_message = "Hi " + first_name + ",\n" + \
                                     "Welcome to the iBeat Study. \n" + \
                            "Your username is " + user_name + " and your password is " + password 
                    user = User.objects.create_user(user_name, email, password)   
                    user.first_name = first_name
                    user.last_name = last_name
                    user.is_active = True
                    user.save()
                    #Send login information to the user
                    sendEmail.send_email_new_user(email, email_message)


    def populate_dataset_table(self, wb):
        """Build Database function"""
        wsDataset = wb["Dataset"]
        # iterating over the rows and
        # getting value from each cell in row
        for row_num, row in enumerate(wsDataset.iter_rows()):
            #Ignore header row
            if row_num > 0:
                pass
               # dataset, _ = Dataset.objects.update_or_create(name =row[0].value, type=row[1].value)
               #  dataset.save()


    def populate_patient_table(self, wb):
        """Build Database function"""
        wsPatient = wb["Patient"]
        # iterating over the rows and
        # getting value from each cell in row
        for row_num, row in enumerate(wsPatient.iter_rows()):
            #Ignore header row
            if row_num > 0:
                QC_Dataset = Dataset.objects.get(name=row[1].value)
                Seg_Dataset = Dataset.objects.get(name=row[2].value)
                patient, _ = Patient.objects.update_or_create(id =row[0].value, QC_dataset_name = QC_Dataset, Seg_dataset_name = Seg_Dataset)
                patient.save()


    #def _reset_job_id_in_jobs_table(self):
    #    """Build Database function"""
    #    con = sqlite3.connect(os.path.join(settings.BASE_DIR, 'db.sqlite3'))
    #    cur = con.cursor()
    #    cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE sqlite_sequence.name = 'app_job'")
    #    con.commit()
    #    con.close()


    def populate_job_table(self):
        """Build Database function"""
        #self._reset_job_id_in_jobs_table()
        patient_list = Patient.objects.all()
        for patient in patient_list:
            patientID = Patient.objects.get(id=patient.id)
            QCDataset = Dataset.objects.get(name=patient.QC_dataset_name )
            SegDataset = Dataset.objects.get(name=patient.Seg_dataset_name)
            if not Job.objects.filter(patient_id=patientID, dataset_name=QCDataset).exists():
                job = Job(patient_id=patientID, dataset_name=QCDataset)
                job.save()
                job = Job(patient_id=patientID, dataset_name=QCDataset)
                job.save()
            if not Job.objects.filter(patient_id=patientID, dataset_name=SegDataset).exists():
                job = Job(patient_id=patientID, dataset_name=SegDataset)
                job.save()
                job = Job(patient_id=patientID, dataset_name=SegDataset)
                job.save()

    