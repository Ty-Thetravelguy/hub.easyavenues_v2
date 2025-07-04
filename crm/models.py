# crm/models.py

from django.db import models
from accounts.models import Business
from django.conf import settings
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
import datetime
from django.urls import reverse


# Choices for industry, company type, client type, and account status
INDUSTRY_CHOICES = [
    ('Agriculture', 'Agriculture'),
    ('Mining', 'Mining'),
    ('Oil and Gas Extraction', 'Oil and Gas Extraction'),
    ('Pharmaceuticals', 'Pharmaceuticals'),
    ('Biotechnology', 'Biotechnology'),
    ('Manufacturing', 'Manufacturing'),
    ('Construction', 'Construction'),
    ('Wholesale Trade', 'Wholesale Trade'),
    ('Retail Trade', 'Retail Trade'),
    ('Transportation', 'Transportation'),
    ('Warehousing', 'Warehousing'),
    ('Information', 'Information'),
    ('Finance', 'Finance'),
    ('Insurance', 'Insurance'),
    ('Real Estate', 'Real Estate'),
    ('Rental and Leasing', 'Rental and Leasing'),
    ('Professional Services', 'Professional Services'),
    ('Scientific Services', 'Scientific Services'),
    ('Technical Services', 'Technical Services'),
    ('Management of Companies', 'Management of Companies'),
    ('Administrative Support', 'Administrative Support'),
    ('Waste Management', 'Waste Management'),
    ('Educational Services', 'Educational Services'),
    ('Health Care', 'Health Care'),
    ('Social Assistance', 'Social Assistance'),
    ('Arts', 'Arts'),
    ('Entertainment', 'Entertainment'),
    ('Recreation', 'Recreation'),
    ('Accommodation', 'Accommodation'),
    ('Food Services', 'Food Services'),
    ('Other Services', 'Other Services'),
    ('Public Administration', 'Public Administration'),
    ('Telecommunications', 'Telecommunications'),
    ('Hospitality', 'Hospitality'),
    ('Legal Services', 'Legal Services'),
    ('Media and Broadcasting', 'Media and Broadcasting'),
    ('Energy', 'Energy'),
    ('Renewable Energy', 'Renewable Energy'),
    ('Automotive', 'Automotive'),
    ('Aerospace', 'Aerospace'),
    ('Defence', 'Defence'),
    ('Tourism', 'Tourism')
]

COMPANY_TYPE = [
    # CLIENT OR SUPPLIER
    ('Client', 'Client'),
    ('Supplier', 'Supplier'),
]


CLIENT_TYPE_CHOICES = [
    # Types of companies the agency manages
    ('White Glove Client', 'White Glove Client'),
    ('Online Client', 'Online Client'),
    ('Blended', 'Blended'),
    ('Supplier', 'Supplier'),
]


SUPPLIER_FOR_DEPARTMENT_CHOICES = [
    # Supplier for which department
    ('Company Supplier', 'Company Supplier'),
    ('Operations Supplier', 'Operations Supplier'),
    ('Finance Supplier', 'Finance Supplier'),
    ('Sales Supplier', 'Sales Supplier'),
    ('Marketing Supplier', 'Marketing Supplier'),
    ('Other', 'Other'),
]


CLIENT_STATUS_CHOICES = [
    # Statuses for the company's account relationship with the agency
    ('Trading', 'Trading'),
    ('No longer Trading', 'No longer Trading'),
    ('On hold', 'On hold'),
    ('Other', 'Other'),
]

SUPPLIER_TYPE_CHOICES = [
    ('Air', 'Air'),
    ('Accommodation', 'Accommodation'),
    ('Car Hire', 'Car Hire'),
    ('Transfer', 'Transfer'),
    ('Rail', 'Rail'),
    ('Other', 'Other'),
]

SUPPLIER_STATUS_CHOICES = [
    # Statuses for the company's account relationship with the agency
    ('Preferred Supplier', 'Preferred Supplier'),
    ('Non-Preferred Supplier', 'Non-Preferred Supplier'),
    ('Other', 'Other'),
]


class Company(models.Model):
    """
    Represents a company that is managed within the CRM system.
    Base model with fields common to both clients and suppliers.
    """
    agency = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='companies', null=False)
    company_name = models.CharField(max_length=255, blank=False, null=False)
    company_type = models.CharField(max_length=255, choices=COMPANY_TYPE, default='Client')
    industry = models.CharField(max_length=255, choices=INDUSTRY_CHOICES, blank=False, null=False)

    # Contact Information
    street_address = models.CharField(max_length=255, blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    state_province = models.CharField(max_length=100, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    linkedin_social_page = models.URLField(blank=True, null=True)
    
    # External system integration
    hubspot_id = models.CharField(max_length=100, blank=True, null=True, help_text="HubSpot Company ID")

    # Timestamps and relationships
    create_date = models.DateTimeField(auto_now_add=True)
    last_activity_date = models.DateTimeField(null=True, blank=True)
    linked_companies = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='linked_to')

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        if not self.last_activity_date:
            self.last_activity_date = timezone.now()
        super().save(*args, **kwargs)

class ClientInvoiceReference(models.Model):
    """
    Through model for client invoice references to store whether each reference is mandatory or optional.
    """
    client_profile = models.ForeignKey('ClientProfile', on_delete=models.CASCADE)
    invoice_reference = models.ForeignKey('accounts.InvoiceReference', on_delete=models.CASCADE)
    is_mandatory = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['client_profile', 'invoice_reference']

    def __str__(self):
        return f"{self.invoice_reference.name} for {self.client_profile.company.company_name}"

class ClientProfile(models.Model):
    """
    Extended profile for companies that are clients.
    Contains all client-specific fields.
    """
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='client_profile')
    client_type = models.CharField(max_length=255, choices=CLIENT_TYPE_CHOICES, default='White Glove Client')
    client_status = models.CharField(max_length=255, choices=CLIENT_STATUS_CHOICES, default='Trading')
    sage_name = models.CharField(max_length=255, blank=True, null=True)
    midoco_crm_number = models.CharField(max_length=255, blank=True, null=True)
    invoice_references = models.TextField(blank=True)
    invoice_reference_options = models.ManyToManyField(
        'accounts.InvoiceReference',
        through='ClientInvoiceReference',
        related_name='clients',
        blank=True
    )
    invoicing_type = models.CharField(max_length=100, blank=True, null=True)
    invoicing_frequency = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    
    # Management
    client_account_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_clients')
    client_ops_team = models.CharField(max_length=255, blank=True, null=True)

    # Corporate rates and memberships
    corporate_hotel_rates = models.TextField(blank=True)
    corporate_airline_fares = models.TextField(blank=True)
    company_memberships = models.TextField(blank=True)

    # Contract and service-related fields
    has_new_contract_signed = models.BooleanField(default=False)
    signed_up_corporate_schemes = models.BooleanField(default=False)
    signed_up_travelogix = models.BooleanField(default=False)
    meetings_events_requirements = models.BooleanField(default=False)
    REPORTING_CHOICES = [
        ('Standard', 'Standard'),
        ('Bespoke', 'Bespoke'),
    ]
    reporting_standard_bespoke = models.CharField(max_length=10, choices=REPORTING_CHOICES, default='Standard')
    access_to_travelogix = models.BooleanField(default=False)
    travel_policy_health_check_offered = models.BooleanField(default=False)
    testimonial_requested = models.BooleanField(default=False)

    # Sustainability fields
    communicated_esg_support = models.BooleanField(default=False)
    receive_co2_reporting = models.BooleanField(default=False)
    discussed_offsetting = models.BooleanField(default=False)

    def __str__(self):
        return f"Client Profile - {self.company.company_name}"

class SupplierProfile(models.Model):
    """
    Extended profile for companies that are suppliers.
    Contains all supplier-specific fields.
    """
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='supplier_profile')
    supplier_type = models.CharField(max_length=255, choices=SUPPLIER_TYPE_CHOICES, default='Air')
    supplier_status = models.CharField(max_length=255, choices=SUPPLIER_STATUS_CHOICES, default='Preferred Supplier')
    supplier_for_department = models.CharField(max_length=255, choices=SUPPLIER_FOR_DEPARTMENT_CHOICES, default='Company Supplier')
    supplier_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='owned_suppliers')

    # Finance/Invoice Information
    invoicing_type = models.CharField(max_length=100, blank=True, null=True)
    invoicing_frequency = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)

    # Service Status
    new_supplier_form_signed = models.BooleanField(default=False)
    contract_signed = models.BooleanField(default=False)

    def __str__(self):
        return f"Supplier Profile - {self.company.company_name}"

class Contact(models.Model):
    """
    Represents a contact associated with a company within the CRM system.
    """
    CONTACT_TAG_CHOICES = [
        ('primary', 'Primary Contact'),
        ('key_personnel', 'Key Personnel'),
        ('booker', 'Booker'),
        ('vip_traveller', 'VIP Traveller'),
        ('traveller', 'Traveller'),
    ]

    SUPPLIER_TAG_CHOICES = [
        ('primary', 'Primary Contact'),
        ('key_personnel', 'Key Personnel'),
    ]

    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    job_role = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    landline = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    hospitality = models.CharField(max_length=100, blank=True, null=True)  # Placeholder for now
    tag_list = models.JSONField(default=list)  # Store tags as a list of strings
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_available_tags(self):
        """Return available tags based on company type"""
        if self.company.company_type == 'Client':
            return dict(self.CONTACT_TAG_CHOICES)
        return dict(self.SUPPLIER_TAG_CHOICES)

    def clean(self):
        """Validate phone numbers if provided"""
        if self.landline:
            if not re.match(r'^\+?1?\d{9,15}$', self.landline):
                raise ValidationError('Invalid landline number format')
        if self.mobile:
            if not re.match(r'^\+?1?\d{9,15}$', self.mobile):
                raise ValidationError('Invalid mobile number format')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_full_name(self):
        """Return the contact's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_absolute_url(self):
        """Return the URL for the contact's detail view."""
        return reverse('crm:contact_detail', kwargs={'pk': self.pk})

class ContactNote(models.Model):
    """
    Represents a note associated with a contact.
    """
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.contact} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class ClientTravelPolicy(models.Model):
    """
    Represents a travel policy for a company. Companies can have multiple travel policies,
    which allows for tracking policy changes over time or different policies for different purposes.
    """
    client = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='travel_policies')
    policy_name = models.CharField(max_length=255, default="Default Policy")
    effective_date = models.DateField(default=datetime.date.today)
    is_active = models.BooleanField(default=True)
    travel_policy = models.TextField(blank=True)
    flight_notes = models.TextField(blank=True)
    accommodation_notes = models.TextField(blank=True)
    car_hire_notes = models.TextField(blank=True)
    transfer_notes = models.TextField(blank=True)
    rail_notes = models.TextField(blank=True)
    other_notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    vip_travelers = models.ManyToManyField('Contact', related_name='travel_policies', blank=True)

    class Meta:
        verbose_name_plural = "Client travel policies"
        ordering = ['-effective_date']  # Most recent policies first

    def __str__(self):
        return f"{self.policy_name} for {self.client.company_name} (Effective: {self.effective_date})"

class TransactionFee(models.Model):
    """
    Represents transaction fees associated with a company.

    Fields:
        - company: The company this fee is associated with.
        - service: The type of service the fee applies to.
        - online_fee, offline_fee: Fee amounts for online and offline transactions.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='transaction_fees')
    service = models.CharField(max_length=100)
    online_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    offline_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.service} fee for {self.company.company_name}"

class Tag(models.Model):
    """
    Flexible tagging system for both companies and contacts.
    """
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # 'position', 'company', 'communication', etc.
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

    class Meta:
        ordering = ['category', 'name']

class CompanyTag(models.Model):
    """
    Links tags to companies with metadata about who added them and when.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'tag')

class ContactTag(models.Model):
    """
    Links tags to contacts with metadata about who added them and when.
    """
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('contact', 'tag')

class Document(models.Model):
    """
    Stores documents related to companies (contracts, agreements, etc.).
    """
    DOCUMENT_TYPES = [
        ('contract', 'Contract'),
        ('agreement', 'Agreement'),
        ('policy', 'Policy'),
        ('presentation', 'Presentation'),
        ('proposal', 'Proposal'),
        ('other', 'Other'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='company_documents/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.title} - {self.company.company_name}"
        
    @property
    def is_expired(self):
        """Check if the document has expired"""
        if not self.expiry_date:
            return False
        from datetime import date
        return self.expiry_date < date.today()
        
    def delete(self, *args, **kwargs):
        """
        Override delete method to clean up the file from storage
        """
        # Delete the file from storage
        if self.file and hasattr(self.file, 'storage'):
            try:
                storage = self.file.storage
                name = self.file.name
                if storage.exists(name):
                    storage.delete(name)
            except Exception as e:
                # Log the error but continue with deletion
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error deleting document file: {e}")
        
        # Call the parent delete method
        super().delete(*args, **kwargs)

# Base Activity model
class Activity(models.Model):
    """
    Base model for all activities and interactions with companies and contacts.
    """
    ACTIVITY_TYPES = (
        ('email', 'Email'),
        ('call', 'Call'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('waiver_favour', 'Savings, Allowances, Favours (SAF)'),
        ('task', 'Task'),
        ('document', 'Document Upload'),
        ('status_change', 'Status Change'),
        ('policy_update', 'Policy Update'),
        # Add other types here
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, db_index=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='activities')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, related_name='activities', null=True, blank=True)
    description = models.TextField()
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    activity_datetime = models.DateTimeField(null=True, blank=True, help_text="Timestamp when the activity actually occurred")
    scheduled_for = models.DateTimeField(null=True, blank=True)
    outcome = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    is_system_activity = models.BooleanField(default=False, help_text="Indicates if this is an automatically generated system activity")
    
    # Fields to track edits
    last_edited_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp of the last edit.")
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='edited_activities', 
        help_text="User who last edited the activity."
    )
    
    # New field to link follow-up tasks
    related_activity = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='follow_up_tasks',
        help_text="The activity this task is following up on."
    )

    def get_activity_type_display(self):
        return dict(self.ACTIVITY_TYPES).get(self.activity_type, self.activity_type.capitalize())

    def debug_info(self):
        """Return a dictionary with debugging information about this activity"""
        subclass_models = ['emailactivity', 'callactivity', 'meetingactivity', 
                         'noteactivity', 'documentactivity', 'statuschangeactivity',
                         'policyupdateactivity', 'waiveractivity', 'taskactivity']
        
        available_subclasses = []
        for model_name in subclass_models:
            if hasattr(self, model_name):
                available_subclasses.append(model_name)
        
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'has_description': bool(self.description),
            'available_subclasses': available_subclasses
        }

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.get_activity_type_display()} with {self.company.company_name}"

class EmailActivity(Activity):
    """
    Model for email activities.
    """
    body = models.TextField()
    email_date = models.DateField()
    email_time = models.TimeField()
    subject = models.CharField(max_length=255, blank=True, null=True)
    email_outcome = models.CharField(
        max_length=50,
        choices=[
            ('Sent', 'Sent'),
            ('Received', 'Received'),
            ('No Response', 'No Response')
        ],
        null=True,
        blank=True
    )
    contact_recipients = models.ManyToManyField(Contact, related_name='received_emails', blank=True)
    user_recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='received_emails', blank=True)

    class Meta:
        verbose_name = 'Email Activity'
        verbose_name_plural = 'Email Activities'
        ordering = ['-email_date', '-email_time']

    def __str__(self):
        recipients = []
        recipients.extend(str(r) for r in self.contact_recipients.all())
        recipients.extend(str(r) for r in self.user_recipients.all())
        return f"Email to {', '.join(recipients)} on {self.email_date}"

class CallActivity(Activity):
    """
    Model for phone call activities.
    """
    CALL_TYPE_CHOICES=[
        ('Inbound', 'Inbound'),
        ('Outbound', 'Outbound'),
        ('Missed', 'Missed'),
        ('Voicemail', 'Voicemail')
    ]
    call_type = models.CharField(max_length=50, choices=CALL_TYPE_CHOICES)
    
    CALL_OUTCOME_CHOICES = [
        ('completed', 'Completed'),
        ('left_message', 'Left Message'),
        ('no_answer', 'No Answer'),
        ('busy', 'Busy'),
        ('wrong_number', 'Wrong Number'),
        ('scheduled_callback', 'Scheduled Callback'),
        ('', '---------')
    ]
    
    duration = models.IntegerField(help_text='Duration in minutes')
    summary = models.TextField()
    call_outcome = models.CharField(max_length=255, choices=CALL_OUTCOME_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = 'Call Activity'
        verbose_name_plural = 'Call Activities'
        ordering = ['-performed_at']

class MeetingActivity(Activity):
    """
    Model for meeting activities.
    """
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    duration = models.IntegerField(help_text='Duration in minutes')
    contact_attendees = models.ManyToManyField(Contact, related_name='attended_meetings', blank=True)
    user_attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='attended_meetings', blank=True)
    agenda = models.TextField()
    minutes = models.TextField()
    meeting_outcome = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Meeting Activity'
        verbose_name_plural = 'Meeting Activities'
        ordering = ['-performed_at']

class NoteActivity(Activity):
    """
    Model for note activities.
    """
    subject = models.ForeignKey(
        'NoteSubject', 
        on_delete=models.SET_NULL, # Keep note even if subject is deleted
        null=True, 
        blank=True, # Allow notes without a subject
        related_name='notes'
    )
    content = models.TextField()
    is_important = models.BooleanField(
        default=False,
        db_column='is_private',  # Keeps the same column name in the database for compatibility
        help_text="Mark this note as important"
    )
    # Property for backwards compatibility
    @property
    def is_private(self):
        return self.is_important
    
    # +++ ADDED ManyToManyField for Contacts +++
    contacts = models.ManyToManyField(
        'Contact',
        related_name='note_activities',
        blank=True # Make this optional
    )
    # --- END --- 
    
    # Removed note_outcome as it seemed unused/unnecessary
    # note_outcome = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Note Activity'
        verbose_name_plural = 'Note Activities'
        ordering = ['-performed_at']

class DocumentActivity(Activity):
    """
    Model for document-related activities.
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=[
        ('Uploaded', 'Uploaded'),
        ('Downloaded', 'Downloaded'),
        ('Updated', 'Updated'),
        ('Deleted', 'Deleted')
    ])
    document_outcome = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Document Activity'
        verbose_name_plural = 'Document Activities'
        ordering = ['-performed_at']

class StatusChangeActivity(Activity):
    """
    Model for status change activities.
    """
    old_status = models.CharField(max_length=100)
    new_status = models.CharField(max_length=100)
    reason = models.TextField()
    status_outcome = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Status Change Activity'
        verbose_name_plural = 'Status Change Activities'
        ordering = ['-performed_at']

class PolicyUpdateActivity(Activity):
    """
    Model for policy update activities.
    """
    policy = models.ForeignKey(ClientTravelPolicy, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=[
        ('Created', 'Created'),
        ('Updated', 'Updated'),
        ('Deleted', 'Deleted')
    ])
    changes = models.TextField()
    policy_outcome = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Policy Update Activity'
        verbose_name_plural = 'Policy Update Activities'
        ordering = ['-performed_at']

class WaiverActivity(Activity):
    """
    Model for waiver/favour activities.
    """
    SAF_TYPE_CHOICES = (
        ('Savings', 'Savings'),
        ('Allowances', 'Allowances'),
        ('Favours', 'Favours'),
    )
    saf_type = models.CharField(max_length=20, choices=SAF_TYPE_CHOICES, blank=False, null=False, default='Savings')

    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_waivers')
    
    is_missed_saving = models.BooleanField(default=False, null=True, blank=True)
    
    # Added M2M for contacts
    contacts = models.ManyToManyField(
        'Contact',
        related_name='waiver_favour_activities',
        blank=True
    )
    
    # Added ForeignKey to WaiverFavourType
    type = models.ForeignKey(
        'WaiverFavourType',
        on_delete=models.SET_NULL, # Keep activity if type is deleted
        null=True,
        blank=False, # Make type mandatory for new waivers/favours?
        related_name='waiver_favour_activities'
    )

    def save(self, *args, **kwargs):
        if not self.pk: # Set activity_type only on creation
            self.activity_type = 'waiver_favour'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "SAF Activity"
        verbose_name_plural = "SAF Activities"

class TaskActivity(Activity):
    """
    Model for task activities.
    """
    title = models.CharField(max_length=255)
    due_datetime = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Date and time the task is due."
    )
    # --- REMOVED single contact ForeignKey ---
    # contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, related_name='tasks', null=True, blank=True)
    
    # +++ RE-ADDED assigned_to field +++
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tasks'
    )
    # --- END --- 
    
    # +++ ADDED ManyToManyFields for contacts and users +++
    contacts = models.ManyToManyField(
        'Contact',
        related_name='task_activities', # Changed related_name from 'tasks' to avoid clash
        blank=True
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='user_tasks',
        blank=True
    )
    # --- END --- 
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='not_started')
    completion_date = models.DateField(null=True, blank=True)
    # New field to track reminder sending
    reminder_sent_at = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Timestamp when the reminder email was sent."
    )

    class Meta:
        verbose_name = 'Task Activity'
        verbose_name_plural = 'Task Activities'
        ordering = ['-due_datetime']

class StatusHistory(models.Model):
    """
    Tracks changes in company status over time.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=255)
    new_status = models.CharField(max_length=255)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Status histories"
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.company.company_name}: {self.old_status} → {self.new_status}"

class CustomField(models.Model):
    """
    Defines custom fields that can be added to companies or contacts.
    """
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('boolean', 'Yes/No'),
        ('choice', 'Choice'),
    ]

    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    choices = models.JSONField(null=True, blank=True)  # For choice fields
    default_value = models.JSONField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.field_type})"

class CustomFieldValue(models.Model):
    """
    Stores values for custom fields for companies and contacts.
    """
    field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='custom_field_values', null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='custom_field_values', null=True, blank=True)
    value = models.JSONField()
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('field', 'company'),
            ('field', 'contact'),
        ]

    def __str__(self):
        return f"{self.field.name}: {self.value}"

class CompanyRelationship(models.Model):
    """Model to define relationships between companies."""
    RELATIONSHIP_TYPES = (
        ('parent', 'Parent Company'),
        ('subsidiary', 'Subsidiary'),
        ('branch', 'Branch Office'),
        ('partner', 'Partner'),
        ('affiliate', 'Affiliate'),
        ('vendor', 'Vendor'),
        ('client', 'Client'),
        ('other', 'Other'),
    )
    from_company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='from_relationships',
        help_text="Company initiating the relationship"
    )
    to_company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='to_relationships',
        help_text="Company receiving the relationship"
    )
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    description = models.TextField(blank=True, null=True)
    established_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_company_relationships'
    )

    class Meta:
        unique_together = ('from_company', 'to_company', 'relationship_type')
        verbose_name = "Company Relationship"
        verbose_name_plural = "Company Relationships"

    def __str__(self):
        return f"{self.from_company.company_name} → {self.relationship_type} → {self.to_company.company_name}"

# +++ Model for NoteSubject +++
class NoteSubject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Note Subject"
        verbose_name_plural = "Note Subjects"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Assuming an update view named 'manage_note_subject_update' exists
        return reverse('crm:manage_note_subject_update', kwargs={'pk': self.pk})
# +++ End NoteSubject Model +++

# +++ Model for WaiverFavourType +++
class WaiverFavourType(models.Model):
    """Model to manage types for Waiver & Favour activities."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "SAF Type"
        verbose_name_plural = "SAF Types"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # This assumes we create an update view named 'manage_waiver_favour_type_update' later
        # We will add this URL name in the urls.py step
        return reverse('crm:manage_waiver_favour_type_update', kwargs={'pk': self.pk}) 
# +++ End WaiverFavourType Model +++

# Map activity types to their specific models
# (Defined here after all Activity subclasses are declared)
ACTIVITY_TYPE_MODELS = {
    'email': EmailActivity,
    'call': CallActivity,
    'meeting': MeetingActivity,
    'note': NoteActivity,
    'waiver_favour': WaiverActivity,
    'task': TaskActivity,
    'document': DocumentActivity,
    'status_change': StatusChangeActivity,
    'policy_update': PolicyUpdateActivity,
    # Add other activity types here if needed
}