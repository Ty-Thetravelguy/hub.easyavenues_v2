# crm/management/commands/send_task_reminders.py

## Run command: python manage.py send_task_reminders for this to work

import logging
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

from crm.models import TaskActivity

# Configure logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sends reminder emails for tasks due today that have not yet had a reminder sent.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        # Query for tasks due today, not completed/cancelled, and reminder not sent
        # We compare the date part of due_datetime
        tasks_due_today = TaskActivity.objects.filter(
            due_datetime__date=today,
            status__in=['not_started', 'in_progress', 'waiting'], # Only remind for active tasks
            reminder_sent_at__isnull=True,
            assigned_to__isnull=False, # Ensure there is someone assigned
            assigned_to__email__isnull=False # Ensure assigned user has an email
        ).exclude(assigned_to__email='') # Exclude empty email addresses

        self.stdout.write(f"Checking for task reminders for {today}. Found {tasks_due_today.count()} tasks due.")
        
        sent_count = 0
        failed_count = 0

        for task in tasks_due_today:
            try:
                # Prepare email context
                context = {'task': task}
                
                # Render email content
                subject = render_to_string('crm/emails/task_reminder.txt', context).splitlines()[0] # Get subject from first line
                text_body = render_to_string('crm/emails/task_reminder.txt', context)
                html_body = render_to_string('crm/emails/task_reminder.html', context)
                
                recipient_email = task.assigned_to.email
                
                # Send the email
                send_mail(
                    subject=subject.replace('Subject: ', ''), # Clean up subject prefix
                    message=text_body, # Plain text version
                    from_email=settings.DEFAULT_FROM_EMAIL, # Use default sender from settings
                    recipient_list=[recipient_email],
                    html_message=html_body, # HTML version
                    fail_silently=False, # Raise errors if sending fails
                )
                
                # Mark reminder as sent
                task.reminder_sent_at = timezone.now()
                task.save(update_fields=['reminder_sent_at'])
                
                self.stdout.write(self.style.SUCCESS(f'Successfully sent reminder for task ID {task.id} to {recipient_email}'))
                sent_count += 1

            except Exception as e:
                logger.error(f"Failed to send reminder for task ID {task.id} to {task.assigned_to.email}: {e}", exc_info=True)
                self.stderr.write(self.style.ERROR(f'Failed to send reminder for task ID {task.id}: {e}'))
                failed_count += 1

        self.stdout.write(f"Finished sending reminders. Sent: {sent_count}, Failed: {failed_count}")
