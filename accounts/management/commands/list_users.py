from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Lists all users and their status'

    def handle(self, *args, **kwargs):
        users = User.objects.all().order_by('email')
        
        self.stdout.write(self.style.SUCCESS(f'\nFound {users.count()} users:\n'))
        
        for user in users:
            # Get email verification status
            email_address = EmailAddress.objects.filter(email=user.email).first()
            email_verified = email_address.verified if email_address else False
            
            # Print user details
            self.stdout.write(self.style.SUCCESS(f'User: {user.email}'))
            self.stdout.write(self.style.SUCCESS(f'- Name: {user.get_full_name() or "Not set"}'))
            self.stdout.write(self.style.SUCCESS(f'- Active: {user.is_active}'))
            self.stdout.write(self.style.SUCCESS(f'- Staff: {user.is_staff}'))
            self.stdout.write(self.style.SUCCESS(f'- Superuser: {user.is_superuser}'))
            self.stdout.write(self.style.SUCCESS(f'- Email Verified: {email_verified}'))
            self.stdout.write(self.style.SUCCESS(f'- Date Joined: {user.date_joined.strftime("%Y-%m-%d %H:%M")}'))
            
            # Print business association if any
            if hasattr(user, 'business'):
                business = user.business
                self.stdout.write(self.style.SUCCESS(f'- Business: {business.business_name if hasattr(business, "business_name") else "Unknown"}'))
            else:
                self.stdout.write(self.style.SUCCESS('- Business: None'))
            
            # Print last login if available
            if user.last_login:
                self.stdout.write(self.style.SUCCESS(f'- Last Login: {user.last_login.strftime("%Y-%m-%d %H:%M")}'))
            else:
                self.stdout.write(self.style.SUCCESS('- Last Login: Never'))
            
            self.stdout.write('')  # Empty line between users 