# Generated by Django 5.1.6 on 2025-04-11 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0026_alter_taskactivity_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskactivity',
            name='reminder_sent_at',
            field=models.DateTimeField(blank=True, help_text='Timestamp when the reminder email was sent.', null=True),
        ),
    ]
