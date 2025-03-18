# crm/models.py

from django.db import models
from accounts.models import Business
from django.conf import settings
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re


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
    PREFERRED_CONTACT_METHOD = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('mobile', 'Mobile'),
        ('teams', 'Microsoft Teams'),
        ('whatsapp', 'WhatsApp'),
    ]

    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    job_title = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    # Contact preferences
    preferred_contact_method = models.CharField(max_length=20, choices=PREFERRED_CONTACT_METHOD, default='email')
    preferred_contact_time = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., 'Mornings only', '9-5 GMT'")
    do_not_contact = models.BooleanField(default=False)
    out_of_office_until = models.DateField(null=True, blank=True)
    teams_id = models.CharField(max_length=100, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Contact roles
    is_primary_contact = models.BooleanField(default=False)
    is_primary_finance_contact = models.BooleanField(default=False)
    is_primary_hr_contact = models.BooleanField(default=False)
    is_primary_it_contact = models.BooleanField(default=False)
    is_travel_booker_contact = models.BooleanField(default=False)
    is_traveller_contact = models.BooleanField(default=False)
    is_vip_traveller_contact = models.BooleanField(default=False)
    
    # Additional fields
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='contacts_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='contacts_updated')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company})"

    def clean(self):
        # Email validation
        if self.email:
            try:
                validate_email(self.email)
            except ValidationError:
                raise ValidationError({'email': 'Please enter a valid email address.'})
        
        # Phone validation (basic format)
        if self.phone and not re.match(r'^\+?1?\d{9,15}$', self.phone):
            raise ValidationError({'phone': 'Phone number must be between 9 and 15 digits.'})
        
        if self.mobile and not re.match(r'^\+?1?\d{9,15}$', self.mobile):
            raise ValidationError({'mobile': 'Mobile number must be between 9 and 15 digits.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ClientTravelPolicy(models.Model):
    """
    Represents a travel policy for a company. Companies can have multiple travel policies,
    which allows for tracking policy changes over time or different policies for different purposes.
    """
    client = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='travel_policies')
    policy_name = models.CharField(max_length=255, default="Default Policy")
    effective_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    travel_policy = models.TextField(blank=True)
    flight_notes = models.TextField(blank=True)
    accommodation_notes = models.TextField(blank=True)
    car_hire_notes = models.TextField(blank=True)
    transfer_notes = models.TextField(blank=True)
    rail_notes = models.TextField(blank=True)
    other_notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

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

class Activity(models.Model):
    """
    Tracks all activities and interactions with companies and contacts.
    """
    ACTIVITY_TYPES = [
        ('meeting', 'Meeting'),
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('note', 'Note'),
        ('document', 'Document Upload'),
        ('status_change', 'Status Change'),
        ('policy_update', 'Policy Update'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='activities')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, related_name='activities', null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    outcome = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.activity_type} with {self.company.company_name}"

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