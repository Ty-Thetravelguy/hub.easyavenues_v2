# Generated by Django 5.1.6 on 2025-05-02 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0037_alter_waiveractivity_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='waiveractivity',
            name='is_missed_saving',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
