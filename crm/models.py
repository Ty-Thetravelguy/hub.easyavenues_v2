# crm/models.py

from django.db import models
from accounts.models import Business
from django.conf import settings
from django.utils import timezone


# Choices for industry, company type, client type, and account status
INDUSTRY_CHOICES = [
    ('agriculture', 'Agriculture'),
    ('mining', 'Mining'),
    ('oil_gas_extraction', 'Oil and Gas Extraction'),
    ('pharmaceuticals', 'Pharmaceuticals'),
    ('biotechnology', 'Biotechnology'),
    ('manufacturing', 'Manufacturing'),
    ('construction', 'Construction'),
    ('wholesale_trade', 'Wholesale Trade'),
    ('retail_trade', 'Retail Trade'),
    ('transportation', 'Transportation'),
    ('warehousing', 'Warehousing'),
    ('information', 'Information'),
    ('finance', 'Finance'),
    ('insurance', 'Insurance'),
    ('real_estate', 'Real Estate'),
    ('rental_leasing', 'Rental and Leasing'),
    ('professional_services', 'Professional Services'),
    ('scientific_services', 'Scientific Services'),
    ('technical_services', 'Technical Services'),
    ('management_companies', 'Management of Companies'),
    ('administrative_support', 'Administrative Support'),
    ('waste_management', 'Waste Management'),
    ('educational_services', 'Educational Services'),
    ('health_care', 'Health Care'),
    ('social_assistance', 'Social Assistance'),
    ('arts', 'Arts'),
    ('entertainment', 'Entertainment'),
    ('recreation', 'Recreation'),
    ('accommodation', 'Accommodation'),
    ('food_services', 'Food Services'),
    ('other_services', 'Other Services'),
    ('public_administration', 'Public Administration'),
    ('telecommunications', 'Telecommunications'),
    ('hospitality', 'Hospitality'),
    ('legal_services', 'Legal Services'),
    ('media_broadcasting', 'Media and Broadcasting'),
    ('energy', 'Energy'),
    ('renewable_energy', 'Renewable Energy'),
    ('automotive', 'Automotive'),
    ('aerospace', 'Aerospace'),
    ('defence', 'Defence'),
    ('tourism', 'Tourism')
]

COMPANY_TYPE_CHOICES = [
    # Types of companies the agency manages
    ('White Glove Client', 'White Glove Client'),
    ('Online Client', 'Online Client'),
    ('Blended', 'Blended'),
    ('Supplier', 'Supplier'),
]


ACCOUNT_STATUS_CHOICES = [
    # Statuses for the company's account relationship with the agency
    ('Trading', 'Trading'),
    ('No longer Trading', 'No longer Trading'),
    ('On hold', 'On hold'),
    ('Other', 'Other'),
]


class Company(models.Model):
    """
    Represents a company that is managed within the CRM system.
    """
    agency = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='companies', null=False)
    company_name = models.CharField(max_length=255, blank=False, null=False)
    sage_name = models.CharField(max_length=255, blank=True, null=True) 
    midoco_crm_number = models.CharField(max_length=50, blank=True, null=True)  
    
    street_address = models.CharField(max_length=255, blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    state_province = models.CharField(max_length=100, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    linkedin_social_page = models.URLField(blank=True, null=True)
    
    industry = models.CharField(max_length=255, blank=False, null=False)
    company_type = models.CharField(max_length=255, default='White Glove Client')
    company_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ops_team = models.CharField(max_length=255, blank=True, null=True)
    account_status = models.CharField(max_length=255, default='Lead')
    invoicing_type = models.CharField(max_length=100, blank=True, null=True) 

    create_date = models.DateTimeField(auto_now_add=True)
    last_activity_date = models.DateTimeField(null=True, blank=True)
    
    linked_companies = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='linked_to')

    # Contract and service-related fields
    has_new_contract_signed = models.BooleanField(default=False)  
    signed_up_corporate_schemes = models.BooleanField(default=False)  
    signed_up_travelogix = models.BooleanField(default=False)  
    meetings_events_requirements = models.BooleanField(default=False)  
    reporting_standard_bespoke = models.BooleanField(default=False)  
    access_to_travelogix = models.BooleanField(default=False)  
    travel_policy_health_check_offered = models.BooleanField(default=False) 
    testimonial_requested = models.BooleanField(default=False) 

    # Sustainability fields
    communicated_esg_support = models.BooleanField(default=False)  
    receive_co2_reporting = models.BooleanField(default=False) 
    discussed_offsetting = models.BooleanField(default=False)  

    # Goals
    our_goals = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        if not self.last_activity_date:
            self.last_activity_date = timezone.now()
        super().save(*args, **kwargs)


class Contact(models.Model):
    """
    Represents a contact associated with a company within the CRM system.

    Fields:
        - company: The company this contact is associated with.
        - first_name, last_name: The contact's name.
        - email, phone, mobile: Contact details.
        - job_title: The contact's job title.
        - department: Department in which the contact works.
        - is_primary_contact: Whether this contact is the primary contact for the company.
        - is_travel_booker_contact: Whether this contact books travel for the company.
        - is_traveller_contact: Whether this contact is a traveller.
        - is_vip_traveller_contact: Whether this contact is considered a VIP traveller.
        - notes: Additional notes about the contact.
    """
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    job_title = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    is_primary_contact = models.BooleanField(default=False)
    is_travel_booker_contact = models.BooleanField(default=False)
    is_traveller_contact = models.BooleanField(default=False)
    is_vip_traveller_contact = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company})"


class CompanyNotes(models.Model):
    """
    Represents detailed notes about a company, including policies, rates, and other information.

    Fields:
        - company: The company these notes are associated with.
        - account_number: The company's account number.
        - fop_limit: Limit for form of payment (FOP).
        - invoice_references: References for invoicing.
        - corporate_hotel_rates, corporate_airline_fares: Details of negotiated rates.
        - company_memberships: Memberships the company holds.
        - travel_policy: Travel policy for the company.
        - flight_notes, accommodation_notes, car_hire_notes, transfer_notes, rail_notes, other_notes: Various notes sections.
        - last_updated: Timestamp of the last update to the notes.
    """
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='notes')
    account_number = models.CharField(max_length=100, blank=True)
    fop_limit = models.CharField(max_length=100, blank=True)
    invoice_references = models.TextField(blank=True)
    corporate_hotel_rates = models.TextField(blank=True)
    corporate_airline_fares = models.TextField(blank=True)
    company_memberships = models.TextField(blank=True)
    travel_policy = models.TextField(blank=True)
    flight_notes = models.TextField(blank=True)
    accommodation_notes = models.TextField(blank=True)
    car_hire_notes = models.TextField(blank=True)
    transfer_notes = models.TextField(blank=True)
    rail_notes = models.TextField(blank=True)
    other_notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notes for {self.company.company_name}"


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