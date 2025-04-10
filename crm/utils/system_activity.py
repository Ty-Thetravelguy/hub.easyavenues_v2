from django.utils import timezone
from crm.models import Activity

def create_system_activity(company, user, activity_type, description, contact=None):
    """
    Create a system activity with consistent formatting.
    
    Args:
        company: Company instance
        user: User instance who performed the action
        activity_type: Type of activity (e.g., 'update', 'document', 'status_change')
        description: Description of the activity
        contact: Optional Contact instance if activity is related to a contact
    
    Returns:
        Activity instance
    """
    # Format the description with timestamp
    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_description = f"{user.get_full_name()} {description} at {timestamp}"
    
    # Create the activity
    activity = Activity.objects.create(
        company=company,
        contact=contact,
        activity_type=activity_type,
        description=formatted_description,
        performed_by=user,
        is_system_activity=True
    )
    
    return activity 