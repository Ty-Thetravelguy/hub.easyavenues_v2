import json
from datetime import datetime
from .models import AgentSupportSupplier
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AgentSupportSupplierForm
from django.contrib import messages

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
            websites = json.loads(request.POST.get('agent_websites', '[]'))
            notes = json.loads(request.POST.get('other_notes', '[]')) 
            supplier.agent_websites = websites
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
            
            print("Notes from form:", request.POST.getlist('note_text[]'))

            # Initialize empty lists (not None)
            supplier.contact_phone = []
            supplier.general_email = []
            supplier.agent_websites = []
            supplier.other_notes = []  # Add this line
            
            # Get the raw form data
            raw_phones = [p for p in request.POST.getlist('phone_number[]') if p.strip()]
            raw_phone_desc = [d for d in request.POST.getlist('phone_description[]') if d.strip()]
            raw_emails = [e for e in request.POST.getlist('email_address[]') if e.strip()]
            raw_email_desc = [d for d in request.POST.getlist('email_description[]') if d.strip()]
            raw_urls = [u for u in request.POST.getlist('website_url[]') if u.strip()]
            raw_url_desc = [d for d in request.POST.getlist('website_description[]') if d.strip()]
            raw_notes = [n for n in request.POST.getlist('note_text[]') if n.strip()]  # Add this line
            
            # Process phone numbers (only if both number and description exist)
            for number, desc in zip(raw_phones, raw_phone_desc):
                if number.strip() and desc.strip():
                    supplier.contact_phone.append({
                        'number': number.strip(),
                        'description': desc.strip()
                    })
            
            # Process emails (only if both email and description exist)
            for email, desc in zip(raw_emails, raw_email_desc):
                if email.strip() and desc.strip():
                    supplier.general_email.append({
                        'email': email.strip(),
                        'description': desc.strip()
                    })
            
            # Process websites (only if both url and description exist)
            for url, desc in zip(raw_urls, raw_url_desc):
                if url.strip() and desc.strip():
                    supplier.agent_websites.append({
                        'url': url.strip(),
                        'description': desc.strip()
                    })

            # Process notes
            for note in raw_notes:
                if note.strip():
                    supplier.other_notes.append({
                        'note': note.strip(),
                        'created_at': datetime.now().isoformat(),
                        'created_by': request.user.get_full_name() or request.user.username
                    })
            
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