# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm
from .models import CustomUser, BusinessDomain, Business


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', 
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, label='Last Name',
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        
        domain = email.split('@')[-1]
        
        try:
            business_domain = BusinessDomain.objects.get(domain=domain, active=True)
            self.business = business_domain.business
        except BusinessDomain.DoesNotExist:
            raise forms.ValidationError(
                "This email domain is not authorized. Please use your company email address or contact your administrator."
            )
        
        return email

    def save(self, request):
        user = super().save(request)
        
        # Set additional fields
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.username = self.cleaned_data.get('email')  # Set username to email
        user.business = getattr(self, 'business', None)
        
        user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any custom initialization here if needed
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
