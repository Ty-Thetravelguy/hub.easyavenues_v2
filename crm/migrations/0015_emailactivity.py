# Generated by Django 5.1.6 on 2025-03-24 07:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0014_activity_data'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_date', models.DateField(help_text='The date the email was sent/received')),
                ('email_time', models.TimeField(help_text='The time the email was sent/received')),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('outcome', models.CharField(choices=[('Sent', 'Sent'), ('Received', 'Received'), ('Bounced', 'Bounced'), ('Opened', 'Opened'), ('Clicked', 'Clicked')], max_length=50)),
                ('attachments', models.FileField(blank=True, null=True, upload_to='email_attachments/')),
                ('logged_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_activities', to='crm.company')),
                ('logged_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('recipients', models.ManyToManyField(related_name='email_activities_received', to='crm.contact')),
            ],
            options={
                'verbose_name': 'Email Activity',
                'verbose_name_plural': 'Email Activities',
                'ordering': ['-email_date', '-email_time'],
            },
        ),
    ]
