from django import forms
from .models import Company, Contact, CompanyNotes, TransactionFee
from django.contrib.auth import get_user_model

User = get_user_model()

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'company_name', 'sage_name', 'midoco_crm_number',
            'street_address', 'city', 'state_province', 'postal_code', 'country',
            'phone_number', 'email', 'description', 'linkedin_social_page',
            'industry', 'company_type', 'company_owner', 'ops_team',
            'account_status', 'invoicing_type',
            'has_new_contract_signed', 'signed_up_corporate_schemes',
            'signed_up_travelogix', 'meetings_events_requirements',
            'reporting_standard_bespoke', 'access_to_travelogix',
            'travel_policy_health_check_offered', 'testimonial_requested',
            'communicated_esg_support', 'receive_co2_reporting',
            'discussed_offsetting', 'our_goals'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'our_goals': forms.Textarea(attrs={'rows': 4}),
            'company_owner': forms.Select(attrs={'class': 'form-select'}),
            'industry': forms.Select(attrs={'class': 'form-select'}),
            'company_type': forms.Select(attrs={'class': 'form-select'}),
            'account_status': forms.Select(attrs={'class': 'form-select'}),
            'invoicing_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            if isinstance(self.fields[field].widget, forms.Textarea):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Update company_owner queryset to only show active users
        if 'company_owner' in self.fields:
            self.fields['company_owner'].queryset = User.objects.filter(is_active=True)

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'mobile',
            'job_title', 'department', 'is_primary_contact',
            'is_travel_booker_contact', 'is_traveller_contact',
            'is_vip_traveller_contact', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            if isinstance(self.fields[field].widget, forms.Textarea):
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class CompanyNotesForm(forms.ModelForm):
    class Meta:
        model = CompanyNotes
        fields = [
            'account_number', 'fop_limit', 'invoice_references',
            'corporate_hotel_rates', 'corporate_airline_fares',
            'company_memberships', 'travel_policy', 'flight_notes',
            'accommodation_notes', 'car_hire_notes', 'transfer_notes',
            'rail_notes', 'other_notes'
        ]
        widgets = {
            'invoice_references': forms.Textarea(attrs={'rows': 3}),
            'corporate_hotel_rates': forms.Textarea(attrs={'rows': 3}),
            'corporate_airline_fares': forms.Textarea(attrs={'rows': 3}),
            'company_memberships': forms.Textarea(attrs={'rows': 3}),
            'travel_policy': forms.Textarea(attrs={'rows': 4}),
            'flight_notes': forms.Textarea(attrs={'rows': 3}),
            'accommodation_notes': forms.Textarea(attrs={'rows': 3}),
            'car_hire_notes': forms.Textarea(attrs={'rows': 3}),
            'transfer_notes': forms.Textarea(attrs={'rows': 3}),
            'rail_notes': forms.Textarea(attrs={'rows': 3}),
            'other_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            if isinstance(self.fields[field].widget, forms.Textarea):
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