from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy, reverse

from crm.models import Company, Contact, Activity, ContactNote
from crm.forms import ContactForm, ContactNoteForm

class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = 'crm/contact_list.html'
    context_object_name = 'contacts'
    
    def get_queryset(self):
        return Contact.objects.all().order_by('company__company_name', 'first_name')

class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    template_name = 'crm/contact_detail.html'
    context_object_name = 'contact'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.object.notes.all().order_by('-created_at')
        return context

class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'crm/contact_form.html'
    
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
    
    def get_success_url(self):
        if self.object.company:
            return reverse_lazy('crm:company_detail', kwargs={'pk': self.object.company.id})
        return reverse_lazy('crm:contact_list')

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

@login_required
def contact_add_note(request, pk):
    """Add a note to a contact"""
    contact = get_object_or_404(Contact, id=pk)
    
    if request.method == 'POST':
        form = ContactNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.contact = contact
            note.created_by = request.user
            note.save()
            
            messages.success(request, "Note added successfully.")
            return redirect('crm:contact_detail', pk=contact.id)
    else:
        form = ContactNoteForm()
    
    context = {
        'form': form,
        'contact': contact
    }
    
    return render(request, 'crm/contact_note_form.html', context)

@login_required
def contact_delete(request, pk):
    """Delete a contact"""
    contact = get_object_or_404(Contact, id=pk)
    company_id = contact.company.id if contact.company else None
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, f"{contact.first_name} {contact.last_name} deleted successfully.")
        
        if company_id:
            return redirect('crm:company_detail', pk=company_id)
        return redirect('crm:contact_list')
    
    context = {
        'contact': contact,
        'company_id': company_id
    }
    
    return render(request, 'crm/contact_confirm_delete.html', context) 