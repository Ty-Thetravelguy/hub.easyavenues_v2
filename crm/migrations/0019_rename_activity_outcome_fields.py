from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0018_activity_models'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailactivity',
            old_name='outcome',
            new_name='email_outcome',
        ),
        migrations.RenameField(
            model_name='callactivity',
            old_name='outcome',
            new_name='call_outcome',
        ),
        migrations.RenameField(
            model_name='meetingactivity',
            old_name='outcome',
            new_name='meeting_outcome',
        ),
        migrations.RenameField(
            model_name='noteactivity',
            old_name='outcome',
            new_name='note_outcome',
        ),
        migrations.RenameField(
            model_name='documentactivity',
            old_name='outcome',
            new_name='document_outcome',
        ),
        migrations.RenameField(
            model_name='statuschangeactivity',
            old_name='outcome',
            new_name='status_outcome',
        ),
        migrations.RenameField(
            model_name='policyupdateactivity',
            old_name='outcome',
            new_name='policy_outcome',
        ),
    ] 