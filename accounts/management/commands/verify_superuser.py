from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Verifies and ensures superuser status'

    def handle(self, *args, **kwargs):
        email = 'tyrone.francis@easyavenues.co.uk'
        
        try:
            user = User.objects.get(email=email)
            self.stdout.write(self.style.SUCCESS(f'Found user: {user.email}'))
            
            # Print current status
            self.stdout.write(self.style.SUCCESS('\nCurrent status:'))
            self.stdout.write(self.style.SUCCESS(f'- is_active: {user.is_active}'))
            self.stdout.write(self.style.SUCCESS(f'- is_staff: {user.is_staff}'))
            self.stdout.write(self.style.SUCCESS(f'- is_superuser: {user.is_superuser}'))
            
            # Ensure superuser status
            if not user.is_superuser:
                user.is_superuser = True
                self.stdout.write(self.style.SUCCESS('\nSetting is_superuser to True'))
            
            if not user.is_staff:
                user.is_staff = True
                self.stdout.write(self.style.SUCCESS('Setting is_staff to True'))
            
            if not user.is_active:
                user.is_active = True
                self.stdout.write(self.style.SUCCESS('Setting is_active to True'))
            
            user.save()
            self.stdout.write(self.style.SUCCESS('\nUser updated successfully'))
            
            # Verify final status
            self.stdout.write(self.style.SUCCESS('\nFinal status:'))
            self.stdout.write(self.style.SUCCESS(f'- is_active: {user.is_active}'))
            self.stdout.write(self.style.SUCCESS(f'- is_staff: {user.is_staff}'))
            self.stdout.write(self.style.SUCCESS(f'- is_superuser: {user.is_superuser}'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User not found!')) 