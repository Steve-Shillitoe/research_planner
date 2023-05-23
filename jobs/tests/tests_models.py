import django
from django.test import TestCase
#import unittest
from jobs.models import   Patient,  Job


#class DatasetModelTest(TestCase):
#    if django.VERSION[:2] >= (1, 7):
#        # Django 1.7 requires an explicit setup() when running tests in PTVS
#        @classmethod
#        def setUpClass(cls):
#            super(DatasetModelTest, cls).setUpClass()
#            django.setup()

#    @classmethod
#    def setUpTestData(cls):
#        # Set up non-modified objects used by all test methods
#        Dataset.objects.create(name='dataset01', type='seg')

#    def test_name_label(self):
#        dataset = Dataset.objects.get(id=1)
#        field_label = dataset._meta.get_field('name').verbose_name
#        self.assertEqual(field_label, 'Dataset Name')

#    def test_type_label(self):
#        dataset = Dataset.objects.get(id=1)
#        field_label = dataset._meta.get_field('type').verbose_name
#        self.assertEqual(field_label, 'Dataset Type')

#    def test_name_max_length(self):
#        dataset = Dataset.objects.get(id=1)
#        max_length = dataset._meta.get_field('name').max_length
#        self.assertEqual(max_length, 30)

#    def test_type_max_length(self):
#        dataset = Dataset.objects.get(id=1)
#        max_length = dataset._meta.get_field('type').max_length
#        self.assertEqual(max_length, 3)

#    def test_object_name_is_name(self):
#        dataset = Dataset.objects.get(id=1)
#        expected_object_name = dataset.name
#        self.assertEqual(str(dataset), expected_object_name)

    
