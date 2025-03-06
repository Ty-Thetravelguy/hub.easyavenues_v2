from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

User = get_user_model()

class Command(BaseCommand):
    help = 'Fixes email confirmation issues'

    def handle(self, *args, **kwargs):
        email = 'tyrone.francis@easyavenues.co.uk'
        
        # First, check all users with this email
        users = User.objects.filter(email=email)
        self.stdout.write(self.style.SUCCESS(f'Found {users.count()} users with email {email}'))
        
        # Print details of each user
        for user in users:
            self.stdout.write(self.style.SUCCESS(f'\nUser details:'))
            self.stdout.write(self.style.SUCCESS(f'- ID: {user.id}'))
            self.stdout.write(self.style.SUCCESS(f'- Email: {user.email}'))
            self.stdout.write(self.style.SUCCESS(f'- is_active: {user.is_active}'))
            self.stdout.write(self.style.SUCCESS(f'- is_staff: {user.is_staff}'))
            self.stdout.write(self.style.SUCCESS(f'- is_superuser: {user.is_superuser}'))
        
        # Check email confirmations
        email_addresses = EmailAddress.objects.filter(email=email)
        self.stdout.write(self.style.SUCCESS(f'\nFound {email_addresses.count()} email confirmations for {email}'))
        
        # Print details of each email confirmation
        for ea in email_addresses:
            self.stdout.write(self.style.SUCCESS(f'\nEmail confirmation details:'))
            self.stdout.write(self.style.SUCCESS(f'- ID: {ea.id}'))
            self.stdout.write(self.style.SUCCESS(f'- Email: {ea.email}'))
            self.stdout.write(self.style.SUCCESS(f'- Verified: {ea.verified}'))
            self.stdout.write(self.style.SUCCESS(f'- Primary: {ea.primary}'))
            self.stdout.write(self.style.SUCCESS(f'- User ID: {ea.user_id}'))
        
        # Fix the issue by removing old email confirmations
        if email_addresses.count() > 1:
            self.stdout.write(self.style.WARNING('\nRemoving duplicate email confirmations...'))
            # Keep only the most recent confirmation
            latest = email_addresses.order_by('-id').first()
            email_addresses.exclude(id=latest.id).delete()
            self.stdout.write(self.style.SUCCESS('Duplicate email confirmations removed'))
        
        # Ensure the remaining email confirmation is verified
        if email_addresses.exists():
            latest = email_addresses.order_by('-id').first()
            if not latest.verified:
                latest.verified = True
                latest.save()
                self.stdout.write(self.style.SUCCESS('Email confirmation marked as verified')) 