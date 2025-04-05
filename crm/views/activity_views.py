from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models import Q
import logging

from crm.models import Company, Activity, Contact, WaiverActivity, TaskActivity, EmailActivity, CallActivity
from crm.forms import (
    EmailActivityForm, CallActivityForm, MeetingActivityForm, 
    NoteActivityForm, WaiverFavorActivityForm, ToDoTaskForm, DocumentActivityForm, 
    StatusChangeActivityForm, PolicyUpdateActivityForm
)
from django.contrib.auth.models import User

@login_required
def activity_form(request, activity_type):
    """Render the appropriate activity form"""
    try:
        company_id = request.GET.get('company_id')
        if not company_id:
            return JsonResponse({'error': 'No company ID provided'}, status=400)
        
        company = get_object_or_404(Company, id=company_id)
        
        # Get all users for task assignment
        users = User.objects.filter(is_active=True)
        
        template_map = {
            'email': 'crm/activities/email_form.html',
            'call': 'crm/activities/call_form.html',
            'meeting': 'crm/activities/meeting_form.html',
            'note': 'crm/activities/note_form.html',
            'waiver': 'crm/activities/waiver_form.html',
            'task': 'crm/activities/task_form.html',
        }
        
        template_name = template_map.get(activity_type)
        if not template_name:
            return JsonResponse({'error': f'Invalid activity type: {activity_type}'}, status=400)
        
        context = {
            'company': company,
            'today_date': timezone.now(),
            'users': users,
        }
        
        html = render_to_string(template_name, context, request)
        return HttpResponse(html)
    except Exception as e:
        import traceback
        logging.error(f"Error in activity_form view for {activity_type}: {str(e)}")
        logging.error(traceback.format_exc())
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@login_required
def company_activities(request, company_id):
    """Get activities for a specific company"""
    try:
        # Add simple health check response if requested
        if 'health_check' in request.GET:
            return HttpResponse("Activity view is responding correctly", content_type="text/plain")
            
        logging.info(f"Starting company_activities view for company_id={company_id}")
        company = get_object_or_404(Company, id=company_id)
        activity_type = request.GET.get('type', 'all')
        logging.info(f"Fetching activities of type '{activity_type}' for company {company.company_name} (ID: {company.id})")
        
        if activity_type == 'all':
            activities = Activity.objects.filter(company=company).select_related(
                'emailactivity', 'callactivity', 'meetingactivity', 'noteactivity', 
                'waiveractivity', 'taskactivity', 'documentactivity', 'statuschangeactivity',
                'policyupdateactivity'
            ).order_by('-performed_at')
        else:
            activities = Activity.objects.filter(
                company=company, activity_type=activity_type
            ).select_related(
                'emailactivity', 'callactivity', 'meetingactivity', 'noteactivity', 
                'waiveractivity', 'taskactivity', 'documentactivity', 'statuschangeactivity',
                'policyupdateactivity'
            ).order_by('-performed_at')
        
        logging.info(f"Found {activities.count()} activities for company {company.id}, type: {activity_type}")
        
        # Log first 5 activities for debugging
        for i, activity in enumerate(activities[:5]):
            logging.info(f"Activity {i+1}: ID={activity.id}, type={activity.activity_type}, performed_at={activity.performed_at}")
            
            # Check if activity type is valid in model choices
            valid_types = [t[0] for t in Activity.ACTIVITY_TYPES]
            if activity.activity_type not in valid_types:
                logging.warning(f"Activity {activity.id} has invalid type: {activity.activity_type}")
        
        context = {
            'company': company,
            'activities': activities,
            'activity_type': activity_type
        }
        
        try:
            # Try to render the template to catch any template errors
            logging.info("Rendering activity_list.html template")
            html = render_to_string('crm/includes/activity_list.html', context, request)
            logging.info(f"Successfully rendered template with {len(html)} characters")
            return HttpResponse(html)
        except Exception as template_error:
            import traceback
            logging.error(f"Template rendering error in activity_list.html: {str(template_error)}")
            logging.error(traceback.format_exc())
            return HttpResponse(f"<div class='alert alert-danger'>Error rendering activities: {str(template_error)}</div>")
            
    except Exception as e:
        import traceback
        logging.error(f"Error in company_activities view: {str(e)}")
        logging.error(traceback.format_exc())
        return HttpResponse(f"<div class='alert alert-danger'>Server error: {str(e)}</div>")

@login_required
@require_POST
def log_email_activity(request):
    """Log an email activity"""
    company_id = request.POST.get('company_id')
    if not company_id:
        return JsonResponse({'success': False, 'message': 'No company ID provided'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    
    try:
        # Get recipient contacts
        recipient_ids = request.POST.getlist('recipients')
        recipients = Contact.objects.filter(id__in=recipient_ids)
        
        # Import the right model
        from crm.models import EmailActivity
        
        # Create email activity
        activity = EmailActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='email',
            description=request.POST.get('content', ''),
            body=request.POST.get('content', ''),
            subject=request.POST.get('subject', ''),
            email_date=request.POST.get('date', timezone.now().date()),
            email_time=timezone.now().time()
        )
        
        # Add recipients as related contacts if the model supports it
        if hasattr(activity, 'contact_recipients'):
            activity.contact_recipients.add(*recipients)
        
        return JsonResponse({
            'success': True,
            'message': 'Email activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error in log_email_activity: {str(e)}")
        logging.error(traceback.format_exc())
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@require_POST
def log_call_activity(request):
    """Log a call activity"""
    company_id = request.POST.get('company_id')
    if not company_id:
        return JsonResponse({'success': False, 'message': 'No company ID provided'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    
    try:
        # Get contact
        contact_id = request.POST.get('contact')
        contact = get_object_or_404(Contact, id=contact_id) if contact_id else None
        
        # Import the right model
        from crm.models import CallActivity
        
        # Create call activity
        activity = CallActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='call',
            description=request.POST.get('notes', ''),
            call_type='Outbound' if bool(request.POST.get('outbound')) else 'Inbound',
            duration=int(request.POST.get('duration', 0)),
            summary=request.POST.get('purpose', ''),
            call_outcome=request.POST.get('outcome', '')
        )
        
        # Set contact if model supports it
        if contact:
            activity.contact = contact
            activity.save()
        
        # Set follow-up date if provided
        if bool(request.POST.get('needs_follow_up')) and request.POST.get('follow_up_date'):
            activity.follow_up_date = request.POST.get('follow_up_date')
            activity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Call activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error in log_call_activity: {str(e)}")
        logging.error(traceback.format_exc())
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@require_POST
def log_meeting_activity(request):
    """Log a meeting activity"""
    company_id = request.POST.get('company_id')
    if not company_id:
        return JsonResponse({'success': False, 'message': 'No company ID provided'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    
    try:
        # Get attendees
        attendee_ids = request.POST.getlist('attendees')
        attendees = Contact.objects.filter(id__in=attendee_ids)
        
        # Import the right model
        from crm.models import MeetingActivity
        
        # Create meeting activity
        activity = MeetingActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='meeting',
            title=request.POST.get('title', ''),
            description=request.POST.get('notes', ''),
            location=request.POST.get('location', ''),
            duration=int(request.POST.get('duration', 0)),
            agenda=request.POST.get('agenda', ''),
            minutes=request.POST.get('notes', ''),
            meeting_outcome=request.POST.get('outcome', '')
        )
        
        # Add attendees if the model supports it
        if hasattr(activity, 'attendees'):
            activity.attendees.add(*attendees)
        
        # Set follow-up date if provided
        if bool(request.POST.get('needs_follow_up')) and request.POST.get('follow_up_date'):
            activity.follow_up_date = request.POST.get('follow_up_date')
            activity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Meeting activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error in log_meeting_activity: {str(e)}")
        logging.error(traceback.format_exc())
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@require_POST
def log_note_activity(request):
    """Log a note activity"""
    company_id = request.POST.get('company_id')
    if not company_id:
        return JsonResponse({'success': False, 'message': 'No company ID provided'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    
    try:
        # Get related contacts
        contact_ids = request.POST.getlist('related_contacts')
        contact = None
        if contact_ids:
            contact = get_object_or_404(Contact, id=contact_ids[0])
        
        # Import the right model
        from crm.models import NoteActivity
        
        # Create note activity
        activity = NoteActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='note',
            description=request.POST.get('content', ''),
            content=request.POST.get('content', ''),
            is_private=False,
            note_outcome=None
        )
        
        # Set contact if provided
        if contact:
            activity.contact = contact
            activity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Note activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error in log_note_activity: {str(e)}")
        logging.error(traceback.format_exc())
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@require_POST
def log_waiver_activity(request):
    """Log a waiver/favor activity"""
    company_id = request.POST.get('company_id')
    if not company_id:
        return JsonResponse({'success': False, 'message': 'No company ID provided'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    
    try:
        # Get contact
        contact_id = request.POST.get('contact')
        contact = get_object_or_404(Contact, id=contact_id) if contact_id else None
        
        # Create waiver activity
        activity = WaiverActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='waiver',
            title=request.POST.get('title', ''),
            description=request.POST.get('reason', ''),
            waiver_type=request.POST.get('waiver_type', 'waiver'),
            amount=request.POST.get('amount') if request.POST.get('amount') else None,
            reason=request.POST.get('reason', ''),
        )
        
        # Set approved_by if provided
        if request.POST.get('approved_by'):
            try:
                approver = User.objects.get(id=request.POST.get('approved_by'))
                activity.approved_by = approver
                activity.save()
            except User.DoesNotExist:
                pass
        
        # Add contact
        if contact:
            activity.contact = contact
            activity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Waiver/favor activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@require_POST
def log_task_activity(request):
    """Log a task activity"""
    company_id = request.POST.get('company_id')
    if not company_id:
        return JsonResponse({'success': False, 'message': 'No company ID provided'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    
    try:
        # Get related contacts
        contact_ids = request.POST.getlist('related_contacts')
        contact = None
        if contact_ids:
            # Just use the first contact for now since TaskActivity has a single contact field
            contact = get_object_or_404(Contact, id=contact_ids[0])
        
        # Get assignee
        assignee_id = request.POST.get('assignee')
        if assignee_id == 'current_user':
            assignee = request.user
        elif assignee_id:
            assignee = get_object_or_404(User, id=assignee_id)
        else:
            assignee = None
        
        # Create task activity
        activity = TaskActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='task',
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
            due_date=request.POST.get('due_date') or timezone.now().date(),
            priority=request.POST.get('priority', 'medium'),
            status=request.POST.get('status', 'not_started'),
            assigned_to=assignee
        )
        
        # Set contact if available
        if contact:
            activity.contact = contact
            activity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Task activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error in log_task_activity: {str(e)}")
        logging.error(traceback.format_exc())
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
def activity_list_template(request):
    """Get the activity list template for a company"""
    company_id = request.GET.get('company_id')
    if not company_id:
        return JsonResponse({'error': 'No company ID provided'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    activity_type = request.GET.get('type', 'all')
    
    if activity_type == 'all':
        activities = Activity.objects.filter(company=company).select_related(
            'emailactivity', 'callactivity', 'meetingactivity', 'noteactivity', 
            'waiveractivity', 'taskactivity', 'documentactivity', 'statuschangeactivity',
            'policyupdateactivity'
        ).order_by('-performed_at')
    else:
        activities = Activity.objects.filter(
            company=company, 
            activity_type=activity_type
        ).select_related(
            'emailactivity', 'callactivity', 'meetingactivity', 'noteactivity', 
            'waiveractivity', 'taskactivity', 'documentactivity', 'statuschangeactivity',
            'policyupdateactivity'
        ).order_by('-performed_at')
    
    context = {
        'company': company,
        'activities': activities,
        'activity_type': activity_type,
    }
    
    html = render_to_string('crm/includes/activity_list.html', context, request)
    return HttpResponse(html)

@login_required
def get_activity_details(request, activity_id):
    """API endpoint to get activity details as JSON"""
    try:
        activity = get_object_or_404(Activity, id=activity_id)
        
        # Prepare the response data
        response_data = {
            'id': activity.id,
            'type': activity.activity_type,
            'description': activity.description,
            'performed_at': activity.performed_at.isoformat(),
            'performed_by': {
                'id': activity.performed_by.id if activity.performed_by else None,
                'name': activity.performed_by.get_full_name() if activity.performed_by else 'System'
            },
            'company': {
                'id': activity.company.id,
                'name': activity.company.company_name
            }
        }
        
        # Add activity-specific data from the data JSONField
        if activity.data:
            response_data.update(activity.data)
        
        return JsonResponse({
            'status': 'success',
            'data': response_data
        })
    except Activity.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Activity not found'
        }, status=404)

@login_required
def edit_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Determine the appropriate form class based on activity type
    if activity.activity_type == 'email':
        form_class = EmailActivityForm
    elif activity.activity_type == 'call':
        form_class = CallActivityForm
    elif activity.activity_type == 'meeting':
        form_class = MeetingActivityForm
    elif activity.activity_type == 'note':
        form_class = NoteActivityForm
    elif activity.activity_type == 'document':
        form_class = DocumentActivityForm
    elif activity.activity_type == 'status_change':
        form_class = StatusChangeActivityForm
    elif activity.activity_type == 'policy_update':
        form_class = PolicyUpdateActivityForm
    elif activity.activity_type == 'waiver':
        form_class = WaiverFavorActivityForm
    else:
        raise Http404("Invalid activity type")
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=activity)
        todo_form = ToDoTaskForm(request.POST)
        if form.is_valid() and todo_form.is_valid():
            activity = form.save(commit=False)
            activity.performed_by = request.user
            activity.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Handle follow-up task if provided
            if todo_form.cleaned_data.get('to_do_task_date'):
                activity.follow_up_date = todo_form.cleaned_data['to_do_task_date']
                activity.follow_up_notes = todo_form.cleaned_data.get('to_do_task_message', '')
                activity.save()
            
            messages.success(request, 'Activity updated successfully.')
            return redirect('crm:company_detail', pk=activity.company.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-populate the form with existing data
        initial_data = {}
        if hasattr(activity, 'data') and activity.data:
            initial_data.update(activity.data)
            if 'todo' in activity.data:
                todo_form = ToDoTaskForm(initial={
                    'to_do_task_date': activity.data['todo']['date'],
                    'to_do_task_message': activity.data['todo'].get('message', '')
                })
            else:
                todo_form = ToDoTaskForm()
        else:
            todo_form = ToDoTaskForm()
        
        form = form_class(instance=activity, initial=initial_data)
    
    context = {
        'form': form,
        'todo_form': todo_form,
        'activity': activity,
        'company': activity.company,
        'title': f'Edit {activity.get_activity_type_display()} Activity'
    }
    return render(request, 'crm/activity_form.html', context)

@login_required
def delete_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    company_id = activity.company.id
    activity.delete()
    messages.success(request, 'Activity deleted successfully.')
    return redirect('crm:company_detail', pk=company_id)

@login_required
def search_recipients(request):
    """API endpoint for searching contacts and users."""
    logger = logging.getLogger(__name__)
    
    # Get parameters with fallbacks
    search_term = request.GET.get('term', '').strip().lower()
    company_id = request.GET.get('company_id', '')
    
    # Initialize results list
    results = []
    
    try:
        # Check search term length
        if len(search_term) < 2:
            return JsonResponse({'results': []})
        
        # Build more flexible search queries for contacts
        contact_query = Q(first_name__icontains=search_term) | \
                       Q(last_name__icontains=search_term)
        
        # Check if email exists before adding to search query
        if hasattr(Contact, 'email'):
            contact_query |= Q(email__icontains=search_term)
        
        # Also search for full name matches (for "first last" style searches)
        name_parts = search_term.split()
        if len(name_parts) > 1:
            # For multiple word searches, try matching first and last name combinations
            for i in range(len(name_parts) - 1):
                first_part = name_parts[i]
                last_part = name_parts[i+1]
                contact_query |= (Q(first_name__icontains=first_part) & Q(last_name__icontains=last_part))
        
        # Search contacts
        if company_id and company_id.isdigit():
            # Search within specific company
            contacts = Contact.objects.filter(contact_query, company_id=company_id)
            
            # If no contacts found for this company, search across all companies instead
            if contacts.count() == 0:
                contacts = Contact.objects.filter(contact_query)
        else:
            # No company specified, search all contacts
            contacts = Contact.objects.filter(contact_query)
            
        # For better performance, limit to top 20 results
        contacts = contacts[:20]
        
        # Format contact results
        for contact in contacts:
            results.append({
                'id': contact.id,
                'text': f"{contact.first_name} {contact.last_name}",
                'email': getattr(contact, 'email', ''),
                'company': contact.company.company_name if contact.company else '',
                'type': 'contact'
            })
        
        return JsonResponse({'results': results})
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': str(e),
            'status': 'error',
            'results': []
        }, status=500)

@login_required
def activity_details(request, activity_id):
    """View for displaying activity details"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Get the specific activity type instance
    activity_details = None
    if activity.activity_type == 'email':
        activity_details = activity.emailactivity
    elif activity.activity_type == 'call':
        activity_details = activity.callactivity
    elif activity.activity_type == 'meeting':
        activity_details = activity.meetingactivity
    elif activity.activity_type == 'note':
        activity_details = activity.noteactivity
    
    context = {
        'activity': activity,
        'activity_details': activity_details,
    }
    
    return render(request, 'crm/activity_details.html', context)

@login_required
def debug_activities(request, company_id):
    """Debug view for activities"""
    try:
        company = get_object_or_404(Company, id=company_id)
        activity_type = request.GET.get('type', 'all')
        
        # Query activities
        if activity_type == 'all':
            activities = Activity.objects.filter(company=company).order_by('-performed_at')
        else:
            activities = Activity.objects.filter(company=company, activity_type=activity_type).order_by('-performed_at')
        
        # Gather debug info for each activity
        activity_data = []
        for activity in activities:
            # Basic activity info
            info = {
                'id': activity.id,
                'type': activity.activity_type,
                'description': activity.description[:50] + '...' if len(activity.description) > 50 else activity.description,
                'performed_at': activity.performed_at.isoformat(),
            }
            
            # Check for subclass instances
            subclass_models = ['emailactivity', 'callactivity', 'meetingactivity', 'noteactivity', 
                               'waiveractivity', 'taskactivity', 'documentactivity']
            for model_name in subclass_models:
                if hasattr(activity, model_name):
                    info[f'has_{model_name}'] = True
                    # Add a few fields from the subclass if they exist
                    subclass = getattr(activity, model_name)
                    if hasattr(subclass, 'title'):
                        info[f'{model_name}_title'] = getattr(subclass, 'title', '')
            
            activity_data.append(info)
        
        # Return as JSON
        return JsonResponse({
            'company': company.company_name,
            'activity_type': activity_type,
            'count': len(activity_data),
            'activities': activity_data
        })
        
    except Exception as e:
        import traceback
        logging.error(f"Error in debug_activities view: {str(e)}")
        logging.error(traceback.format_exc())
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

@login_required
def company_activities_json(request, company_id):
    """Get activities for a specific company as JSON"""
    try:
        company = get_object_or_404(Company, id=company_id)
        activity_type = request.GET.get('type', 'all')
        
        if activity_type == 'all':
            activities = Activity.objects.filter(company=company).order_by('-performed_at')[:50]
        else:
            activities = Activity.objects.filter(
                company=company, activity_type=activity_type
            ).order_by('-performed_at')[:50]
        
        # Format activities as simple JSON
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'activity_type': activity.activity_type,
                'type_display': activity.get_activity_type_display(),
                'description': str(activity.description)[:100] if activity.description else '',
                'performed_at': activity.performed_at.strftime('%Y-%m-%d %H:%M:%S'),
                'performed_by': activity.performed_by.get_full_name() if activity.performed_by else 'System'
            })
        
        return JsonResponse({
            'status': 'success',
            'company': company.company_name,
            'activity_type': activity_type,
            'count': len(activities_data),
            'activities': activities_data
        })
            
    except Exception as e:
        import traceback
        logging.error(f"Error in company_activities_json view: {str(e)}")
        logging.error(traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }, status=500) 