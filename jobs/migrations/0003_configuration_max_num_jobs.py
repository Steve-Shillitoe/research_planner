# Generated by Django 4.1.7 on 2023-04-10 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0002_alter_configuration_number_days_to_complete"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuration",
            name="max_num_jobs",
            field=models.IntegerField(
                default=4, verbose_name="Maximum number of active jobs per user"
            ),
        ),
    ]