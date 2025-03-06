from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from accounts.models import Business, BusinessDomain

User = get_user_model()

class Command(BaseCommand):
    help = 'Sets up initial data including business, domain, superuser, and groups'

    def handle(self, *args, **kwargs):
        # Create or get the business
        business, created = Business.objects.get_or_create(
            business_name='Easy Avenues',
            defaults={
                'main_contact': 'Tyrone Francis',
                'main_contact_email': 'tyrone.francis@easyavenues.co.uk',
                'main_contact_phone': '',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Business created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Business already exists'))

        # Create or get the domain
        domain, created = BusinessDomain.objects.get_or_create(
            business=business,
            domain='easyavenues.co.uk',
            defaults={'active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Domain created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Domain already exists'))

        # Create superuser
        if not User.objects.filter(email='tyrone.francis@easyavenues.co.uk').exists():
            User.objects.create_superuser(
                email='tyrone.francis@easyavenues.co.uk',
                password='your_password_here',  # You'll need to change this
                first_name='Tyrone',
                last_name='Francis',
                business=business
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))

        # Create groups
        agent_group, created = Group.objects.get_or_create(name='Agent')
        if created:
            self.stdout.write(self.style.SUCCESS('Agent group created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Agent group already exists'))

        marketing_group, created = Group.objects.get_or_create(name='Marketing')
        if created:
            self.stdout.write(self.style.SUCCESS('Marketing group created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Marketing group already exists')) 