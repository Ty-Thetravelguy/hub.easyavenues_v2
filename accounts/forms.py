# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm
from .models import CustomUser, BusinessDomain, Business, Team, InvoiceReference
from django.core.validators import RegexValidator, validate_email
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
import uuid
from django.db import transaction
import logging
from django.urls import reverse
from django.utils.http import int_to_base36
from django.contrib.auth import get_user_model

User = get_user_model()

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
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    business = forms.ModelChoiceField(
        queryset=Business.objects.filter(active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'role', 'business')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        user = kwargs.pop('user', None)  # Get the user creating the form
        super().__init__(*args, **kwargs)
        
        # Filter role choices based on the user's permissions
        if user and user.is_superuser:
            self.fields['role'].choices = CustomUser.ROLE_CHOICES
        else:
            # Non-superusers can't create superusers
            self.fields['role'].choices = [
                choice for choice in CustomUser.ROLE_CHOICES 
                if choice[0] != 'superuser'
            ]
        
        # Set 'agent' as the default selected value
        self.initial['role'] = 'agent'

        # If there's only one business, select it by default
        if Business.objects.filter(active=True).count() == 1:
            self.initial['business'] = Business.objects.filter(active=True).first()

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
        try:
            # First create and save the user
            user = super().save(commit=False)
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.is_active = True
            user.role = self.cleaned_data['role']
            user.business = self.cleaned_data['business']

            # Set temporary password
            temp_password = uuid.uuid4().hex[:10]
            user.set_password(temp_password)
            
            # Save user
            user.save()

            # Create EmailAddress record
            from allauth.account.models import EmailAddress
            email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False
            )

            # Send password reset email
            try:
                from allauth.account.adapter import get_adapter
                from allauth.account.utils import user_email
                from django.contrib.sites.shortcuts import get_current_site
                from allauth.account.forms import default_token_generator
                logger = logging.getLogger('accounts')
                
                adapter = get_adapter(self.request)
                current_site = get_current_site(self.request)
                
                # Generate the reset token using AllAuth's token generator
                temp_key = default_token_generator.make_token(user)
                
                logger.info(f"Sending password set email to {user.email}")
                
                # Generate password reset URL
                uidb36 = int_to_base36(user.id)
                path = reverse("account_reset_password_from_key",
                    kwargs={"uidb36": uidb36, "key": temp_key})
                password_reset_url = self.request.build_absolute_uri(path)
                
                # Include the temp_key in the context
                adapter.send_mail(
                    'account/email/password_reset_key',
                    user.email,
                    {
                        'user': user,
                        'current_site': current_site,
                        'key': temp_key,
                        'password_reset_url': password_reset_url,
                    }
                )
                
                logger.info(f"Password set email sent successfully to {user.email}")
                
            except Exception as mail_error:
                logger.error(f"Failed to send password set email: {str(mail_error)}")
                # Don't raise the error since the user is created
                pass

            return user

        except Exception as e:
            if 'user' in locals() and user.pk:
                try:
                    user.delete()
                except Exception:
                    pass
            
            raise forms.ValidationError(f"Failed to create user: {str(e)}")


class EditUserForm(forms.ModelForm):
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
        choices=CustomUser.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'role', 'is_active')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        
        domain = email.split('@')[-1]
        if domain != 'easyavenues.co.uk':
            raise forms.ValidationError(
                "Only @easyavenues.co.uk email addresses are allowed."
            )
        
        # Check if email exists for other users
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "A user with this email address already exists."
            )
        
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        user.is_active = self.cleaned_data['is_active']
        
        if commit:
            user.save()
            
            # Update email address record if email changed
            from allauth.account.models import EmailAddress
            email_address = EmailAddress.objects.filter(user=user).first()
            if email_address and email_address.email != user.email:
                email_address.email = user.email
                email_address.verified = False  # Require re-verification if email changed
                email_address.save()
                
                # Send verification email
                from allauth.account.utils import user_email
                from allauth.account.adapter import get_adapter
                adapter = get_adapter()
                adapter.send_confirmation_mail(self.instance, user_email(user))
        
        return user

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class InvoiceReferenceForm(forms.ModelForm):
    class Meta:
        model = InvoiceReference
        fields = ['name', 'backoffice_code', 'amadeus_code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'backoffice_code': forms.TextInput(attrs={'class': 'form-control'}),
            'amadeus_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
