# accounts/adapters.py

from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        
        # Get data from the form
        data = form.cleaned_data
        user.email = data.get('email')
        user.username = data.get('email') 
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        
        if hasattr(form, 'business'):
            user.business = form.business
            
        if commit:
            user.save()
        return user