from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models import Q
import logging
from datetime import timedelta

from crm.models import (
    Company, Activity, Contact, WaiverActivity, TaskActivity, EmailActivity, 
    CallActivity, MeetingActivity, NoteActivity, DocumentActivity, 
    StatusChangeActivity, PolicyUpdateActivity
)
from crm.forms import (
    EmailActivityForm, CallActivityForm, MeetingActivityForm, 
    NoteActivityForm, WaiverFavorActivityForm, ToDoTaskForm, DocumentActivityForm, 
    StatusChangeActivityForm, PolicyUpdateActivityForm, TaskActivityForm
)
from django.contrib.auth import get_user_model

# Get the User model
User = get_user_model()

@login_required
def activity_form(request, activity_type):
    """Render the appropriate activity form with its Django Form instance"""
    try:
        company_id = request.GET.get('company_id')
        if not company_id:
            return JsonResponse({'error': 'No company ID provided'}, status=400)
        
        company = get_object_or_404(Company, id=company_id)
        
        # Get all users for task assignment dropdown if needed (can be optimized later)
        users = User.objects.filter(is_active=True)
        
        form = None
        template_name = None
        
        # Map activity type to form class and template
        if activity_type == 'email':
            form = EmailActivityForm()
            template_name = 'crm/activities/email_form.html'
        elif activity_type == 'call':
            form = CallActivityForm()
            template_name = 'crm/activities/call_form.html'
        elif activity_type == 'meeting':
            form = MeetingActivityForm()
            template_name = 'crm/activities/meeting_form.html'
        elif activity_type == 'note':
            form = NoteActivityForm() # Instantiate the Note form
            template_name = 'crm/activities/note_form.html'
        elif activity_type == 'waiver_favour':
            form = WaiverFavorActivityForm() 
            template_name = 'crm/activities/waiver_form.html'
        elif activity_type == 'task':
            # Ensure TaskActivityForm is imported and used
            form = TaskActivityForm(initial={'assigned_to': request.user}) 
            template_name = 'crm/activities/task_form.html'
        # Add mappings for other activity types like 'document' if needed
        # elif activity_type == 'document':
        #     form = DocumentActivityForm()
        #     template_name = 'crm/activities/document_form.html'
            
        if not template_name or form is None:
            logging.warning(f"Invalid or unmapped activity type requested: {activity_type}")
            return JsonResponse({'error': f'Invalid activity type: {activity_type}'}, status=400)
        
        context = {
            'company': company,
            'today_date': timezone.now(),
            'users': users, # Keep users for task form assignee dropdown
            'form': form    # Add the instantiated form to the context
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
                company=company, activity_type=activity_type
            ).select_related(
                'emailactivity', 'callactivity', 'meetingactivity', 'noteactivity', 
                'waiveractivity', 'taskactivity', 'documentactivity', 'statuschangeactivity',
                'policyupdateactivity'
            ).order_by('-performed_at')
        
        context = {
            'company': company,
            'activities': activities,
            'activity_type': activity_type
        }
        
        html = render_to_string('crm/includes/activity_list.html', context, request)
        return HttpResponse(html)
            
    except Exception as e:
        import traceback
        logging.error(f"Error in company_activities view: {str(e)}")
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
        # Get recipient IDs
        recipient_ids = request.POST.getlist('recipients')
        logging.info(f"Email activity - recipient_ids from form: {recipient_ids}")
        
        # Separate contact and user recipients
        contact_recipient_ids = []
        user_recipient_ids = []
        
        for recipient_id in recipient_ids:
            if recipient_id.startswith('contact_'):
                contact_recipient_ids.append(recipient_id.replace('contact_', ''))
            elif recipient_id.startswith('user_'):
                user_recipient_ids.append(recipient_id.replace('user_', ''))
        
        logging.info(f"Email activity - processed contact_recipient_ids: {contact_recipient_ids}")
        logging.info(f"Email activity - processed user_recipient_ids: {user_recipient_ids}")
        
        # Get contact recipients
        contacts = Contact.objects.filter(id__in=contact_recipient_ids)
        logging.info(f"Email activity - found contacts: {list(contacts.values_list('id', 'first_name', 'last_name'))}")
        
        # Get user recipients
        users = User.objects.filter(id__in=user_recipient_ids)
        logging.info(f"Email activity - found users: {list(users.values_list('id', 'first_name', 'last_name'))}")
        
        # Get date and time, providing defaults
        email_date_str = request.POST.get('date', '')
        email_time_str = request.POST.get('time', '')
        
        # Attempt to parse date and time, using defaults on failure
        try:
            email_date = timezone.datetime.strptime(email_date_str, '%Y-%m-%d').date() if email_date_str else timezone.now().date()
        except ValueError:
            email_date = timezone.now().date() # Default to today if format is wrong
            
        try:
            email_time = timezone.datetime.strptime(email_time_str, '%H:%M').time() if email_time_str else timezone.now().time()
        except ValueError:
             email_time = timezone.now().time() # Default to now if format is wrong

        # Import the right model
        from crm.models import EmailActivity, TaskActivity
        
        # Create email activity
        activity = EmailActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='email',
            description=request.POST.get('content', ''),
            body=request.POST.get('content', ''),
            subject=request.POST.get('subject', ''),
            email_date=email_date, # Use parsed/default date
            email_time=email_time  # Use parsed/default time
        )
        
        # Add recipients as related contacts if the model supports it
        if hasattr(activity, 'contact_recipients'):
            logging.info(f"Email activity {activity.id} - adding {len(contacts)} contacts to contact_recipients")
            try:
                activity.contact_recipients.add(*contacts)
                # Verify contacts were added
                added_contacts = activity.contact_recipients.all()
                logging.info(f"Email activity {activity.id} - verified added contacts: {list(added_contacts.values_list('id', 'first_name', 'last_name'))}")
            except Exception as e:
                logging.error(f"Error adding contact recipients: {str(e)}")
        
        # Add user recipients if the model supports it
        if hasattr(activity, 'user_recipients'):
            logging.info(f"Email activity {activity.id} - adding {len(users)} users to user_recipients")
            try:
                activity.user_recipients.add(*users)
                # Verify users were added
                added_users = activity.user_recipients.all()
                logging.info(f"Email activity {activity.id} - verified added users: {list(added_users.values_list('id', 'first_name', 'last_name'))}")
            except Exception as e:
                logging.error(f"Error adding user recipients: {str(e)}")
        
        # --- Create Follow-up Task if requested --- 
        if request.POST.get('create_follow_up_task'):
            try:
                task_title = request.POST.get('follow_up_task_title', '').strip()
                if not task_title:
                    default_title = f"Follow up on: {activity.subject or 'Email Activity'}"
                    task_title = default_title[:255] 
                    
                # Get and parse the due date, defaulting to next day
                due_date_str = request.POST.get('follow_up_due_date', '')
                try:
                    due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else timezone.now().date() + timedelta(days=1)
                    if due_date < timezone.now().date():
                         due_date = timezone.now().date() + timedelta(days=1) 
                except ValueError:
                    due_date = timezone.now().date() + timedelta(days=1) # Default if format is wrong
                    
                # Get and parse the due time, defaulting to 09:00
                due_time_str = request.POST.get('follow_up_due_time', '')
                try:
                    due_time = timezone.datetime.strptime(due_time_str, '%H:%M').time() if due_time_str else timezone.datetime.min.time().replace(hour=9)
                except ValueError:
                    due_time = timezone.datetime.min.time().replace(hour=9) # Default if format is wrong
                    
                # Combine date and time into a datetime object
                # Ensure it's timezone-aware using Django's current timezone
                naive_datetime = timezone.datetime.combine(due_date, due_time)
                due_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
                
                # Get optional notes
                task_notes = request.POST.get('follow_up_task_notes', '').strip()
                base_description = f"Follow-up task automatically created for Email Activity ID: {activity.id}"
                task_description = f"{task_notes}\n\n---\n{base_description}" if task_notes else base_description
                
                # Create the linked task
                TaskActivity.objects.create(
                    company=activity.company,
                    performed_by=request.user, 
                    activity_type='task',
                    title=task_title,
                    description=task_description, # Use combined description
                    due_datetime=due_datetime, # Use combined datetime
                    assigned_to=request.user, 
                    status='not_started',
                    priority='medium', 
                    related_activity=activity 
                )
                # You could add a specific success message for the task here if needed
                # messages.success(request, 'Follow-up task created.') 
            except Exception as task_error:
                # Log error creating task, but don't fail the whole email logging
                logging.error(f"Error creating follow-up task for email {activity.id}: {task_error}", exc_info=True)
                # Optionally add a message to the user about the task creation failure
                # messages.warning(request, f'Email logged, but failed to create follow-up task: {task_error}')
        # --- End Follow-up Task --- 
        
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
        # Get contact ID (handle potential prefix from Tom Select)
        contact_input_id = request.POST.get('contact')
        contact_id = None
        contact = None
        if contact_input_id:
            if contact_input_id.startswith('contact_'):
                contact_id = contact_input_id.replace('contact_', '')
            elif contact_input_id.isdigit(): # Allow plain ID for robustness
                contact_id = contact_input_id
            
            if contact_id:
                contact = get_object_or_404(Contact, id=contact_id)
        
        # Get date and time, providing defaults
        call_date_str = request.POST.get('date', '')
        call_time_str = request.POST.get('time', '')
        
        try:
            call_date = timezone.datetime.strptime(call_date_str, '%Y-%m-%d').date() if call_date_str else timezone.now().date()
        except ValueError:
            call_date = timezone.now().date()
            
        try:
            call_time = timezone.datetime.strptime(call_time_str, '%H:%M').time() if call_time_str else timezone.now().time()
        except ValueError:
            call_time = timezone.now().time()
            
        naive_datetime = timezone.datetime.combine(call_date, call_time)
        performed_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
        
        # Import the right models
        from crm.models import CallActivity, TaskActivity
        
        # Create call activity with all fields
        # Field mappings:
        # - call_purpose (form) -> summary (database)
        # - call_summary (form) -> description (database)
        activity = CallActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='call',
            performed_at=performed_datetime,
            call_type='Outbound' if bool(request.POST.get('outbound')) else 'Inbound',
            duration=int(request.POST.get('duration', 0)),
            # Get 'call_purpose' parameter (falling back to 'purpose' for backwards compatibility)
            summary=request.POST.get('call_purpose', request.POST.get('purpose', '')),
            call_outcome=request.POST.get('call_outcome', request.POST.get('outcome', '')),
            contact=contact
        )
        
        # Save call_summary to description separately
        # Get 'call_summary' parameter (falling back to 'notes' for backwards compatibility)
        activity.description = request.POST.get('call_summary', request.POST.get('notes', ''))
        activity.save(update_fields=['description'])
        
        # --- Create Follow-up Task if requested --- 
        if request.POST.get('create_follow_up_task'):
            try:
                task_title = request.POST.get('follow_up_task_title', '').strip()
                if not task_title:
                    contact_name = f" with {contact.get_full_name()}" if contact else ""
                    default_title = f"Follow up on call{contact_name} ({activity.summary or 'Call Activity'})"
                    task_title = default_title[:255]
                    
                due_date_str = request.POST.get('follow_up_due_date', '')
                try:
                    due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else timezone.now().date() + timedelta(days=1)
                    if due_date < timezone.now().date():
                         due_date = timezone.now().date() + timedelta(days=1) 
                except ValueError:
                    due_date = timezone.now().date() + timedelta(days=1)
                    
                due_time_str = request.POST.get('follow_up_due_time', '')
                try:
                    due_time = timezone.datetime.strptime(due_time_str, '%H:%M').time() if due_time_str else timezone.datetime.min.time().replace(hour=9)
                except ValueError:
                    due_time = timezone.datetime.min.time().replace(hour=9)
                    
                naive_followup_datetime = timezone.datetime.combine(due_date, due_time)
                due_datetime = timezone.make_aware(naive_followup_datetime, timezone.get_current_timezone())
                
                task_notes = request.POST.get('follow_up_task_notes', '').strip()
                base_description = f"Follow-up task automatically created for Call Activity ID: {activity.id}"
                task_description = f"{task_notes}\n\n---\n{base_description}" if task_notes else base_description
                
                TaskActivity.objects.create(
                    company=activity.company,
                    performed_by=request.user,
                    activity_type='task',
                    title=task_title,
                    description=task_description,
                    due_datetime=due_datetime,
                    assigned_to=request.user,
                    status='not_started',
                    priority='medium',
                    related_activity=activity
                )
            except Exception as task_error:
                logging.error(f"Error creating follow-up task for call {activity.id}: {task_error}", exc_info=True)
        # --- End Follow-up Task --- 
        
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
        # Get attendees (handle multiple, prefixed IDs)
        attendee_input_ids = request.POST.getlist('attendees')
        contact_attendee_ids = []
        user_attendee_ids = []
        for attendee_id in attendee_input_ids:
            if attendee_id.startswith('contact_'):
                contact_attendee_ids.append(attendee_id.replace('contact_', ''))
            elif attendee_id.startswith('user_'):
                user_attendee_ids.append(attendee_id.replace('user_', ''))
            elif attendee_id.isdigit(): # Allow plain IDs just in case
                 # Try resolving as contact first, then user? Or rely on prefix.
                 # For now, assume prefixed IDs are used reliably from TomSelect.
                 pass 
        
        contacts = Contact.objects.filter(id__in=contact_attendee_ids)
        users = User.objects.filter(id__in=user_attendee_ids)
        
        # Get date and time, providing defaults
        meeting_date_str = request.POST.get('date', '')
        meeting_time_str = request.POST.get('time', '')
        
        try:
            meeting_date = timezone.datetime.strptime(meeting_date_str, '%Y-%m-%d').date() if meeting_date_str else timezone.now().date()
        except ValueError:
            meeting_date = timezone.now().date()
            
        try:
            meeting_time = timezone.datetime.strptime(meeting_time_str, '%H:%M').time() if meeting_time_str else timezone.now().time()
        except ValueError:
            meeting_time = timezone.now().time()
            
        naive_datetime = timezone.datetime.combine(meeting_date, meeting_time)
        performed_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
        
        # Import the right models
        from crm.models import MeetingActivity, TaskActivity # Add TaskActivity
        
        # Create meeting activity - set performed_at explicitly
        activity = MeetingActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='meeting',
            performed_at=performed_datetime, # Use parsed datetime
            title=request.POST.get('title', ''),
            # description set below
            location=request.POST.get('location', ''),
            duration=int(request.POST.get('duration', 0)),
            agenda=request.POST.get('agenda', ''),
            # minutes set below (same as notes)
            meeting_outcome=request.POST.get('outcome', '')
        )
        
        # Set description/minutes from 'notes' field
        notes = request.POST.get('notes', '')
        activity.description = notes # Assuming notes field is for general description
        activity.minutes = notes    # Assuming notes field also serves as minutes
        
        # Add attendees (Contacts and Users)
        activity.contact_attendees.add(*contacts)
        activity.user_attendees.add(*users)
        
        # Save changes (like description, minutes, M2M relations)
        activity.save() 
        
        # --- Create Follow-up Task if requested --- 
        if request.POST.get('create_follow_up_task'):
            try:
                task_title = request.POST.get('follow_up_task_title', '').strip()
                if not task_title:
                    default_title = f"Follow up on meeting: {activity.title or 'Meeting Activity'}"
                    task_title = default_title[:255]
                    
                due_date_str = request.POST.get('follow_up_due_date', '')
                try:
                    due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else timezone.now().date() + timedelta(days=1)
                    if due_date < timezone.now().date():
                         due_date = timezone.now().date() + timedelta(days=1) 
                except ValueError:
                    due_date = timezone.now().date() + timedelta(days=1)
                    
                due_time_str = request.POST.get('follow_up_due_time', '')
                try:
                    due_time = timezone.datetime.strptime(due_time_str, '%H:%M').time() if due_time_str else timezone.datetime.min.time().replace(hour=9)
                except ValueError:
                    due_time = timezone.datetime.min.time().replace(hour=9)
                    
                naive_followup_datetime = timezone.datetime.combine(due_date, due_time)
                due_datetime = timezone.make_aware(naive_followup_datetime, timezone.get_current_timezone())
                
                task_notes = request.POST.get('follow_up_task_notes', '').strip()
                base_description = f"Follow-up task automatically created for Meeting Activity ID: {activity.id}"
                task_description = f"{task_notes}\n\n---\n{base_description}" if task_notes else base_description
                
                TaskActivity.objects.create(
                    company=activity.company,
                    performed_by=request.user,
                    activity_type='task',
                    title=task_title,
                    description=task_description,
                    due_datetime=due_datetime,
                    assigned_to=request.user,
                    status='not_started',
                    priority='medium',
                    related_activity=activity
                )
            except Exception as task_error:
                logging.error(f"Error creating follow-up task for meeting {activity.id}: {task_error}", exc_info=True)
        # --- End Follow-up Task --- 
                
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
        
        # Get subject if provided
        subject_id = request.POST.get('subject')
        subject = None
        if subject_id:
            from crm.models import NoteSubject
            try:
                subject = NoteSubject.objects.get(id=subject_id)
            except (NoteSubject.DoesNotExist, ValueError):
                # If subject doesn't exist, we'll continue without it
                pass
        
        # Import the right model
        from crm.models import NoteActivity
        
        # Create note activity
        activity = NoteActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='note',
            description=request.POST.get('content', ''),
            content=request.POST.get('content', ''),
            is_important=request.POST.get('is_important') == 'on',
            subject=subject
        )
        
        # Set contact if provided
        if contact:
            activity.contact = contact
            activity.save()
            
        # Create follow-up task if requested
        if request.POST.get('create_follow_up_task'):
            try:
                from crm.models import TaskActivity
                
                task_title = request.POST.get('follow_up_task_title', '').strip()
                if not task_title:
                    default_title = f"Follow up on note: {activity.content[:50]}..." if len(activity.content) > 50 else f"Follow up on note: {activity.content}"
                    task_title = default_title[:255]
                    
                due_date_str = request.POST.get('follow_up_due_date', '')
                try:
                    due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else timezone.now().date() + timedelta(days=1)
                    if due_date < timezone.now().date():
                         due_date = timezone.now().date() + timedelta(days=1) 
                except ValueError:
                    due_date = timezone.now().date() + timedelta(days=1)
                    
                due_time_str = request.POST.get('follow_up_due_time', '')
                try:
                    due_time = timezone.datetime.strptime(due_time_str, '%H:%M').time() if due_time_str else timezone.datetime.min.time().replace(hour=9)
                except ValueError:
                    due_time = timezone.datetime.min.time().replace(hour=9)
                    
                naive_followup_datetime = timezone.datetime.combine(due_date, due_time)
                due_datetime = timezone.make_aware(naive_followup_datetime, timezone.get_current_timezone())
                
                task_notes = request.POST.get('follow_up_task_notes', '').strip()
                base_description = f"Follow-up task automatically created for Note Activity ID: {activity.id}"
                task_description = f"{task_notes}\n\n---\n{base_description}" if task_notes else base_description
                
                TaskActivity.objects.create(
                    company=activity.company,
                    performed_by=request.user,
                    activity_type='task',
                    title=task_title,
                    description=task_description,
                    due_datetime=due_datetime,
                    assigned_to=request.user,
                    status='not_started',
                    priority='medium',
                    related_activity=activity
                )
            except Exception as task_error:
                logging.error(f"Error creating follow-up task for note {activity.id}: {task_error}", exc_info=True)
        
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
def log_waiver_favour_activity(request):
    """Log a waiver & favour activity"""
    company_id = request.POST.get('company_id')
    if not company_id:
        return JsonResponse({'success': False, 'message': 'No company ID provided'}, status=400)
    
    try:
        company = get_object_or_404(Company, id=company_id)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid Company ID'}, status=400)
    
    try:
        # Get contacts (handle multiple, prefixed IDs) similar to meeting activity
        contact_input_ids = request.POST.getlist('contacts')
        contact_ids = []
        for contact_id in contact_input_ids:
            if contact_id.startswith('contact_'):
                contact_ids.append(contact_id.replace('contact_', ''))
            elif contact_id.isdigit(): # Allow plain IDs for robustness
                contact_ids.append(contact_id)
                
        # Get contacts queryset
        contacts = Contact.objects.filter(id__in=contact_ids, company=company)
        
        # Get type if provided
        type_id = request.POST.get('type')
        waiver_type = None
        if type_id:
            from crm.models import WaiverFavourType
            try:
                waiver_type = WaiverFavourType.objects.get(id=type_id)
            except (WaiverFavourType.DoesNotExist, ValueError):
                # If type doesn't exist, we'll continue without it
                pass
        
        # Get approved_by if provided
        approved_by_id = request.POST.get('approved_by')
        approved_by = None
        if approved_by_id and approved_by_id != '':
            try:
                approved_by = get_user_model().objects.get(id=approved_by_id)
            except (get_user_model().DoesNotExist, ValueError):
                # If user doesn't exist, we'll continue without it
                pass
        
        # Import the right model
        from crm.models import WaiverActivity
        
        # Create waiver activity
        activity = WaiverActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='waiver_favour',
            description=request.POST.get('reason', ''),
            reason=request.POST.get('reason', ''),
            amount=request.POST.get('amount') if request.POST.get('amount') else None,
            approved_by=approved_by,
            type=waiver_type
        )
        
        # Add contacts
        if contacts:
            activity.contacts.add(*contacts)
            
        # Save changes
        activity.save()
            
        return JsonResponse({
            'success': True,
            'message': 'Waiver & Favour activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error saving waiver/favour activity: {str(e)}")
        logging.error(traceback.format_exc())
        error_message = f'Error saving activity: {str(e)}'
        return JsonResponse({'success': False, 'message': error_message}, status=500)

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
            assignee = get_object_or_404(get_user_model(), id=assignee_id)
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
    """API endpoint to get activity details as HTML fragment for modal"""
    try:
        # Add debug logging
        logging.info(f"get_activity_details called for activity_id: {activity_id}")
        
        # Get the activity with its subclass
        activity = get_object_or_404(Activity, id=activity_id)
        logging.info(f"Activity found: {activity.id}, type: {activity.activity_type}")
        
        # Get the specific activity type instance
        activity_details = None
        document = None
        
        # Handle special cases for activity types with naming mismatches
        if activity.activity_type == 'waiver_favour':
            # For waiver_favour activities, check for waiveractivity
            if hasattr(activity, 'waiveractivity'):
                activity_details = activity.waiveractivity
                logging.info(f"Found waiver activity details for ID: {activity.id}")
            else:
                logging.warning(f"No waiveractivity attribute found on activity {activity.id}")
        elif hasattr(activity, f"{activity.activity_type}activity"):
            activity_details = getattr(activity, f"{activity.activity_type}activity")
            logging.info(f"Activity details found for type: {activity.activity_type}")
            
            # Add debug for email activity recipients
            if activity.activity_type == 'email' and activity_details:
                try:
                    # Prefetch related recipient data for EmailActivity
                    from django.db.models import Prefetch
                    from crm.models import Contact, EmailActivity
                    
                    # Re-query with prefetch_related for better performance
                    activity_details = EmailActivity.objects.filter(id=activity_details.id).prefetch_related(
                        'contact_recipients', 'user_recipients'
                    ).first()
                    
                    # Debug counts
                    contact_recipients_count = activity_details.contact_recipients.count() if activity_details else 0
                    user_recipients_count = activity_details.user_recipients.count() if activity_details else 0
                    
                    logging.info(f"Email activity {activity.id} has {contact_recipients_count} contact recipients and {user_recipients_count} user recipients")
                    
                    # List the actual recipients for debugging
                    contact_recipients = []
                    if activity_details:
                        contact_recipients = list(activity_details.contact_recipients.all().values_list('id', 'first_name', 'last_name'))
                    
                    logging.info(f"Contact recipients: {contact_recipients}")
                    
                    # Check if the exists() method works as expected
                    exists_result = activity_details.contact_recipients.exists() if activity_details else False
                    logging.info(f"activity_details.contact_recipients.exists() returns: {exists_result}")
                    
                except Exception as e:
                    logging.error(f"Error debugging email recipients: {str(e)}")
        else:
            # For document activities, try to find the document from the description
            found_document = False
            if activity.activity_type == 'document' and activity.is_system_activity:
                from crm.models import Document
                
                # Parse document title from description
                # Formats like: "Uploaded document: Contract.pdf", "Updated document: Invoice.xlsx", etc.
                import re
                match = re.search(r'(?:Uploaded|Updated|Deleted|Downloaded) document: (.+)$', activity.description)
                
                if match:
                    document_title = match.group(1)
                    logging.info(f"Parsed document title from description: {document_title}")
                    
                    # Try to find the document (the most recent one with this title for this company)
                    try:
                        document = Document.objects.filter(
                            company=activity.company,
                            title=document_title
                        ).order_by('-uploaded_at').first()
                        
                        if document:
                            logging.info(f"Found document: {document.id} - {document.title}")
                            found_document = True
                        else:
                            logging.warning(f"No document found with title: {document_title}")
                    except Exception as doc_err:
                        logging.error(f"Error finding document: {str(doc_err)}")
            
            # Only log a warning if we couldn't find the document by other means
            if activity.activity_type == 'document' and activity.is_system_activity and not found_document:
                logging.warning(f"No {activity.activity_type}activity attribute found on activity {activity.id} and couldn't find document from description")
            elif not (activity.activity_type == 'document' and activity.is_system_activity):
                logging.warning(f"No {activity.activity_type}activity attribute found on activity {activity.id}")
        
        context = {
            'activity': activity,
            'activity_details': activity_details,
            'document': document,
        }
        
        # Log the template that will be used
        template_path = 'crm/includes/activity_detail_fragment.html'
        logging.info(f"Rendering template: {template_path}")
        
        # Return HTML fragment instead of JSON
        html_content = render_to_string(template_path, context, request)
        logging.info(f"HTML rendered, length: {len(html_content)}")
        
        if request.GET.get('format') == 'json':
            # For backward compatibility with any code that still expects JSON
            logging.info("Returning JSON response with HTML content")
            return JsonResponse({
                'status': 'success',
                'html': html_content
            })
        else:
            # Return just the HTML fragment
            logging.info("Returning direct HTML response")
            return HttpResponse(html_content)
            
    except Activity.DoesNotExist:
        logging.error(f"Activity with id {activity_id} not found")
        error_html = f"""
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Activity not found
            </div>
        """
        return HttpResponse(error_html, status=404)
    except Exception as e:
        import traceback
        logging.error(f"Error in get_activity_details: {str(e)}")
        logging.error(traceback.format_exc())
        error_html = f"""
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error loading activity details: {str(e)}
            </div>
        """
        return HttpResponse(error_html, status=500)

@login_required
def edit_activity(request, activity_id):
    activity = get_object_or_404(Activity.objects.select_subclasses(), id=activity_id)
    form_class = None
    template_name = 'crm/edit_activity_form.html' # Or a specific one?

    # Determine the appropriate form class based on activity type
    if isinstance(activity, EmailActivity):
        form_class = EmailActivityForm
    elif isinstance(activity, CallActivity):
        form_class = CallActivityForm
    elif isinstance(activity, MeetingActivity):
        form_class = MeetingActivityForm
    elif isinstance(activity, NoteActivity):
        form_class = NoteActivityForm
    elif isinstance(activity, DocumentActivity):
        form_class = DocumentActivityForm
    elif isinstance(activity, StatusChangeActivity):
        form_class = StatusChangeActivityForm
    elif isinstance(activity, PolicyUpdateActivity):
        form_class = PolicyUpdateActivityForm
    elif isinstance(activity, WaiverActivity): # Check specific model type
        form_class = WaiverFavorActivityForm
        activity.activity_type_check = 'waiver_favour' # Pass identifier for consistency if needed
    elif isinstance(activity, TaskActivity):
         form_class = TaskActivityForm
    else:
        # Handle unknown type or generic Activity if needed
        messages.error(request, f"Editing not supported for this activity type: {type(activity).__name__}")
        return redirect('crm:company_detail', pk=activity.company.id)

    if request.method == 'POST':
        # TODO: Review how follow-up task (ToDoTaskForm) is handled here, may need removal/update
        form = form_class(request.POST, request.FILES, instance=activity)
        # todo_form = ToDoTaskForm(request.POST) # Remove if follow-up is handled differently
        if form.is_valid(): # Add check for todo_form.is_valid() if kept
            activity = form.save(commit=False)
            # Ensure performed_by isn't overwritten if not editable
            # activity.performed_by = request.user 
            activity.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Remove old follow-up logic?
            # if todo_form.cleaned_data.get('to_do_task_date'):
            #     activity.follow_up_date = todo_form.cleaned_data['to_do_task_date']
            #     activity.follow_up_notes = todo_form.cleaned_data.get('to_do_task_message', '')
            #     activity.save()
            
            messages.success(request, 'Activity updated successfully.')
            return redirect('crm:company_detail', pk=activity.company.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-populate the form with existing data
        initial_data = {}
        # Remove old data field handling if fields are now direct model fields
        # if hasattr(activity, 'data') and activity.data:
        #     initial_data.update(activity.data)
        #     # Handle old follow-up data?
        #     if 'todo' in activity.data:
        #         todo_form = ToDoTaskForm(initial={...})
        #     else:
        #         todo_form = ToDoTaskForm()
        # else:
        #     todo_form = ToDoTaskForm()
        
        form = form_class(instance=activity, initial=initial_data)
        # todo_form = ToDoTaskForm() # Instantiate blank if not pre-filled

    context = {
        'form': form,
        # 'todo_form': todo_form, # Remove if not used
        'activity': activity,
        'company': activity.company,
        'title': f'Edit {activity.get_activity_type_display()} Activity' # This should update automatically if model verbose name changes
    }
    return render(request, template_name, context)

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
    search_term = request.GET.get('q', '').strip().lower()
    company_id = request.GET.get('company_id', '')
    contacts_only = request.GET.get('contacts_only', '0') == '1'
    limit = int(request.GET.get('limit', '10'))  # Add limit parameter with default 10
    
    logger.info(f"Search recipients: term='{search_term}', company_id='{company_id}', contacts_only={contacts_only}, limit={limit}")
    
    # Initialize results list
    results = []
    
    try:
        # Special case for empty search term - return a few contacts for the company
        # This is useful for initially populating the dropdown
        if not search_term and company_id and company_id.isdigit():
            logger.info(f"Empty search term, returning initial contacts for company {company_id}")
            # Get most recently updated contacts for the company
            contacts = Contact.objects.filter(company_id=company_id).order_by('-updated_at')[:limit]
            
            # Format contact results
            for contact in contacts:
                results.append({
                    'id': f"contact_{contact.id}",
                    'text': f"{contact.first_name} {contact.last_name}",
                    'email': getattr(contact, 'email', ''),
                    'company': contact.company.company_name if contact.company else '',
                    'type': 'contact'
                })
            
            logger.info(f"Returning {len(results)} initial contacts")
            return JsonResponse({'results': results})
        
        # Regular search when term has 2+ characters
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
            if contacts.count() == 0 and not contacts_only:
                logger.info(f"No contacts found for company {company_id}, searching all companies")
                contacts = Contact.objects.filter(contact_query)
        else:
            # No company specified, search all contacts
            contacts = Contact.objects.filter(contact_query)
            
        # For better performance, limit results
        contacts = contacts[:limit]
        
        # Format contact results
        for contact in contacts:
            results.append({
                'id': f"contact_{contact.id}",
                'text': f"{contact.first_name} {contact.last_name}",
                'email': getattr(contact, 'email', ''),
                'company': contact.company.company_name if contact.company else '',
                'type': 'contact'
            })
        
        # Only search users if not limited to contacts
        if not contacts_only:
            # Search users
            User = get_user_model()
            
            user_query = Q(first_name__icontains=search_term) | \
                        Q(last_name__icontains=search_term) | \
                        Q(email__icontains=search_term)
            
            # Also search for full name matches
            if len(name_parts) > 1:
                for i in range(len(name_parts) - 1):
                    first_part = name_parts[i]
                    last_part = name_parts[i+1]
                    user_query |= (Q(first_name__icontains=first_part) & Q(last_name__icontains=last_part))
            
            users = User.objects.filter(user_query, is_active=True)
            users = users[:limit]  # Use the limit parameter
            
            # Format user results
            for user in users:
                results.append({
                    'id': f"user_{user.id}",
                    'text': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'type': 'user'
                })
        
        logger.info(f"Search results: {len(results)} items found")
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
        logging.error(f"Error in company_activities_json view: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def approve_waiver_favor(request, activity_id):
    """Approve a waiver/favor activity."""
    activity = get_object_or_404(Activity, id=activity_id)
    
    if request.method == 'POST':
        try:
            # Get the approver
            User = get_user_model()
            approver = User.objects.get(id=request.POST.get('approved_by'))
            
            # Update the waiver activity
            waiver = activity.waiveractivity
            waiver.approved_by = approver
            waiver.save()
            
            # Update the activity outcome
            activity.outcome = request.POST.get('outcome', '')
            activity.save()
            
            messages.success(request, 'Waiver/Favor activity approved successfully.')
            return redirect('crm:company_detail', pk=activity.company.id)
        except Exception as e:
            messages.error(request, f'Error approving waiver/favor: {str(e)}')
            return redirect('crm:company_detail', pk=activity.company.id)
    else:
        return redirect('crm:company_detail', pk=activity.company.id) 