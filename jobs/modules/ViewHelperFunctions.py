from jobs.models import Job, Patient, Task, Configuration
from django.middleware.csrf import get_token
from django.contrib import messages

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