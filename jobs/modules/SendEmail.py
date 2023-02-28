from django.contrib import messages
from django.core.mail import BadHeaderError, send_mail
from django.conf import settings
from smtplib import SMTPException
from datetime import date
from datetime import datetime
from datetime import timedelta
from django.contrib.auth.models import User
from jobs.models import Configuration, Job


class SendEmail:
    """This class contains methods that send emails"""

    def report_uploaded_user_email(self, request, jobID, patient_id, task_name):
        """Email the user confirmation of their successful report upload"""
        try:
            report_uploader_name = request.user.first_name + " " + request.user.last_name
            email_message = ('Hi {}, \n you successfully uploaded a report at {} on {} for job {}, patient {} & dataset {}'
                             .format(report_uploader_name, datetime.now().strftime("%H:%M:%S"), date.today(), jobID, patient_id, task_name))
            send_mail(
                        subject = '{} report uploaded'.format(Configuration.objects.get(id=1).main_title),
                        message = email_message,
                        from_email = settings.EMAIL_HOST_USER,   # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
                        recipient_list = [request.user.email],    # This is a list
                        fail_silently = False     # Set this to False so that you will be notified if any exception raised
                    )
        except BadHeaderError:
            messages.error(request,"Invalid email header found.")
            print("Invalid email header found.")
        except SMTPException as e:
            messages.error(request,"Could not send an email to the System Administrator about a report upload due to {} error".format(str(e)))
            print("Could not send an email to the admins about a report upload due to {} error".format(str(e)))
        except Exception as e:
                messages.error(request,"Could not send an email to the System Administrator about a report upload due to {} error".format(str(e)))
                print("Could not send an email to the admins about a report upload due to {} error".format(str(e)))
   

    def report_uploaded_admins_email(self, new_file_name, request):
        """Sends an email to all admins informing them that a report has been uploaded"""
        try:
            superusers = User.objects.filter(is_superuser=True)
            superusers_emails = list(User.objects.filter(is_superuser=True).values_list('email',flat=True))
            report_uploader_name = request.user.first_name + " " + request.user.last_name
            email_message = ('The report  {}  was uploaded by {} on {}'.format(new_file_name, report_uploader_name, date.today()))
            send_mail(
                        subject = '{} report uploaded'.format(Configuration.objects.get(id=1).main_title),
                        message = email_message,
                        from_email = settings.EMAIL_HOST_USER,   # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
                        recipient_list = superusers_emails,    # This is a list
                        fail_silently = False     # Set this to False so that you will be notified if any exception raised
                    )
        except BadHeaderError:
            messages.error(request,"Invalid email header found.")
            print("Invalid email header found.")
        except SMTPException as e:
            messages.error(request,"Could not send an email to the System Administrator about a report upload due to {} error".format(str(e)))
            print("Could not send an email to the admins about a report upload due to {} error".format(str(e)))
        except Exception as e:
                messages.error(request,"Could not send an email to the System Administrator about a report upload due to {} error".format(str(e)))
                print("Could not send an email to the admins about a report upload due to {} error".format(str(e)))
   
    
    def deadline_reminder_email(self):
        """Sends an email to the user, 
        the day before the deadline for the submission of a report
        for a job they have allocated to themselves."""
        tomorrow = date.today() + timedelta(days=1)
        jobs = Job.objects.filter(deadline_date=tomorrow, reminder_sent='no', status ='In Progress').values_list(
            'id', 'user_id', 'patient_id', 'task_name')
        if jobs:
            for job in jobs:
                #get student email
                user = User.objects.get(id=job[1])
                email_address = user.email
                details =list(job)
                email_message = "The report for job {}, patient {}, dataset {} is due to be submitted tomorrow.".format(details[0], details[2], details[3])
                try:
                    send_mail(
                                subject = '{} Job report deadline reminder'.format(Configuration.objects.get(id=1).main_title),
                                message = email_message,
                                from_email = settings.EMAIL_HOST_USER,   # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
                                recipient_list = [email_address],    # This is a list
                                fail_silently = False     # Set this to False so that you will be notified if any exception raised
                            )
                    Job.objects.filter(id=job[0]).update(reminder_sent='yes')
                except BadHeaderError:
                    #messages.error(request, "Invalid email header found.")
                    print("Invalid email header found.")
                except SMTPException as e:
                    #messages.error(request,"Could not send an email deadline reminder due to {} error".format(str(e)))
                    print("Could not send an email deadline reminder due to {} error".format(str(e)))
                except Exception as e:
                    #messages.error(request,"Could not send an email deadline reminder due to {} error".format(str(e)))
                    print("Could not send an email deadline reminder due to {} error".format(str(e)))


    def job_allocation_email(self, job_details, deadline_date, request):
        """Sends an email to the user with details of a job they have just allocated to themselves."""
        try:
                email_message = ('You have allocated a job {} to yourself. Please complete it by {}'
                                .format(job_details, datetime.strptime(str(deadline_date), "%Y-%m-%d").strftime("%d/%m/%Y")))
                send_mail(
                        subject = '{} Job allocation'.format(Configuration.objects.get(id=1).main_title),
                        message = email_message,
                        from_email = settings.EMAIL_HOST_USER,   # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
                        recipient_list = [request.user.email],    # This is a list
                        fail_silently = False     # Set this to False so that you will be notified if any exception raised
                    )
        except BadHeaderError:
                messages.error(request,"Invalid email header found.")
                print("Invalid email header found.")
        except SMTPException as se:
            messages.error(request,"Could not send an email acknowledging job allocation to The System Administrator due to {} error".format(str(se)))
            print("Could not send an email acknowledging job allocation to The System Administrator due to {} error".format(str(se)))
        except Exception as e:
            messages.error(request,"Could not send an email acknowledging job allocation to The System Administrator due to {} error".format(str(e)))
            print("Could not send an email acknowledging job allocation to The System Administrator due to {} error".format(str(e)))
