from django.core.management.base import BaseCommand
from crm.models import Activity

class Command(BaseCommand):
    help = 'Deletes all activities from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        count = Activity.objects.count()
        
        if not options['force']:
            confirm = input(f'Are you sure you want to delete {count} activities? This cannot be undone. (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Delete all activities
        Activity.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} activities.')) 