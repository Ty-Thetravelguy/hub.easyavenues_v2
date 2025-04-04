# Generated by Django 5.1.6 on 2025-03-25 05:53

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0020_remove_emailactivity_attachments_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailactivity',
            name='recipients',
        ),
        migrations.AddField(
            model_name='emailactivity',
            name='contact_recipients',
            field=models.ManyToManyField(blank=True, related_name='received_emails', to='crm.contact'),
        ),
        migrations.AddField(
            model_name='emailactivity',
            name='user_recipients',
            field=models.ManyToManyField(blank=True, related_name='received_emails', to=settings.AUTH_USER_MODEL),
        ),
    ]
