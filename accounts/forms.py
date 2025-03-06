# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm
from .models import CustomUser, BusinessDomain, Business
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


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


class AdminUserCreationForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('agent', 'Agent'),
        ('marketing', 'Marketing'),
        ('admin', 'Admin'),
    ]

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'role')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        
        domain = email.split('@')[-1]
        if domain != 'easyavenues.co.uk':
            raise forms.ValidationError(
                "Only @easyavenues.co.uk email addresses are allowed."
            )
        
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email address already exists."
            )
        
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Set username to email
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = True
        
        # Set role-based permissions
        role = self.cleaned_data['role']
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = False  # Admin users are staff but not superusers
        elif role == 'agent':
            user.is_staff = True
            user.is_superuser = False
        else:  # marketing
            user.is_staff = False
            user.is_superuser = False
        
        if commit:
            user.save()
            
            # Create email address record
            from allauth.account.models import EmailAddress
            EmailAddress.objects.create(
                user=user,
                email=user.email,
                verified=False,  # User needs to verify their email
                primary=True
            )
            
            # Send verification email
            from allauth.account.utils import user_email
            from allauth.account.adapter import get_adapter
            adapter = get_adapter()
            adapter.send_confirmation_mail(self.instance, user_email(user))
        
        return user
