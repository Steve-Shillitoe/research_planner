"""
Definition of views.
"""
import mimetypes
from datetime import date
from datetime import datetime
from datetime import timedelta
from wsgiref.util import request_uri
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token 
from django.views.decorators.csrf import csrf_protect 
from django.conf import settings
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages
import openpyxl
import xlwt
from xlwt import Workbook
import os
from pathlib import Path
from jobs.models import Job, Patient, Task, Configuration
from django.db import connection
from .modules.SendEmail import SendEmail
import environ
env = environ.Env()
environ.Env.read_env()
from .modules.DatabaseOperations import DatabaseOperations
dbOps = DatabaseOperations()

#Link status to a colour
TYPE_OF_STATUS = {'Available': "green",'Not Available': "red",'In Progress': "yellow",'Received': "Magenta",
                    'Approved': "SkyBlue" }

def password_reset_request(request):
    msg=""
    password_reset_form = PasswordResetForm()
    if request.method == "POST":
        if request.POST['email']:
            data = request.POST['email'].strip()
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists() == False:
                msg="No user found who is associated with this email address"
            else:
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "jobs/password/password_reset_email.txt"
                    c = {"email":user.email,
					'domain':env('DOMAIN'),
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http'}
                    email = render_to_string(email_template_name, c)
                    try:    
                        send_mail(subject, email, settings.EMAIL_HOST_USER,[user.email], fail_silently=False)
                        return redirect ("/password_reset/done/")
                    except BadHeaderError:
                        return HttpResponse("Could not send an email to the user due to an invalid email header found.")
                    except SMTPException as e:
                        return HttpResponse("Could not send an email to the user due to {} error".format(str(e)))
                    except Exception as e:
                        return HttpResponse("Could not send an email to the user due to {} error".format(str(e)))
                       
        else:
            print("Form not valid")
            msg="Entered email is not valid"
    return render(request=request, template_name="jobs/password/password_reset.html",
                  context={'main_title':Configuration.objects.get(id=1).main_title,
                           'email_not_found_db':msg,
                           'password_reset_form':password_reset_form})

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")
        else:
            form = NewUserForm()
            form.fields['username'].initial = request.POST['username']
            form.fields['email'].initial = request.POST['email']
            form.fields['first_name'].initial = request.POST['first_name']
            form.fields['last_name'].initial = request.POST['last_name']
            messages.error(request, "Unsuccessful registration. Invalid password.")
    else:
        form = NewUserForm()
    return render (request=request, template_name="jobs/register.html",
                   context={'main_title':Configuration.objects.get(id=1).main_title,
                            'register_form':form})


@csrf_protect #Require Cross Site Request Forgery protection
@login_required   #If the user is not logged in, redirect to Login form
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    dbOps.populate_Configuration_table()
    #if job report deadline passed, make the job available again
    dbOps.deadline_passed_set_job_available()
    #Send deadline one day away reminders
    sendEmail = SendEmail()
    sendEmail.deadline_reminder_email()

    FourJobsWarning = ""
    SameJobWarning = ""
    if request.method == 'POST':
        jobId = request.POST['jobId']
        if "select_job" in request.POST:
            #Update main jobs table. Available button clicked. Job assigned to a student
            #and status changed to 'In Progress'
            FourJobsWarning, SameJobWarning =  select_job(request, jobId, sendEmail)
        elif  'cancel' in request.POST:
            #Update individual job table. Cancel button clicked. Setting dates=None, gives them the value of Null
            Job.objects.filter(id=jobId).update(status ='Available', 
                               user_id_id = "", start_date =None, deadline_date =None)
        elif 'upload_report' in request.POST:
            job = Job.objects.get(id=jobId)
            if job.status == "In Progress":
                #The above check prevents a report being uploaded twice by
                #refreshing the screen or using the back button
                uploaded_report_file = request.FILES['upload_report_file']
                #Make a standard format report name
                new_file_name = "job_" + str(jobId) + "_" + str(job.patient_id) + "_" + str(job.task_id)
                new_file_name = new_file_name.replace(" ", "")
                #Get file extension of uploaded report
                _, file_extension = os.path.splitext(uploaded_report_file.name)
                #Make new report name with original file extension
                new_file_name = new_file_name + file_extension
                #Save uploaded report to \media\reports in the web app folder structure
                save_uploaded_file_to_disc(uploaded_report_file,  new_file_name)
                Job.objects.filter(id=jobId).update(status ='Received', report_name=new_file_name, submission_date=date.today())
                #Email admins about uploaded report
                sendEmail.report_uploaded_admins_email(new_file_name, request)
                #Email user about thier uploaded report
                sendEmail.report_uploaded_user_email(request, job)
            
    return render(
        request,
        template_name =  'jobs/index.html',
        context={'main_title':Configuration.objects.get(id=1).main_title,
                 'main_intro':Configuration.objects.get(id=1).main_intro,
                 'indiv_intro':Configuration.objects.get(id=1).indiv_intro,
                 'max_jobs':Configuration.objects.get(id=1).max_num_jobs,
                 'NumJobs':Job.objects.all().count(),
                 'JobTable': buildMainJobsTable(request),
                 'UsersJobTable': buildUsersJobTable(request),
                'FourJobsWarning': FourJobsWarning,
                'SameJobWarning': SameJobWarning}
                )


def save_uploaded_file_to_disc(file, new_file_name):  
    """File handling function"""
    try:
        new_file_path = settings.MEDIA_ROOT + '/reports/'+ new_file_name
        with open(new_file_path, 'wb+') as destination:  
            for chunk in file.chunks():  
                destination.write(chunk)
    except FileNotFoundError:
        print("{} does not exist".format(new_file_path))
    except Exception as e:
        print("Error: " + str(e))


def select_job(request, jobId, sendEmail):
    fourJobsWarning = ""
    sameJobWarning = ""
    jobs = Job.objects.filter(user_id = request.user, status ='In Progress')
    numJobs = len(jobs)
    #Make sure this student has not already selected the same subject and task
    job = Job.objects.get(id=jobId)
    same_patient_task_job = Job.objects.filter(user_id = request.user, 
                            task_id = job.task_id, patient_id = job.patient_id)
    if same_patient_task_job.exists():
        sameJobWarning = "You may only select the same subject-task combination once."
    #check student does not already have the maximum number of jobs assigned to them
    max_num_jobs = Configuration.objects.get(id=1).max_num_jobs
    if numJobs < max_num_jobs:
        deadline_date = date.today() + timedelta(Configuration.objects.get(id=1).number_days_to_complete)
        Job.objects.filter(id=jobId).update(status ='In Progress', 
                                            user_id = request.user,
                                            start_date = date.today(),
                                            deadline_date = deadline_date)
        sendEmail.job_allocation_email(jobId, deadline_date, request)
    if numJobs == max_num_jobs:
        fourJobsWarning = "You may only have a maximum of {} jobs in progress.".format(max_num_jobs)
    return  fourJobsWarning, sameJobWarning 


def buildMainJobsTable(request):
    """Builds the main HTML table of jobs for display on the home page"""
    strRow = ""
    strPatient = ""
    strRows = ""
    patients = Patient.objects.all()
    if patients:
        #the database is populated, so build the jobs table
        task_list_from_jobs = Job.objects.filter(patient_id=patients[0].patient_id)
        #Build colgroups
        task_list = Task.objects.all()
        strTable = "<table cellspacing=3 bgcolor=#000000>"
        strColGroup = "<colgroup><col span=1 style=background-color:#66ccfd>"
        for i, task in enumerate(task_list):
            num_cols = str(task.repetitions)
            if (i % 2) == 0:
                strColGroup += "<col span=" + chr(34) + num_cols + chr(34) + "style=" + chr(34) + "background-color:#0099e6" + chr(34) + ">"
            else:
                strColGroup += "<col span=" + chr(34) + num_cols + chr(34) + "style=" + chr(34) + "background-color:#66ccff" + chr(34) + ">"
        strColGroup += "</colgroup>"
        #Build table header row
        strHeader = "<TR><TH>Subject</TH>"
        for task in task_list_from_jobs:
            strHeader += "<TH>" + str(task.task_id) + "</TH>"
        strHeader += "</TR>"
        for patient in patients:
            strPatient = "\n<TR>\n<TD>" + str(patient.patient_id) + "</TD>"
            strStatus = ""  
            jobs = Job.objects.filter(patient_id=patient.patient_id).order_by('id')
            for job in jobs:
                if job.status == "Available":
                    csrf_token = get_token(request)
                    csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                    strStatus += "<td>" + \
                        "<form method="+ chr(34) +"post"+ chr(34) +">"  + csrf_token_html + \
                        "<input type="+ chr(34) +"hidden" + chr(34) + "id=" + chr(34) + \
                        "jobId" + chr(34) + "name=" + chr(34) + "jobId" + chr(34) + \
                        "value="  + chr(34) + str(job.id) + chr(34) +"/>" +\
                        "<input type="+ chr(34) + "submit" + chr(34) + " name=" + chr(34) + "select_job" + chr(34) +\
                        " title=" + chr(34) + "Click to select this job" + chr(34) + \
                        " value="+ chr(34) + "AVAILABLE"+ chr(34) + "></form></td>" 
                else:
                    strStatus += "<TD bgcolor=" + TYPE_OF_STATUS[job.status] + ">" + job.status + "</TD>"
            strRow = strPatient + strStatus + "</TR>"
            #strStatus = ""
            strRows +=strRow 
        returnString = strTable + "\n" + strColGroup + "\n" + strHeader + "\n" + strRows + "\n" + "</TABLE>"
    else:
        returnString = "<p>There is no data in the database"
    return returnString


def buildUsersJobTable(request):
    """
    Builds a HTML table of the jobs the user has assigned to themselves."""
    try:
        strRows = ""
        if request.user:
            jobs = Job.objects.filter(user_id=request.user).order_by('patient_id')
            if jobs:
                strTable = "<table cellspacing=" + chr(34) + "3" + chr(34) + "><tr><th>Subject</th><th>Task</th>" \
                    + "<th>Job Status</th><th>Deadline Date</th><th></th><th></th><th>Submission Date</th><th>Report</th></tr>"
                for job in jobs:
                        strSubject = "<td>" + str(job.patient_id) + "</td>"
                        strTask = "<td>" + str(job. task_id) + "</td>"
                        strStatus = "<TD bgcolor=" + TYPE_OF_STATUS[job.status] + ">" + str(job.status) + "</TD>"
    
                        if job.status == "In Progress": 
                            strHiddenJobID = "<input type="+ chr(34) +"hidden" + chr(34) + "id=" + chr(34) + \
                            "jobId" + chr(34) + "name=" + chr(34) + "jobId" + chr(34) + " value="  + chr(34) + str(job.id) + chr(34) +"/>"
                            
                            csrf_token = get_token(request)
                            csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                            
                            strCancelButton = "<td>" + str(job.deadline_date) + "</td><td>" + \
                            "<form method="+ chr(34) +"post"+ chr(34) +">"  + \
                            strHiddenJobID + csrf_token_html + \
                            "<input type="+ chr(34) + "submit" + chr(34) + " name=" + chr(34) + "cancel" + chr(34) + \
                            "value="+ chr(34) + "Cancel"+ chr(34) + " title=" + chr(34) + "Click to make this job available again to other users" + chr(34) +  "></form></td><td>\n" + \
                            "<form method="+ chr(34) +"post"+ chr(34) + " enctype=" + chr(34) + "multipart/form-data" + chr(34)  + ">"  + \
                            strHiddenJobID + csrf_token_html +\
                            "<input type=" + chr(34) + "file" + chr(34) + "id=" + chr(34) + "upload_report_file" + chr(34) + "onChange=" + chr(34) + "return validateUploadedFile()" + chr(34) + \
                            "name=" + chr(34) + "upload_report_file" + chr(34)  + \
                            " accept="+ chr(34) + ".pdf,.doc,.docx,.xml,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document, .xlsx, application/vnd.ms-excel, .csv, .txt" + chr(34) + \
                            " required=" + chr(34) + "required" + chr(34) + "class=" + chr(34) + "buttonStyle"+ chr(34) +">" + \
                            "<input type="+ chr(34) + "submit"  + chr(34) + " name=" + chr(34) + "upload_report" + chr(34) + \
                            " title=" + chr(34) + "Click to upload your report" + chr(34) + \
                            " value="+ chr(34) + "Upload Report"+ chr(34) + "class=" + chr(34) + "btn" + chr(34) +\
                            " title=" + chr(34) + "Click to upload your selected report" + chr(34) +  ">\n" + \
                            "</form></td>" 
                            
                            link_to_report ="<td>&nbsp;</td>"
                        else:
                            report_href = chr(34) +  "/download_report/?report=" + str(job.report_name) + chr(34)
                            link_to_report = "<td><a href=" +  report_href +  " name=" + chr(39) + "download_report" + chr(39) + ">" + str(job.report_name) + "</a></td>"
                            strCancelButton = "<td>"+ str(job.deadline_date) +"</td><td>&nbsp;</td><td>&nbsp;</td><td>" + str(job.submission_date) + "</td>"
                        strRow = "<TR>" + strSubject + strTask  + strStatus + strCancelButton + link_to_report + "</TR>\n"
                        strRows += strRow
                individualJobs = strTable + strRows + "</TABLE>"
            else:
                individualJobs = "<p>There are no jobs are assigned to you at the moment.</p>"

        return  individualJobs
    except TypeError as te:
        print ("Function buildUsersJobTable - Type Error {}".format(te))
        return ''
    except Exception as e:
       print ("Function buildUsersJobTable - Error {}".format(e))


def build_status_list(request, strStatus, strHiddenJobID):
    csrf_token = get_token(request)
    csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
    status_list = ['Available', 'Not Available', 'In Progress', 'Received', 'Approved', 'Not Approved']
    start = "<form method=" + chr(34) + "POST" + chr(34) + "> " + strHiddenJobID + " " + csrf_token_html +" <select name=" + chr(34) + "status" + chr(34) + ">\n" 
    options = ''
    for status in status_list:
        selected = ""
        if status == strStatus:
            selected = " selected "
        options += "<option value="+ chr(34) + status +  chr(34) + selected + ">" + chr(34) + status +  chr(34) + "</option>\n"
    
    end = "</select>\n <input type="+ chr(34) + "submit" + chr(34) + " name=" + chr(34) + "updateStatus" + chr(34) +  \
                            "value="+ chr(34) + "Update Status"+ chr(34) + " title=" + chr(34) + "Click to update the status of this report" + chr(34) + "> \n </form>"  
    return start + options + end
    

def build_uploaded_report_table(request, status_type):
    """This function builds the table of uploaded reports whose status is status"""
    jobs = Job.objects.filter(status = status_type).values_list(
        'id', 'user_id', 'patient_id', 'task_id', 'status', 'report_name', 'submission_date')
    if len(jobs) == 0:
        returnStr =  "<p>There are no reports uploaded to the database with status " + status_type + "</p>"
    else:
        #make table
        strRows = ""
        tableHeader = ("<table><tr><th>Job ID</th><th>User</th><th>Patient ID</th>" +
                "<th>Task</th><th>Status</th><th>Report</th><th>Submission Date</th><th></th></tr>")
        for job in jobs: 
            user = User.objects.get(id=job[1])
            user_name = user.first_name + " " + user.last_name
            report_href = chr(34) +  "/download_report/?report=" + str(job[5]) + chr(34)

            link_to_report = "<a href=" +  report_href +  " name=" + chr(39) + "download_report" + chr(39) + ">" + str(job[5]) + "</a>"

            csrf_token = get_token(request)
            csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)

            strHiddenJobID = "<input type="+ chr(34) +"hidden" + chr(34) + " id=" + chr(34) + \
                            "jobId" + chr(34) + " name=" + chr(34) + "jobId" + chr(34) + " value="  + chr(34) + str(job[0]) + chr(34) +"/>"

            strDeleteButton = "<td><form method="+ chr(34) +"post"+ chr(34) +">" +  strHiddenJobID  + csrf_token_html + \
                            "<input type="+ chr(34) + "submit" + chr(34) + " name=" + chr(34) + "delete" + chr(34) + " onclick="+ chr(34) + "return deleteReportCheck();" + chr(34) + \
                            "value="+ chr(34) + "Delete Report"+ chr(34) + " title=" + chr(34) + "Click to delete this report and make this job available again" + chr(34) + ">" + \
                            "</form></td>"
            task = Task.objects.get(task_id=job[3])
            strRows += ("<tr><td>" + str(job[0]) + "</td><td>" + user_name + "</td><td>" + str(job[2]) +
                       "</td><td>" + task.task_name + "</td><td>" +  build_status_list(request,str(job[4]), strHiddenJobID) + "</td><td>" +  link_to_report + "</td><td>" + str(job[6]) + "</td>" +
                         strDeleteButton + "</tr>\n")
            returnStr = tableHeader + strRows + "</table>"
        return returnStr 


def download_report(request):
    """Prepares a report for download from a link"""
    try:
        report = request.GET.get('report')
        path_to_report = settings.BASE_DIR + '/media/reports/' + report
        if os.path.exists(path_to_report):
            content = open(path_to_report, 'rb')
            # Set the mime type
            mime_type, _ = mimetypes.guess_type(path_to_report)
            # Set the return value of the HttpResponse
            response =  HttpResponse(content, content_type=mime_type)
            # Set the HTTP header for sending to browser
            response['Content-Disposition'] = "attachment; filename=%s" % report
            # Return the response value
            return response
        else:
            return render(request, 'file_not_found.html')
    except TypeError as te:
        print ("Error {} with file {}".format(te, path_to_report))
    except FileNotFoundError:
        print('File {} does not exist'.format(path_to_report))
    except Exception as e:
       print ("Error {} with file {}".format(e, path_to_report))


@csrf_protect #Require Cross Site Request Forgery protection
@login_required   #If the user is not logged in, redirect to Login form
def dbAdmin(request):  
   """View function linked to template dbAdmin.html"""
   try:
        assert isinstance(request, HttpRequest)
        if request.method == 'POST':
            if "deleteDatabase" in request.POST:
                #clear data from the database but leave User data
                dbOps.clear_database()
                return render(request,
                    template_name =  'jobs/dbAdmin.html',context={'main_title':Configuration.objects.get(id=1).main_title,
                                                                    'delete_db_message':"Database deleted",
                                                                    'received_reports':"<p>There are no reports uploaded to the database</p>",
                                                                    'approved_reports':"<p>There are no approved reports in the database</p>"})
            elif "deleteAllReports"  in request.POST:
                #delete all the reports uploaded to the server
                [f.unlink() for f in Path(settings.MEDIA_ROOT + '/reports/').glob("*") if f.is_file()] 
                return render(request,
                    template_name =  'jobs/dbAdmin.html',
                    context={'main_title':Configuration.objects.get(id=1).main_title,
                             'delete_reports_message':"All reports deleted",
                            'received_reports':"<p>There are no reports uploaded to the database</p>",
                            'approved_reports':"<p>There are no approved reports in the database</p>"})
            elif 'uploadFile' in request.POST:
                #populate database from data in a spreadsheet
                populate_database(request)
                received_reports = build_uploaded_report_table(request, 'Received')
                approved_reports = build_uploaded_report_table(request, 'Approved')
                return render(request,
                    template_name =  'jobs/dbAdmin.html',
                    context={'main_title':Configuration.objects.get(id=1).main_title,
                             'upload_message':"Data successfully uploaded to database",
                             'received_reports':received_reports,
                             'approved_reports':approved_reports })
            elif 'delete' in request.POST:
                #delete an uploaded report
                report_to_delete = delete_report(request)
                received_reports = build_uploaded_report_table(request, 'Received')
                approved_reports = build_uploaded_report_table(request, 'Approved')
                return render(request,
                    template_name =  'jobs/dbAdmin.html',
                    context={'main_title':Configuration.objects.get(id=1).main_title,
                             'delete_message':"Report {} deleted".format(report_to_delete),  
                             'received_reports':received_reports,
                             'approved_reports':approved_reports})
            
            elif 'updateStatus' in request.POST:
                 #update status of an uploaded report
                 jobId = request.POST['jobId']
                 new_status = request.POST['status']
                 job = Job.objects.get(id=jobId)
                 if new_status == 'Not Approved':
                     #delete physical report
                     report_to_delete = delete_report(request)
                     Job.objects.filter(id=jobId).update(status = 'Available', report_name ='', submission_date=None, start_date=None, deadline_date=None, user_id=None)
                 else:
                    Job.objects.filter(id=jobId).update(status = new_status)

                 received_reports = build_uploaded_report_table(request, 'Received')
                 approved_reports = build_uploaded_report_table(request, 'Approved')
                 return render(request,
                    template_name =  'jobs/dbAdmin.html',context={'main_title':Configuration.objects.get(id=1).main_title,
                                                                  'received_reports':received_reports,
                                                                  'approved_reports':approved_reports})
        else:
            received_reports = build_uploaded_report_table(request, 'Received')
            approved_reports = build_uploaded_report_table(request, 'Approved')
            return render(
            request,
            template_name =  'jobs/dbAdmin.html',context={'main_title':Configuration.objects.get(id=1).main_title,
                                                          'received_reports':received_reports,
                                                          'approved_reports':approved_reports})
   except FileNotFoundError:
        print('File does not exist')
   except Exception as e:
       print ("Error {}".format(e))


def delete_report(request):
    jobId = request.POST['jobId']
    job = Job.objects.get(id=jobId)
    report_to_delete = settings.BASE_DIR + '/media/reports/' + str(job.report_name)
    if os.path.exists(report_to_delete):
        os.remove(report_to_delete)
    Job.objects.filter(id=jobId).update(status = 'In Progress', report_name ='', submission_date = None)
    return job.report_name


def download_jobs(dummy):
    """This function writes the contents of the Jobs table to an Excel spreadsheet
    for download.

    This function is executed when the 'Download Jobs Spreadsheet' link is clicked. """
    try:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=jobs.xls'
        wb = Workbook(encoding='utf-8')
        ws = wb.add_sheet('Jobs')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        #set up column header
        columns = ['job id', 'User Name', 'Patient ID', 'Task', 'Status', 'Report Name', 'Start Date', 'Deadline Date', 'Submission Date', 'Reminder_Sent']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()
        #add date to the header row
        todays_date = "  Report Date: " + str(date.today())
        ws.write(row_num, len(columns)+1, todays_date, font_style)
        jobs = Job.objects.all().values_list('id', 'user_id', 'patient_id', 'task_id', 'status', 'report_name', 'start_date', 'deadline_date', 'submission_date', 'reminder_sent').order_by('id')
        for job in jobs:
            row_num +=1
            for col_num in range(len(job)):
                if col_num == 1:
                    if job[1]:
                        #If a job is allocated to a user, get their full name
                        cursor = connection.cursor()
                        cursor.execute("SELECT first_name, last_name FROM public.auth_user WHERE id =" + str(job[1]))
                        querySet = cursor.fetchall()
                        user_name = querySet[0][0] + ' ' + querySet[0][1]
                        connection.close()
                    else:
                        user_name = ''
                    cell_content = str(user_name)
                elif col_num == 3:
                    #The jobs table only contains the task_id, 
                    #so get the name of the task from the Task table.
                    cell_content = str(Task.objects.get(task_id=str(job[3])).task_name)
                else:
                    cell_content = str(job[col_num])
                if cell_content.lower() == 'none': cell_content = ''
                ws.write(row_num, col_num, cell_content, font_style)
        wb.save(response)
        return response     
    except Exception as e:
       print ("Error {}".format(e))
       wb.save(response)
       return response


def populate_database(request):
    """Deletes the contents of the database and then repopulates it"""
    excel_file = request.FILES['excel_file']
    wb = openpyxl.load_workbook(excel_file)
    dbOps.clear_database()
    dbOps.populate_task_table(wb)
    dbOps.populate_patient_table(wb)
    #create job table
    dbOps.populate_job_table()


def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'jobs/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )


def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'jobs/contact.html',
        {
            'title':'Contact',
            'message':'QIB Sheffield',
            'year':datetime.now().year,
        }
    )