import json
from datetime import datetime
from .models import AgentSupportSupplier
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AgentSupportSupplierForm
from django.contrib import messages
from .models import SupplierAttachment
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def agent_support_view(request):
    """Landing page for agent support section"""
    return render(request, 'agent_support/agent_support_view.html')

@login_required
def supplier_contacts(request):
    """View for managing supplier contacts"""
    search_query = request.GET.get('search', '')
    supplier_type = request.GET.get('type', '')
    
    suppliers = AgentSupportSupplier.objects.all()
    
    if search_query:
        suppliers = suppliers.filter(
            Q(supplier_name__icontains=search_query) |
            Q(account_manager_name__icontains=search_query) |
            Q(account_manager_email__icontains=search_query)
        )
    
    if supplier_type:
        suppliers = suppliers.filter(supplier_type=supplier_type)
    
    suppliers = suppliers.order_by('supplier_name')
    
    paginator = Paginator(suppliers, 10)  # Show 10 suppliers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'supplier_type': supplier_type,
        'supplier_types': AgentSupportSupplier.SUPPLIER_TYPE
    }
    
    return render(request, 'agent_support/supplier_contacts.html', context)

@login_required
def add_agent_supplier(request):
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier {supplier.supplier_name} has been added successfully.')
            return redirect('agent_support:supplier_contacts')
    else:
        form = AgentSupportSupplierForm()
    
    return render(request, 'agent_support/add_agent_supplier.html', {
        'form': form,
        'supplier_types': AgentSupportSupplier.SUPPLIER_TYPE
    })

@login_required
def edit_agent_supplier(request, pk):
    supplier = get_object_or_404(AgentSupportSupplier, pk=pk)
    
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier {supplier.supplier_name} has been updated successfully.')
            return redirect('agent_support:supplier_contacts')
    else:
        form = AgentSupportSupplierForm(instance=supplier)
    
    return render(request, 'agent_support/edit_agent_supplier.html', {
        'form': form,
        'supplier': supplier,
        'supplier_types': AgentSupportSupplier.SUPPLIER_TYPE
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
def delete_attachment(request, pk):
    if request.method == 'POST':
        attachment = get_object_or_404(SupplierAttachment, pk=pk)
        supplier_pk = attachment.supplier.pk
        attachment.delete()
        messages.success(request, 'Attachment deleted successfully.')
        return redirect('agent_support:supplier_contacts')
    return JsonResponse({'error': 'Invalid request method'}, status=400)
