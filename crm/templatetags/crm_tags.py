from django import template
import re

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get a dictionary value by key."""
    return dictionary.get(key) 

@register.filter
def split(value, delimiter):
    """Split a string by a delimiter and return a list."""
    return value.split(delimiter) 

@register.filter
def split_email_desc(description, activity=None):
    """
    Parse an email activity description into structured data.
    If activity is provided and has data field, use that instead.
    """
    if activity and activity.data and isinstance(activity.data, dict):
        # Use stored structured data if available
        email_data = {}
        email_data['subject'] = activity.data.get('subject', '')
        email_data['content'] = activity.data.get('content', '')
        
        # Format recipients if available
        recipients = []
        recipient_ids = activity.data.get('recipients', [])
        if recipient_ids:
            from crm.models import Contact
            for recipient_id in recipient_ids:
                try:
                    contact = Contact.objects.get(id=recipient_id)
                    recipients.append(f"{contact.first_name} {contact.last_name}")
                except Contact.DoesNotExist:
                    pass
        
        # If recipient data not in data field or contact lookup failed
        if not recipients and 'contact_id' in activity.data:
            try:
                from crm.models import Contact
                contact = Contact.objects.get(id=activity.data['contact_id'])
                recipients = [f"{contact.first_name} {contact.last_name}"]
            except Contact.DoesNotExist:
                pass
            
        email_data['recipients'] = ", ".join(recipients) if recipients else "No recipients specified"
        return email_data

    # Fall back to parsing description
    pattern = r"Email (?:sent|to) (?:to |)([^:]+)(?:: )(.+)"
    match = re.search(pattern, description)
    
    if match:
        recipients = match.group(1).strip()
        subject = match.group(2).strip()
        
        return {
            'subject': subject,
            'recipients': recipients,
            'content': 'Content details not available'  # Placeholder
        }
    
    # If no match, return a default structure
    return {
        'subject': 'No subject',
        'recipients': 'No recipients',
        'content': 'No content available'
    }

@register.filter
def split_call_desc(description, activity=None):
    """
    Parse a call activity description into structured data.
    If activity is provided and has data field, use that instead.
    """
    if activity and activity.data and isinstance(activity.data, dict):
        # Use stored structured data if available
        call_data = {}
        
        # Get contact name
        contact_name = "Unknown"
        if 'contact_id' in activity.data:
            try:
                from crm.models import Contact
                contact = Contact.objects.get(id=activity.data['contact_id'])
                contact_name = f"{contact.first_name} {contact.last_name}"
            except Contact.DoesNotExist:
                pass
        
        call_data['contact'] = contact_name
        call_data['duration'] = activity.data.get('duration', 'Not specified')
        call_data['call_type'] = activity.data.get('call_type', 'outgoing').title()
        call_data['summary'] = activity.data.get('summary', '')
        return call_data

    # Fall back to parsing description
    pattern = r"(?:(Incoming|Outgoing) )?[cC]all with ([^()]+)(?:\s+\((\d+)\s+mins\))?: (.+)"
    match = re.search(pattern, description)
    
    if match:
        call_type = match.group(1) if match.group(1) else "Outgoing"
        contact = match.group(2).strip()
        duration = match.group(3) if match.group(3) else "Not specified"
        summary = match.group(4).strip()
        
        return {
            'call_type': call_type,
            'contact': contact,
            'duration': duration,
            'summary': summary
        }
    
    # If no match, return a default structure
    return {
        'call_type': 'Unknown',
        'contact': 'Unknown',
        'duration': 'Not specified',
        'summary': 'No summary available'
    }

@register.filter
def split_note_desc(description, activity=None):
    """
    Parse a note activity description into structured data.
    If activity is provided and is a NoteActivity, use its content field.
    """
    if activity and hasattr(activity, 'noteactivity'):
        # Use the NoteActivity model's content field
        note_data = {
            'content': activity.noteactivity.content,
            'contact': None
        }
        
        # Get contact name if applicable
        if activity.contact:
            note_data['contact'] = f"{activity.contact.first_name} {activity.contact.last_name}"
        
        return note_data

    # Fall back to parsing description
    pattern = r"Note(?:\s+about\s+([^:]+))?: (.+)"
    match = re.search(pattern, description)
    
    if match:
        contact = match.group(1) if match.group(1) else None
        content = match.group(2).strip()
        
        return {
            'contact': contact,
            'content': content
        }
    
    # If no match, just return the description as content
    return {
        'contact': None,
        'content': description
    }

@register.filter
def split_exception_desc(description, activity=None):
    """
    Parse an exception activity description into structured data.
    If activity is provided and has data field, use that instead.
    """
    if activity and activity.data and isinstance(activity.data, dict):
        # Use stored structured data if available
        exception_data = {}
        
        # Format exception type
        exception_type = activity.data.get('exception_type', '')
        exception_data['type'] = exception_type.replace('_', ' ').title() if exception_type else 'Unknown'
        
        # Get value amount
        exception_data['value'] = activity.data.get('value_amount', 'Not specified')
        
        # Get contact name
        contact_name = "Unknown"
        if 'contact_id' in activity.data:
            try:
                from crm.models import Contact
                contact = Contact.objects.get(id=activity.data['contact_id'])
                contact_name = f"{contact.first_name} {contact.last_name}"
            except Contact.DoesNotExist:
                pass
        
        exception_data['contact'] = contact_name
        
        # Format approval info
        approved_by = activity.data.get('approved_by')
        if approved_by and approved_by != 'none':
            exception_data['approval'] = approved_by.replace('_', ' ').title()
        else:
            exception_data['approval'] = 'Not approved'
        
        exception_data['description'] = activity.data.get('description', '')
        return exception_data

    # Fall back to parsing description
    pattern = r"([\w\s]+)(?:\s+\(£([\d.]+)\))?\s+for\s+([^,]+)(?:,\s+approved\s+by\s+([^:]+))?: (.+)"
    match = re.search(pattern, description)
    
    if match:
        exception_type = match.group(1).strip()
        value = match.group(2) if match.group(2) else 'Not specified'
        contact = match.group(3).strip()
        approval = match.group(4) if match.group(4) else 'Not approved'
        desc = match.group(5).strip()
        
        return {
            'type': exception_type,
            'value': value,
            'contact': contact,
            'approval': approval,
            'description': desc
        }
    
    # If no match, return a default structure
    return {
        'type': 'Unknown',
        'value': 'Not specified',
        'contact': 'Unknown',
        'approval': 'Not specified',
        'description': description
    }

@register.filter
def get_activity_details(activity, model_name):
    """
    Get a related activity model instance (e.g., EmailActivity, CallActivity) for an Activity.
    
    Usage:
        {% with email=activity|get_activity_details:'emailactivity' %}
            {{ email.subject }}
        {% endwith %}
    """
    try:
        # Use Django's _meta API to get the related objects
        if not hasattr(activity, model_name.lower()):
            return None
        
        # Get the specific activity model (e.g., emailactivity, callactivity)
        related_activity = getattr(activity, model_name.lower())
        return related_activity
    except Exception as e:
        # In case of error, return None
        return None 