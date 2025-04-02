from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import (
    Company, Contact, ClientProfile, SupplierProfile, INDUSTRY_CHOICES, 
    COMPANY_TYPE, CLIENT_TYPE_CHOICES, CLIENT_STATUS_CHOICES, 
    SUPPLIER_TYPE_CHOICES, SUPPLIER_STATUS_CHOICES, SUPPLIER_FOR_DEPARTMENT_CHOICES, 
    ClientInvoiceReference, CompanyRelationship, ContactNote, Document, 
    Activity, ClientTravelPolicy, NoteActivity
)
from accounts.models import InvoiceReference
from django.urls import reverse_lazy, reverse
from formtools.wizard.views import SessionWizardView
from django.shortcuts import redirect
from django.contrib import messages
from django import forms
from .forms import (
    CompanyForm, CompanyRelationshipForm, ContactForm, ContactNoteForm, 
    DocumentUploadForm, ManageRelationshipsForm, ClientInvoiceReferenceFormSet, 
    TravelPolicyForm, EmailActivityForm, CallActivityForm, MeetingActivityForm, 
    NoteActivityForm, WaiverFavorActivityForm, ToDoTaskForm, DocumentActivityForm,
    StatusChangeActivityForm, PolicyUpdateActivityForm
)
from django.contrib.auth import get_user_model
from accounts.models import Team
import json
from django.http import JsonResponse, HttpResponseRedirect, Http404
from .utils import hubspot_api
from django.conf import settings
import requests
import re
import os
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.db import connection
from django.db.models.functions import Concat
from django.db.models import Value
import datetime
from django.utils import timezone
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
import logging

# Create your views here.

def crm(request):
    return render(request, 'crm/crm.html')

@login_required
def company_list(request):
    """
    View a list of all companies
    """
    # Get companies ordered by name
    companies = Company.objects.all().order_by('company_name')
    
    # Handle filtering by company type
    company_type = request.GET.get('type', None)
    if company_type:
        companies = companies.filter(company_type=company_type)
    
    # Get company types for filter dropdown
    company_types = COMPANY_TYPE
    
    context = {
        'companies': companies,
        'company_types': company_types,
        'selected_type': company_type,
    }
    
    return render(request, 'crm/company_list.html', context)

@login_required
def company_detail(request, pk):
    """Display company details."""
    company = get_object_or_404(Company, id=pk)
    
    # Get all contacts for this company
    contacts = company.contacts.all().order_by('first_name', 'last_name')
    
    # Get all documents for this company
    documents = company.documents.all().order_by('-uploaded_at')
    
    # Get travel policies if company is a client
    travel_policies = None
    if company.company_type == 'Client':
        travel_policies = company.travel_policies.all().order_by('-last_updated')
    
    # Get all activities
    activities = company.activities.all().order_by('-performed_at')
    
    # Initialize all activity forms
    email_form = EmailActivityForm(company=company)
    call_form = CallActivityForm()
    meeting_form = MeetingActivityForm()
    note_form = NoteActivityForm()
    waiver_form = WaiverFavorActivityForm()
    todo_form = ToDoTaskForm()
    
    context = {
        'company': company,
        'contacts': contacts,
        'documents': documents,
        'travel_policies': travel_policies,
        'activities': activities,
        # Add forms to context
        'email_form': email_form,
        'call_form': call_form,
        'meeting_form': meeting_form,
        'note_form': note_form,
        'waiver_form': waiver_form,
        'todo_form': todo_form,
    }
    
    return render(request, 'crm/company_detail.html', context)

class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'crm/company_form.html'
    
    def get_success_url(self):
        return reverse_lazy('crm:company_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Update {self.object.company_name}"
        context['submit_text'] = "Update Company"
        context['teams'] = Team.objects.all()
        
        # Only add invoice reference data for clients
        if self.object.company_type == 'Client':
            # Add invoice reference data for the modal
            all_references = InvoiceReference.objects.all()
            selected_references_ids = []
            mandatory_references_ids = []
            
            if hasattr(self.object, 'client_profile'):
                for ref in self.object.client_profile.invoice_reference_options.all():
                    selected_references_ids.append(ref.id)
                    if ref.clientinvoicereference_set.get(client_profile=self.object.client_profile).is_mandatory:
                        mandatory_references_ids.append(ref.id)
            
            context.update({
                'all_references': all_references,
                'selected_references_ids': selected_references_ids,
                'mandatory_references_ids': mandatory_references_ids,
            })
        
        return context

    def form_valid(self, form):
        messages.success(self.request, f"{self.object.company_name} has been updated successfully.")
        return super().form_valid(form)

class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'crm/contact_form.html'
    success_url = reverse_lazy('crm:company_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        company_id = self.kwargs.get('company_id')
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                kwargs['company'] = company
            except Company.DoesNotExist:
                messages.error(self.request, "Company not found. Please create the company first.")
                return redirect('crm:company_list')
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        company_id = self.kwargs.get('company_id')
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                form.instance.company = company
            except Company.DoesNotExist:
                messages.error(self.request, "Company not found. Please create the company first.")
                return redirect('crm:company_list')
                
        # Save the form to create the contact
        response = super().form_valid(form)
        
        # Create an activity record for the contact creation
        Activity.objects.create(
            company=form.instance.company,
            contact=form.instance,
            activity_type='status_change',
            description=f"Contact {form.instance.first_name} {form.instance.last_name} was created",
            performed_by=self.request.user,
            is_system_activity=True
        )
        
        messages.success(self.request, "Contact created successfully.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.kwargs.get('company_id')
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                context['company'] = company
                context['title'] = f"Add Contact to {company.company_name}"
            except Company.DoesNotExist:
                messages.error(self.request, "Company not found. Please create the company first.")
                return redirect('crm:company_list')
        else:
            context['title'] = "Add Contact"
            
        context['submit_text'] = "Create Contact"
        return context

class CompanyTypeForm(forms.Form):
    company_type = forms.ChoiceField(
        choices=COMPANY_TYPE,
        widget=forms.RadioSelect(attrs={
            'class': 'btn-check',
            'required': 'required'
        }),
        label="Select Company Type",
        required=True,
        initial=None
    )

COMPANY_FORMS = [
    ('type', CompanyTypeForm),  # Use our custom form for company type selection
    ('basic', forms.Form),  # Will create this form for basic company info
    ('profile', forms.Form),  # Will create this form for type-specific fields
]

class CompanyCreateWizardView(LoginRequiredMixin, SessionWizardView):
    template_name = 'crm/company_wizard_form.html'
    form_list = COMPANY_FORMS

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        
        # Customize each form based on the step
        if step is None:
            step = self.steps.current
            
        if step == 'basic':
            # Second step: Basic Company Information
            form.fields.update({
                'company_name': forms.CharField(max_length=255),
                'industry': forms.ChoiceField(choices=INDUSTRY_CHOICES),
                'street_address': forms.CharField(max_length=255),
                'city': forms.CharField(max_length=100),
                'state_province': forms.CharField(max_length=100),
                'postal_code': forms.CharField(max_length=20),
                'country': forms.CharField(max_length=100),
                'phone_number': forms.CharField(max_length=20, required=False),
                'email': forms.EmailField(),
                'description': forms.CharField(widget=forms.Textarea, required=False),
                'linkedin_social_page': forms.URLField(required=False),
            })
        elif step == 'profile':
            # Third step: Type-specific fields
            company_type = self.get_cleaned_data_for_step('type')['company_type']
            if company_type == 'Client':
                # Basic Client Information
                form.fields.update({
                    'client_type': forms.ChoiceField(choices=CLIENT_TYPE_CHOICES, label='Client Type'),
                    'client_status': forms.ChoiceField(choices=CLIENT_STATUS_CHOICES, label='Client Status'),
                    'client_account_manager': forms.ModelChoiceField(
                        queryset=get_user_model().objects.all(),
                        required=False,
                        label='Account Manager'
                    ),
                    'client_ops_team': forms.CharField(max_length=255, required=False, label='Operations Team'),
                    
                    # Finance/Invoice Information
                    'sage_name': forms.CharField(max_length=255, required=False, label='Sage Name'),
                    'midoco_crm_number': forms.CharField(max_length=255, required=False, label='Midoco CRM Number'),
                    'invoice_reference_options': forms.ModelMultipleChoiceField(
                        queryset=InvoiceReference.objects.all(),
                        required=False,
                        widget=forms.MultipleHiddenInput(),
                        label='Invoice References'
                    ),
                    'mandatory_references': forms.ModelMultipleChoiceField(
                        queryset=InvoiceReference.objects.all(),
                        required=False,
                        widget=forms.MultipleHiddenInput(),
                        label='Mandatory References'
                    ),
                    'invoicing_type': forms.CharField(max_length=100, required=False, label='Invoicing Type'),
                    'invoicing_frequency': forms.CharField(max_length=100, required=False, label='Invoicing Frequency'),
                    'payment_terms': forms.CharField(max_length=100, required=False, label='Payment Terms'),
                    
                    # Corporate Benefits
                    'corporate_hotel_rates': forms.CharField(widget=forms.Textarea, required=False, label='Corporate Hotel Rates'),
                    'corporate_airline_fares': forms.CharField(widget=forms.Textarea, required=False, label='Corporate Airline Fares'),
                    'company_memberships': forms.CharField(widget=forms.Textarea, required=False, label='Company Memberships'),
                    
                    # Service Status
                    'has_new_contract_signed': forms.BooleanField(required=False, label='New Contract Signed'),
                    'signed_up_corporate_schemes': forms.BooleanField(required=False, label='Signed Up for Corporate Schemes'),
                    'signed_up_travelogix': forms.BooleanField(required=False, label='Signed Up for Travelogix'),
                    'meetings_events_requirements': forms.BooleanField(required=False, label='Has Meetings & Events Requirements'),
                    'reporting_standard_bespoke': forms.BooleanField(required=False, label='Has Standard/Bespoke Reporting'),
                    'access_to_travelogix': forms.BooleanField(required=False, label='Has Access to Travelogix'),
                    'travel_policy_health_check_offered': forms.BooleanField(required=False, label='Travel Policy Health Check Offered'),
                    'testimonial_requested': forms.BooleanField(required=False, label='Testimonial Requested'),
                    
                    # Sustainability Information
                    'communicated_esg_support': forms.BooleanField(required=False, label='ESG Support Communicated'),
                    'receive_co2_reporting': forms.BooleanField(required=False, label='Receives CO2 Reporting'),
                    'discussed_offsetting': forms.BooleanField(required=False, label='Offsetting Discussed')
                })
            else:
                form.fields.update({
                    'supplier_type': forms.ChoiceField(choices=SUPPLIER_TYPE_CHOICES),
                    'supplier_status': forms.ChoiceField(choices=SUPPLIER_STATUS_CHOICES),
                    'supplier_for_department': forms.ChoiceField(choices=SUPPLIER_FOR_DEPARTMENT_CHOICES),
                    'supplier_owner': forms.ModelChoiceField(
                        queryset=get_user_model().objects.all(),
                        required=False,
                        label='Supplier Owner'
                    ),
                    'invoicing_type': forms.CharField(max_length=100, required=False, label='Invoicing Type'),
                    'invoicing_frequency': forms.CharField(max_length=100, required=False, label='Invoicing Frequency'),
                    'payment_terms': forms.CharField(max_length=100, required=False, label='Payment Terms'),
                    'new_supplier_form_signed': forms.BooleanField(required=False, label='New Supplier Form Signed'),
                    'contract_signed': forms.BooleanField(required=False, label='Contract Signed')
                })

        # Add Bootstrap classes to all fields
        for field in form.fields.values():
            if isinstance(field.widget, (forms.TextInput, forms.Select, forms.Textarea, forms.URLInput, forms.EmailInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})

        return form

    def done(self, form_list, **kwargs):
        # Get cleaned data from all steps
        type_data = self.get_cleaned_data_for_step('type')
        basic_data = self.get_cleaned_data_for_step('basic')
        profile_data = self.get_cleaned_data_for_step('profile')

        try:
            # Create the company with the agency
            company = Company.objects.create(
                company_type=type_data['company_type'],
                agency=self.request.user.business,  # Set the agency from the logged-in user's business
                **basic_data
            )

            # Create the appropriate profile
            if type_data['company_type'] == 'Client':
                ClientProfile.objects.create(company=company, **profile_data)
            else:
                SupplierProfile.objects.create(company=company, **profile_data)

            messages.success(self.request, f"Successfully created {company.company_name}")
            return redirect('crm:company_detail', pk=company.pk)
        except Exception as e:
            messages.error(self.request, f"Error creating company: {str(e)}")
            return redirect('crm:company_list')

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context['wizard_steps_names'] = ['Company Type', 'Basic Information', 'Additional Information']
        context['teams'] = Team.objects.all()
        
        # Add invoice reference data to context if we're on the profile step for a client
        if self.steps.current == 'profile':
            # Get company type from previous step
            company_type = self.get_cleaned_data_for_step('type')['company_type']
            
            # Only add reference data for client profiles
            if company_type == 'Client':
                all_references = InvoiceReference.objects.all()
                selected_references_ids = []
                mandatory_references_ids = []
                
                # Get cleaned data from current step if it exists
                step_data = self.get_cleaned_data_for_step('profile')
                if step_data:
                    for ref in step_data.get('invoice_reference_options', []):
                        selected_references_ids.append(ref.id)
                        if ref in step_data.get('mandatory_references', []):
                            mandatory_references_ids.append(ref.id)
                
                context.update({
                    'all_references': all_references,
                    'selected_references_ids': selected_references_ids,
                    'mandatory_references_ids': mandatory_references_ids,
                    'current_step_name': 'Client Profile' if company_type == 'Client' else 'Supplier Profile'
                })
            else:
                context['current_step_name'] = 'Supplier Profile'
        
        return context

@login_required
def update_invoice_references(request, company_id):
    """Update invoice references for a company."""
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.POST.get('selected_references', '[]'))
            client_profile = company.client_profile
            
            # Clear existing references
            client_profile.invoice_reference_options.clear()
            
            # Add new references
            for ref_data in data:
                reference = InvoiceReference.objects.get(id=ref_data['id'])
                ClientInvoiceReference.objects.create(
                    client_profile=client_profile,
                    invoice_reference=reference,
                    is_mandatory=ref_data['is_mandatory']
                )
            
            messages.success(request, 'Invoice references updated successfully.')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            messages.error(request, f'Error updating invoice references: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def manage_company_relationships(request, company_id):
    """View to manage company relationships."""
    company = get_object_or_404(Company, id=company_id)
    
    # Get existing relationships
    relationships_from = CompanyRelationship.objects.filter(from_company=company, is_active=True)
    relationships_to = CompanyRelationship.objects.filter(to_company=company, is_active=True)
    
    if request.method == 'POST':
        form = CompanyRelationshipForm(request.POST, from_company=company)
        if form.is_valid():
            to_company = form.cleaned_data['to_company']
            relationship_type = form.cleaned_data['relationship_type']
            
            # Check if relationship already exists
            existing_relationship = CompanyRelationship.objects.filter(
                from_company=company,
                to_company=to_company,
                relationship_type=relationship_type
            ).first()
            
            if existing_relationship:
                # If relationship exists but was marked inactive, reactivate it
                if not existing_relationship.is_active:
                    existing_relationship.is_active = True
                    existing_relationship.description = form.cleaned_data['description']
                    existing_relationship.save()
                    messages.success(request, f"Relationship with {to_company.company_name} has been reactivated.")
                else:
                    messages.warning(request, f"Relationship with {to_company.company_name} as {dict(CompanyRelationship.RELATIONSHIP_TYPES)[relationship_type]} already exists.")
            else:
                # Create new relationship
                relationship = form.save(commit=False)
                relationship.from_company = company
                relationship.created_by = request.user
                relationship.save()
                messages.success(request, f"Relationship with {relationship.to_company.company_name} added successfully.")
            
            return redirect('crm:manage_company_relationships', company_id=company.id)
    else:
        form = CompanyRelationshipForm(from_company=company)
    
    context = {
        'company': company,
        'form': form,
        'relationships_from': relationships_from,
        'relationships_to': relationships_to,
    }
    
    return render(request, 'crm/manage_company_relationships.html', context)

@login_required
def delete_company_relationship(request, relationship_id):
    """Delete a company relationship."""
    relationship = get_object_or_404(CompanyRelationship, id=relationship_id)
    company_id = relationship.from_company.id
    
    # Check if the user has permission (could add more checks)
    relationship.is_active = False
    relationship.save()
    
    messages.success(request, f"Relationship with {relationship.to_company.company_name} has been removed.")
    return redirect('crm:manage_company_relationships', company_id=company_id)

@login_required
def hubspot_search(request):
    """
    Search for companies in HubSpot and display the results.
    """
    search_results = []
    search_query = request.GET.get('query', '')
    error_message = None
    
    if search_query:
        try:
            # Import here to avoid circular imports
            from crm.utils import hubspot_api
            
            # Search HubSpot API for companies
            results = hubspot_api.search_companies(search_query)
            
            # Check if there's an error
            if 'error' in results:
                error_message = f"Error searching HubSpot: {results.get('error')}"
                messages.error(request, error_message)
            else:
                search_results = results.get('results', [])
                
                # Check which companies we already have in our system
                for result in search_results:
                    hubspot_id = result['id']
                    # See if this company is already linked
                    exists = Company.objects.filter(hubspot_id=hubspot_id).exists()
                    result['is_imported'] = exists
                
                if not search_results:
                    messages.info(request, "No companies found matching your search criteria.")
        
        except Exception as e:
            error_message = f"Error searching HubSpot companies: {str(e)}"
            messages.error(request, error_message)
    
    context = {
        'search_query': search_query,
        'search_results': search_results,
        'error_message': error_message,
    }
    
    return render(request, 'crm/hubspot_search.html', context)

@login_required
def hubspot_company_detail(request, hubspot_id):
    """
    View details of a HubSpot company before importing it.
    """
    # Get company details from HubSpot
    company_data = hubspot_api.get_company_details(hubspot_id)
    
    # Also get associated contacts
    contacts = hubspot_api.get_company_contacts(hubspot_id)
    
    # Check if already imported
    is_imported = Company.objects.filter(hubspot_id=hubspot_id).exists()
    
    if not company_data:
        messages.error(request, "Could not retrieve company details from HubSpot.")
        return redirect('crm:hubspot_search')
    
    context = {
        'company_data': company_data,
        'contacts': contacts,
        'is_imported': is_imported,
        'hubspot_id': hubspot_id,
    }
    
    return render(request, 'crm/hubspot_company_detail.html', context)

@login_required
def import_hubspot_company(request, hubspot_id):
    """
    Import a company from HubSpot into our system.
    """
    if request.method != 'POST':
        return redirect('crm:hubspot_company_detail', hubspot_id=hubspot_id)
    
    # Check if already imported
    existing_company = Company.objects.filter(hubspot_id=hubspot_id).first()
    if existing_company:
        messages.info(request, f"This company is already imported as {existing_company.company_name}.")
        return redirect('crm:company_detail', pk=existing_company.id)
    
    # Get company details from HubSpot
    company_data = hubspot_api.get_company_details(hubspot_id)
    if not company_data:
        messages.error(request, "Could not retrieve company details from HubSpot.")
        return redirect('crm:hubspot_search')
    
    # Get properties from the company data
    properties = company_data.get('properties', {})
    
    # Determine if this is a client or supplier based on form data
    company_type = request.POST.get('company_type', 'Client')
    
    # Create a new company record
    try:
        company = Company(
            agency=request.user.business,
            company_name=properties.get('name', ''),
            company_type=company_type,
            industry=properties.get('industry', 'Other Services'),  # May need mapping
            street_address=properties.get('address', ''),
            city=properties.get('city', ''),
            state_province=properties.get('state', ''),
            postal_code=properties.get('zip', ''),
            country=properties.get('country', ''),
            phone_number=properties.get('phone', ''),
            email='info@' + properties.get('domain', 'example.com'),  # Use domain or placeholder
            description=properties.get('description', ''),
            linkedin_social_page=properties.get('linkedin_company_page', ''),
            hubspot_id=hubspot_id
        )
        company.save()
        
        # Create the appropriate profile
        if company_type == 'Client':
            ClientProfile.objects.create(company=company)
        else:
            SupplierProfile.objects.create(company=company)
        
        # Optionally import contacts as well
        if request.POST.get('import_contacts') == 'on':
            contacts = hubspot_api.get_company_contacts(hubspot_id)
            for contact_data in contacts:
                contact_properties = contact_data.get('properties', {})
                contact = Contact(
                    company=company,
                    first_name=contact_properties.get('firstname', ''),
                    last_name=contact_properties.get('lastname', ''),
                    email=contact_properties.get('email', ''),
                    phone=contact_properties.get('phone', ''),
                    job_title=contact_properties.get('jobtitle', ''),
                    created_by=request.user
                )
                contact.save()
        
        messages.success(request, f"Successfully imported {company.company_name} from HubSpot.")
        return redirect('crm:company_detail', pk=company.id)
        
    except Exception as e:
        messages.error(request, f"Error importing company: {str(e)}")
        return redirect('crm:hubspot_company_detail', hubspot_id=hubspot_id)

@login_required
def hubspot_api_test(request):
    """
    Test the HubSpot API connection and display diagnostic information.
    """
    api_key = settings.HUBSPOT_API_KEY
    api_connected = False
    api_error = None
    api_key_set = bool(api_key)
    api_key_format_valid = False
    api_endpoint = "https://api.hubapi.com/crm/v3/objects/companies"
    
    # Check API key format - modern HubSpot API keys start with "pat-"
    if api_key_set:
        # HubSpot is transitioning to Private App tokens that start with "pat-"
        if api_key.startswith('pat-'):
            api_key_format_valid = True
        else:
            # Legacy API keys might still work, so we'll check the format
            api_key_format_valid = re.match(r'^[a-zA-Z0-9-]+$', api_key) is not None
    
    # Test connection to HubSpot API
    if api_key_set:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "limit": 1,
            "properties": "name",
            "archived": "false"
        }
        
        try:
            response = requests.get(api_endpoint, headers=headers, params=params)
            
            if response.status_code == 200:
                api_connected = True
            else:
                api_error = f"{response.status_code} {response.reason}: {response.text}"
        except Exception as e:
            api_error = str(e)
    
    context = {
        'api_connected': api_connected,
        'api_error': api_error,
        'api_key_set': api_key_set,
        'api_key_format_valid': api_key_format_valid,
        'api_endpoint': api_endpoint,
    }
    
    return render(request, 'crm/hubspot_api_debug.html', context)

@login_required
def hubspot_setup_guide(request):
    """
    Display a guide for setting up the HubSpot integration.
    """
    return render(request, 'crm/hubspot_setup_guide.html')

class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = 'crm/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 25

    def get_queryset(self):
        queryset = Contact.objects.all().select_related('company')
        
        # Filter by company if specified
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(job_role__icontains=search_query) |
                Q(company__company_name__icontains=search_query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['company_id'] = self.request.GET.get('company', '')
        if context['company_id']:
            try:
                context['company'] = Company.objects.get(id=context['company_id'])
            except Company.DoesNotExist:
                context['company'] = None
        return context

class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    template_name = 'crm/contact_detail.html'
    context_object_name = 'contact'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'activities': self.object.activities.all().order_by('-performed_at'),
            'notes': self.object.notes.all().order_by('-created_at')
        })
        return context

class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'crm/contact_form.html'

    def get_success_url(self):
        return reverse_lazy('crm:contact_detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['company'] = self.object.company
        return kwargs

    def form_valid(self, form):
        # Get the original contact data before saving
        original_contact = Contact.objects.get(pk=self.object.pk)
        original_data = {
            'first_name': original_contact.first_name,
            'last_name': original_contact.last_name,
            'email': original_contact.email,
            'mobile': original_contact.mobile,
            'landline': original_contact.landline,
            'job_role': original_contact.job_role,
            'date_of_birth': original_contact.date_of_birth,
            'hospitality': original_contact.hospitality,
            'tag_list': original_contact.tag_list,
        }

        # Save the updated contact
        response = super().form_valid(form)
        updated_contact = self.object

        # Compare original and updated data
        changes = []
        for field, original_value in original_data.items():
            updated_value = getattr(updated_contact, field)
            if original_value != updated_value:
                if field == 'tag_list':
                    # Format tags with proper capitalization
                    def format_tag(tag):
                        tag_map = {
                            'primary': 'Primary Contact',
                            'key_personnel': 'Key Personnel',
                            'booker': 'Booker',
                            'vip_traveller': 'VIP Traveller',
                            'traveller': 'Traveller'
                        }
                        return tag_map.get(tag, tag.title().replace('_', ' '))

                    original_tags = [format_tag(tag) for tag in (original_value or [])]
                    updated_tags = [format_tag(tag) for tag in (updated_value or [])]
                    
                    # Format the tag list change without Python list syntax
                    original_tags_str = ', '.join(original_tags) if original_tags else 'None'
                    updated_tags_str = ', '.join(updated_tags) if updated_tags else 'None'
                    changes.append(f"Tag List: {original_tags_str} → {updated_tags_str}")
                else:
                    # Format field name for display
                    field_display = field.replace('_', ' ').title()
                    changes.append(f"{field_display}: {original_value} → {updated_value}")

        if changes:
            # Create activity record for the update
            Activity.objects.create(
                company=updated_contact.company,
                contact=updated_contact,
                activity_type='update',
                description=f"Contact {updated_contact.first_name} {updated_contact.last_name} was updated:\n" + "\n".join(f"• {change}" for change in changes),
                performed_by=self.request.user,
                is_system_activity=True
            )

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        context['title'] = f"Edit Contact: {self.object.first_name} {self.object.last_name}"
        context['submit_text'] = "Update Contact"
        return context

@login_required
def contact_add_note(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Create the note
            note = ContactNote.objects.create(
                contact=contact,
                content=content,
                created_by=request.user
            )
            
            # Create a note activity record
            note_activity = NoteActivity.objects.create(
                company=contact.company,
                contact=contact,
                activity_type='note',
                description=f"Note added to contact {contact.first_name} {contact.last_name}: {content[:100]}{'...' if len(content) > 100 else ''}",
                performed_by=request.user,
                is_system_activity=True,
                content=content
            )
            
            messages.success(request, 'Note added successfully.')
        else:
            messages.error(request, 'Note content cannot be empty.')
    return redirect('crm:contact_detail', pk=pk)

@login_required
def document_upload(request, company_id):
    """
    Handle document uploads for a company
    """
    company = get_object_or_404(Company, id=company_id)
    
    # Check if user has permission (superuser, admin, or marketing)
    if request.user.role not in ['superuser', 'admin', 'marketing']:
        messages.error(request, "You don't have permission to upload documents.")
        return redirect('crm:company_detail', pk=company_id)
    
    if request.method == 'POST':
        # Validate file size (limit to 10MB)
        if 'file' in request.FILES:
            file = request.FILES['file']
            
            # Size validation
            if file.size > 10 * 1024 * 1024:  # 10MB in bytes
                messages.error(request, "File size exceeds the 10MB limit. Please upload a smaller file.")
                return redirect('crm:document_upload', company_id=company_id)
            
            # File type validation
            ext = os.path.splitext(file.name)[1].lower()
            allowed_extensions = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                '.ppt', '.pptx', '.txt', '.csv', '.rtf', '.odt', '.ods'
            ]
            
            if ext not in allowed_extensions:
                messages.error(request, f"Unsupported file type. Allowed file types: {', '.join(allowed_extensions)}")
                return redirect('crm:document_upload', company_id=company_id)
                
        # Create a new document
        document = Document(
            company=company,
            title=request.POST['title'],
            document_type=request.POST['document_type'],
            file=request.FILES['file'],
            uploaded_by=request.user,
            description=request.POST.get('description', ''),
            version=request.POST.get('version', '')
        )
        
        # Handle expiry date if provided
        expiry_date = request.POST.get('expiry_date')
        if expiry_date:
            document.expiry_date = expiry_date
            
        document.save()
        
        # Create activity record for document upload
        Activity.objects.create(
            company=company,
            activity_type='document',
            description=f"Uploaded document: {document.title}",
            performed_by=request.user,
            is_system_activity=True
        )
        
        messages.success(request, f"Document '{document.title}' uploaded successfully.")
        return redirect('crm:company_detail', pk=company_id)
    
    # Handle GET request - render a form
    context = {
        'company': company,
        'document_types': Document.DOCUMENT_TYPES
    }
    return render(request, 'crm/document_upload.html', context)

@login_required
def document_delete(request, document_id):
    """
    Delete a document
    """
    document = get_object_or_404(Document, id=document_id)
    company_id = document.company.id
    
    # Check if user has permission (superuser, admin, or marketing)
    if request.user.role not in ['superuser', 'admin', 'marketing']:
        messages.error(request, "You don't have permission to delete documents.")
        return redirect('crm:company_detail', pk=company_id)
    
    # Only allow POST requests for deletion
    if request.method != 'POST':
        messages.error(request, "Invalid request method for document deletion.")
        return redirect('crm:company_detail', pk=company_id)
    
    document_title = document.title
    
    # Delete the document
    document.delete()
    
    # Create activity record for document deletion
    Activity.objects.create(
        company=document.company,
        activity_type='document',
        description=f"Deleted document: {document_title}",
        performed_by=request.user,
        is_system_activity=True
    )
    
    messages.success(request, f"Document '{document_title}' deleted successfully.")
    return redirect('crm:company_detail', pk=company_id)

@login_required
def document_detail(request, document_id):
    """
    View detailed information about a document
    """
    document = get_object_or_404(Document, id=document_id)
    company = document.company
    
    # Check if user has permission
    if request.user.role not in ['superuser', 'admin', 'marketing', 'operations']:
        messages.error(request, "You don't have permission to view document details.")
        return redirect('crm:company_detail', pk=company.id)
    
    context = {
        'document': document,
        'company': company,
    }
    return render(request, 'crm/document_detail.html', context)

@login_required
def document_update(request, document_id):
    """
    Update document details
    """
    document = get_object_or_404(Document, id=document_id)
    company = document.company
    
    # Check if user has permission
    if request.user.role not in ['superuser', 'admin', 'marketing']:
        messages.error(request, "You don't have permission to update documents.")
        return redirect('crm:company_detail', pk=company.id)
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            updated_document = form.save(commit=False)
            
            # If a new file is uploaded, handle it
            if 'file' in request.FILES:
                file = request.FILES['file']
                
                # Size validation
                if file.size > 10 * 1024 * 1024:  # 10MB in bytes
                    messages.error(request, "File size exceeds the 10MB limit. Please upload a smaller file.")
                    return redirect('crm:document_update', document_id=document_id)
                
                # File type validation
                ext = os.path.splitext(file.name)[1].lower()
                allowed_extensions = [
                    '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                    '.ppt', '.pptx', '.txt', '.csv', '.rtf', '.odt', '.ods'
                ]
                
                if ext not in allowed_extensions:
                    messages.error(request, f"Unsupported file type. Allowed file types: {', '.join(allowed_extensions)}")
                    return redirect('crm:document_update', document_id=document_id)
            
            updated_document.save()
            
            # Create activity record for document update
            Activity.objects.create(
                company=company,
                activity_type='document',
                description=f"Updated document: {document.title}",
                performed_by=request.user,
                is_system_activity=True
            )
            
            messages.success(request, f"Document '{document.title}' updated successfully.")
            return redirect('crm:document_detail', document_id=document.id)
    else:
        form = DocumentUploadForm(instance=document)
    
    context = {
        'form': form,
        'document': document,
        'company': company,
    }
    return render(request, 'crm/document_update.html', context)

@login_required
def travel_policy_create(request, company_id):
    """Create a new travel policy for a company."""
    company = get_object_or_404(Company, id=company_id)
    
    # Ensure the company is a client
    if company.company_type != 'Client':
        messages.error(request, "Travel policies can only be created for client companies.")
        return redirect('crm:company_detail', pk=company_id)
    
    # Get all contacts from this company
    company_contacts = company.contacts.all().order_by('first_name', 'last_name')
    
    # Separate VIP travelers from regular contacts for better organization in the dropdown
    vip_travelers = []
    other_contacts = []
    
    for contact in company_contacts:
        if 'vip_traveller' in contact.tag_list:
            vip_travelers.append(contact)
        else:
            other_contacts.append(contact)
    
    # Combine lists with VIP travelers first
    organized_contacts = vip_travelers + other_contacts
    
    if request.method == 'POST':
        form = TravelPolicyForm(request.POST)
        
        if form.is_valid():
            try:
                # Get form data before saving
                policy = form.save(commit=False)
                
                # Set the client company
                policy.client = company
                
                # Save the policy
                policy.save()
                
                # Handle VIP travelers (multi-select from form)
                vip_traveler_ids = request.POST.getlist('vip_travelers')
                
                if vip_traveler_ids:
                    policy.vip_travelers.set(vip_traveler_ids)
                
                messages.success(request, f"Travel policy '{policy.policy_name}' created successfully.")
                
                # Create activity log
                Activity.objects.create(
                    activity_type='policy_update',
                    description=f"Created travel policy '{policy.policy_name}' for {company.company_name}.",
                    performed_by=request.user,
                    company=company,
                    is_system_activity=True
                )
                
                return redirect('crm:travel_policy_detail', policy_id=policy.id)
            
            except Exception as e:
                messages.error(request, f"Error creating travel policy: {str(e)}")
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = TravelPolicyForm()
    
    context = {
        'form': form,
        'company': company,
        'company_contacts': organized_contacts,
        'title': 'Create Travel Policy',
        'submit_text': 'Create Policy',
        'vip_travelers': vip_travelers  # Pass VIP travelers separately for special styling
    }
    
    return render(request, 'crm/travel_policy_form.html', context)

@login_required
def travel_policy_detail(request, policy_id):
    """View a travel policy's details."""
    policy = get_object_or_404(ClientTravelPolicy, id=policy_id)
    company = policy.client
    
    context = {
        'policy': policy,
        'company': company,
        'vip_travelers': policy.vip_travelers.all()
    }
    
    return render(request, 'crm/travel_policy_detail.html', context)

@login_required
def travel_policy_update(request, policy_id):
    """Update an existing travel policy."""
    policy = get_object_or_404(ClientTravelPolicy, id=policy_id)
    company = policy.client
    
    # Get all contacts from this company
    company_contacts = company.contacts.all().order_by('first_name', 'last_name')
    
    # Separate VIP travelers from regular contacts for better organization in the dropdown
    vip_travelers = []
    other_contacts = []
    
    for contact in company_contacts:
        if 'vip_traveller' in contact.tag_list:
            vip_travelers.append(contact)
        else:
            other_contacts.append(contact)
    
    # Combine lists with VIP travelers first
    organized_contacts = vip_travelers + other_contacts
    
    if request.method == 'POST':
        form = TravelPolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            
            # Handle VIP travelers (multi-select from form)
            vip_traveler_ids = request.POST.getlist('vip_travelers')
            policy.vip_travelers.set(vip_traveler_ids)
            
            messages.success(request, f"Travel policy '{policy.policy_name}' updated successfully.")
            
            # Create activity log
            Activity.objects.create(
                activity_type='policy_update',
                description=f"Updated travel policy '{policy.policy_name}' for {company.company_name}.",
                performed_by=request.user,
                company=company,
                is_system_activity=True
            )
            
            return redirect('crm:travel_policy_detail', policy_id=policy.id)
    else:
        form = TravelPolicyForm(instance=policy)
    
    context = {
        'form': form,
        'policy': policy,
        'company': company,
        'company_contacts': organized_contacts,
        'title': f"Edit Travel Policy: {policy.policy_name}",
        'submit_text': 'Update Policy',
        'selected_vip_travelers': policy.vip_travelers.values_list('id', flat=True),
        'vip_travelers': vip_travelers  # Pass VIP travelers separately for special styling
    }
    
    return render(request, 'crm/travel_policy_form.html', context)

@login_required
def travel_policy_delete(request, policy_id):
    """Delete a travel policy."""
    policy = get_object_or_404(ClientTravelPolicy, id=policy_id)
    company = policy.client
    
    if request.method == 'POST':
        policy_name = policy.policy_name
        company_id = company.id
        
        # Create activity log before deletion
        Activity.objects.create(
            activity_type='policy_update',
            description=f"Deleted travel policy '{policy_name}' from {company.company_name}.",
            performed_by=request.user,
            company=company,
            is_system_activity=True
        )
        
        policy.delete()
        messages.success(request, f"Travel policy '{policy_name}' deleted successfully.")
        
        return redirect('crm:company_detail', pk=company_id)
    
    # For GET requests, display confirmation page
    return render(request, 'crm/travel_policy_confirm_delete.html', {'policy': policy})

@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    company = contact.company
    contact_name = f"{contact.first_name} {contact.last_name}"
    
    if request.method == 'POST':
        # Create an activity record for the deletion before deleting the contact
        Activity.objects.create(
            company=company,
            contact=None,  # Contact will be deleted, so set to None
            activity_type='status_change',
            description=f"Contact {contact_name} was deleted",
            performed_by=request.user,
            is_system_activity=True
        )
        
        # Delete the contact
        contact.delete()
        messages.success(request, f"Contact {contact_name} has been deleted successfully.")
        return redirect('crm:company_detail', pk=company.pk)
    
    return render(request, 'crm/contact_confirm_delete.html', {'contact': contact})

@login_required
def log_email(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        form = EmailActivityForm(request.POST, request.FILES, company=company)
        todo_form = ToDoTaskForm(request.POST)
        if form.is_valid() and todo_form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.performed_by = request.user
            activity.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Handle follow-up task if provided
            if todo_form.cleaned_data.get('to_do_task_date'):
                activity.follow_up_date = todo_form.cleaned_data['to_do_task_date']
                activity.follow_up_notes = todo_form.cleaned_data.get('to_do_task_message', '')
                activity.save()
            
            messages.success(request, 'Email activity logged successfully.')
            return redirect('crm:company_detail', pk=company_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmailActivityForm(company=company)
        todo_form = ToDoTaskForm()
    
    context = {
        'form': form,
        'todo_form': todo_form,
        'company': company,
        'title': 'Log Email Activity'
    }
    return render(request, 'crm/activity_form.html', context)

@login_required
def log_call(request, company_id):
    """Log a call activity for a company."""
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = CallActivityForm(request.POST)
        todo_form = ToDoTaskForm(request.POST)
        
        if form.is_valid() and todo_form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.performed_by = request.user
            activity.activity_type = 'call'
            
            # Save the activity
            activity.save()
            
            # Handle to-do task if provided
            if todo_form.cleaned_data.get('to_do_task_date'):
                activity.data['todo'] = {
                    'date': todo_form.cleaned_data['to_do_task_date'].isoformat(),
                    'message': todo_form.cleaned_data.get('to_do_task_message', '')
                }
                activity.save()
            
            messages.success(request, 'Call activity logged successfully.')
            return redirect('crm:company_detail', pk=company_id)
    else:
        form = CallActivityForm()
        todo_form = ToDoTaskForm()
    
    context = {
        'form': form,
        'todo_form': todo_form,
        'company': company,
        'title': 'Log Call Activity'
    }
    return render(request, 'crm/activity_form.html', context)

@login_required
def log_meeting(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        form = MeetingActivityForm(request.POST)
        todo_form = ToDoTaskForm(request.POST)
        if form.is_valid() and todo_form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.performed_by = request.user
            activity.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Handle follow-up task if provided
            if todo_form.cleaned_data.get('to_do_task_date'):
                activity.follow_up_date = todo_form.cleaned_data['to_do_task_date']
                activity.follow_up_notes = todo_form.cleaned_data.get('to_do_task_message', '')
                activity.save()
            
            messages.success(request, 'Meeting activity logged successfully.')
            return redirect('crm:company_detail', pk=company_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MeetingActivityForm()
        todo_form = ToDoTaskForm()
    
    context = {
        'form': form,
        'todo_form': todo_form,
        'company': company,
        'title': 'Log Meeting Activity'
    }
    return render(request, 'crm/activity_form.html', context)

@login_required
def log_note(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        form = NoteActivityForm(request.POST)
        todo_form = ToDoTaskForm(request.POST)
        if form.is_valid() and todo_form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.performed_by = request.user
            activity.save()
            
            # Handle follow-up task if provided
            if todo_form.cleaned_data.get('to_do_task_date'):
                activity.follow_up_date = todo_form.cleaned_data['to_do_task_date']
                activity.follow_up_notes = todo_form.cleaned_data.get('to_do_task_message', '')
                activity.save()
            
            messages.success(request, 'Note activity logged successfully.')
            return redirect('crm:company_detail', pk=company_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NoteActivityForm()
        todo_form = ToDoTaskForm()
    
    context = {
        'form': form,
        'todo_form': todo_form,
        'company': company,
        'title': 'Log Note Activity'
    }
    return render(request, 'crm/activity_form.html', context)

@login_required
def log_waiver_favor(request, company_id):
    """Log a waiver/favor activity for a company."""
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = WaiverFavorActivityForm(request.POST)
        todo_form = ToDoTaskForm(request.POST)
        
        if form.is_valid() and todo_form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.performed_by = request.user
            activity.activity_type = 'waiver'
            
            # Save the activity
            activity.save()
            
            # Handle to-do task if provided
            if todo_form.cleaned_data.get('to_do_task_date'):
                activity.data['todo'] = {
                    'date': todo_form.cleaned_data['to_do_task_date'].isoformat(),
                    'message': todo_form.cleaned_data.get('to_do_task_message', '')
                }
                activity.save()
            
            messages.success(request, 'Waiver/Favor activity logged successfully.')
            return redirect('crm:company_detail', pk=company_id)
    else:
        form = WaiverFavorActivityForm()
        todo_form = ToDoTaskForm()
    
    context = {
        'form': form,
        'todo_form': todo_form,
        'company': company,
        'title': 'Log Waiver/Favor Activity'
    }
    return render(request, 'crm/activity_form.html', context)

@login_required
def get_activity_details(request, activity_id):
    """API endpoint to get activity details as JSON"""
    try:
        activity = get_object_or_404(Activity, id=activity_id)
        
        # Prepare the response data
        response_data = {
            'id': activity.id,
            'type': activity.activity_type,
            'description': activity.description,
            'performed_at': activity.performed_at.isoformat(),
            'performed_by': {
                'id': activity.performed_by.id if activity.performed_by else None,
                'name': activity.performed_by.get_full_name() if activity.performed_by else 'System'
            },
            'company': {
                'id': activity.company.id,
                'name': activity.company.company_name
            }
        }
        
        # Add activity-specific data from the data JSONField
        if activity.data:
            response_data.update(activity.data)
        
        return JsonResponse({
            'status': 'success',
            'data': response_data
        })
    except Activity.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Activity not found'
        }, status=404)

@login_required
def edit_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Determine the appropriate form class based on activity type
    if activity.activity_type == 'email':
        form_class = EmailActivityForm
    elif activity.activity_type == 'call':
        form_class = CallActivityForm
    elif activity.activity_type == 'meeting':
        form_class = MeetingActivityForm
    elif activity.activity_type == 'note':
        form_class = NoteActivityForm
    elif activity.activity_type == 'document':
        form_class = DocumentActivityForm
    elif activity.activity_type == 'status_change':
        form_class = StatusChangeActivityForm
    elif activity.activity_type == 'policy_update':
        form_class = PolicyUpdateActivityForm
    elif activity.activity_type == 'waiver':
        form_class = WaiverFavorActivityForm
    else:
        raise Http404("Invalid activity type")
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=activity)
        todo_form = ToDoTaskForm(request.POST)
        if form.is_valid() and todo_form.is_valid():
            activity = form.save(commit=False)
            activity.performed_by = request.user
            activity.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Handle follow-up task if provided
            if todo_form.cleaned_data.get('to_do_task_date'):
                activity.follow_up_date = todo_form.cleaned_data['to_do_task_date']
                activity.follow_up_notes = todo_form.cleaned_data.get('to_do_task_message', '')
                activity.save()
            
            messages.success(request, 'Activity updated successfully.')
            return redirect('crm:company_detail', pk=activity.company.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-populate the form with existing data
        initial_data = {}
        if hasattr(activity, 'data') and activity.data:
            initial_data.update(activity.data)
            if 'todo' in activity.data:
                todo_form = ToDoTaskForm(initial={
                    'to_do_task_date': activity.data['todo']['date'],
                    'to_do_task_message': activity.data['todo'].get('message', '')
                })
            else:
                todo_form = ToDoTaskForm()
        else:
            todo_form = ToDoTaskForm()
        
        form = form_class(instance=activity, initial=initial_data)
    
    context = {
        'form': form,
        'todo_form': todo_form,
        'activity': activity,
        'company': activity.company,
        'title': f'Edit {activity.get_activity_type_display()} Activity'
    }
    return render(request, 'crm/activity_form.html', context)

@login_required
def delete_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    company_id = activity.company.id
    activity.delete()
    messages.success(request, 'Activity deleted successfully.')
    return redirect('crm:company_detail', pk=company_id)

@login_required
def search_recipients(request):
    """API endpoint for searching contacts and users."""
    logger = logging.getLogger(__name__)
    
    # Log the full request parameters
    logger.debug(f"🔍 SEARCH DEBUG - Full request: {request.GET}")
    logger.debug(f"🔍 SEARCH DEBUG - Headers: {request.headers}")
    
    # Get parameters with fallbacks
    search_term = request.GET.get('term', '').strip().lower()  # Convert to lowercase for case-insensitive search
    company_id = request.GET.get('company_id', '')
    
    logger.debug(f"🔍 SEARCH DEBUG - Term: '{search_term}', Company ID: '{company_id}'")
    
    # Initialize results list
    results = []
    
    try:
        # Check search term length
        if len(search_term) < 2:
            logger.debug("🔍 SEARCH DEBUG - Term too short, returning empty results")
            return JsonResponse({'results': []})
        
        # Build more flexible search queries for contacts
        contact_query = Q(first_name__icontains=search_term) | \
                       Q(last_name__icontains=search_term)
        
        # Check if email exists before adding to search query
        if hasattr(Contact, 'email'):
            contact_query |= Q(email__icontains=search_term)
            logger.debug("🔍 SEARCH DEBUG - Adding email field to contact search query")
        
        # Also search for full name matches (for "first last" style searches)
        name_parts = search_term.split()
        if len(name_parts) > 1:
            # For multiple word searches, try matching first and last name combinations
            for i in range(len(name_parts) - 1):
                first_part = name_parts[i]
                last_part = name_parts[i+1]
                contact_query |= (Q(first_name__icontains=first_part) & Q(last_name__icontains=last_part))
        
        logger.debug(f"🔍 SEARCH DEBUG - Contact query: {contact_query}")
        
        # CRITICAL - List all contacts for debugging
        all_contacts = Contact.objects.all()[:5]  # Just get a few for debugging
        logger.debug(f"🔍 SEARCH DEBUG - Total contacts in database: {Contact.objects.count()}")
        logger.debug(f"🔍 SEARCH DEBUG - Sample contacts:")
        for contact in all_contacts:
            logger.debug(f"🔍 SEARCH DEBUG - Contact: {contact.id} - {contact.first_name} {contact.last_name} - Company ID: {contact.company_id}")
            
        # Debug companies
        from .models import Company
        all_companies = Company.objects.all()[:5]
        logger.debug(f"🔍 SEARCH DEBUG - Total companies in database: {Company.objects.count()}")
        logger.debug(f"🔍 SEARCH DEBUG - Sample companies:")
        for company in all_companies:
            logger.debug(f"🔍 SEARCH DEBUG - Company: {company.id} - {company.company_name}")
        
        # Search contacts
        if company_id and company_id.isdigit():
            # Search within specific company
            logger.debug(f"🔍 SEARCH DEBUG - Searching contacts for company {company_id}")
            
            # Check if this company exists
            try:
                from .models import Company
                company = Company.objects.get(id=company_id)
                logger.debug(f"🔍 SEARCH DEBUG - Found company: {company.company_name}")
                
                # Get all contacts for this company first to confirm they exist
                all_company_contacts = Contact.objects.filter(company_id=company_id)
                logger.debug(f"🔍 SEARCH DEBUG - Company has {all_company_contacts.count()} contacts total")
                for contact in all_company_contacts[:5]:  # List first 5 only
                    logger.debug(f"🔍 SEARCH DEBUG - Company contact: {contact.id} - {contact.first_name} {contact.last_name}")
                
            except Exception as e:
                logger.debug(f"🔍 SEARCH DEBUG - Company check error: {str(e)}")
            
            # Now search for contacts matching the term
            contacts = Contact.objects.filter(contact_query, company_id=company_id)
            logger.debug(f"🔍 SEARCH DEBUG - Found {contacts.count()} contacts matching '{search_term}' for company {company_id}")
            
            # If no contacts found for this company, search across all companies instead
            if contacts.count() == 0:
                logger.debug(f"🔍 SEARCH DEBUG - No contacts found for company {company_id}, searching all companies instead")
                contacts = Contact.objects.filter(contact_query)
                logger.debug(f"🔍 SEARCH DEBUG - Found {contacts.count()} contacts matching '{search_term}' across all companies")
        else:
            # Search all contacts
            logger.debug("🔍 SEARCH DEBUG - Searching all contacts (no company specified)")
            contacts = Contact.objects.filter(contact_query)
            logger.debug(f"🔍 SEARCH DEBUG - Found {contacts.count()} contacts matching '{search_term}' across all companies")
        
        # Debug contacts - log the SQL query being executed
        from django.db import connection
        queries = connection.queries
        last_query = queries[-1] if queries else None
        if last_query:
            logger.debug(f"🔍 SEARCH DEBUG - Contact SQL: {last_query['sql']}")
        
        # Debug: log all matching contacts with detailed info
        logger.debug(f"🔍 SEARCH DEBUG - Contact search details:")
        logger.debug(f"🔍 SEARCH DEBUG - Contact model fields: {[f.name for f in Contact._meta.fields]}")
        
        # List all matching contacts
        logger.debug(f"🔍 SEARCH DEBUG - Matching contacts:")
        for contact in contacts[:10]:
            logger.debug(f"🔍 SEARCH DEBUG - Found contact: {contact.id} - {contact.first_name} {contact.last_name} (company {contact.company_id})")
        
        # Add contacts to results
        for contact in contacts[:10]:  # Limit to 10 contacts
            # Get company name for this contact
            company_name = None
            try:
                if contact.company:
                    company_name = contact.company.company_name
            except:
                pass
                
            results.append({
                'id': f'contact_{contact.id}',
                'text': f'{contact.first_name} {contact.last_name}',
                'type': 'contact',
                'company_id': contact.company_id,
                'company_name': company_name
            })
        
        # Search users - CustomUser has first_name, last_name, and email fields but NOT username
        User = get_user_model()
        logger.debug(f"🔍 SEARCH DEBUG - User model: {User.__name__}")
        logger.debug(f"🔍 SEARCH DEBUG - User model fields: {[f.name for f in User._meta.fields]}")
        
        user_query = Q(first_name__icontains=search_term) | \
                     Q(last_name__icontains=search_term) | \
                     Q(email__icontains=search_term)
        
        # Also search for full name matches for users
        if len(name_parts) > 1:
            for i in range(len(name_parts) - 1):
                first_part = name_parts[i]
                last_part = name_parts[i+1]
                user_query |= (Q(first_name__icontains=first_part) & Q(last_name__icontains=last_part))
        
        users = User.objects.filter(user_query, is_active=True)
        logger.debug(f"🔍 SEARCH DEBUG - Found {users.count()} active users matching '{search_term}'")
        
        # Debug user search SQL query
        queries = connection.queries
        last_query = queries[-1] if queries else None
        if last_query:
            logger.debug(f"🔍 SEARCH DEBUG - User SQL: {last_query['sql']}")
        
        # Debug: log all matching users with detailed info
        for user in users[:5]:
            logger.debug(f"🔍 SEARCH DEBUG - Found user: {user.id} - {user.get_full_name()} - {user.email}")
        
        # Add users to results
        for user in users[:5]:  # Limit to 5 users
            results.append({
                'id': f'user_{user.id}',
                'text': user.get_full_name() or user.email,
                'type': 'user'
            })
        
        # Log results
        logger.debug(f"🔍 SEARCH DEBUG - Returning {len(results)} total results")
        
        # Return results with success status for clarity
        response_data = {
            'results': results,
            'pagination': {'more': False},  # No pagination
            'status': 'success',
            'count': len(results)
        }
        logger.debug(f"🔍 SEARCH DEBUG - Response: {response_data}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"❌ SEARCH DEBUG ERROR: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': str(e),
            'status': 'error',
            'results': []
        }, status=500)

@login_required
def activity_details(request, activity_id):
    """View for displaying activity details"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Get the specific activity type instance
    activity_details = None
    if activity.activity_type == 'email':
        activity_details = activity.emailactivity
    elif activity.activity_type == 'call':
        activity_details = activity.callactivity
    elif activity.activity_type == 'meeting':
        activity_details = activity.meetingactivity
    elif activity.activity_type == 'note':
        activity_details = activity.noteactivity
    
    context = {
        'activity': activity,
        'activity_details': activity_details,
    }
    
    return render(request, 'crm/activity_details.html', context)

