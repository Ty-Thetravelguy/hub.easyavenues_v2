from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Resets a user\'s password'

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.get(email='tyrone.francis@easyavenues.co.uk')
            # Set a new password
            new_password = 'EasyAvenues2024!'  # You can change this password
            user.set_password(new_password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Password reset successfully for {user.email}'))
            self.stdout.write(self.style.SUCCESS(f'New password: {new_password}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User not found!')) 