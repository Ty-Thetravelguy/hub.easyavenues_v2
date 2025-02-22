import json
from .models import AgentSupportSupplier
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AgentSupportSupplierForm

# Create your views here.
@login_required
def agent_support_view(request):
    suppliers = AgentSupportSupplier.objects.all().order_by('supplier_type')
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
            supplier.agent_websites = websites
            supplier.save()
            return redirect('agent_support:agent_support_view')
    else:
        form = AgentSupportSupplierForm()
    
    return render(request, 'agent_support/add_agent_supplier.html', {
        'form': form
    })
