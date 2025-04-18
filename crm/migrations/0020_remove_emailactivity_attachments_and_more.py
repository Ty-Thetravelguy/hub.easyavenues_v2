# Generated by Django 5.1.6 on 2025-03-25 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0019_activity_outcome_alter_callactivity_call_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailactivity',
            name='attachments',
        ),
        migrations.RemoveField(
            model_name='emailactivity',
            name='subject',
        ),
        migrations.AlterField(
            model_name='emailactivity',
            name='email_outcome',
            field=models.CharField(blank=True, choices=[('Sent', 'Sent'), ('Received', 'Received'), ('No Response', 'No Response')], max_length=50, null=True),
        ),
    ]
