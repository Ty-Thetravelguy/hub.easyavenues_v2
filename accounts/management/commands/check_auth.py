from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Business, BusinessDomain

User = get_user_model()

class Command(BaseCommand):
    help = 'Checks and fixes authentication issues'

    def handle(self, *args, **kwargs):
        # Check business
        try:
            business = Business.objects.get(business_name='Easy Avenues')
            self.stdout.write(self.style.SUCCESS('Business exists'))
        except Business.DoesNotExist:
            business = Business.objects.create(
                business_name='Easy Avenues',
                main_contact='Tyrone Francis',
                main_contact_email='tyrone.francis@easyavenues.co.uk',
                main_contact_phone=''
            )
            self.stdout.write(self.style.SUCCESS('Business created'))

        # Check domain
        try:
            domain = BusinessDomain.objects.get(domain='easyavenues.co.uk')
            self.stdout.write(self.style.SUCCESS('Domain exists'))
        except BusinessDomain.DoesNotExist:
            BusinessDomain.objects.create(
                business=business,
                domain='easyavenues.co.uk',
                active=True
            )
            self.stdout.write(self.style.SUCCESS('Domain created'))

        # Check and fix user
        try:
            user = User.objects.get(email='tyrone.francis@easyavenues.co.uk')
            if not user.business:
                user.business = business
                user.save()
                self.stdout.write(self.style.SUCCESS('User business association fixed'))
            self.stdout.write(self.style.SUCCESS('User exists and is properly configured'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User does not exist!')) 