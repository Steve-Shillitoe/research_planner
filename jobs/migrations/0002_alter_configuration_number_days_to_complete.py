# Generated by Django 4.1.7 on 2023-04-10 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configuration",
            name="number_days_to_complete",
            field=models.IntegerField(
                default=7, verbose_name="Number of days to complete a job"
            ),
        ),
    ]
