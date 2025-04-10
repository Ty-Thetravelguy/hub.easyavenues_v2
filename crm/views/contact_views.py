from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy, reverse

from crm.models import Company, Contact, Activity, ContactNote
from crm.forms import ContactForm, ContactNoteForm
from crm.utils import create_system_activity

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
            kwargs['company'] = get_object_or_404(Company, pk=company_id)
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create system activity for contact creation
        create_system_activity(
            company=self.object.company,
            user=self.request.user,
            activity_type='create',
            description=f"created new contact {self.object.get_full_name()}",
            contact=self.object
        )
        
        messages.success(self.request, 'Contact created successfully.')
        return response
    
    def get_success_url(self):
        if self.object.company:
            return reverse_lazy('crm:company_detail', kwargs={'pk': self.object.company.id})
        return reverse_lazy('crm:contact_list')

class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'crm/contact_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.object.company
        return kwargs
    
    def form_valid(self, form):
        # Get the old tags before saving
        old_tags = set(self.object.tag_list or [])
        
        # Save the form to update the contact
        response = super().form_valid(form)
        
        # Get the new tags after saving
        new_tags = set(form.instance.tag_list or [])
        
        # Calculate added and removed tags
        added_tags = new_tags - old_tags
        removed_tags = old_tags - new_tags
        
        # Get the appropriate choices based on company type
        tag_choices = dict(self.object.CONTACT_TAG_CHOICES if self.object.company.company_type == 'Client' 
                         else self.object.SUPPLIER_TAG_CHOICES)
        
        # Create activity for tag changes if any tags were modified
        if added_tags or removed_tags:
            tag_changes = []
            if added_tags:
                added_labels = [tag_choices.get(tag, tag) for tag in added_tags]
                tag_changes.append(f"added tags: {', '.join(added_labels)}")
            if removed_tags:
                removed_labels = [tag_choices.get(tag, tag) for tag in removed_tags]
                tag_changes.append(f"removed tags: {', '.join(removed_labels)}")
            
            create_system_activity(
                company=self.object.company,
                user=self.request.user,
                activity_type='update',
                description=f"updated contact {self.object.get_full_name()} - {', '.join(tag_changes)}",
                contact=self.object
            )
        
        messages.success(self.request, 'Contact updated successfully.')
        return response

class ContactDeleteView(LoginRequiredMixin, DeleteView):
    model = Contact
    template_name = 'crm/contact_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('crm:company_detail', kwargs={'pk': self.object.company.pk})
    
    def delete(self, request, *args, **kwargs):
        contact = self.get_object()
        company = contact.company
        
        # Create system activity before deletion
        create_system_activity(
            company=company,
            user=request.user,
            activity_type='delete',
            description=f"deleted contact {contact.get_full_name()}",
            contact=contact
        )
        
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Contact deleted successfully.')
        return response

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