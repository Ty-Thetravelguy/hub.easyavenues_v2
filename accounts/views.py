# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomSignupForm

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

