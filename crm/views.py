from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Company, Contact, ClientProfile, SupplierProfile, INDUSTRY_CHOICES, COMPANY_TYPE, CLIENT_TYPE_CHOICES, CLIENT_STATUS_CHOICES, SUPPLIER_TYPE_CHOICES, SUPPLIER_STATUS_CHOICES, SUPPLIER_FOR_DEPARTMENT_CHOICES
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView
from django.shortcuts import redirect
from django.contrib import messages
from django import forms
from .forms import CompanyForm
from django.contrib.auth import get_user_model
from accounts.models import Team

# Create your views here.

def crm(request):
    return render(request, 'crm/crm.html')

class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'crm/company_list.html'
    context_object_name = 'companies'
    paginate_by = 10

    def get_queryset(self):
        queryset = Company.objects.all()
        
        # Filter by company type
        company_type = self.request.GET.get('type')
        if company_type in ['Client', 'Supplier']:
            queryset = queryset.filter(company_type=company_type)

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(company_name__icontains=search_query) |
                Q(industry__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(country__icontains=search_query)
            )

        return queryset.order_by('-create_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_type'] = self.request.GET.get('type', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'crm/company_detail.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'contacts': self.object.contacts.all(),
            'activities': self.object.activities.all().order_by('-performed_at'),
            'documents': self.object.documents.all().order_by('-uploaded_at')
        })
        return context

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
        return context

    def form_valid(self, form):
        messages.success(self.request, f"{self.object.company_name} has been updated successfully.")
        return super().form_valid(form)

class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    template_name = 'crm/contact_form.html'
    fields = [
        'first_name', 'last_name', 'job_title', 'email',
        'phone_number', 'mobile_number', 'preferred_contact_method',
        'preferred_contact_time', 'do_not_contact', 'teams_id',
        'whatsapp_number'
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_pk = self.kwargs.get('company_pk')
        if company_pk:
            company = Company.objects.get(pk=company_pk)
            context['company'] = company
            context['title'] = f"Add Contact to {company.company_name}"
        else:
            context['title'] = "Add New Contact"
        context['submit_text'] = "Create Contact"
        return context

    def form_valid(self, form):
        company_pk = self.kwargs.get('company_pk')
        if company_pk:
            form.instance.company_id = company_pk
        messages.success(self.request, f"Contact {form.instance.get_full_name()} has been created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.company:
            return reverse_lazy('crm:company_detail', kwargs={'pk': self.object.company.pk})
        return reverse_lazy('crm:company_list')

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
                    'invoice_references': forms.CharField(widget=forms.Textarea, required=False, label='Invoice References'),
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

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context['wizard_steps_names'] = ['Company Type', 'Basic Information', 'Additional Information']
        context['teams'] = Team.objects.all()
        return context

