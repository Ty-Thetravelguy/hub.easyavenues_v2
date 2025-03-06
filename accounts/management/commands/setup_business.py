from django.core.management.base import BaseCommand
from accounts.models import Business, BusinessDomain

class Command(BaseCommand):
    help = 'Sets up the initial business and domain for Easy Avenues'

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