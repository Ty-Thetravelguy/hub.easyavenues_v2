# Generated by Django 5.1.6 on 2025-02-22 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent_support', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentsupportsupplier',
            name='agent_websites',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
