from django import forms
from django.db import models
from .models import Company, Contact, ClientProfile, SupplierProfile, TransactionFee, INDUSTRY_CHOICES
from django.contrib.auth import get_user_model

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
        
        # Add Bootstrap classes to all fields
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
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
            'invoice_references', 'invoicing_type', 'invoicing_frequency',
            'payment_terms', 'client_account_manager', 'client_ops_team',
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
                if isinstance(field, models.BooleanField):
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
                if isinstance(field, models.BooleanField):
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
            
            # Create or update profile based on company type
            if company.company_type == 'Client':
                client_profile, created = ClientProfile.objects.get_or_create(company=company)
                for field_name in self.get_client_field_names():
                    if field_name in self.cleaned_data:
                        setattr(client_profile, field_name, self.cleaned_data[field_name])
                client_profile.save()
            else:
                supplier_profile, created = SupplierProfile.objects.get_or_create(company=company)
                for field_name in self.get_supplier_field_names():
                    if field_name in self.cleaned_data:
                        setattr(supplier_profile, field_name, self.cleaned_data[field_name])
                supplier_profile.save()
                
        return company

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'mobile',
            'job_title', 'department', 'preferred_contact_method',
            'preferred_contact_time', 'do_not_contact', 'out_of_office_until',
            'teams_id', 'whatsapp_number', 'is_primary_contact',
            'is_primary_finance_contact', 'is_primary_hr_contact',
            'is_primary_it_contact', 'is_travel_booker_contact',
            'is_traveller_contact', 'is_vip_traveller_contact',
            'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
            'out_of_office_until': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})

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