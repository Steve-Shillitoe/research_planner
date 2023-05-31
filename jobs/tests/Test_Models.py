import django
from django.test import TestCase
from jobs.models import Patient, Job, Configuration, Task
from django.contrib.auth.models import User

class PatientModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Patient.objects.create(patient_id="patient_1")

    def test_patient_id_label(self):
        patient = Patient.objects.get(patient_id="patient_1")
        field_label = patient._meta.get_field('patient_id').verbose_name
        self.assertEqual(field_label, 'patient id')

    def test_str_representation(self):
        patient = Patient.objects.get(patient_id="patient_1")
        self.assertEqual(str(patient), 'patient_1')

    def test_patient_id_max_length(self):
        patient = Patient.objects.get(patient_id="patient_1")
        max_length = patient._meta.get_field('patient_id').max_length
        self.assertEqual(max_length, 30)

class TaskModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Task.objects.create(task_name="Task 1", repetitions=3)

    def test_task_name_label(self):
        task = Task.objects.get(task_name="Task 1")
        field_label = task._meta.get_field('task_name').verbose_name
        self.assertEqual(field_label, 'task name')

    def test_str_representation(self):
        task = Task.objects.get(task_name="Task 1")
        self.assertEqual(str(task), 'Task 1')

    def test_repetitions_default_value(self):
        task = Task.objects.get(task_name="Task 1")
        self.assertEqual(task.repetitions, 3)

    def test_patient_id_max_length(self):
        task = Task.objects.get(task_name="Task 1")
        max_length = task._meta.get_field('task_name').max_length
        self.assertEqual(max_length, 50)


class JobModelTest(TestCase):
    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.patient_A = Patient.objects.create(patient_id="patient_A")
        self.task_A = Task.objects.create(task_name="Task_A")
        user = User.objects.create(username="test_user")
        self.job = Job.objects.create(
            user_id=user,
            patient_id=self.patient_A,
            task_id=self.task_A,
            repetition_num=2,
            status="In Progress",
            report_name="Report 1",
            start_date="2023-01-01",
            deadline_date="2023-01-10",
            submission_date="2023-01-09",
            reminder_sent="yes"
        )

    def test_job_str_representation(self):
        expected_str = str(self.job.id) + ', patient_A, Task_A, 2'
        self.assertEqual(str(self.job), expected_str)

    def test_job_ordering(self):
        patient_B = Patient.objects.create(patient_id="patient_B")
        task_B = Task.objects.create(task_name="Task_B")
        job1 = Job.objects.create(patient_id=patient_B, task_id=self.task_A)
        job2 = Job.objects.create(patient_id=self.patient_A, task_id=self.task_A)
        job3 = Job.objects.create(patient_id=self.patient_A, task_id=task_B)
        job4 = Job.objects.create(patient_id=patient_B, task_id=task_B)

        expected_ordering = [job2, job3, job1, job4]
        all_jobs = Job.objects.all()
        actual_ordering = list(all_jobs.exclude(id=self.job.id))
        self.assertEqual(actual_ordering, expected_ordering)
        #test default job status value of 'Available'
        self.assertEquals(job1.status, 'Available')
        #test default job repetition_num value of 1
        self.assertEquals(job1.repetition_num, 1)
        #test default task repetitions value of 1
        self.assertEquals(task_B.repetitions, 1)


    def test_job_verbose_name_plural(self):
        self.assertEqual(Job._meta.verbose_name_plural, "Jobs")

    def test_job_meta_ordering(self):
        ordering = Job._meta.ordering
        self.assertEqual(ordering, ['patient_id', 'task_id'])


class ConfigurationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Configuration.objects.create(
            main_title="Test Title",
            main_intro="Test Main Intro",
            indiv_intro="Test Individual Intro",
            number_days_to_complete=5,
            max_num_jobs=3
        )

    def test_Configuration_str_representation(self):
        configuration = Configuration.objects.get(main_title="Test Title")
        self.assertEqual(str(configuration), "Test Title")

    def test_Configuration_verbose_name_plural(self):
        verbose_name_plural = Configuration._meta.verbose_name_plural
        self.assertEqual(verbose_name_plural, "Configuration")

    def test_Configuration_default_values(self):
        configuration = Configuration.objects.get(main_title="Test Title")
        self.assertEqual(configuration.number_days_to_complete, 5)
        self.assertEqual(configuration.max_num_jobs, 3)