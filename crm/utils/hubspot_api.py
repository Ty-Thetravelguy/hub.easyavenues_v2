"""
Utility functions for interacting with the HubSpot API.
"""

import requests
import json
import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)

# Base API URL
HUBSPOT_API_BASE_URL = "https://api.hubapi.com"

def get_hubspot_headers():
    """
    Get headers for HubSpot API requests using the API key.
    """
    api_key = settings.HUBSPOT_API_KEY
    
    if not api_key:
        logger.error("HubSpot API key is not configured. Please set HUBSPOT_API_KEY in your environment.")
        return None
        
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def search_companies(query, limit=10):
    """
    Search for companies in HubSpot that match the given query.
    
    Args:
        query (str): Search term to match against HubSpot companies.
        limit (int): Maximum number of results to return.
        
    Returns:
        dict: JSON response from HubSpot API.
    """
    headers = get_hubspot_headers()
    if not headers:
        return {"results": [], "error": "API key not configured"}
    
    # First try the search endpoint
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/companies/search"
    payload = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "name",
                        "operator": "CONTAINS_TOKEN",
                        "value": query
                    }
                ]
            }
        ],
        "limit": limit,
        "properties": [
            "name", 
            "domain", 
            "phone", 
            "address", 
            "city", 
            "state", 
            "zip", 
            "country", 
            "industry", 
            "description", 
            "linkedin_company_page",
            "website"
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching HubSpot companies with POST: {e}")
        
        # If POST fails, try a GET request to list companies
        try:
            # Fallback to list endpoint with name filter
            list_url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/companies"
            params = {
                "limit": limit,
                "properties": "name,domain,phone,address,city,state,zip,country,industry,description,linkedin_company_page,website",
                "archived": "false"
            }
            response = requests.get(list_url, headers=headers, params=params)
            response.raise_for_status()
            
            # Filter results manually
            all_results = response.json()
            filtered_results = {"results": []}
            
            for result in all_results.get("results", []):
                company_name = result.get("properties", {}).get("name", "").lower()
                if query.lower() in company_name:
                    filtered_results["results"].append(result)
            
            return filtered_results
        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing HubSpot companies with GET: {e}")
            return {"results": [], "error": str(e)}

def get_company_details(hubspot_company_id):
    """
    Get detailed information about a specific company in HubSpot.
    
    Args:
        hubspot_company_id (str): HubSpot ID for the company.
        
    Returns:
        dict: JSON response containing company details.
    """
    headers = get_hubspot_headers()
    if not headers:
        return {}
    
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/companies/{hubspot_company_id}"
    params = {
        "properties": "name,domain,phone,address,city,state,zip,country,industry,description,linkedin_company_page,website,hubspot_owner_id"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting HubSpot company details: {e}")
        return {}

def get_company_contacts(hubspot_company_id, limit=100):
    """
    Get contacts associated with a specific company in HubSpot.
    
    Args:
        hubspot_company_id (str): HubSpot ID for the company.
        limit (int): Maximum number of contacts to return.
        
    Returns:
        list: List of contact dictionaries.
    """
    headers = get_hubspot_headers()
    if not headers:
        return []
    
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/companies/{hubspot_company_id}/associations/contacts"
    params = {"limit": limit}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        # Now get details for each contact
        contact_data = response.json()
        contact_ids = [result["id"] for result in contact_data.get("results", [])]
        
        contacts = []
        for contact_id in contact_ids:
            contact_details = get_contact_details(contact_id)
            if contact_details:
                contacts.append(contact_details)
                
        return contacts
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting contacts for HubSpot company: {e}")
        return []

def get_contact_details(hubspot_contact_id):
    """
    Get detailed information about a specific contact in HubSpot.
    
    Args:
        hubspot_contact_id (str): HubSpot ID for the contact.
        
    Returns:
        dict: JSON response containing contact details.
    """
    headers = get_hubspot_headers()
    if not headers:
        return {}
    
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/contacts/{hubspot_contact_id}"
    params = {
        "properties": "email,firstname,lastname,phone,jobtitle,company,website"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting HubSpot contact details: {e}")
        return {}

def link_company_to_hubspot(company_id, hubspot_company_id):
    """
    Store the HubSpot company ID for a company in our database.
    
    Args:
        company_id (int): ID of the company in our database.
        hubspot_company_id (str): HubSpot ID for the company.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    from crm.models import Company
    
    try:
        company = Company.objects.get(id=company_id)
        company.hubspot_id = hubspot_company_id
        company.save(update_fields=['hubspot_id'])
        return True
    except Exception as e:
        logger.error(f"Error linking company to HubSpot: {e}")
        return False 