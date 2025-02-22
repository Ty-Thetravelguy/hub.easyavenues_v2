from django.core.management.base import BaseCommand
from agent_support.models import AgentSupportSupplier

class Command(BaseCommand):
    help = 'Fix None values in JSON fields to empty lists'

    def handle(self, *args, **options):
        suppliers = AgentSupportSupplier.objects.all()
        for supplier in suppliers:
            supplier.contact_phone = supplier.contact_phone or []
            supplier.general_email = supplier.general_email or []
            supplier.agent_websites = supplier.agent_websites or []
            supplier.save()
        self.stdout.write(self.style.SUCCESS('Successfully fixed JSON fields'))