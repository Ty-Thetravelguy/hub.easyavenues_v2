from django import forms
from .models import AgentSupportSupplier

class AgentSupportSupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    class Meta:
        model = AgentSupportSupplier
        fields = [
            'supplier_type', 
            'supplier_name',
            'agent_websites', 
            'contact_phone',  
            'general_email',   
            'group_phone',
            'group_email',
            'account_manager_name',
            'account_manager_email',
            'account_manager_phone',
            'other_notes'
        ]
        widgets = {
            'supplier_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'agent_websites': forms.HiddenInput(),
            'contact_phone': forms.HiddenInput(),
            'general_email': forms.HiddenInput(),
            'group_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +44 123 456 7890'
            }),
            'group_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., group@supplier.com'
            }),
            'account_manager_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., John Smith'
            }),
            'account_manager_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., john.smith@supplier.com'
            }),
            'account_manager_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +44 123 456 7890'
            }),
            'other_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter any additional notes about the supplier'
            }),
        }
        help_texts = {
            'supplier_type': 'Select the type of supplier from the dropdown',
            'supplier_name': 'Enter the full name of the supplier',
            'group_phone': 'Contact number for group bookings',
            'group_email': 'Email address for group booking enquiries',
            'account_manager_name': 'Your dedicated account manager\'s name',
            'account_manager_email': 'Direct email for your account manager',
            'account_manager_phone': 'Direct phone number for your account manager',
            'other_notes': 'Additional notes about the supplier'
        }