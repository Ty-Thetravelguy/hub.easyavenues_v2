# Generated by Django 5.1.6 on 2025-04-05 15:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0023_activity_is_system_activity'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='activity_type',
            field=models.CharField(choices=[('meeting', 'Meeting'), ('call', 'Phone Call'), ('email', 'Email'), ('note', 'Note'), ('document', 'Document Upload'), ('status_change', 'Status Change'), ('policy_update', 'Policy Update'), ('waiver', 'Waiver/Favor'), ('task', 'Task')], max_length=20),
        ),
        migrations.CreateModel(
            name='TaskActivity',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='crm.activity')),
                ('title', models.CharField(max_length=255)),
                ('due_date', models.DateField()),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20)),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('waiting', 'Waiting'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='not_started', max_length=20)),
                ('completion_date', models.DateField(blank=True, null=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Task Activity',
                'verbose_name_plural': 'Task Activities',
                'ordering': ['-due_date'],
            },
            bases=('crm.activity',),
        ),
        migrations.CreateModel(
            name='WaiverActivity',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='crm.activity')),
                ('waiver_type', models.CharField(choices=[('waiver', 'Fee Waiver'), ('favor', 'Special Favor'), ('exception', 'Policy Exception')], max_length=50)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('reason', models.TextField()),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_waivers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Waiver/Favor Activity',
                'verbose_name_plural': 'Waiver/Favor Activities',
                'ordering': ['-performed_at'],
            },
            bases=('crm.activity',),
        ),
    ]
