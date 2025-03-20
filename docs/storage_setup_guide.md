# Document Storage Setup Guide with Amazon S3

This guide explains how to set up Amazon S3 for document storage in the Easy Avenues Hub application.

## Benefits of Using Amazon S3

- Virtually unlimited storage capacity
- High durability and availability of documents
- Cost-effective (pay only for what you use)
- Automatic scaling without infrastructure management
- Geographically distributed for redundancy

## Setup Steps

### 1. AWS Account Setup

1. Create an AWS account if you don't have one: [AWS Sign Up](https://aws.amazon.com/)
2. Navigate to the S3 service in the AWS Console

### 2. Create an S3 Bucket

1. Click "Create bucket"
2. Choose a unique bucket name (e.g., `easyavenues-documents`)
3. Select a region close to your users (e.g., `eu-west-2` for UK)
4. Configure bucket settings:
   - Block all public access (recommended for security)
   - Enable versioning (optional, for document history)
   - Enable server-side encryption (for document security)
5. Click "Create bucket"

### 3. Create IAM User for Access

1. Navigate to IAM in the AWS Console
2. Create a new user with programmatic access
3. Attach the `AmazonS3FullAccess` policy (or create a custom policy with more limited permissions)
4. Save the Access Key ID and Secret Access Key securely

### 4. Django Configuration

1. Install required packages:

```bash
pip install django-storages boto3
```

2. Add to `INSTALLED_APPS` in settings.py:

```python
INSTALLED_APPS = [
    # ... existing apps
    'storages',
]
```

3. Add S3 configuration to settings.py:

```python
# S3 Storage Configuration
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_ID'  # Store these in environment variables
AWS_SECRET_ACCESS_KEY = 'YOUR_SECRET_ACCESS_KEY'  # Don't hardcode credentials
AWS_STORAGE_BUCKET_NAME = 'easyavenues-documents'
AWS_S3_REGION_NAME = 'eu-west-2'  # Change to your bucket's region
AWS_S3_FILE_OVERWRITE = False  # Don't overwrite files with the same name
AWS_DEFAULT_ACL = 'private'  # Keep files private
AWS_S3_CUSTOM_DOMAIN = None  # Don't use a custom domain

# File size limits
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
```

### 5. Document Model Updates

The existing `Document` model already uses Django's `FileField`, which will automatically work with S3 once the configuration is applied. No model changes are needed.

### 6. Security Considerations

- Never store AWS credentials in source code
- Use environment variables or a secure vault service
- Implement a lifecycle policy on the S3 bucket for automatic archiving/deletion of old files
- Consider enabling CloudTrail for audit logs of all S3 actions

### 7. Testing The Configuration

1. Upload a test document through the application
2. Verify the document is stored in S3 (check AWS Console)
3. Download the document to ensure it's retrievable

## Document Optimization Recommendations

1. **File Validation**:
   - Validate file types to only accept recognized formats
   - Implement more robust validation to check actual file contents

2. **Compression**:
   - Consider server-side compression for PDFs and other documents
   - Implement a background job for compressing large files after upload

3. **Caching**:
   - Set up CloudFront as a CDN for frequently accessed documents
   - Configure appropriate cache headers

4. **Data Migration**:
   - Create a management command to migrate existing documents to S3

## Cost Considerations

S3 pricing is based on:
- Storage used
- Data transfer out
- API requests

For a typical small to medium business, costs should be minimal. Monitor usage with AWS Cost Explorer to stay within budget. 