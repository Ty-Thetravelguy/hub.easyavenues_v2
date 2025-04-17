from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from formtools.wizard.views import SessionWizardView
from django import forms
from django.contrib.auth import get_user_model
import json

from crm.models import (
    Company, Contact, ClientProfile, SupplierProfile, Activity, Document, 
    ClientTravelPolicy, COMPANY_TYPE, INDUSTRY_CHOICES, CLIENT_TYPE_CHOICES,
    CLIENT_STATUS_CHOICES, SUPPLIER_TYPE_CHOICES, SUPPLIER_STATUS_CHOICES,
    SUPPLIER_FOR_DEPARTMENT_CHOICES, ClientInvoiceReference, CompanyRelationship
)
from crm.forms import CompanyForm, CompanyRelationshipForm
from accounts.models import InvoiceReference, Team

# Define the form list for the company creation wizard (if needed)
COMPANY_FORMS = [
    ('type', forms.Form),
    ('basic', forms.Form),
    ('profile', forms.Form),
]

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
    
    # Get the company's contacts
    contacts = Contact.objects.filter(company=company).order_by('-created_at')
    
    # Get the company's documents
    documents = Document.objects.filter(company=company).order_by('-uploaded_at')
    
    # Get travel policies if this is a client
    travel_policies = []
    if company.company_type == 'Client':
        travel_policies = ClientTravelPolicy.objects.filter(client=company).order_by('-effective_date')
    
    # Get activities
    activities = Activity.objects.filter(company=company).order_by('-performed_at')
    
    context = {
        'company': company,
        'contacts': contacts,
        'documents': documents,
        'travel_policies': travel_policies,
        'activities': activities,
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
        # Get original company data before saving
        original_company = Company.objects.get(pk=self.object.pk)
        
        # Save the form
        response = super().form_valid(form)
        
        # Get updated company
        updated_company = self.object
        
        # Track changes
        changes = []
        
        # Compare fields and record changes
        if original_company.company_name != updated_company.company_name:
            changes.append(f"Name changed from '{original_company.company_name}' to '{updated_company.company_name}'")
            
        if original_company.industry != updated_company.industry:
            changes.append(f"Industry changed from '{original_company.industry}' to '{updated_company.industry}'")
            
        if original_company.street_address != updated_company.street_address:
            changes.append(f"Street Address changed from '{original_company.street_address}' to '{updated_company.street_address}'")
            
        if original_company.city != updated_company.city:
            changes.append(f"City changed from '{original_company.city}' to '{updated_company.city}'")
            
        if original_company.state_province != updated_company.state_province:
            changes.append(f"State/Province changed from '{original_company.state_province}' to '{updated_company.state_province}'")
            
        if original_company.postal_code != updated_company.postal_code:
            changes.append(f"Postal Code changed from '{original_company.postal_code}' to '{updated_company.postal_code}'")
            
        if original_company.country != updated_company.country:
            changes.append(f"Country changed from '{original_company.country}' to '{updated_company.country}'")
            
        if original_company.phone_number != updated_company.phone_number:
            changes.append(f"Phone Number changed from '{original_company.phone_number}' to '{updated_company.phone_number}'")
            
        if original_company.email != updated_company.email:
            changes.append(f"Email changed from '{original_company.email}' to '{updated_company.email}'")
            
        if original_company.description != updated_company.description:
            changes.append(f"Description was updated")
            
        if original_company.linkedin_social_page != updated_company.linkedin_social_page:
            changes.append(f"LinkedIn page was updated")
        
        # Only log if there were actual changes
        if changes:
            # Create activity record for the update
            Activity.objects.create(
                company=updated_company,
                activity_type='update',
                description=f"Company {updated_company.company_name} was updated:\n" + "\n".join(f"• {change}" for change in changes),
                performed_by=self.request.user,
                is_system_activity=True
            )
        
        messages.success(self.request, f"{self.object.company_name} has been updated successfully.")
        return response

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

            # Log system activity for company creation
            Activity.objects.create(
                company=company,
                activity_type='status_change',
                description=f"Company {company.company_name} was created",
                performed_by=self.request.user,
                is_system_activity=True
            )

            messages.success(self.request, f"Successfully created {company.company_name}")
            return redirect('crm:company_detail', pk=company.pk)
        except Exception as e:
            messages.error(self.request, f"Error creating company: {str(e)}")
            return redirect('crm:company_list')

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context['title'] = "Create New Company"
        context['submit_text'] = "Next"
        context['teams'] = Team.objects.all()
        
        # Add invoice reference data for the modal if on the client profile step
        if self.steps.current == 'client_profile':
            all_references = InvoiceReference.objects.all()
            context['invoice_references'] = all_references
        
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
                if existing_relationship.is_active:
                    messages.warning(request, f"This relationship with {to_company.company_name} already exists.")
                else:
                    # Reactivate the existing relationship
                    existing_relationship.is_active = True
                    existing_relationship.save()
                    messages.success(request, f"Reactivated relationship with {to_company.company_name}.")
                    
                    # Create activity record for relationship reactivation
                    Activity.objects.create(
                        company=company,
                        activity_type='update',
                        description=f"Reactivated {relationship_type} relationship with {to_company.company_name}",
                        performed_by=request.user,
                        is_system_activity=True
                    )
            else:
                # Create new relationship
                relationship = CompanyRelationship.objects.create(
                    from_company=company,
                    to_company=to_company,
                    relationship_type=relationship_type,
                    created_by=request.user
                )
                messages.success(request, f"Added {to_company.company_name} as a {relationship_type}.")
                
                # Create activity record for new relationship
                Activity.objects.create(
                    company=company,
                    activity_type='update',
                    description=f"Added {relationship_type} relationship with {to_company.company_name}",
                    performed_by=request.user,
                    is_system_activity=True
                )
            
            return redirect('crm:manage_company_relationships', company_id=company_id)
    else:
        form = CompanyRelationshipForm(from_company=company)
    
    context = {
        'company': company,
        'form': form,
        'relationships_from': relationships_from,
        'relationships_to': relationships_to
    }
    
    return render(request, 'crm/company_relationships.html', context)

@login_required
def delete_company_relationship(request, relationship_id):
    """Delete a company relationship."""
    relationship = get_object_or_404(CompanyRelationship, id=relationship_id)
    company_id = relationship.from_company.id
    
    # Check if the user has permission (could add more checks)
    relationship.is_active = False
    relationship.save()
    
    # Create activity record for relationship deletion
    Activity.objects.create(
        company=relationship.from_company,
        activity_type='update',
        description=f"Removed {relationship.relationship_type} relationship with {relationship.to_company.company_name}",
        performed_by=request.user,
        is_system_activity=True
    )
    
    messages.success(request, f"Relationship with {relationship.to_company.company_name} has been removed.")
    return redirect('crm:manage_company_relationships', company_id=company_id) 