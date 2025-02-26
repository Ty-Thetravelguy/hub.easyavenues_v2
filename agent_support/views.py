import json
from datetime import datetime
from .models import AgentSupportSupplier
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AgentSupportSupplierForm
from django.contrib import messages
from .models import SupplierAttachment

@login_required
def agent_support_view(request):
    suppliers = AgentSupportSupplier.objects.all().order_by('supplier_type', 'supplier_name')

    for supplier in suppliers:
        # Ensure contact_phone is a list
        if supplier.contact_phone is None or supplier.contact_phone == '[]':
            supplier.contact_phone = []
        elif isinstance(supplier.contact_phone, str):
            try:
                supplier.contact_phone = json.loads(supplier.contact_phone)
            except json.JSONDecodeError:
                supplier.contact_phone = []
        
        # Ensure general_email is a list
        if supplier.general_email is None or supplier.general_email == '[]':
            supplier.general_email = []
        elif isinstance(supplier.general_email, str):
            try:
                supplier.general_email = json.loads(supplier.general_email)
            except json.JSONDecodeError:
                supplier.general_email = []

        # Ensure other_notes is a list
        if supplier.other_notes is None or supplier.other_notes == '[]':
            supplier.other_notes = []
        elif isinstance(supplier.other_notes, str):
            try:
                supplier.other_notes = json.loads(supplier.other_notes)
            except json.JSONDecodeError:
                supplier.other_notes = []
    
    return render(request, 'agent_support/agent_support_view.html', {
        'suppliers': suppliers,
        'supplier_types': AgentSupportSupplier.SUPPLIER_TYPE
    })

@login_required
def add_agent_supplier(request):
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            
            # Process websites
            website_urls = request.POST.getlist('website_url[]')
            website_descriptions = request.POST.getlist('website_description[]')
            websites = []
            for url, description in zip(website_urls, website_descriptions):
                if url and description:
                    websites.append({'url': url, 'description': description})
            supplier.agent_websites = websites
            
            # Process phone numbers
            phone_numbers = request.POST.getlist('phone_number[]')
            phone_descriptions = request.POST.getlist('phone_description[]')
            phones = []
            for number, description in zip(phone_numbers, phone_descriptions):
                if number and description:
                    phones.append({'number': number, 'description': description})
            supplier.contact_phone = phones
            
            # Process email addresses
            email_addresses = request.POST.getlist('email_address[]')
            email_descriptions = request.POST.getlist('email_description[]')
            emails = []
            for email, description in zip(email_addresses, email_descriptions):
                if email and description:
                    emails.append({'email': email, 'description': description})
            supplier.general_email = emails
            
            # Process notes
            notes = []
            for note in request.POST.getlist('note_text[]'):
                if note:
                    notes.append({
                        'note': note,
                        'created_by': request.user.username,
                        'created_at': datetime.now().isoformat()
                    })
            if notes:
                supplier.other_notes = notes
            
            supplier.save()
            messages.success(request, f'Supplier "{supplier.supplier_name}" was added successfully!')
            return redirect('agent_support:agent_support_view')
    else:
        form = AgentSupportSupplierForm()
    
    return render(request, 'agent_support/add_agent_supplier.html', {
        'form': form
    })

@login_required
def edit_agent_supplier(request, supplier_id):
    supplier = get_object_or_404(AgentSupportSupplier, id=supplier_id)
    
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save(commit=False)
            
            # Process websites
            website_urls = request.POST.getlist('website_url[]')
            website_descriptions = request.POST.getlist('website_description[]')
            websites = []
            for url, description in zip(website_urls, website_descriptions):
                if url and description:  # Only add if both fields are filled
                    websites.append({'url': url, 'description': description})
            supplier.agent_websites = websites
            
            # Process phone numbers
            phone_numbers = request.POST.getlist('phone_number[]')
            phone_descriptions = request.POST.getlist('phone_description[]')
            phones = []
            for number, description in zip(phone_numbers, phone_descriptions):
                if number and description:  # Only add if both fields are filled
                    phones.append({'number': number, 'description': description})
            supplier.contact_phone = phones
            
            # Process email addresses
            email_addresses = request.POST.getlist('email_address[]')
            email_descriptions = request.POST.getlist('email_description[]')
            emails = []
            for email, description in zip(email_addresses, email_descriptions):
                if email and description:  # Only add if both fields are filled
                    emails.append({'email': email, 'description': description})
            supplier.general_email = emails
            
            # Process notes
            notes = []
            for note in request.POST.getlist('note_text[]'):
                if note:  # Only add if note is not empty
                    notes.append({
                        'note': note,
                        'created_by': request.user.username,
                        'created_at': datetime.now().isoformat()
                    })
            if notes:
                supplier.other_notes = notes
            
            supplier.save()
            messages.success(request, f'Successfully updated {supplier.supplier_name}')
            return redirect('agent_support:agent_support_view')
    else:
        form = AgentSupportSupplierForm(instance=supplier)
    
    return render(request, 'agent_support/edit_agent_supplier.html', {
        'form': form,
        'supplier': supplier
    })
@login_required
def delete_agent_supplier(request, supplier_id):
    supplier = get_object_or_404(AgentSupportSupplier, id=supplier_id)
    if request.method == 'POST':
        supplier_name = supplier.supplier_name
        supplier.delete()
        messages.success(request, f'Supplier "{supplier_name}" was successfully deleted.')
        return redirect('agent_support:agent_support_view')
    return redirect('agent_support:agent_support_view')


@login_required
def add_attachment(request, supplier_id):
    if request.method == 'POST':
        supplier = get_object_or_404(AgentSupportSupplier, id=supplier_id)
        
        attachment = SupplierAttachment.objects.create(
            supplier=supplier,
            heading=request.POST['heading'],
            description=request.POST.get('description'), 
            pdf_file=request.FILES['pdf_file'],
            created_by=request.user
        )
        
        return redirect('agent_support:agent_support_view')
    
    return redirect('agent_support:agent_support_view')

@login_required
def delete_attachment(request, supplier_id, attachment_id):
    if request.method == 'POST':
        attachment = get_object_or_404(SupplierAttachment, 
                                     id=attachment_id,
                                     supplier_id=supplier_id)
        attachment.delete()
        messages.success(request, 'Attachment deleted successfully.')
        return redirect('agent_support:agent_support_view')
    return redirect('agent_support:agent_support_view')
