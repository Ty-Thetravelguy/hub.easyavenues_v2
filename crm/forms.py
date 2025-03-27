from django import forms
from django.db import models
from .models import (
    Company, Contact, ClientProfile, SupplierProfile, TransactionFee,
    INDUSTRY_CHOICES, ClientInvoiceReference, CompanyRelationship, ContactNote,
    ClientTravelPolicy, Document, Activity, EmailActivity, CallActivity,
    MeetingActivity, NoteActivity, DocumentActivity, StatusChangeActivity,
    PolicyUpdateActivity
)
from django.contrib.auth import get_user_model
import datetime
import logging

User = get_user_model()

class CompanyForm(forms.ModelForm):
    """
    Dynamic form for creating/editing companies with their respective profiles.
    """
    industry = forms.ChoiceField(
        choices=INDUSTRY_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Invoice reference fields - hidden fields that will be populated by the modal
    invoice_references = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.MultipleHiddenInput(),
        label='Invoice References'
    )
    
    mandatory_references = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.MultipleHiddenInput(),
        label='Mandatory References'
    )
    
    class Meta:
        model = Company
        fields = [
            'company_name', 'company_type', 'industry',
            'street_address', 'city', 'state_province', 'postal_code', 'country',
            'phone_number', 'email', 'description', 'linkedin_social_page',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        # Set up invoice references queryset - only for clients
        from accounts.models import InvoiceReference
        if not instance or instance.company_type == 'Client':
            self.fields['invoice_references'].queryset = InvoiceReference.objects.all()
            self.fields['mandatory_references'].queryset = InvoiceReference.objects.all()
        else:
            # Remove invoice reference fields for suppliers
            if 'invoice_references' in self.fields:
                del self.fields['invoice_references']
            if 'mandatory_references' in self.fields:
                del self.fields['mandatory_references']
        
        # If we have an instance and it's a client, set initial values
        if instance and instance.company_type == 'Client' and hasattr(instance, 'client_profile'):
            client_profile = instance.client_profile
            # Set initial values for invoice references
            if 'invoice_references' in self.fields:
                self.fields['invoice_references'].initial = client_profile.invoice_reference_options.all()
            if 'mandatory_references' in self.fields:
                self.fields['mandatory_references'].initial = client_profile.invoice_reference_options.filter(
                    clientinvoicereference__is_mandatory=True
                )

        # Add Bootstrap classes to all fields
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.HiddenInput, forms.MultipleHiddenInput)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})

        # Add client-specific fields if company_type is Client
        if instance and instance.company_type == 'Client':
            self.add_client_fields(instance)
        elif instance and instance.company_type == 'Supplier':
            self.add_supplier_fields(instance)

        # Add data-type attribute to company_type field for JavaScript handling
        self.fields['company_type'].widget.attrs.update({
            'class': 'form-control company-type-select',
            'data-client-fields': ','.join(self.get_client_field_names()),
            'data-supplier-fields': ','.join(self.get_supplier_field_names()),
        })

    def get_client_field_names(self):
        """Get list of client-specific field names."""
        return [
            'client_type', 'client_status', 'sage_name', 'midoco_crm_number',
            'invoicing_type', 'invoicing_frequency', 'payment_terms', 
            'client_account_manager', 'client_ops_team', 'invoice_reference_options',
            'corporate_hotel_rates', 'corporate_airline_fares', 'company_memberships',
            'has_new_contract_signed', 'signed_up_corporate_schemes',
            'signed_up_travelogix', 'meetings_events_requirements',
            'reporting_standard_bespoke', 'access_to_travelogix',
            'travel_policy_health_check_offered', 'testimonial_requested',
            'communicated_esg_support', 'receive_co2_reporting', 'discussed_offsetting'
        ]

    def get_supplier_field_names(self):
        """Get list of supplier-specific field names."""
        return [
            'supplier_type', 'supplier_status', 'supplier_for_department',
            'supplier_owner', 'invoicing_type', 'invoicing_frequency',
            'payment_terms', 'new_supplier_form_signed', 'contract_signed'
        ]

    def add_client_fields(self, instance):
        """Add fields specific to clients."""
        client_profile = instance.client_profile if instance else None
        
        # Add all client-specific fields
        for field_name in self.get_client_field_names():
            if hasattr(ClientProfile, field_name):
                field = ClientProfile._meta.get_field(field_name)
                
                # Special handling for client_account_manager field
                if field_name == 'client_account_manager':
                    self.fields[field_name] = forms.ModelChoiceField(
                        queryset=User.objects.all(),
                        required=False,
                        initial=getattr(client_profile, field_name) if client_profile else None,
                        widget=forms.Select(attrs={'class': 'form-control'}),
                        label='Account Manager'
                    )
                elif field_name == 'invoice_reference_options':
                    # This field is already set up in __init__
                    if client_profile:
                        self.initial[field_name] = client_profile.invoice_reference_options.all()
                elif isinstance(field, models.BooleanField):
                    self.fields[field_name] = forms.BooleanField(
                        required=False,
                        initial=getattr(client_profile, field_name) if client_profile else False,
                        widget=forms.CheckboxInput(attrs={
                            'class': 'form-check-input',
                            'role': 'switch'
                        })
                    )
                elif hasattr(field, 'choices') and field.choices:
                    self.fields[field_name] = forms.ChoiceField(
                        choices=field.choices,
                        required=not field.blank,
                        initial=getattr(client_profile, field_name) if client_profile else None,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
                else:
                    self.fields[field_name] = forms.CharField(
                        required=not field.blank,
                        initial=getattr(client_profile, field_name) if client_profile else None,
                        widget=forms.TextInput(attrs={'class': 'form-control'})
                    )

    def add_supplier_fields(self, instance):
        """Add fields specific to suppliers."""
        supplier_profile = instance.supplier_profile if instance else None
        
        # Add all supplier-specific fields
        for field_name in self.get_supplier_field_names():
            if hasattr(SupplierProfile, field_name):
                field = SupplierProfile._meta.get_field(field_name)
                
                # Special handling for supplier_owner field
                if field_name == 'supplier_owner':
                    self.fields[field_name] = forms.ModelChoiceField(
                        queryset=User.objects.all(),
                        required=False,
                        initial=getattr(supplier_profile, field_name) if supplier_profile else None,
                        widget=forms.HiddenInput()
                    )
                elif isinstance(field, models.BooleanField):
                    self.fields[field_name] = forms.BooleanField(
                        required=False,
                        initial=getattr(supplier_profile, field_name) if supplier_profile else False,
                        widget=forms.CheckboxInput(attrs={
                            'class': 'form-check-input',
                            'role': 'switch'
                        })
                    )
                elif hasattr(field, 'choices') and field.choices:
                    self.fields[field_name] = forms.ChoiceField(
                        choices=field.choices,
                        required=not field.blank,
                        initial=getattr(supplier_profile, field_name) if supplier_profile else None,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
                else:
                    self.fields[field_name] = forms.CharField(
                        required=not field.blank,
                        initial=getattr(supplier_profile, field_name) if supplier_profile else None,
                        widget=forms.TextInput(attrs={'class': 'form-control'})
                    )

    def save(self, commit=True):
        company = super().save(commit=False)
        if commit:
            company.save()
            
            if company.company_type == 'Client':
                client_profile, created = ClientProfile.objects.get_or_create(company=company)
                
                # Update all client profile fields from cleaned_data
                for field_name in self.get_client_field_names():
                    if field_name in self.cleaned_data and hasattr(client_profile, field_name):
                        setattr(client_profile, field_name, self.cleaned_data[field_name])
                
                # Handle invoice references
                selected_references = self.cleaned_data.get('invoice_references', [])
                mandatory_references = self.cleaned_data.get('mandatory_references', [])
                
                # Clear existing references
                ClientInvoiceReference.objects.filter(client_profile=client_profile).delete()
                
                # Add new references
                for reference in selected_references:
                    ClientInvoiceReference.objects.create(
                        client_profile=client_profile,
                        invoice_reference=reference,
                        is_mandatory=reference in mandatory_references
                    )
                
                client_profile.save()
            elif company.company_type == 'Supplier':
                supplier_profile, created = SupplierProfile.objects.get_or_create(company=company)
                
                # Update all supplier profile fields from cleaned_data
                for field_name in self.get_supplier_field_names():
                    if field_name in self.cleaned_data and hasattr(supplier_profile, field_name):
                        setattr(supplier_profile, field_name, self.cleaned_data[field_name])
                
                supplier_profile.save()
            
        return company

    def clean(self):
        cleaned_data = super().clean()
        mandatory_refs = cleaned_data.get('mandatory_references', [])
        selected_refs = cleaned_data.get('invoice_references', [])
        
        # Ensure all mandatory references are also selected
        for ref in mandatory_refs:
            if ref not in selected_refs:
                self.add_error('mandatory_references', 
                             f'Reference "{ref}" is marked as mandatory but not selected')
        
        return cleaned_data

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'job_role', 'email',
            'landline', 'mobile', 'date_of_birth', 'hospitality'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'job_role': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'landline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hospitality': forms.TextInput(attrs={'class': 'form-control'})
        }

    tags = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            # Set available tags based on company type
            if company.company_type == 'Client':
                self.fields['tags'].choices = Contact.CONTACT_TAG_CHOICES
            else:
                self.fields['tags'].choices = Contact.SUPPLIER_TAG_CHOICES

            # Set initial tags if editing
            if self.instance.pk:
                self.fields['tags'].initial = self.instance.tag_list

    def save(self, commit=True):
        contact = super().save(commit=False)
        contact.tag_list = self.cleaned_data.get('tags', [])
        if commit:
            contact.save()
        return contact

class ContactNoteForm(forms.ModelForm):
    class Meta:
        model = ContactNote
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

class TransactionFeeForm(forms.ModelForm):
    class Meta:
        model = TransactionFee
        fields = ['service', 'online_fee', 'offline_fee']
        widgets = {
            'online_fee': forms.NumberInput(attrs={'step': '0.01'}),
            'offline_fee': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class ManageRelationshipsForm(forms.Form):
    """
    Form for managing company relationships.
    """
    relationship_type = forms.ChoiceField(
        choices=CompanyRelationship.RELATIONSHIP_TYPES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    to_company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )

# Form for company relationships
class CompanyRelationshipForm(forms.ModelForm):
    class Meta:
        model = CompanyRelationship
        fields = ['to_company', 'relationship_type', 'description']
        widgets = {
            'to_company': forms.Select(attrs={'class': 'form-control'}),
            'relationship_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.from_company = kwargs.pop('from_company', None)
        super().__init__(*args, **kwargs)
        
        # Filter the to_company queryset to exclude the current company
        if self.from_company:
            self.fields['to_company'].queryset = Company.objects.exclude(
                id=self.from_company.id
            )
            
            # Filter by company type if needed
            if self.from_company.company_type == 'Client':
                # For clients, allow linking to other clients only
                self.fields['to_company'].queryset = self.fields['to_company'].queryset.filter(
                    company_type='Client'
                )
            elif self.from_company.company_type == 'Supplier':
                # For suppliers, allow linking to other suppliers only  
                self.fields['to_company'].queryset = self.fields['to_company'].queryset.filter(
                    company_type='Supplier'
                )

# Create a formset for ClientInvoiceReference
ClientInvoiceReferenceFormSet = forms.inlineformset_factory(
    ClientProfile, 
    ClientInvoiceReference,
    fields=('invoice_reference', 'is_mandatory'),
    extra=1,
    can_delete=True
)

class TravelPolicyForm(forms.ModelForm):
    """
    Form for creating and updating travel policies.
    """
    effective_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=datetime.date.today
    )
    
    class Meta:
        model = ClientTravelPolicy
        fields = [
            'policy_name', 'effective_date', 'is_active', 
            'travel_policy', 'flight_notes', 'accommodation_notes',
            'car_hire_notes', 'transfer_notes', 'rail_notes', 'other_notes'
        ]
        widgets = {
            'policy_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'travel_policy': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'flight_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'accommodation_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'car_hire_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'transfer_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'rail_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'other_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'travel_policy': 'Travel Policy Overview',
            'flight_notes': 'Flight Policy',
            'accommodation_notes': 'Accommodation Policy',
            'car_hire_notes': 'Car Hire Policy',
            'transfer_notes': 'Transfers/Taxi Policy',
            'rail_notes': 'Rail Policy',
            'other_notes': 'Other Policy Details',
        }

class DocumentUploadForm(forms.ModelForm):
    """
    Form for uploading documents related to companies.
    """
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    class Meta:
        model = Document
        fields = [
            'title', 'document_type', 'file', 'expiry_date', 
            'description', 'version', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class EmailActivityForm(forms.ModelForm):
    email_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Select date'
        })
    )
    email_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
            'placeholder': 'Select time'
        })
    )
    subject = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email subject'
        }),
        required=True
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Start typing to log an email...'
        }),
        required=True
    )
    recipients = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control select2-multiple',
            'multiple': 'multiple'
        }),
        help_text="Search and select contacts or staff members",
        required=True
    )
    
    class Meta:
        model = EmailActivity
        fields = ['recipients', 'email_date', 'email_time', 'subject', 'body', 'email_outcome']
        widgets = {
            'email_outcome': forms.Select(
                attrs={'class': 'form-select'},
                choices=[
                    ('Sent', 'Sent'),
                    ('Received', 'Received'),
                    ('No Response', 'No Response')
                ]
            )
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Set default values for date and time if not provided
        if not self.fields['email_date'].initial:
            self.fields['email_date'].initial = datetime.date.today()
        if not self.fields['email_time'].initial:
            self.fields['email_time'].initial = datetime.datetime.now().strftime('%H:%M')

    def clean_recipients(self):
        """Clean recipients data from Select2 AJAX."""
        logger = logging.getLogger(__name__)
        
        recipients = self.cleaned_data.get('recipients', [])
        logger.debug(f"⚙️ FORM: Cleaning recipients: {recipients!r}")
        
        if not recipients:
            raise forms.ValidationError('Please select at least one recipient.')
        
        # Handle both string and list formats
        recipient_list = []
        if isinstance(recipients, str):
            # Split comma-separated string (from Select2 multiple)
            recipient_list = [r.strip() for r in recipients.split(',') if r.strip()]
            logger.debug(f"⚙️ FORM: Split recipients into list: {recipient_list}")
        elif isinstance(recipients, list):
            recipient_list = recipients
            logger.debug(f"⚙️ FORM: Recipients already in list format: {recipient_list}")
        else:
            logger.warning(f"⚙️ FORM: Unexpected recipients format: {type(recipients)}")
        
        cleaned_recipients = []
        for recipient in recipient_list:
            if not recipient:
                continue
                
            try:
                # Handle both 'type_id' format and separate type/id
                if isinstance(recipient, str) and '_' in recipient:
                    recipient_type, recipient_id = recipient.split('_')
                    recipient_id = int(recipient_id)
                    logger.debug(f"⚙️ FORM: Processing recipient: type={recipient_type}, id={recipient_id}")
                elif isinstance(recipient, dict) and 'id' in recipient and 'type' in recipient:
                    # Handle dictionary format from Select2 AJAX
                    recipient_type = recipient['type']
                    if '_' in recipient['id']:
                        # Extract ID from string like 'contact_123'
                        recipient_id = int(recipient['id'].split('_')[1])
                    else:
                        recipient_id = int(recipient['id'])
                    logger.debug(f"⚙️ FORM: Processing dict recipient: {recipient}")
                else:
                    logger.warning(f"⚙️ FORM: Cannot parse recipient: {recipient!r}")
                    continue
                
                if recipient_type == 'contact':
                    # Fetch contact regardless of company to support contacts from any company
                    contact = Contact.objects.filter(id=recipient_id).first()
                    if contact:
                        logger.debug(f"⚙️ FORM: Found valid contact: {contact}")
                        cleaned_recipients.append(('contact', contact))
                    else:
                        logger.warning(f"⚙️ FORM: Contact not found: id={recipient_id}")
                        
                elif recipient_type == 'user':
                    # Verify user exists and is active
                    User = get_user_model()
                    user = User.objects.filter(
                        id=recipient_id,
                        is_active=True
                    ).first()
                    if user:
                        logger.debug(f"⚙️ FORM: Found valid user: {user}")
                        cleaned_recipients.append(('user', user))
                    else:
                        logger.warning(f"⚙️ FORM: User not found or not active: id={recipient_id}")
                        
            except (ValueError, AttributeError) as e:
                logger.error(f"⚙️ FORM: Error processing recipient {recipient!r}: {e}")
                continue
        
        if not cleaned_recipients:
            logger.error("⚙️ FORM: No valid recipients found")
            raise forms.ValidationError('Please select at least one valid recipient.')
            
        logger.debug(f"⚙️ FORM: Final cleaned recipients: {cleaned_recipients}")
        return cleaned_recipients

    def save(self, commit=True):
        """Save the email activity and associate recipients."""
        instance = super().save(commit=False)
        
        # Set activity type
        instance.activity_type = 'email'
        
        if commit:
            instance.save()
            
            # Get cleaned recipients from clean_recipients method
            recipients = self.cleaned_data.get('recipients', [])
            
            # Clear existing recipients
            instance.contact_recipients.clear()
            instance.user_recipients.clear()
            
            # Add new recipients
            for recipient_type, recipient in recipients:
                if recipient_type == 'contact':
                    instance.contact_recipients.add(recipient)
                elif recipient_type == 'user':
                    instance.user_recipients.add(recipient)
            
            # Save many-to-many relationships
            instance.save()
        
        return instance

class CallActivityForm(forms.ModelForm):
    class Meta:
        model = CallActivity
        fields = [
            'call_type', 'duration', 'summary', 'description',
            'call_outcome', 'scheduled_for', 'follow_up_date', 'follow_up_notes'
        ]
        widgets = {
            'call_type': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'call_outcome': forms.TextInput(attrs={'class': 'form-control'}),
            'scheduled_for': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'follow_up_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        activity = super().save(commit=False)
        activity.activity_type = 'call'
        if commit:
            activity.save()
        return activity

class MeetingActivityForm(forms.ModelForm):
    class Meta:
        model = MeetingActivity
        fields = [
            'title', 'location', 'duration', 'attendees',
            'agenda', 'minutes', 'description', 'meeting_outcome',
            'scheduled_for', 'follow_up_date', 'follow_up_notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 15, 'step': 15}),
            'attendees': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'agenda': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'minutes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'meeting_outcome': forms.TextInput(attrs={'class': 'form-control'}),
            'scheduled_for': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'follow_up_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        activity = super().save(commit=False)
        activity.activity_type = 'meeting'
        if commit:
            activity.save()
            self.save_m2m()  # Save many-to-many relationships
        return activity

class NoteActivityForm(forms.ModelForm):
    class Meta:
        model = NoteActivity
        fields = [
            'content', 'is_private', 'description',
            'note_outcome', 'follow_up_date', 'follow_up_notes'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'note_outcome': forms.TextInput(attrs={'class': 'form-control'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'follow_up_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        activity = super().save(commit=False)
        activity.activity_type = 'note'
        if commit:
            activity.save()
        return activity

class DocumentActivityForm(forms.ModelForm):
    class Meta:
        model = DocumentActivity
        fields = ['description', 'document', 'action', 'document_outcome', 'scheduled_for', 'follow_up_date', 'follow_up_notes']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'document': forms.Select(attrs={'class': 'form-control'}),
            'action': forms.Select(attrs={'class': 'form-control'}),
            'document_outcome': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'scheduled_for': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'follow_up_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.activity_type = 'document'
        if commit:
            instance.save()
        return instance

class StatusChangeActivityForm(forms.ModelForm):
    class Meta:
        model = StatusChangeActivity
        fields = ['description', 'old_status', 'new_status', 'reason', 'status_outcome', 'scheduled_for', 'follow_up_date', 'follow_up_notes']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'old_status': forms.Select(attrs={'class': 'form-control'}),
            'new_status': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status_outcome': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'scheduled_for': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'follow_up_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.activity_type = 'status_change'
        if commit:
            instance.save()
        return instance

class PolicyUpdateActivityForm(forms.ModelForm):
    class Meta:
        model = PolicyUpdateActivity
        fields = ['description', 'policy', 'action', 'changes', 'policy_outcome', 'scheduled_for', 'follow_up_date', 'follow_up_notes']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'policy': forms.Select(attrs={'class': 'form-control'}),
            'action': forms.Select(attrs={'class': 'form-control'}),
            'changes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'policy_outcome': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'scheduled_for': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'follow_up_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.activity_type = 'policy_update'
        if commit:
            instance.save()
        return instance

class WaiverFavorActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['description', 'outcome', 'follow_up_date', 'follow_up_notes']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'outcome': forms.TextInput(attrs={'class': 'form-control'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'follow_up_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # Additional fields for waiver/favor-specific data
    subject = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    waiver_type = forms.ChoiceField(
        choices=[
            ('waiver', 'Waiver'),
            ('favor', 'Favor'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    value_amount = forms.DecimalField(
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    approved_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    def save(self, commit=True):
        activity = super().save(commit=False)
        activity.activity_type = 'waiver'
        
        # Store waiver/favor-specific data in the data JSONField
        activity.data = {
            'subject': self.cleaned_data['subject'],
            'waiver_type': self.cleaned_data['waiver_type'],
            'value_amount': str(self.cleaned_data['value_amount']),
            'approved_by': self.cleaned_data['approved_by'].id,
            'contacts': [contact.id for contact in self.cleaned_data['contacts']],
            'users': [user.id for user in self.cleaned_data['users']],
        }
        
        if commit:
            activity.save()
        
        return activity

class ToDoTaskForm(forms.Form):
    to_do_task_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    to_do_task_message = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    ) 