from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class DocumentStorage(S3Boto3Storage):
    """
    Custom storage backend for company documents
    
    This storage class inherits from S3Boto3Storage and adds
    specific configuration for document uploads.
    """
    # Set the location within the bucket where files will be stored
    location = 'company_documents'
    
    # Keep files private by default
    default_acl = 'private'
    
    # Don't generate querystring authentication by default - use presigned URLs when needed
    querystring_auth = True
    
    # Set a reasonable expiry time for URLs (2 hours)
    querystring_expire = 7200  # 2 hours in seconds
    
    # Use server-side encryption
    encryption = True
    
    # Don't automatically overwrite files with the same name
    file_overwrite = False
    
    # Custom headers for files
    object_parameters = {
        'CacheControl': 'max-age=86400',  # Cache for 24 hours
    }
    
    def get_accessed_time(self, name):
        """
        S3 doesn't track access time, so we return modified time
        """
        return self.get_modified_time(name)
    
    def get_created_time(self, name):
        """
        S3 doesn't track creation time, so we return modified time
        """
        return self.get_modified_time(name) 