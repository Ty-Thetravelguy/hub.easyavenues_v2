# Generated by Django 5.1.6 on 2025-03-06 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('agent', 'Agent'), ('marketing', 'Marketing'), ('admin', 'Admin')], default='agent', max_length=20),
        ),
    ]
