from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from crm.models import Company, ClientTravelPolicy, Activity, Contact
from crm.forms import TravelPolicyForm

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
                    company=company,
                    is_system_activity=True
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
                company=company,
                is_system_activity=True
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
            company=company,
            is_system_activity=True
        )
        
        policy.delete()
        messages.success(request, f"Travel policy '{policy_name}' deleted successfully.")
        
        return redirect('crm:company_detail', pk=company_id)
    
    # For GET requests, display confirmation page
    return render(request, 'crm/travel_policy_confirm_delete.html', {'policy': policy}) 