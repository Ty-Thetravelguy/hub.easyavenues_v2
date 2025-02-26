from django.core.management.base import BaseCommand
from django.conf import settings
from agent_support.models import SupplierAttachment
import os

class Command(BaseCommand):
    help = 'Removes orphaned PDF files from media directory'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        attachments_dir = os.path.join(media_root, 'supplier_attachments')
        
        # Get all files in the directory
        existing_files = set()
        for root, dirs, files in os.walk(attachments_dir):
            for filename in files:
                existing_files.add(os.path.join(root, filename))
        
        # Get all files referenced in the database
        db_files = set()
        for attachment in SupplierAttachment.objects.all():
            if attachment.pdf_file:
                db_files.add(attachment.pdf_file.path)
        
        # Find orphaned files
        orphaned_files = existing_files - db_files
        
        # Delete orphaned files
        for file_path in orphaned_files:
            try:
                os.remove(file_path)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted orphaned file: {file_path}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error deleting {file_path}: {str(e)}')
                )
