from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def migrate_activities(apps, schema_editor):
    Activity = apps.get_model('crm', 'Activity')
    Email = apps.get_model('crm', 'Email')
    Call = apps.get_model('crm', 'Call')
    Meeting = apps.get_model('crm', 'Meeting')
    Note = apps.get_model('crm', 'Note')
    WaiverFavor = apps.get_model('crm', 'WaiverFavor')

    for activity in Activity.objects.all():
        if activity.activity_type == 'email':
            # Extract data from JSON field
            data = activity.data or {}
            Email.objects.create(
                subject=data.get('subject', ''),
                company=activity.company,
                creator=activity.performed_by,
                outcome=data.get('outcome', 'Sent'),
                date=activity.performed_at.date(),
                time=activity.performed_at.time(),
                details=data.get('content', ''),
                to_do_task_date=activity.follow_up_date,
                to_do_task_message=activity.follow_up_notes
            )
        elif activity.activity_type == 'call':
            data = activity.data or {}
            Call.objects.create(
                subject=data.get('subject', ''),
                company=activity.company,
                creator=activity.performed_by,
                outcome=data.get('outcome', 'Connected'),
                date=activity.performed_at.date(),
                time=activity.performed_at.time(),
                duration=data.get('duration', 0),
                details=data.get('summary', ''),
                to_do_task_date=activity.follow_up_date,
                to_do_task_message=activity.follow_up_notes
            )
        elif activity.activity_type == 'meeting':
            data = activity.data or {}
            Meeting.objects.create(
                subject=data.get('title', ''),
                company=activity.company,
                creator=activity.performed_by,
                outcome=data.get('outcome', 'Scheduled'),
                location=data.get('location', 'Online'),
                date=activity.performed_at.date(),
                time=activity.performed_at.time(),
                duration=data.get('duration', 30),
                details=data.get('notes', ''),
                to_do_task_date=activity.follow_up_date,
                to_do_task_message=activity.follow_up_notes
            )
        elif activity.activity_type == 'note':
            data = activity.data or {}
            Note.objects.create(
                subject=activity.description[:255],  # Truncate if too long
                company=activity.company,
                creator=activity.performed_by,
                content=data.get('content', activity.description),
                to_do_task_date=activity.follow_up_date,
                to_do_task_message=activity.follow_up_notes
            )
        elif activity.activity_type == 'exception':
            data = activity.data or {}
            WaiverFavor.objects.create(
                subject=activity.description[:255],  # Truncate if too long
                company=activity.company,
                creator=activity.performed_by,
                waiver_type=data.get('exception_type', 'other'),
                value_amount=data.get('value_amount'),
                approved_by=data.get('approved_by', 'manager'),
                details=data.get('description', activity.description),
                to_do_task_date=activity.follow_up_date,
                to_do_task_message=activity.follow_up_notes
            )


def reverse_migrate(apps, schema_editor):
    Activity = apps.get_model('crm', 'Activity')
    Email = apps.get_model('crm', 'Email')
    Call = apps.get_model('crm', 'Call')
    Meeting = apps.get_model('crm', 'Meeting')
    Note = apps.get_model('crm', 'Note')
    WaiverFavor = apps.get_model('crm', 'WaiverFavor')

    # Convert back to Activity model if needed
    for email in Email.objects.all():
        Activity.objects.create(
            company=email.company,
            performed_by=email.creator,
            activity_type='email',
            description=email.subject,
            performed_at=email.created_at,
            follow_up_date=email.to_do_task_date,
            follow_up_notes=email.to_do_task_message,
            data={
                'subject': email.subject,
                'content': email.details,
                'outcome': email.outcome
            }
        )

    for call in Call.objects.all():
        Activity.objects.create(
            company=call.company,
            performed_by=call.creator,
            activity_type='call',
            description=call.subject,
            performed_at=call.created_at,
            follow_up_date=call.to_do_task_date,
            follow_up_notes=call.to_do_task_message,
            data={
                'subject': call.subject,
                'summary': call.details,
                'outcome': call.outcome,
                'duration': call.duration
            }
        )

    for meeting in Meeting.objects.all():
        Activity.objects.create(
            company=meeting.company,
            performed_by=meeting.creator,
            activity_type='meeting',
            description=meeting.subject,
            performed_at=meeting.created_at,
            follow_up_date=meeting.to_do_task_date,
            follow_up_notes=meeting.to_do_task_message,
            data={
                'title': meeting.subject,
                'notes': meeting.details,
                'outcome': meeting.outcome,
                'location': meeting.location,
                'duration': meeting.duration
            }
        )

    for note in Note.objects.all():
        Activity.objects.create(
            company=note.company,
            performed_by=note.creator,
            activity_type='note',
            description=note.subject,
            performed_at=note.created_at,
            follow_up_date=note.to_do_task_date,
            follow_up_notes=note.to_do_task_message,
            data={
                'content': note.content
            }
        )

    for waiver in WaiverFavor.objects.all():
        Activity.objects.create(
            company=waiver.company,
            performed_by=waiver.creator,
            activity_type='exception',
            description=waiver.subject,
            performed_at=waiver.created_at,
            follow_up_date=waiver.to_do_task_date,
            follow_up_notes=waiver.to_do_task_message,
            data={
                'exception_type': waiver.waiver_type,
                'value_amount': str(waiver.value_amount) if waiver.value_amount else None,
                'approved_by': waiver.approved_by,
                'description': waiver.details
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0015_emailactivity'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create Meeting model
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('outcome', models.CharField(choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Rescheduled', 'Rescheduled'), ('No-show', 'No-show'), ('Cancelled', 'Cancelled')], max_length=20)),
                ('location', models.CharField(choices=[('Online', 'Online'), ('In-person', 'In-person')], max_length=20)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('duration', models.IntegerField(choices=[(i, f"{i} minutes") for i in range(15, 481, 15) if i % 15 == 0])),
                ('details', models.TextField(blank=True, default='', verbose_name='Details')),
                ('to_do_task_date', models.DateField(blank=True, null=True)),
                ('to_do_task_message', models.TextField(blank=True, null=True, verbose_name='To Do Task Message')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='crm.company')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_meetings', to=settings.AUTH_USER_MODEL)),
                ('contacts', models.ManyToManyField(related_name='meeting_attended', to='crm.contact')),
                ('users', models.ManyToManyField(blank=True, related_name='meeting_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date', '-time'],
            },
        ),

        # Create Call model
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('outcome', models.CharField(choices=[('Connected', 'Connected'), ('Voicemail', 'Left Voicemail'), ('No Answer', 'No Answer'), ('Busy', 'Busy'), ('Disconnected', 'Disconnected')], max_length=20)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('duration', models.IntegerField(choices=[(i, f"{i} minutes") for i in range(1, 61)])),
                ('details', models.TextField(blank=True, default='', verbose_name='Details')),
                ('to_do_task_date', models.DateField(blank=True, null=True)),
                ('to_do_task_message', models.TextField(blank=True, null=True, verbose_name='To Do Task Message')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calls', to='crm.company')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_calls', to=settings.AUTH_USER_MODEL)),
                ('contacts', models.ManyToManyField(related_name='calls_attended', to='crm.contact')),
                ('users', models.ManyToManyField(blank=True, related_name='call_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date', '-time'],
            },
        ),

        # Create Email model
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('outcome', models.CharField(choices=[('Sent', 'Sent'), ('Received', 'Received'), ('Bounced', 'Bounced'), ('Opened', 'Opened'), ('Clicked', 'Clicked')], max_length=20)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('details', models.TextField(blank=True, default='', verbose_name='Details')),
                ('to_do_task_date', models.DateField(blank=True, null=True)),
                ('to_do_task_message', models.TextField(blank=True, null=True, verbose_name='To Do Task Message')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emails', to='crm.company')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_emails', to=settings.AUTH_USER_MODEL)),
                ('contacts', models.ManyToManyField(related_name='emails_attended', to='crm.contact')),
                ('users', models.ManyToManyField(blank=True, related_name='email_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date', '-time'],
            },
        ),

        # Create Note model
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('to_do_task_date', models.DateField(blank=True, null=True)),
                ('to_do_task_message', models.TextField(blank=True, null=True, verbose_name='To Do Task Message')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='crm.company')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_notes', to=settings.AUTH_USER_MODEL)),
                ('contacts', models.ManyToManyField(related_name='notes_attended', to='crm.contact')),
                ('users', models.ManyToManyField(blank=True, related_name='note_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Create WaiverFavor model
        migrations.CreateModel(
            name='WaiverFavor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('waiver_type', models.CharField(choices=[('refund_waiver', 'Refund Waiver'), ('fee_waiver', 'Fee Waiver'), ('loyalty_points', 'Loyalty Points'), ('rate_match', 'Rate Match'), ('other', 'Other')], max_length=50)),
                ('value_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('approved_by', models.CharField(choices=[('manager', 'Manager'), ('director', 'Director'), ('operations', 'Operations'), ('account_manager', 'Account Manager')], max_length=50)),
                ('details', models.TextField()),
                ('to_do_task_date', models.DateField(blank=True, null=True)),
                ('to_do_task_message', models.TextField(blank=True, null=True, verbose_name='To Do Task Message')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='waivers_favors', to='crm.company')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_waivers_favors', to=settings.AUTH_USER_MODEL)),
                ('contacts', models.ManyToManyField(related_name='waivers_favors_attended', to='crm.contact')),
                ('users', models.ManyToManyField(blank=True, related_name='waiver_favor_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Run data migration
        migrations.RunPython(migrate_activities, reverse_migrate),

        # Remove old Activity model
        migrations.DeleteModel(
            name='Activity',
        ),
    ] 