#agent_support/forms.py

from django import forms
from .models import AgentSupportSupplier

class AgentSupportSupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Bootstap classes to all feilds
        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    class Meta:
        model = AgentSupportSupplier
        fields = ['supplier_type', 'supplier_name', 'agent_websites', 'contact_phone', 'general_email', 'group_phone', 'group_email', 'account_manager_name', 'account_manager_email', 'account_manager_phone']
        help_texts = {
            'supplier_type': 'Select the type of supplier from the dropdown',
            'supplier_name': 'Enter the full name of the supplier',
            'agent_websites': 'Enter any relevant website URLs (one per line)',
            'contact_phone': 'Main contact number for general enquiries/support (one per line)',
            'general_email': 'Main email address for general enquiries/support (one per line)',
            'group_phone': 'Contact number for group bookings',
            'group_email': 'Email address for group booking enquiries',
            'account_manager_name': 'Your dedicated account manager\'s name',
            'account_manager_email': 'Direct email for your account manager',
            'account_manager_phone': 'Direct phone number for your account manager'
        }
        widgets = {
            'supplier_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'agent_websites': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter websites (one per line)'
            }),
            'contact_phone': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'e.g., +44 123 456 7890 (one per line)'
            }),
            'general_email': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'e.g., info@supplier.com (one per line)'
            }),
            'group_phone': forms.TextInput(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'e.g., +44 123 456 7890 (one per line)'
            }),
            'group_email': forms.EmailInput(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'e.g., group@supplier.com (one per line)'
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

        }
