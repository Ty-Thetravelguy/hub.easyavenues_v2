# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .forms import CustomSignupForm, AdminUserCreationForm, EditUserForm
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

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
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.get_full_name()} has been created. A verification email has been sent to {user.email}.')
            return redirect('admin:accounts_customuser_changelist')
    else:
        form = AdminUserCreationForm()
    
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

