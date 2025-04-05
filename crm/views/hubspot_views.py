from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import requests
import re

from crm.models import Company, Contact, ClientProfile, SupplierProfile
from crm.utils import hubspot_api

@login_required
def hubspot_search(request):
    """
    Search for companies in HubSpot and display the results.
    """
    search_results = []
    search_query = request.GET.get('query', '')
    error_message = None
    
    if search_query:
        try:
            # Import here to avoid circular imports
            from crm.utils import hubspot_api
            
            # Search HubSpot API for companies
            results = hubspot_api.search_companies(search_query)
            
            # Check if there's an error
            if 'error' in results:
                error_message = f"Error searching HubSpot: {results.get('error')}"
                messages.error(request, error_message)
            else:
                search_results = results.get('results', [])
                
                # Check which companies we already have in our system
                for result in search_results:
                    hubspot_id = result['id']
                    # See if this company is already linked
                    exists = Company.objects.filter(hubspot_id=hubspot_id).exists()
                    result['is_imported'] = exists
                
                if not search_results:
                    messages.info(request, "No companies found matching your search criteria.")
        
        except Exception as e:
            error_message = f"Error searching HubSpot companies: {str(e)}"
            messages.error(request, error_message)
    
    context = {
        'search_query': search_query,
        'search_results': search_results,
        'error_message': error_message,
    }
    
    return render(request, 'crm/hubspot_search.html', context)

@login_required
def hubspot_company_detail(request, hubspot_id):
    """
    View details of a HubSpot company before importing it.
    """
    # Get company details from HubSpot
    company_data = hubspot_api.get_company_details(hubspot_id)
    
    # Also get associated contacts
    contacts = hubspot_api.get_company_contacts(hubspot_id)
    
    # Check if already imported
    is_imported = Company.objects.filter(hubspot_id=hubspot_id).exists()
    
    if not company_data:
        messages.error(request, "Could not retrieve company details from HubSpot.")
        return redirect('crm:hubspot_search')
    
    context = {
        'company_data': company_data,
        'contacts': contacts,
        'is_imported': is_imported,
        'hubspot_id': hubspot_id,
    }
    
    return render(request, 'crm/hubspot_company_detail.html', context)

@login_required
def import_hubspot_company(request, hubspot_id):
    """
    Import a company from HubSpot into our system.
    """
    if request.method != 'POST':
        return redirect('crm:hubspot_company_detail', hubspot_id=hubspot_id)
    
    # Check if already imported
    existing_company = Company.objects.filter(hubspot_id=hubspot_id).first()
    if existing_company:
        messages.info(request, f"This company is already imported as {existing_company.company_name}.")
        return redirect('crm:company_detail', pk=existing_company.id)
    
    # Get company details from HubSpot
    company_data = hubspot_api.get_company_details(hubspot_id)
    if not company_data:
        messages.error(request, "Could not retrieve company details from HubSpot.")
        return redirect('crm:hubspot_search')
    
    # Get properties from the company data
    properties = company_data.get('properties', {})
    
    # Determine if this is a client or supplier based on form data
    company_type = request.POST.get('company_type', 'Client')
    
    # Create a new company record
    try:
        company = Company(
            agency=request.user.business,
            company_name=properties.get('name', ''),
            company_type=company_type,
            industry=properties.get('industry', 'Other Services'),  # May need mapping
            street_address=properties.get('address', ''),
            city=properties.get('city', ''),
            state_province=properties.get('state', ''),
            postal_code=properties.get('zip', ''),
            country=properties.get('country', ''),
            phone_number=properties.get('phone', ''),
            email='info@' + properties.get('domain', 'example.com'),  # Use domain or placeholder
            description=properties.get('description', ''),
            linkedin_social_page=properties.get('linkedin_company_page', ''),
            hubspot_id=hubspot_id
        )
        company.save()
        
        # Create the appropriate profile
        if company_type == 'Client':
            ClientProfile.objects.create(company=company)
        else:
            SupplierProfile.objects.create(company=company)
        
        # Optionally import contacts as well
        if request.POST.get('import_contacts') == 'on':
            contacts = hubspot_api.get_company_contacts(hubspot_id)
            for contact_data in contacts:
                contact_properties = contact_data.get('properties', {})
                contact = Contact(
                    company=company,
                    first_name=contact_properties.get('firstname', ''),
                    last_name=contact_properties.get('lastname', ''),
                    email=contact_properties.get('email', ''),
                    phone=contact_properties.get('phone', ''),
                    job_title=contact_properties.get('jobtitle', ''),
                    created_by=request.user
                )
                contact.save()
        
        messages.success(request, f"Successfully imported {company.company_name} from HubSpot.")
        return redirect('crm:company_detail', pk=company.id)
        
    except Exception as e:
        messages.error(request, f"Error importing company: {str(e)}")
        return redirect('crm:hubspot_company_detail', hubspot_id=hubspot_id)

@login_required
def hubspot_api_test(request):
    """
    Test the HubSpot API connection and display diagnostic information.
    """
    api_key = settings.HUBSPOT_API_KEY
    api_connected = False
    api_error = None
    api_key_set = bool(api_key)
    api_key_format_valid = False
    api_endpoint = "https://api.hubapi.com/crm/v3/objects/companies"
    
    # Check API key format - modern HubSpot API keys start with "pat-"
    if api_key_set:
        # HubSpot is transitioning to Private App tokens that start with "pat-"
        if api_key.startswith('pat-'):
            api_key_format_valid = True
        else:
            # Legacy API keys might still work, so we'll check the format
            api_key_format_valid = re.match(r'^[a-zA-Z0-9-]+$', api_key) is not None
    
    # Test connection to HubSpot API
    if api_key_set:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "limit": 1,
            "properties": "name",
            "archived": "false"
        }
        
        try:
            response = requests.get(api_endpoint, headers=headers, params=params)
            
            if response.status_code == 200:
                api_connected = True
            else:
                api_error = f"{response.status_code} {response.reason}: {response.text}"
        except Exception as e:
            api_error = str(e)
    
    context = {
        'api_connected': api_connected,
        'api_error': api_error,
        'api_key_set': api_key_set,
        'api_key_format_valid': api_key_format_valid,
        'api_endpoint': api_endpoint,
    }
    
    return render(request, 'crm/hubspot_api_debug.html', context)

@login_required
def hubspot_setup_guide(request):
    """
    Display a guide for setting up the HubSpot integration.
    """
    return render(request, 'crm/hubspot_setup_guide.html') 