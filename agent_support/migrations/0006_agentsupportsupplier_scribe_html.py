# Generated by Django 5.1.6 on 2025-02-26 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent_support', '0005_rename_discriptions_supplierattachment_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='agentsupportsupplier',
            name='scribe_html',
            field=models.TextField(blank=True, help_text='Paste the Scribe HTML content here', null=True, verbose_name='Scribe HTML Content'),
        ),
    ]
