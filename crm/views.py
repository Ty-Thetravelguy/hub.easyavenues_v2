from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Company, Contact, ClientProfile, SupplierProfile
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView
from django.shortcuts import redirect
from django.contrib import messages
from django import forms

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
            'activities': self.object.activity_set.all().order_by('-timestamp'),
            'documents': self.object.document_set.all().order_by('-upload_date')
        })
        return context

class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    template_name = 'crm/company_form.html'
    success_url = reverse_lazy('crm:company_list')
    fields = [
        'company_name', 'industry', 'email', 'phone_number',
        'street_address', 'city', 'state_province', 'postal_code',
        'country', 'description', 'linkedin_social_page'
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Update {self.object.company_name}"
        context['submit_text'] = "Update Company"
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
        company_id = self.request.GET.get('company')
        if company_id:
            company = Company.objects.get(pk=company_id)
            context['company'] = company
            context['title'] = f"Add Contact to {company.company_name}"
        else:
            context['title'] = "Add New Contact"
        context['submit_text'] = "Create Contact"
        return context

    def form_valid(self, form):
        company_id = self.request.GET.get('company')
        if company_id:
            form.instance.company_id = company_id
        messages.success(self.request, f"Contact {form.instance.get_full_name()} has been created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.company:
            return reverse_lazy('crm:company_detail', kwargs={'pk': self.object.company.pk})
        return reverse_lazy('crm:company_list')

COMPANY_FORMS = [
    ('type', forms.Form),  # Will create this form for company type selection
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
            
        if step == 'type':
            # First step: Company Type Selection
            form.fields['company_type'] = forms.ChoiceField(
                choices=[('Client', 'Client'), ('Supplier', 'Supplier')],
                widget=forms.RadioSelect,
                label="Select Company Type"
            )
        elif step == 'basic':
            # Second step: Basic Company Information
            form.fields.update({
                'company_name': forms.CharField(max_length=255),
                'industry': forms.ChoiceField(choices=[
                    ('Travel', 'Travel'),
                    ('Technology', 'Technology'),
                    ('Finance', 'Finance'),
                    ('Other', 'Other')
                ]),
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
                form.fields.update({
                    'client_type': forms.ChoiceField(choices=[
                        ('Corporate', 'Corporate'),
                        ('Individual', 'Individual')
                    ]),
                    'client_status': forms.ChoiceField(choices=[
                        ('Active', 'Active'),
                        ('Inactive', 'Inactive'),
                        ('Prospect', 'Prospect')
                    ]),
                    'sage_name': forms.CharField(max_length=255, required=False),
                    'midoco_crm_number': forms.CharField(max_length=255, required=False),
                })
            else:
                form.fields.update({
                    'supplier_type': forms.ChoiceField(choices=[
                        ('Airline', 'Airline'),
                        ('Hotel', 'Hotel'),
                        ('Car Rental', 'Car Rental'),
                        ('Other', 'Other')
                    ]),
                    'supplier_status': forms.ChoiceField(choices=[
                        ('Active', 'Active'),
                        ('Inactive', 'Inactive')
                    ]),
                    'supplier_for_department': forms.ChoiceField(choices=[
                        ('Sales', 'Sales'),
                        ('Operations', 'Operations'),
                        ('Finance', 'Finance')
                    ]),
                })

        return form

    def done(self, form_list, **kwargs):
        # Get cleaned data from all steps
        type_data = self.get_cleaned_data_for_step('type')
        basic_data = self.get_cleaned_data_for_step('basic')
        profile_data = self.get_cleaned_data_for_step('profile')

        # Create the company
        company = Company.objects.create(
            company_type=type_data['company_type'],
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
        wizard_steps_names = ['Company Type', 'Basic Information', 'Additional Information']
        step_indices = {'type': 0, 'basic': 1, 'profile': 2}
        context = super().get_context_data(form=form, **kwargs)
        context['wizard_steps_names'] = wizard_steps_names
        context['current_step_name'] = wizard_steps_names[step_indices[self.steps.current]]
        return context

