# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomSignupForm, AdminUserCreationForm, EditUserForm, TeamForm, InvoiceReferenceForm
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from django.http import HttpResponseForbidden, JsonResponse
from .models import Team, InvoiceReference

User = get_user_model()

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully!')
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomSignupForm()
    
    return render(request, 'account/signup.html', {'form': form})

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST, request=request, user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.get_full_name()} has been created. A verification email has been sent to {user.email}.')
            return redirect('accounts:user_list')
    else:
        form = AdminUserCreationForm(request=request, user=request.user)
    
    return render(request, 'accounts/create_user.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all().order_by('email')
    for user in users:
        email_address = EmailAddress.objects.filter(email=user.email).first()
        user.email_verified = email_address.verified if email_address else False
    
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.get_full_name()} has been updated successfully.')
            return redirect('accounts:user_list')
    else:
        form = EditUserForm(instance=user)
    
    return render(request, 'accounts/edit_user.html', {
        'form': form,
        'user': user
    })

@login_required
def toggle_user_active(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
        
    target_user = get_object_or_404(User, id=user_id)
    
    # Check permissions
    if request.user.role not in ['superuser', 'admin']:
        return HttpResponseForbidden("You don't have permission to perform this action.")
        
    # Admin can't deactivate superuser
    if request.user.role == 'admin' and target_user.role == 'superuser':
        messages.error(request, "Administrators cannot deactivate superusers.")
        return redirect('accounts:user_list')
        
    # Admin can't deactivate other admins
    if request.user.role == 'admin' and target_user.role == 'admin' and request.user != target_user:
        messages.error(request, "Administrators cannot deactivate other administrators.")
        return redirect('accounts:user_list')
        
    # Users can't deactivate themselves
    if request.user == target_user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('accounts:user_list')
    
    # Toggle active status
    target_user.is_active = not target_user.is_active
    target_user.save()
    
    status = "activated" if target_user.is_active else "deactivated"
    messages.success(request, f"User {target_user.get_full_name()} has been {status}.")
    
    return redirect('accounts:user_list')

def is_admin_or_superuser(user):
    return user.is_superuser or user.role == 'admin'

@login_required
@user_passes_test(is_admin_or_superuser)
def admin_dashboard(request):
    return render(request, 'accounts/admin/dashboard.html', {
        'active_tab': 'dashboard'
    })

@login_required
@user_passes_test(is_admin_or_superuser)
def admin_user_list(request):
    users = User.objects.all().order_by('email')
    for user in users:
        email_address = EmailAddress.objects.filter(email=user.email).first()
        user.email_verified = email_address.verified if email_address else False
    
    return render(request, 'accounts/admin/user_list.html', {
        'users': users,
        'active_tab': 'users'
    })

@login_required
@user_passes_test(is_admin_or_superuser)
def admin_user_create(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST, request=request, user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.get_full_name()} has been created.')
            return redirect('accounts:admin_user_list')
    else:
        form = AdminUserCreationForm(request=request, user=request.user)
    
    return render(request, 'accounts/admin/user_form.html', {
        'form': form,
        'active_tab': 'users',
        'title': 'Create User'
    })

@login_required
@user_passes_test(is_admin_or_superuser)
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.get_full_name()} has been updated.')
            return redirect('accounts:admin_user_list')
    else:
        form = EditUserForm(instance=user)
    
    return render(request, 'accounts/admin/user_form.html', {
        'form': form,
        'user': user,
        'active_tab': 'users',
        'title': 'Edit User'
    })

@login_required
@user_passes_test(is_admin_or_superuser)
def admin_toggle_user_active(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    
    if request.user.role == 'admin' and target_user.is_superuser:
        messages.error(request, "Administrators cannot deactivate superusers.")
        return redirect('accounts:admin_user_list')
    
    if request.user.role == 'admin' and target_user.role == 'admin' and request.user != target_user:
        messages.error(request, "Administrators cannot deactivate other administrators.")
        return redirect('accounts:admin_user_list')
    
    if request.user == target_user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('accounts:admin_user_list')
    
    target_user.is_active = not target_user.is_active
    target_user.save()
    
    status = "activated" if target_user.is_active else "deactivated"
    messages.success(request, f"User {target_user.get_full_name()} has been {status}.")
    
    return redirect('accounts:admin_user_list')

@login_required
@user_passes_test(is_admin_or_superuser)
def admin_team_list(request):
    teams = Team.objects.all()
    return render(request, 'accounts/admin/team_list.html', {
        'teams': teams,
        'active_tab': 'teams'
    })

@login_required
@user_passes_test(is_admin_or_superuser)
def admin_team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            messages.success(request, f'Team "{team.name}" has been created.')
            return redirect('accounts:admin_team_list')
    else:
        form = TeamForm()
    
    return render(request, 'accounts/admin/team_form.html', {
        'form': form,
        'active_tab': 'teams',
        'title': 'Create Team'
    })

@login_required
@user_passes_test(is_admin_or_superuser)
def admin_team_edit(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            team = form.save()
            messages.success(request, f'Team "{team.name}" has been updated.')
            return redirect('accounts:admin_team_list')
    else:
        form = TeamForm(instance=team)
    
    return render(request, 'accounts/admin/team_form.html', {
        'form': form,
        'team': team,
        'active_tab': 'teams',
        'title': 'Edit Team'
    })

@login_required
@user_passes_test(is_admin_or_superuser)
def admin_team_members(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    users = User.objects.all()
    
    if request.method == 'POST':
        member_ids = request.POST.getlist('members')
        team.members.set(member_ids)
        messages.success(request, f'Team members for "{team.name}" have been updated.')
        return redirect('accounts:admin_team_list')
    
    return render(request, 'accounts/admin/team_members.html', {
        'team': team,
        'users': users,
        'active_tab': 'teams'
    })

@login_required
@user_passes_test(is_admin_or_superuser)
def admin_team_delete(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    team_name = team.name
    team.delete()
    messages.success(request, f'Team "{team_name}" has been deleted.')
    return redirect('accounts:admin_team_list')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_invoice_reference_list(request):
    invoice_references = InvoiceReference.objects.all()
    return render(request, 'accounts/admin/invoice_reference_list.html', {
        'invoice_references': invoice_references,
        'active_tab': 'invoice_references',
        'title': 'Invoice References'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_invoice_reference_create(request):
    if request.method == 'POST':
        form = InvoiceReferenceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Invoice reference created successfully.')
            return redirect('accounts:admin_invoice_reference_list')
    else:
        form = InvoiceReferenceForm()

    return render(request, 'accounts/admin/invoice_reference_form.html', {
        'form': form,
        'active_tab': 'invoice_references',
        'title': 'Create Invoice Reference'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_invoice_reference_edit(request, reference_id):
    invoice_reference = get_object_or_404(InvoiceReference, id=reference_id)
    
    if request.method == 'POST':
        form = InvoiceReferenceForm(request.POST, instance=invoice_reference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Invoice reference updated successfully.')
            return redirect('accounts:admin_invoice_reference_list')
    else:
        form = InvoiceReferenceForm(instance=invoice_reference)

    return render(request, 'accounts/admin/invoice_reference_form.html', {
        'form': form,
        'invoice_reference': invoice_reference,
        'active_tab': 'invoice_references',
        'title': 'Edit Invoice Reference'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_invoice_reference_delete(request, reference_id):
    reference = get_object_or_404(InvoiceReference, id=reference_id)
    
    if request.method == 'POST':
        reference.delete()
        messages.success(request, f'Invoice reference "{reference.name}" has been deleted.')
        return redirect('accounts:admin_invoice_reference_list')
    
    return redirect('accounts:admin_invoice_reference_list')

@login_required
def get_team_members(request, team_id):
    """API endpoint to get team members."""
    try:
        team = Team.objects.get(id=team_id)
        members = team.members.all()
        members_data = [{
            'id': member.id,
            'full_name': member.get_full_name(),
            'role': member.get_role_display()
        } for member in members]
        return JsonResponse(members_data, safe=False)
    except Team.DoesNotExist:
        return JsonResponse({'error': 'Team not found'}, status=404)

