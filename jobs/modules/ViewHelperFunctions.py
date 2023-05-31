from jobs.models import Job, Patient, Task, Configuration
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.contrib import messages
from django.conf import settings
from datetime import date, timedelta
import os

#Link job status to a colour. Used to set the background colour of table cells
#displaying the status of a job
TYPE_OF_STATUS = {'Available': "green",'Not Available': "red",'In Progress': "yellow",'Received': "Magenta",
                    'Approved': "SkyBlue" }

def buildMainJobsTable(request):
    """Builds the main HTML table of jobs for display on the home page"""
    strRow = ""
    strPatient = ""
    strRows = ""
    patients = Patient.objects.all()
    if patients:
        #the database is populated, so build the jobs table
        try:
            task_list_from_jobs = Job.objects.filter(patient_id=patients[0].patient_id)
        except Exception as e:
            messages.error(request,"Exception in function views.buildMainJobsTable.task_list_from_jobs: {}".format(str(e)))
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
            try:
                jobs = Job.objects.filter(patient_id=patient.patient_id).order_by('id')
            except Exception as e:
                messages.error(request,"Exception in function views.buildMainJobsTable getting jobs for each subject: {}".format(str(e)))
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
        messages.error(request,"Function buildUsersJobTable - Type Error {}".format(te))
        return ''
    except Exception as e:
       messages.error(request,"Error in function views.buildUsersJobTable: {}".format(te))

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
