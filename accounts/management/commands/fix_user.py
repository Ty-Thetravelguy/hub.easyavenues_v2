from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Business, BusinessDomain

User = get_user_model()

class Command(BaseCommand):
    help = 'Fixes user authentication issues'

    def handle(self, *args, **kwargs):
        # First, ensure business and domain exist
        business, _ = Business.objects.get_or_create(
            business_name='Easy Avenues',
            defaults={
                'main_contact': 'Tyrone Francis',
                'main_contact_email': 'tyrone.francis@easyavenues.co.uk',
                'main_contact_phone': '',
            }
        )
        self.stdout.write(self.style.SUCCESS('Business checked/created'))

        domain, _ = BusinessDomain.objects.get_or_create(
            business=business,
            domain='easyavenues.co.uk',
            defaults={'active': True}
        )
        self.stdout.write(self.style.SUCCESS('Domain checked/created'))

        # Check and fix user
        try:
            user = User.objects.get(email='tyrone.francis@easyavenues.co.uk')
            self.stdout.write(self.style.SUCCESS(f'Found user: {user.email}'))
            
            # Print user details
            self.stdout.write(self.style.SUCCESS(f'User details:'))
            self.stdout.write(self.style.SUCCESS(f'- is_active: {user.is_active}'))
            self.stdout.write(self.style.SUCCESS(f'- is_staff: {user.is_staff}'))
            self.stdout.write(self.style.SUCCESS(f'- is_superuser: {user.is_superuser}'))
            self.stdout.write(self.style.SUCCESS(f'- business: {user.business}'))
            
            # Fix user if needed
            if not user.is_staff:
                user.is_staff = True
                self.stdout.write(self.style.SUCCESS('Setting is_staff to True'))
            
            if not user.is_superuser:
                user.is_superuser = True
                self.stdout.write(self.style.SUCCESS('Setting is_superuser to True'))
            
            if not user.business:
                user.business = business
                self.stdout.write(self.style.SUCCESS('Setting business association'))
            
            if user.is_active != True:
                user.is_active = True
                self.stdout.write(self.style.SUCCESS('Setting is_active to True'))
            
            user.save()
            self.stdout.write(self.style.SUCCESS('User updated successfully'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User does not exist!'))
            # Create the user if it doesn't exist
            user = User.objects.create_superuser(
                email='tyrone.francis@easyavenues.co.uk',
                username='tyrone.francis@easyavenues.co.uk',  # Set username to email
                password='your_existing_password',  # You'll need to change this
                first_name='Tyrone',
                last_name='Francis',
                business=business
            )
            self.stdout.write(self.style.SUCCESS('User created successfully')) 