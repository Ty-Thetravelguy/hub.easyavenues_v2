# accounts/adapters.py

from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        This is called when saving user via allauth registration.
        We override this to handle our custom fields.
        """
        # Get data from the form
        data = form.cleaned_data
        
        # Set email (required by allauth)
        user.email = data.get('email')
        
        # Set custom fields
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        
        # Set business if available
        if hasattr(form, 'business'):
            user.business = form.business
            
        if commit:
            user.save()
        return user