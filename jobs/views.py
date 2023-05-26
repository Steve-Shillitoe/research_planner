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
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token 
from django.views.decorators.csrf import csrf_protect 
from django.conf import settings
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages
from django.core.exceptions import *
import openpyxl
import xlwt
from xlwt import Workbook
import os
from pathlib import Path
from jobs.models import Job, Patient, Task, Configuration
from django.db import connection
from .modules.SendEmail import SendEmail
from .modules.ViewHelperFunctions import buildMainJobsTable, buildUsersJobTable
import environ
env = environ.Env()
environ.Env.read_env()
from .modules.DatabaseOperations import DatabaseOperations
dbOps = DatabaseOperations()


def password_reset_request(request):
    """
    This function is used to email a user a password reset link.

    This function is executed when the Forgot password? link is clicked
    on the login.html template file when displayed in a web browser.

    First the email address entered by the user is checked to 
    determine if that email address is associated with a user in
    the database. If not a warning message is displayed on the web page,
    otherwise an email is sent to the user. 
    """
    msg=""
    password_reset_form = PasswordResetForm()
    if request.method == "POST":
        if request.POST['email']:
            email_address = request.POST['email'].strip()
            associated_users = User.objects.filter(Q(email=email_address))
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
                        return HttpResponse("Could not send an email to the user due to {} SMTP error".format(str(e)))
                    except Exception as e:
                        return HttpResponse("Could not send an email to the user due to {} error".format(str(e)))
                       
        else:
            msg="Entered email is not valid"
    return render(request=request, template_name="jobs/password/password_reset.html",
                  context={'main_title':Configuration.objects.first().main_title,
                           'email_not_found_db':msg,
                           'password_reset_form':password_reset_form})

def register_request(request):
    """
    This function registers a new user in the database.

    This function is executed when the Create an account link is clicked on 
    the login.html template file when displayed in a web browser.

    If all the new user data is entered correctly, a new user is saved to the database
    and the user is redirected to the login web page.
    Otherwise, the new user form is redisplayed for the user to try again.
    """
    if request.method == "POST":
        form = NewUserForm(request.POST)  #See forms.py for the definition of this form class
        if form.is_valid():
            user = form.save()
            return redirect("login")
        else:
            #If the data entered in the form is invalid, usually this
            #happens when the password is not valid, then the 
            #following code ensures that the other data entered is
            #retained in the form when it is redisplayed.
            form = NewUserForm()
            form.fields['username'].initial = request.POST['username']
            form.fields['email'].initial = request.POST['email']
            form.fields['first_name'].initial = request.POST['first_name']
            form.fields['last_name'].initial = request.POST['last_name']
            messages.error(request, "Unsuccessful registration. Invalid password.")
    else:
        form = NewUserForm()
    return render (request=request, template_name="jobs/register.html",
                   context={'main_title':Configuration.objects.first().main_title,
                            'register_form':form})


def process_uploaded_file(job, job_id, request, sendEmail):
    uploaded_report_file = request.FILES['upload_report_file']
    #Make a standard format report name
    new_file_name = "job_" + str(job_id) + "_" + str(job.patient_id) + "_" + str(job.task_id)
    new_file_name = new_file_name.replace(" ", "")
    #Get file extension of uploaded report
    _, file_extension = os.path.splitext(uploaded_report_file.name)
    #Make new report name with original file extension
    new_file_name = new_file_name + file_extension
    #Save uploaded report to \media\reports in the web app folder structure
    save_uploaded_file_to_disc(uploaded_report_file,  new_file_name)
    
    Job.objects.filter(id=job_id).update(status ='Received', report_name=new_file_name, submission_date=date.today())
    
    #Email admins about uploaded report
    sendEmail.report_uploaded_admins_email(new_file_name, request)
    #Email user about thier uploaded report
    sendEmail.report_uploaded_user_email(request, job)


@csrf_protect #Require Cross Site Request Forgery protection
@login_required   #If the user is not logged in, redirect to Login form
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    #If the database Configuration table has not been populated
    #yet, populate it with default initial values. 
    dbOps.populate_Configuration_table()
    #if job report deadline has passed, make the job available again
    dbOps.deadline_passed_set_job_available()
    #Send deadline one day away reminders
    sendEmail = SendEmail()
    sendEmail.deadline_reminder_email(request)

    FourJobsWarning = ""
    SameJobWarning = ""
    if request.method == 'POST':
        job_id = request.POST['jobId']
        if "select_job" in request.POST:
            #Update main jobs table. Available button clicked. Job assigned to a student
            #and status changed to 'In Progress'
            FourJobsWarning, SameJobWarning =  select_job(request, job_id, sendEmail)
        elif  'cancel' in request.POST:
            #Update individual job table. Cancel button clicked. Setting dates=None, 
            #gives them the value of Null
            try:
                Job.objects.filter(id=job_id).update(status ='Available', 
                               user_id_id = "", start_date =None, deadline_date =None)
            except Exception:
                return HttpResponse("Exception in function views.select_job: " + \
                    "Error updating a job when a user cancels it.")
        elif 'upload_report' in request.POST:
            try:
                job = Job.objects.get(id=job_id)
            except ObjectDoesNotExist:
                return HttpResponse("Exception in function views.home when uploading a report: Error getting selected job object.")
            if job.status == "In Progress":
                #The above check prevents a report being uploaded twice by
                #refreshing the screen or using the back button
                process_uploaded_file(job, job_id, request, sendEmail)
            
    try:
        configuration = Configuration.objects.first()
        main_title = configuration.main_title
        main_intro = configuration.main_intro
        indiv_intro = configuration.indiv_intro
        max_num_jobs = configuration.max_num_jobs
    except ObjectDoesNotExist:
        main_title = ""
        main_intro = ""
        indiv_intro = ""
        max_num_jobs = 4
    return render(
        request,
        template_name =  'jobs/index.html',
        context={'main_title':main_title,
                 'main_intro':main_intro,
                 'indiv_intro':indiv_intro,
                 'max_jobs':max_num_jobs,
                 'NumJobs':Job.objects.all().count(),
                 'JobTable': buildMainJobsTable(request),
                 'UsersJobTable': buildUsersJobTable(request),
                'FourJobsWarning': FourJobsWarning,
                'SameJobWarning': SameJobWarning}
                )


def save_uploaded_file_to_disc(file, new_file_name):  
    """
    This function writes an uploaded report, file, to disc with the filename, new_file_name.
    """
    try:
        new_file_path = settings.MEDIA_ROOT + '/reports/'+ new_file_name
        with open(new_file_path, 'wb+') as destination:  
            for chunk in file.chunks():  
                destination.write(chunk)
    except FileNotFoundError:
        return HttpResponse("Exception in function views.save_uploaded_file_to_disc: file {} does not exist".format(new_file_path))
    except Exception as e:
        return HttpResponse("Exception in function views.save_uploaded_file_to_disc: {}".format(str(e)))


def select_job(request, job_id, sendEmail):
    fourJobsWarning = ""
    sameJobWarning = ""
    #Get a list of 'in progress' jobs belonging to the user
    try:
        jobs = Job.objects.filter(user_id = request.user, status ='In Progress')
    except Exception:
        return HttpResponse("Exception in function views.select_job: Error getting in progress job list for the user.")
    numJobs = len(jobs)

    #Make sure this student has not already selected the same subject and task
    try:
        job = Job.objects.get(id=job_id)
    except ObjectDoesNotExist:
        return HttpResponse("Exception in function views.select_job: Error getting selected job object.")
    
    try:
        same_patient_task_job = Job.objects.filter(user_id = request.user, 
                            task_id = job.task_id, patient_id = job.patient_id)
    except Exception:
        return HttpResponse("Exception in function views.select_job: Error getting same_patient_task_job.")
    
    if same_patient_task_job.exists():
        sameJobWarning = "You may only select the same subject-task combination once."
    #check student does not already have the maximum number of jobs assigned to them
    max_num_jobs = Configuration.objects.first().max_num_jobs
    if numJobs < max_num_jobs:
        deadline_date = date.today() + timedelta(Configuration.objects.first().number_days_to_complete)
        try:
            Job.objects.filter(id=job_id).update(status ='In Progress', 
                                            user_id = request.user,
                                            start_date = date.today(),
                                            deadline_date = deadline_date)
        except Exception as e:
            messages.error(request,"Exception in function views.select_job: " + \
                "Error {} allocating this job to the user.".format(e))
    
        sendEmail.job_allocation_email(job_id, deadline_date, request)
    if numJobs == max_num_jobs:
        fourJobsWarning = "You may only have a maximum of {} jobs in progress.".format(max_num_jobs)
    return  fourJobsWarning, sameJobWarning 



def build_status_list(request, strJobID, strStatus, strHiddenJobID):
    """
    This function builds a dropdown list of status values.
    """
    csrf_token = get_token(request)
    csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
    status_list = ['Available', 'Not Available', 'In Progress', 'Received', 'Approved', 'Not Approved']
    start = "<form id=" + chr(34) + strJobID + "form" + chr(34) + " method=" + chr(34) + "POST" + chr(34) + "> " + strHiddenJobID + " " + csrf_token_html + "\n" + \
        " <select id=" + chr(34) + strJobID + "dropdown" + chr(34) + " name=" + chr(34) + "updateStatus" + chr(34) + ">\n" 
    options = ''
    for status in status_list:
        selected = ""
        if status == strStatus:
            selected = " selected "
        options += "<option value="+ chr(34) + status +  chr(34) + selected + ">" + chr(34) + status +  chr(34) + "</option>\n"
    end = "</select>\n  </form>\n"  
    return start + options + end
 

def build_submit_javascript(strJobID):
    """
    This function build the javascript necessary to make the dropdown list of 
    status strings to cause a form submission when the selected status is changed.

    This javascript function removes the need to have a submit button associated with
    the dropdown list.

    This javascript function attaches an eventlistener to each status dropdown list
    and when a change event is triggered, a form submit event is triggered.
    """
    return "<script> document.getElementById(" + \
        chr(34) + strJobID + "dropdown" + chr(34) + \
        ").addEventListener(" + chr(34) + "change"  + chr(34) + ", function() {" + \
        "document.getElementById(" + chr(34) + strJobID +  "form" + chr(34) + ").submit();" + \
        "});  </script>"


def build_uploaded_report_table(request, status_type):
    """
    This function builds the table of uploaded reports whose status is status
    for display on the Database Admin page
    """
    try:
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
                           "</td><td>" + task.task_name + "</td><td>" +  build_status_list(request,str(job[0]), str(job[4]), strHiddenJobID) + " " + build_submit_javascript(str(job[0])) +
                           "</td><td>" +  link_to_report + "</td><td>" + str(job[6]) + "</td>" +
                             strDeleteButton + "</tr>\n")
                returnStr = tableHeader + strRows + "</table>"
            return returnStr 
    except Exception as e:
        messages.error(request, 'Error {} building report table when status={}'.format(e, status_type))



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
        messages.error(request,"Error {} in views.download_report with file {}".format(te, path_to_report))
    except FileNotFoundError:
        messages.error(request,'Error in views.download_report, file {} does not exist'.format(path_to_report))
    except Exception as e:
        messages.error(request,"Error {} in views.download_report with file {}".format(e, path_to_report))


def superuser_required(view_func):
    def test_func(user):
        return user.is_superuser
    decorated_view_func = user_passes_test(test_func)(view_func)
    return decorated_view_func

@superuser_required #Only superusers may access this function
@csrf_protect #Require Cross Site Request Forgery protection
@login_required   #If the user is not logged in, redirect to Login form
def dbAdmin(request):  
    """View function linked to template dbAdmin.html"""
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        if "deleteDatabase" in request.POST:
            #clear data from the database but leave User data
            dbOps.clear_database()
            return render(request,
                template_name =  'jobs/dbAdmin.html',context={'main_title':Configuration.objects.first().main_title,
                                                                'delete_db_message':"Database deleted",
                                                                'received_reports':"<p>There are no reports uploaded to the database</p>",
                                                                'approved_reports':"<p>There are no approved reports in the database</p>"})
        elif "deleteAllReports"  in request.POST:
            #delete all the reports uploaded to the server
            try:
                [f.unlink() for f in Path(settings.MEDIA_ROOT + '/reports/').glob("*") if f.is_file()] 
            except Exception as e:
                messages.error(request,"Error in views.dbAdmin.deleteAllReports")
            return render(request,
                template_name =  'jobs/dbAdmin.html',
                context={'main_title':Configuration.objects.first().main_title,
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
                context={'main_title':Configuration.objects.first().main_title,
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
                context={'main_title':Configuration.objects.first().main_title,
                            'delete_message':"Report {} deleted".format(report_to_delete),  
                            'received_reports':received_reports,
                            'approved_reports':approved_reports})
            
        elif 'updateStatus' in request.POST:
                #update status of an uploaded report
                try:
                    job_id = request.POST['jobId']
                    new_status = request.POST['updateStatus']
                    job = Job.objects.get(id=job_id)
                    if new_status == 'Not Approved':
                        #delete physical report
                        report_to_delete = delete_report(request)
                        Job.objects.filter(id=job_id).update(status = 'Available', report_name ='', submission_date=None, start_date=None, deadline_date=None, user_id=None)
                    else:
                        Job.objects.filter(id=job_id).update(status = new_status)
                    received_reports = build_uploaded_report_table(request, 'Received')
                    approved_reports = build_uploaded_report_table(request, 'Approved')

                    return render(request,
                        template_name =  'jobs/dbAdmin.html',
                        context={'main_title':Configuration.objects.first().main_title,
                                'received_reports':received_reports,
                                'approved_reports':approved_reports})
                except Exception as e:
                    messages.error(request,'Error {} in views.dbAdmin when updating report status'.format(e))
    else:
        received_reports = build_uploaded_report_table(request, 'Received')
        approved_reports = build_uploaded_report_table(request, 'Approved')
        return render(
        request,
        template_name =  'jobs/dbAdmin.html',context={'main_title':Configuration.objects.first().main_title,
                                                        'received_reports':received_reports,
                                                        'approved_reports':approved_reports})


def delete_report(request):
    try:
        job_id = request.POST['jobId']
        job = Job.objects.get(id=job_id)
        report_to_delete = settings.BASE_DIR + '/media/reports/' + str(job.report_name)
        if os.path.exists(report_to_delete):
            os.remove(report_to_delete)
        Job.objects.filter(id=job_id).update(status = 'In Progress', report_name ='', submission_date = None)
        return job.report_name
    except Exception as e:
        messages.error(request, 'Error {} deleting report.'.format(e))

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
       messages.error(request, 'Error {} downloading Jobs spreadsheet'.format(e))
       wb.save(response)
       return response


def populate_database(request):
    """Deletes the contents of the database and then repopulates it"""
    try:
        excel_file = request.FILES['excel_file']
        wb = openpyxl.load_workbook(excel_file)
    except Exception as e:
        messages.error(request,"Error in views.dbAdmin.populate_database opening uploaded Excel file.")
                
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