from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Company, Contact, ClientProfile, SupplierProfile, INDUSTRY_CHOICES, COMPANY_TYPE, CLIENT_TYPE_CHOICES, CLIENT_STATUS_CHOICES, SUPPLIER_TYPE_CHOICES, SUPPLIER_STATUS_CHOICES, SUPPLIER_FOR_DEPARTMENT_CHOICES, ClientInvoiceReference, CompanyRelationship, ContactNote, Document, Activity, ClientTravelPolicy
from accounts.models import InvoiceReference
from django.urls import reverse_lazy, reverse
from formtools.wizard.views import SessionWizardView
from django.shortcuts import redirect
from django.contrib import messages
from django import forms
from .forms import CompanyForm, CompanyRelationshipForm, ContactForm, ContactNoteForm, DocumentUploadForm, ManageRelationshipsForm, ClientInvoiceReferenceFormSet, TravelPolicyForm
from django.contrib.auth import get_user_model
from accounts.models import Team
import json
from django.http import JsonResponse, HttpResponseRedirect
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
    company_types = Company.COMPANY_TYPES
    
    context = {
        'companies': companies,
        'company_types': company_types,
        'selected_type': company_type,
    }
    
    return render(request, 'crm/company_list.html', context)

@login_required
def company_detail(request, pk):
    """
    View a company's complete profile, including contacts, activities, and notes.
    """
    company = get_object_or_404(Company, pk=pk)
    
    # Get company contacts, ordered by name
    contacts = company.contacts.all().annotate(
        full_name=Concat('first_name', Value(' '), 'last_name')
    ).order_by('full_name')
    
    # Get activities for this company
    activities = company.activities.all().order_by('-performed_at')[:10]
    
    # Get company documents
    documents = company.documents.all().order_by('-uploaded_at')
    
    # Get transaction fees
    transaction_fees = company.transaction_fees.all()
    
    # Notes - check if related manager exists or skip
    try:
        notes = company.notes.all().order_by('-created_at')
    except AttributeError:
        notes = []

    # Get travel policies if this is a client company
    travel_policies = ClientTravelPolicy.objects.filter(client=company)
    
    # Additional data for the template
    invoice_references = None
    profile = None
    if company.company_type == 'Client':
        # Get or create client profile
        profile, created = ClientProfile.objects.get_or_create(company=company)
        # Get invoice references
        invoice_references = ClientInvoiceReference.objects.filter(client_profile=profile)
    
    context = {
        'company': company,
        'contacts': contacts,
        'activities': activities,
        'documents': documents,
        'notes': notes,
        'transaction_fees': transaction_fees,
        'travel_policies': travel_policies,
        'profile': profile,
        'invoice_references': invoice_references,
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
            performed_by=self.request.user
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
        kwargs['company'] = self.object.company
        return kwargs

    def form_valid(self, form):
        # Get the original contact data before saving
        original_contact = Contact.objects.get(pk=self.object.pk)
        original_data = {
            'first_name': original_contact.first_name,
            'last_name': original_contact.last_name,
            'job_role': original_contact.job_role,
            'email': original_contact.email,
            'landline': original_contact.landline,
            'mobile': original_contact.mobile,
            'date_of_birth': original_contact.date_of_birth,
            'hospitality': original_contact.hospitality,
            'tag_list': original_contact.tag_list
        }
        
        # Save the form to update the contact
        response = super().form_valid(form)
        
        # Compare original data with updated data
        updated_contact = self.object
        changed_fields = []
        
        for field, original_value in original_data.items():
            updated_value = getattr(updated_contact, field)
            
            # Check for date field (date_of_birth)
            if field == 'date_of_birth' and original_value != updated_value:
                orig_str = str(original_value) if original_value else "Not set"
                updated_str = str(updated_value) if updated_value else "Not set"
                changed_fields.append(f"{field.replace('_', ' ').title()}: {orig_str} → {updated_str}")
            # Handle other fields
            elif original_value != updated_value:
                orig_str = str(original_value) if original_value else "Not set"
                updated_str = str(updated_value) if updated_value else "Not set"
                changed_fields.append(f"{field.replace('_', ' ').title()}: {orig_str} → {updated_str}")
        
        # Create activity record if fields were changed
        if changed_fields:
            description = f"Contact {updated_contact.first_name} {updated_contact.last_name} was updated:\n• " + "\n• ".join(changed_fields)
            
            Activity.objects.create(
                company=updated_contact.company,
                contact=updated_contact,
                activity_type='status_change',
                description=description,
                performed_by=self.request.user
            )
        
        messages.success(self.request, f"Contact {self.object.first_name} {self.object.last_name} has been updated successfully.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Update {self.object.first_name} {self.object.last_name}"
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
            
            # Create an activity record for the note
            Activity.objects.create(
                company=contact.company,
                contact=contact,
                activity_type='note',
                description=f"Note added to contact {contact.first_name} {contact.last_name}: {content[:100]}{'...' if len(content) > 100 else ''}",
                performed_by=request.user
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
            performed_by=request.user
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
        performed_by=request.user
    )
    
    messages.success(request, f"Document '{document_title}' deleted successfully.")
    return redirect('crm:company_detail', pk=company_id)

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
                    company=company
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
                company=company
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
            company=company
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
            performed_by=request.user
        )
        
        # Delete the contact
        contact.delete()
        messages.success(request, f"Contact {contact_name} has been deleted successfully.")
        return redirect('crm:company_detail', pk=company.pk)
    
    return render(request, 'crm/contact_confirm_delete.html', {'contact': contact})

"""
Hubspot Setup Guide View
"""
def hubspot_setup_guide(request):
    return render(request, 'crm/hubspot_setup_guide.html')


# Activity Logging Views
@login_required
def log_activity(request, company_id, activity_type):
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        try:
            # Common data for all activity types
            description = ""
            activity_data = {}  # Store detailed content in this dict
            
            # Process based on activity type
            if activity_type == 'email':
                subject = request.POST.get('subject')
                content = request.POST.get('content')
                recipients = request.POST.getlist('recipients')
                
                # Store full content
                activity_data['subject'] = subject
                activity_data['content'] = content
                activity_data['recipients'] = recipients
                
                # Format description (summary)
                recipient_names = []
                if recipients:
                    for recipient_id in recipients:
                        try:
                            contact = Contact.objects.get(id=recipient_id)
                            recipient_names.append(f"{contact.first_name} {contact.last_name}")
                        except Contact.DoesNotExist:
                            pass
                
                recipient_text = ", ".join(recipient_names) if recipient_names else "No specific recipients"
                description = f"Email sent: {subject}"
                activity_icon = 'fa-envelope'
                
            elif activity_type == 'call':
                contact_id = request.POST.get('contact')
                duration = request.POST.get('duration')
                summary = request.POST.get('summary')
                
                # Store full content
                activity_data['contact_id'] = contact_id
                activity_data['duration'] = duration
                activity_data['summary'] = summary
                
                # Get contact name if provided
                contact_name = "Unknown"
                if contact_id:
                    try:
                        contact = Contact.objects.get(id=contact_id)
                        contact_name = f"{contact.first_name} {contact.last_name}"
                    except Contact.DoesNotExist:
                        pass
                
                # Format description
                duration_text = f" ({duration} mins)" if duration else ""
                description = f"Call with {contact_name}{duration_text}: {summary}"
                activity_icon = 'fa-phone'
                
            elif activity_type == 'note':
                content = request.POST.get('content')
                
                # Store full content
                activity_data['content'] = content
                
                # Truncate content for the description if it's too long
                if len(content) > 100:
                    short_content = content[:97] + "..."
                else:
                    short_content = content
                
                description = f"Note: {short_content}"
                activity_icon = 'fa-sticky-note'
                
            elif activity_type == 'meeting':
                title = request.POST.get('title')
                date = request.POST.get('date')
                start_time = request.POST.get('start_time')
                end_time = request.POST.get('end_time')
                location = request.POST.get('location', '')
                notes = request.POST.get('notes')
                attendees = request.POST.getlist('attendees')
                
                # Store full content
                activity_data['title'] = title
                activity_data['date'] = date
                activity_data['start_time'] = start_time
                activity_data['end_time'] = end_time
                activity_data['location'] = location
                activity_data['notes'] = notes
                activity_data['attendees'] = attendees
                
                # Format location text
                location_text = f" at {location}" if location else ""
                
                # Format attendee names
                attendee_names = []
                if attendees:
                    for attendee_id in attendees:
                        try:
                            contact = Contact.objects.get(id=attendee_id)
                            attendee_names.append(f"{contact.first_name} {contact.last_name}")
                        except Contact.DoesNotExist:
                            pass
                
                attendee_text = ""
                if attendee_names:
                    attendee_text = f" with {', '.join(attendee_names)}"
                
                # Format description
                description = f"Meeting: {title}{location_text}{attendee_text} on {date} ({start_time}-{end_time})"
                activity_icon = 'fa-users'
                
            elif activity_type == 'exception':
                exception_type = request.POST.get('exception_type')
                value_amount = request.POST.get('value_amount')
                contact_id = request.POST.get('contact')
                approved_by = request.POST.get('approved_by')
                description_text = request.POST.get('description')
                
                # Store full content
                activity_data['exception_type'] = exception_type
                activity_data['value_amount'] = value_amount
                activity_data['contact_id'] = contact_id
                activity_data['approved_by'] = approved_by
                activity_data['description'] = description_text
                
                # Get contact name if provided
                contact_name = "Unknown"
                if contact_id:
                    try:
                        contact = Contact.objects.get(id=contact_id)
                        contact_name = f"{contact.first_name} {contact.last_name}"
                    except Contact.DoesNotExist:
                        pass
                
                # Format exception type for display
                exception_display = exception_type.replace('_', ' ').title()
                
                # Format value if provided
                value_text = f" (£{value_amount})" if value_amount else ""
                
                # Format approval info
                approval_text = ""
                if approved_by and approved_by != 'none':
                    approval_text = f", approved by {approved_by.replace('_', ' ').title()}"
                
                # Format description
                description = f"{exception_display}{value_text} for {contact_name}{approval_text}: {description_text}"
                activity_icon = 'fa-star'
            
            # Create activity record
            Activity.objects.create(
                company=company,
                activity_type=activity_type,
                description=description,
                performed_by=request.user,
                data=activity_data  # Save the detailed activity data
            )
            
            messages.success(request, f"{activity_type.title()} activity logged successfully!")
            
        except Exception as e:
            messages.error(request, f"Error logging activity: {str(e)}")
        
    return redirect('crm:company_detail', pk=company_id)

@login_required
def log_contact_activity(request, contact_id, activity_type):
    contact = get_object_or_404(Contact, id=contact_id)
    company = contact.company
    
    if request.method == 'POST':
        try:
            # Common data for all activity types
            description = ""
            activity_data = {}  # Store detailed content in this dict
            
            # Process based on activity type
            if activity_type == 'email':
                subject = request.POST.get('subject')
                content = request.POST.get('content')
                
                # Store full content
                activity_data['subject'] = subject
                activity_data['content'] = content
                activity_data['contact_id'] = contact_id
                
                # Format description
                description = f"Email to {contact.first_name} {contact.last_name}: {subject}"
                activity_icon = 'fa-envelope'
                
            elif activity_type == 'call':
                duration = request.POST.get('duration')
                call_type = request.POST.get('call_type', 'outgoing')
                summary = request.POST.get('summary')
                
                # Store full content
                activity_data['duration'] = duration
                activity_data['call_type'] = call_type
                activity_data['summary'] = summary
                activity_data['contact_id'] = contact_id
                
                # Format description
                duration_text = f" ({duration} mins)" if duration else ""
                description = f"{call_type.title()} call with {contact.first_name} {contact.last_name}{duration_text}: {summary}"
                activity_icon = 'fa-phone'
                
            elif activity_type == 'note':
                content = request.POST.get('content')
                
                # Store full content
                activity_data['content'] = content
                activity_data['contact_id'] = contact_id
                
                # Truncate content for the description if it's too long
                if len(content) > 100:
                    short_content = content[:97] + "..."
                else:
                    short_content = content
                
                description = f"Note about {contact.first_name} {contact.last_name}: {short_content}"
                activity_icon = 'fa-sticky-note'
                
            elif activity_type == 'meeting':
                title = request.POST.get('title')
                date = request.POST.get('date')
                start_time = request.POST.get('start_time')
                end_time = request.POST.get('end_time')
                location = request.POST.get('location', '')
                notes = request.POST.get('notes')
                attendees = request.POST.getlist('attendees')
                
                # Store full content
                activity_data['title'] = title
                activity_data['date'] = date
                activity_data['start_time'] = start_time
                activity_data['end_time'] = end_time
                activity_data['location'] = location
                activity_data['notes'] = notes
                activity_data['attendees'] = attendees
                
                # Format location text
                location_text = f" at {location}" if location else ""
                
                # Format attendee names
                attendee_names = []
                if attendees:
                    for attendee_id in attendees:
                        try:
                            contact = Contact.objects.get(id=attendee_id)
                            attendee_names.append(f"{contact.first_name} {contact.last_name}")
                        except Contact.DoesNotExist:
                            pass
                
                attendee_text = ""
                if attendee_names:
                    attendee_text = f" with {', '.join(attendee_names)}"
                
                # Format description
                description = f"Meeting: {title}{location_text}{attendee_text} on {date} ({start_time}-{end_time})"
                activity_icon = 'fa-users'
                
            elif activity_type == 'exception':
                exception_type = request.POST.get('exception_type')
                value_amount = request.POST.get('value_amount')
                approved_by = request.POST.get('approved_by')
                description_text = request.POST.get('description')
                
                # Store full content
                activity_data['exception_type'] = exception_type
                activity_data['value_amount'] = value_amount
                activity_data['approved_by'] = approved_by
                activity_data['description'] = description_text
                activity_data['contact_id'] = contact_id
                
                # Format exception type for display
                exception_display = exception_type.replace('_', ' ').title()
                
                # Format value if provided
                value_text = f" (£{value_amount})" if value_amount else ""
                
                # Format approval info
                approval_text = ""
                if approved_by and approved_by != 'none':
                    approval_text = f", approved by {approved_by.replace('_', ' ').title()}"
                
                # Format description
                description = f"{exception_display}{value_text} for {contact.first_name} {contact.last_name}{approval_text}: {description_text}"
                activity_icon = 'fa-star'
            
            # Create activity record
            Activity.objects.create(
                company=company,
                contact=contact,
                activity_type=activity_type,
                description=description,
                performed_by=request.user,
                data=activity_data  # Save the detailed activity data
            )
            
            messages.success(request, f"{activity_type.title()} activity logged successfully!")
            
        except Exception as e:
            messages.error(request, f"Error logging activity: {str(e)}")
        
    return redirect('crm:contact_detail', pk=contact_id)

