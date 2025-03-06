from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress, EmailConfirmation
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Fixes email verification issues by cleaning up email confirmations'

    def handle(self, *args, **kwargs):
        email = 'tyrone.francis@easyavenues.co.uk'
        
        try:
            # Get the user
            user = User.objects.get(email=email)
            self.stdout.write(self.style.SUCCESS(f'Found user: {user.email}'))
            
            # Get all email addresses for this email
            email_addresses = EmailAddress.objects.filter(email=email)
            self.stdout.write(self.style.SUCCESS(f'\nFound {email_addresses.count()} email address records'))
            
            # Get all email confirmations for this email
            email_confirmations = EmailConfirmation.objects.filter(email_address__email=email)
            self.stdout.write(self.style.SUCCESS(f'Found {email_confirmations.count()} email confirmation records'))
            
            # Handle duplicate email addresses
            if email_addresses.count() > 1:
                self.stdout.write(self.style.WARNING('\nMultiple email addresses found. Cleaning up...'))
                
                # Keep only the most recent email address
                latest_email = email_addresses.order_by('-id').first()
                email_addresses.exclude(pk=latest_email.pk).delete()
                
                # Update the latest email address
                if not latest_email.verified:
                    latest_email.verified = True
                    latest_email.primary = True
                    latest_email.save()
                    self.stdout.write(self.style.SUCCESS('Marked remaining email address as verified and primary'))
            
            # Handle email confirmations
            if email_confirmations.count() > 1:
                self.stdout.write(self.style.WARNING('\nMultiple email confirmations found. Cleaning up...'))
                
                # Keep only the most recent confirmation
                latest_confirmation = email_confirmations.order_by('-created').first()
                email_confirmations.exclude(pk=latest_confirmation.pk).delete()
                
                # Ensure the latest confirmation is verified
                if not latest_confirmation.verified:
                    latest_confirmation.verified = True
                    latest_confirmation.verified_at = timezone.now()
                    latest_confirmation.save()
                
                self.stdout.write(self.style.SUCCESS('Cleaned up email confirmations'))
            
            # Print final status
            self.stdout.write(self.style.SUCCESS('\nFinal status:'))
            self.stdout.write(self.style.SUCCESS(f'Email addresses: {EmailAddress.objects.filter(email=email).count()}'))
            self.stdout.write(self.style.SUCCESS(f'Email confirmations: {EmailConfirmation.objects.filter(email_address__email=email).count()}'))
            
            # Verify final email address status
            final_email = EmailAddress.objects.filter(email=email).first()
            if final_email:
                self.stdout.write(self.style.SUCCESS(f'\nFinal email address status:'))
                self.stdout.write(self.style.SUCCESS(f'- Email: {final_email.email}'))
                self.stdout.write(self.style.SUCCESS(f'- Verified: {final_email.verified}'))
                self.stdout.write(self.style.SUCCESS(f'- Primary: {final_email.primary}'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User not found!')) 