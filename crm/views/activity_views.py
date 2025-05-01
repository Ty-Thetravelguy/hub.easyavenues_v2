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
from django.urls import reverse
from decimal import Decimal, InvalidOperation

from crm.models import (
    Company, Activity, Contact, WaiverActivity, TaskActivity, EmailActivity, 
    CallActivity, MeetingActivity, NoteActivity, DocumentActivity, 
    StatusChangeActivity, PolicyUpdateActivity, NoteSubject, WaiverFavourType
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
            'today_date': timezone.localtime(timezone.now()),
            'current_time': timezone.localtime(timezone.now()),
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
        
        html = render_to_string('crm/activities/activity_list.html', context, request)
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
                task_title = request.POST.get('follow_up_task_title', f'Follow up on email: {activity.subject}')
                task_notes = request.POST.get('follow_up_task_notes', '')
                
                # Handle due date/time
                due_date_str = request.POST.get('follow_up_due_date')
                due_time_str = request.POST.get('follow_up_due_time')
                
                due_datetime = None
                if due_date_str:
                    try:
                        due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                        # Set default time to 9am if not provided
                        due_time = timezone.datetime.strptime(due_time_str or '09:00', '%H:%M').time()
                        due_datetime = timezone.datetime.combine(due_date, due_time)
                    except ValueError:
                        # Default to tomorrow at 9am if date parsing fails
                        due_datetime = timezone.now() + timedelta(days=1)
                        due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                else:
                    # Default to tomorrow at 9am if no date provided
                    due_datetime = timezone.now() + timedelta(days=1)
                    due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                
                # Create the task
                task = TaskActivity.objects.create(
                    company=activity.company,
                    title=task_title,
                    description=task_notes,
                    performed_by=request.user,
                    assigned_to=request.user,
                    status='not_started',
                    priority='medium',
                    due_datetime=due_datetime
                )
                
                # Add the same recipients to the task
                for contact in activity.contact_recipients.all():
                    task.contacts.add(contact)
                for user in activity.user_recipients.all():
                    task.users.add(user)
                
                # Update the message
                messages.success(request, 'Email activity updated successfully with follow-up task')
                return redirect('crm:company_detail', pk=activity.company.id)
            except Exception as task_error:
                logging.error(f"Error creating follow-up task for email {activity.id}: {task_error}", exc_info=True)
                messages.warning(request, f'Email logged, but failed to create follow-up task: {task_error}')
        # --- End Follow-up Task --- 
        
        # Add Django success message for the email activity
        messages.success(request, 'Email activity logged successfully.')
        
        return JsonResponse({
            'success': True,
            'message': 'Email activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error in log_email_activity: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Add Django error message
        messages.error(request, f'Error logging email activity: {str(e)}')
        
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
                # Add Django message for task creation
                messages.success(request, 'Follow-up task created successfully.')
            except Exception as task_error:
                logging.error(f"Error creating follow-up task for call {activity.id}: {task_error}", exc_info=True)
                # Add Django warning message for task creation failure
                messages.warning(request, f'Call logged, but failed to create follow-up task: {task_error}')
        # --- End Follow-up Task --- 
        
        # Add Django success message for call activity
        messages.success(request, 'Call activity logged successfully.')
        
        return JsonResponse({
            'success': True,
            'message': 'Call activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error in log_call_activity: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Add Django error message
        messages.error(request, f'Error logging call activity: {str(e)}')
        
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@require_POST
def log_meeting_activity(request):
    """Log a meeting activity"""
    company_id = request.POST.get('company_id')
    if not company_id:
        return JsonResponse({'success': False, 'message': 'No company ID provided'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    
    # +++ Define is_ajax +++
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    # --- End --- 
    
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
                due_time_str = request.POST.get('follow_up_due_time')
                
                due_datetime = None
                if due_date_str:
                    try:
                        due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                        due_time = timezone.datetime.strptime(due_time_str or '09:00', '%H:%M').time()
                        due_datetime = timezone.make_aware(timezone.datetime.combine(due_date, due_time))
                    except ValueError:
                        due_datetime = timezone.now() + timedelta(days=1)
                        due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                else:
                    due_datetime = timezone.now() + timedelta(days=1)
                    due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                    
                task_notes = request.POST.get('follow_up_task_notes', '').strip()
                base_description = f"Follow-up task automatically created for Meeting Activity ID: {activity.id}"
                task_description = f"{task_notes}\n\n---\n{base_description}" if task_notes else base_description
                
                task = TaskActivity.objects.create(
                    company=activity.company,
                    performed_by=request.user,
                    activity_type='task',
                    title=task_title,
                    description=task_description,
                    due_datetime=due_datetime,
                    assigned_to=request.user,
                    status='not_started',
                    priority='medium',
                    related_activity=activity # Link task to the original meeting activity
                )
                
                # Add attendees to the follow-up task
                for contact in activity.contact_attendees.all():
                    task.contacts.add(contact)
                for user in activity.user_attendees.all():
                    task.users.add(user)
                
                if is_ajax:
                    return JsonResponse({'success': True, 'message': 'Meeting activity updated successfully with follow-up task', 'reload_page': True})
                else:
                    messages.success(request, 'Meeting activity updated successfully with follow-up task')
                    return redirect('crm:company_detail', pk=activity.company.id)
            except Exception as task_error:
                logging.error(f"Error creating follow-up task for edited meeting {activity.id}: {task_error}", exc_info=True)
                if is_ajax:
                    return JsonResponse({'success': True, 'message': f'Meeting updated, but failed to create follow-up task: {task_error}', 'reload_page': True})
                else:
                    messages.warning(request, f'Meeting updated, but failed to create follow-up task: {task_error}')
                    return redirect('crm:company_detail', pk=activity.company.id)
            
            # Return success response for meeting update without task
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Meeting activity updated successfully', 'reload_page': True})
            else:
                messages.success(request, 'Meeting activity updated successfully')
                return redirect('crm:company_detail', pk=activity.company.id)
        
        # Return success response for meeting update without task
        if is_ajax:
            return JsonResponse({'success': True, 'message': 'Meeting activity updated successfully', 'reload_page': True})
        else:
            messages.success(request, 'Meeting activity updated successfully')
            return redirect('crm:company_detail', pk=activity.company.id)
    except Exception as e:
        import traceback
        logging.error(f"Error in log_meeting_activity: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Add Django error message
        messages.error(request, f'Error logging meeting activity: {str(e)}')
        
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
        # Get related contacts (handle multiple, prefixed IDs)
        contact_input_ids = request.POST.getlist('contacts') # Use 'contacts' as the field name
        contact_ids = []
        for contact_id_str in contact_input_ids:
            if contact_id_str.startswith('contact_'):
                contact_ids.append(contact_id_str.replace('contact_', ''))
            elif contact_id_str.isdigit(): # Allow plain IDs for robustness
                contact_ids.append(contact_id_str)
                
        # Get contacts queryset
        selected_contacts = Contact.objects.filter(id__in=contact_ids, company=company)

        # Get subject if provided
        subject_id = request.POST.get('subject')
        subject = None
        if subject_id:
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
        
        # Add selected contacts to the ManyToManyField
        if selected_contacts.exists():
            activity.contacts.set(selected_contacts)
        
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
                # Add Django message for task creation
                messages.success(request, 'Follow-up task created successfully.')
            except Exception as task_error:
                logging.error(f"Error creating follow-up task for note {activity.id}: {task_error}", exc_info=True)
                # Add Django warning message for task creation failure
                messages.warning(request, f'Note logged, but failed to create follow-up task: {task_error}')
        
        # Add Django success message for the note activity
        messages.success(request, 'Note activity logged successfully.')
        
        return JsonResponse({
            'success': True,
            'message': 'Note activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error in log_note_activity: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Add Django error message
        messages.error(request, f'Error logging note activity: {str(e)}')
        
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
        messages.error(request, 'Invalid Company ID')
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
        
        # Add Django success message for the waiver/favour activity
        messages.success(request, 'Waiver & Favour activity logged successfully.')
            
        return JsonResponse({
            'success': True,
            'message': 'Waiver & Favour activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error saving waiver/favour activity: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Add Django error message
        messages.error(request, f'Error logging waiver/favour activity: {str(e)}')
        
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
        # Get related contacts - now handling prefixed IDs from Tom Select
        related_contacts_ids = request.POST.getlist('related_contacts')
        logging.info(f"Task activity - related contact IDs from form: {related_contacts_ids}")
        
        # Separate contact and user recipients (similar to email activity)
        contact_recipient_ids = []
        user_recipient_ids = [] # Added list for user IDs
        
        for recipient_id in related_contacts_ids:
            if recipient_id.startswith('contact_'):
                contact_recipient_ids.append(recipient_id.replace('contact_', ''))
            elif recipient_id.startswith('user_'): # Added handling for user IDs
                user_recipient_ids.append(recipient_id.replace('user_', ''))
        
        # Get contacts and users querysets
        selected_contacts = Contact.objects.filter(id__in=contact_recipient_ids)
        selected_users = User.objects.filter(id__in=user_recipient_ids)
        
        # Removed logic for single primary contact
        # contact = None
        # if contact_recipient_ids:
        #     contact = get_object_or_404(Contact, id=contact_recipient_ids[0])
        #     logging.info(f"Task activity - using primary contact: {contact.get_full_name()}")
        
        # Get assignee
        assignee_id = request.POST.get('assignee')
        if assignee_id == 'current_user':
            assignee = request.user
        elif assignee_id:
            assignee = get_object_or_404(get_user_model(), id=assignee_id)
        else:
            assignee = None
        
        # Get and parse the due date and time
        due_date_str = request.POST.get('due_date', '')
        due_time_str = request.POST.get('due_time', '')
        
        try:
            due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else timezone.now().date()
        except ValueError:
            due_date = timezone.now().date()  # Default to today if format is wrong
            
        try:
            due_time = timezone.datetime.strptime(due_time_str, '%H:%M').time() if due_time_str else timezone.datetime.min.time().replace(hour=9)
        except ValueError:
            due_time = timezone.datetime.min.time().replace(hour=9)  # Default to 9:00 AM if format is wrong
            
        # Combine date and time into a datetime object with timezone
        naive_datetime = timezone.datetime.combine(due_date, due_time)
        due_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
        
        # Create task activity
        activity = TaskActivity.objects.create(
            company=company,
            performed_by=request.user,
            activity_type='task',
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
            due_datetime=due_datetime,  # Now using due_datetime with proper combined values
            priority=request.POST.get('priority', 'medium'),
            status=request.POST.get('status', 'not_started'),
            assigned_to=assignee
        )
        
        # Add selected contacts and users to the M2M fields
        if selected_contacts.exists():
            activity.contacts.set(selected_contacts)
        if selected_users.exists():
            activity.users.set(selected_users)
            
        # Removed logic for setting single contact FK
        # if contact:
        #     activity.contact = contact
        #     activity.save()
        
        # Add Django success message for task activity
        messages.success(request, 'Task activity logged successfully.')
        
        return JsonResponse({
            'success': True,
            'message': 'Task activity logged successfully',
            'activity_id': activity.id
        })
    except Exception as e:
        import traceback
        logging.error(f"Error in log_task_activity: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Add Django error message
        messages.error(request, f'Error logging task activity: {str(e)}')
        
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
    
    html = render_to_string('crm/activities/activity_list.html', context, request)
    return HttpResponse(html)

@login_required
def get_activity_details(request, activity_id):
    """API endpoint to get activity details as HTML fragment for modal or sidepanel"""
    try:
        # Add debug logging
        logging.info(f"get_activity_details called for activity_id: {activity_id}")
        
        # Determine if this is a sidepanel request
        is_sidepanel = 'sidepanel' in request.path
        logging.info(f"Is sidepanel request: {is_sidepanel}")
        
        # Get the activity with its subclass
        activity = get_object_or_404(Activity, id=activity_id)
        logging.info(f"Activity found: {activity.id}, type: {activity.activity_type}")
        
        # Get the specific activity type instance
        activity_details = None
        document = None
        found_document = False
        
        # Handle special cases for activity types with naming mismatches
        if activity.activity_type == 'waiver_favour':
            # For waiver_favour activities, check for waiveractivity
            if hasattr(activity, 'waiveractivity'):
                activity_details = activity.waiveractivity
                logging.debug(f"Found waiver activity details for ID: {activity.id}")
            else:
                # Only log at debug level, not warning
                logging.debug(f"No waiveractivity attribute found on activity {activity.id}")
        elif activity.activity_type == 'task':
            # For task activities, check for taskactivity
            if hasattr(activity, 'taskactivity'):
                activity_details = activity.taskactivity
                logging.debug(f"Found task activity details for ID: {activity.id}")
            else:
                # Only log at debug level, not warning
                logging.debug(f"No taskactivity attribute found on activity {activity.id}")
        elif activity.activity_type == 'email':
            # Special handling for email activities
            logging.info(f"Processing email activity with ID: {activity.id}")
            if hasattr(activity, 'emailactivity'):
                activity_details = activity.emailactivity
                logging.info(f"Found email activity details via attribute for ID: {activity.id}")
            else:
                # Try direct query
                try:
                    from django.apps import apps
                    email_model = apps.get_model('crm', 'EmailActivity')
                    activity_details = email_model.objects.get(activity_ptr_id=activity.id)
                    logging.info(f"Found email activity details via query for ID: {activity.id}")
                except Exception as e:
                    logging.error(f"Error retrieving email activity details: {str(e)}")
                    # Create a default empty activity details for rendering
                    activity_details = {
                        'subject': '(Email details unavailable)',
                        'body': f'Error retrieving email details: {str(e)}',
                        'email_date': activity.performed_at.date(),
                        'email_time': activity.performed_at.time(),
                        'contact_recipients': {'exists': False, 'all': []},
                        'user_recipients': {'exists': False, 'all': []}
                    }
        else:
            # For all other activity types, try to get the appropriate subclass
            subclass_name = f"{activity.activity_type}activity"
            if hasattr(activity, subclass_name):
                activity_details = getattr(activity, subclass_name)
                logging.debug(f"Found {subclass_name} details for ID: {activity.id}")
            else:
                # Fall back to direct query if attribute access fails - but don't log warnings
                try:
                    from django.apps import apps
                    activity_model = apps.get_model('crm', f"{activity.activity_type.capitalize()}Activity")
                    activity_details = activity_model.objects.get(activity_ptr_id=activity.id)
                    logging.debug(f"Found {activity.activity_type} details via query for ID: {activity.id}")
                except Exception as model_e:
                    # Just log at debug level to avoid filling logs with warnings
                    logging.debug(f"Could not get activity details via query: {str(model_e)}")
                    
            # Skip warning about missing activity subclass - log at debug level if needed
            if activity.activity_type == 'document' and activity.is_system_activity and not found_document:
                logging.debug(f"No {activity.activity_type}activity attribute found on activity {activity.id}")
        
        context = {
            'activity': activity,
            'activity_details': activity_details,
            'document': document,
        }
        
        # Always use the sidepanel template
        template_path = 'crm/activities/activity_detail_sidepanel_content.html'
            
        logging.info(f"Rendering template: {template_path}")
        
        # Return HTML fragment instead of JSON
        html_content = render_to_string(template_path, context, request)
        return HttpResponse(html_content)
        
    except Exception as e:
        logging.error(f"Error in get_activity_details view: {str(e)}", exc_info=True)
        error_html = f"""
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Error loading activity details:</strong><br>
            {str(e)}
        </div>
        """
        return HttpResponse(error_html)

@login_required
def edit_activity(request, activity_id):
    # Get basic activity first
    activity = get_object_or_404(Activity, id=activity_id)
    is_sidepanel = request.GET.get('sidepanel') == '1' or 'sidepanel' in request.path
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Check if we're handling a specific activity type
    activity_type = request.GET.get('activity_type') or activity.activity_type
    
    # Get the specialized activity model
    specialized_activity = None
    if activity_type == 'email':
        try:
            specialized_activity = EmailActivity.objects.get(id=activity_id)
            template_name = 'crm/activities/edit/email_edit_form.html'
            form_class = EmailActivityForm
        except EmailActivity.DoesNotExist:
            pass
    elif activity_type == 'call':
        try:
            specialized_activity = CallActivity.objects.get(id=activity_id)
            template_name = 'crm/activities/edit/call_edit_form.html'
            form_class = None # Define if needed
        except CallActivity.DoesNotExist:
            pass
    elif activity_type == 'meeting':
        try:
            specialized_activity = MeetingActivity.objects.get(id=activity_id)
            template_name = 'crm/activities/edit/meeting_edit_form.html'
            form_class = None # Define if needed
        except MeetingActivity.DoesNotExist:
            pass
    elif activity_type == 'note':
        try:
            specialized_activity = NoteActivity.objects.get(id=activity_id)
            template_name = 'crm/activities/edit/note_edit_form.html'
            form_class = None # No Django form used here
        except NoteActivity.DoesNotExist:
            pass
    elif activity_type == 'task':
        try:
            specialized_activity = TaskActivity.objects.get(id=activity_id)
            template_name = 'crm/activities/edit/task_edit_form.html'
            form_class = None # No Django form used here
        except TaskActivity.DoesNotExist:
            pass
    elif activity_type == 'waiver_favour':
        try:
            specialized_activity = WaiverActivity.objects.get(id=activity_id)
            template_name = 'crm/activities/edit/waiver_edit_form.html'
            form_class = None # No Django form used here
        except WaiverActivity.DoesNotExist:
            pass
    # Add other activity types here...
    
    # Handle POST submission
    if request.method == 'POST':
        # Process the form submission and update the activity
        if activity_type == 'email':
            # Get the form data
            subject = request.POST.get('subject', '')
            body = request.POST.get('body', '')
            recipient_ids = request.POST.getlist('recipients', [])
            
            # Update basic fields
            specialized_activity.subject = subject
            specialized_activity.body = body
            
            # Update date/time if provided
            email_date_str = request.POST.get('date')
            email_time_str = request.POST.get('time')
            
            if email_date_str:
                try:
                    specialized_activity.email_date = timezone.datetime.strptime(email_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
                    
            if email_time_str:
                try:
                    specialized_activity.email_time = timezone.datetime.strptime(email_time_str, '%H:%M').time()
                except ValueError:
                    pass
            
            # Save the changes
            specialized_activity.save()
            
            # Update edit tracking fields on base activity
            activity.last_edited_at = timezone.now()
            activity.last_edited_by = request.user
            activity.save(update_fields=['last_edited_at', 'last_edited_by'])
            
            # Update recipients
            # First clear existing recipients
            specialized_activity.contact_recipients.clear()
            specialized_activity.user_recipients.clear()
            
            # Add new recipients
            for recipient_id in recipient_ids:
                if recipient_id.startswith('contact_'):
                    contact_id = recipient_id.replace('contact_', '')
                    contact = get_object_or_404(Contact, id=contact_id)
                    specialized_activity.contact_recipients.add(contact)
                elif recipient_id.startswith('user_'):
                    user_id = recipient_id.replace('user_', '')
                    user = get_object_or_404(User, id=user_id)
                    specialized_activity.user_recipients.add(user)
            
            # Check if we should create a follow-up task
            if request.POST.get('create_follow_up_task'):
                task_title = request.POST.get('follow_up_task_title', f'Follow up on email: {specialized_activity.subject}')
                task_notes = request.POST.get('follow_up_task_notes', '')
                
                # Handle due date/time
                due_date_str = request.POST.get('follow_up_due_date')
                due_time_str = request.POST.get('follow_up_due_time')
                
                due_datetime = None
                if due_date_str:
                    try:
                        due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                        # Set default time to 9am if not provided
                        due_time = timezone.datetime.strptime(due_time_str or '09:00', '%H:%M').time()
                        due_datetime = timezone.make_aware(timezone.datetime.combine(due_date, due_time))
                    except ValueError:
                        due_datetime = timezone.now() + timedelta(days=1)
                        due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                else:
                    due_datetime = timezone.now() + timedelta(days=1)
                    due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                
                # Create the task
                task = TaskActivity.objects.create(
                    company=activity.company,
                    title=task_title,
                    description=task_notes,
                    performed_by=request.user,
                    assigned_to=request.user,
                    status='not_started',
                    priority='medium',
                    due_datetime=due_datetime
                )
                
                # Add the same recipients to the task
                for contact in specialized_activity.contact_recipients.all():
                    task.contacts.add(contact)
                for user in specialized_activity.user_recipients.all():
                    task.users.add(user)
                
                # Update the message
                if is_ajax:
                    return JsonResponse({'success': True, 'message': 'Email activity updated successfully with follow-up task'})
                else:
                    messages.success(request, 'Email activity updated successfully with follow-up task')
                    return redirect('crm:company_detail', pk=activity.company.id)
            
            # Return success response for AJAX requests
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Email activity updated successfully'})
            else:
                messages.success(request, 'Email activity updated successfully')
                return redirect('crm:company_detail', pk=activity.company.id)
        
        elif activity_type == 'call':
            # Get form data for call
            contact_input_id = request.POST.get('contact')
            call_purpose = request.POST.get('call_purpose', '')
            call_summary = request.POST.get('call_summary', '')
            call_outcome = request.POST.get('call_outcome', '')
            duration = request.POST.get('duration')
            is_outbound = request.POST.get('outbound') == '1'
            
            # Update basic fields
            specialized_activity.summary = call_purpose # Map call_purpose to summary
            specialized_activity.description = call_summary # Map call_summary to description
            specialized_activity.call_outcome = call_outcome
            specialized_activity.call_type = 'Outbound' if is_outbound else 'Inbound'
            if duration and duration.isdigit():
                specialized_activity.duration = int(duration)
                
            # Update contact
            contact = None
            if contact_input_id:
                if contact_input_id.startswith('contact_'):
                    contact_id = contact_input_id.replace('contact_', '')
                elif contact_input_id.isdigit(): 
                    contact_id = contact_input_id
                else:
                    contact_id = None
                    
                if contact_id:
                    try:
                        contact = Contact.objects.get(id=contact_id)
                        specialized_activity.contact = contact
                    except Contact.DoesNotExist:
                        specialized_activity.contact = None # Clear if contact not found
            else:
                specialized_activity.contact = None # Clear if no contact provided
                
            # Update date/time (using the base activity's performed_at)
            call_date_str = request.POST.get('date')
            call_time_str = request.POST.get('time')
            
            try:
                call_date = timezone.datetime.strptime(call_date_str, '%Y-%m-%d').date() if call_date_str else activity.performed_at.date()
                call_time = timezone.datetime.strptime(call_time_str, '%H:%M').time() if call_time_str else activity.performed_at.time()
                naive_datetime = timezone.datetime.combine(call_date, call_time)
                activity.performed_at = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
                activity.save(update_fields=['performed_at'])
            except ValueError:
                # Keep existing datetime if parsing fails
                pass
                
            # Save the specialized activity changes
            specialized_activity.save()
            
            # Update edit tracking fields on base activity
            activity.last_edited_at = timezone.now()
            activity.last_edited_by = request.user
            activity.save(update_fields=['performed_at', 'last_edited_at', 'last_edited_by'])
            
            # Handle follow-up task creation for call
            if request.POST.get('create_follow_up_task'):
                try:
                    task_title = request.POST.get('follow_up_task_title', '').strip()
                    if not task_title:
                        contact_name = f" with {specialized_activity.contact.get_full_name()}" if specialized_activity.contact else ""
                        default_title = f"Follow up on call{contact_name} ({specialized_activity.summary or 'Call Activity'})"
                        task_title = default_title[:255]
                    
                    due_date_str = request.POST.get('follow_up_due_date')
                    due_time_str = request.POST.get('follow_up_due_time')
                    
                    due_datetime = None
                    if due_date_str:
                        try:
                            due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                            due_time = timezone.datetime.strptime(due_time_str or '09:00', '%H:%M').time()
                            due_datetime = timezone.make_aware(timezone.datetime.combine(due_date, due_time))
                        except ValueError:
                            due_datetime = timezone.now() + timedelta(days=1)
                            due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                    else:
                        due_datetime = timezone.now() + timedelta(days=1)
                        due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                    
                    task_notes = request.POST.get('follow_up_task_notes', '').strip()
                    base_description = f"Follow-up task automatically created for edited Call Activity ID: {activity.id}"
                    task_description = f"{task_notes}\n\n---\n{base_description}" if task_notes else base_description
                    
                    task = TaskActivity.objects.create(
                        company=activity.company,
                        performed_by=request.user,
                        activity_type='task',
                        title=task_title,
                        description=task_description,
                        due_datetime=due_datetime,
                        assigned_to=request.user,
                        status='not_started',
                        priority='medium',
                        related_activity=activity # Link task to the original call activity
                    )
                    
                    if is_ajax:
                        return JsonResponse({'success': True, 'message': 'Call activity updated successfully with follow-up task', 'reload_page': True})
                    else:
                        messages.success(request, 'Call activity updated successfully with follow-up task')
                        return redirect('crm:company_detail', pk=activity.company.id)
                except Exception as task_error:
                    logging.error(f"Error creating follow-up task for edited call {activity.id}: {task_error}", exc_info=True)
                    if is_ajax:
                        return JsonResponse({'success': True, 'message': f'Call updated, but failed to create follow-up task: {task_error}', 'reload_page': True})
                    else:
                        messages.warning(request, f'Call updated, but failed to create follow-up task: {task_error}')
                        return redirect('crm:company_detail', pk=activity.company.id)
            
            # Return success response for call update without task
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Call activity updated successfully', 'reload_page': True})
            else:
                messages.success(request, 'Call activity updated successfully')
                return redirect('crm:company_detail', pk=activity.company.id)
        
        elif activity_type == 'meeting':
            # Get form data for meeting
            title = request.POST.get('title', '')
            attendee_ids = request.POST.getlist('attendees', [])
            location = request.POST.get('location', '')
            agenda = request.POST.get('agenda', '')
            notes = request.POST.get('notes', '') # This maps to minutes
            outcome = request.POST.get('outcome', '')
            duration = request.POST.get('duration')
            
            # Update basic fields
            specialized_activity.title = title
            specialized_activity.location = location
            specialized_activity.agenda = agenda
            specialized_activity.minutes = notes # Use notes field for minutes
            specialized_activity.meeting_outcome = outcome
            if duration and duration.isdigit():
                specialized_activity.duration = int(duration)
                
            # Update date/time (using the base activity's performed_at)
            meeting_date_str = request.POST.get('date')
            meeting_time_str = request.POST.get('time')
            
            try:
                meeting_date = timezone.datetime.strptime(meeting_date_str, '%Y-%m-%d').date() if meeting_date_str else activity.performed_at.date()
                meeting_time = timezone.datetime.strptime(meeting_time_str, '%H:%M').time() if meeting_time_str else activity.performed_at.time()
                naive_datetime = timezone.datetime.combine(meeting_date, meeting_time)
                activity.performed_at = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
            except ValueError:
                # Keep existing datetime if parsing fails
                pass
                
            # Update attendees
            specialized_activity.contact_attendees.clear()
            specialized_activity.user_attendees.clear()
            for attendee_id in attendee_ids:
                if attendee_id.startswith('contact_'):
                    contact_id = attendee_id.replace('contact_', '')
                    contact = get_object_or_404(Contact, id=contact_id)
                    specialized_activity.contact_attendees.add(contact)
                elif attendee_id.startswith('user_'):
                    user_id = attendee_id.replace('user_', '')
                    user = get_object_or_404(User, id=user_id)
                    specialized_activity.user_attendees.add(user)
            
            # Save the specialized activity changes first
            specialized_activity.save()
            
            # Update edit tracking fields and potentially performed_at on base activity
            activity.last_edited_at = timezone.now()
            activity.last_edited_by = request.user
            activity.save(update_fields=['performed_at', 'last_edited_at', 'last_edited_by'])
            
            # Handle follow-up task creation for meeting
            if request.POST.get('create_follow_up_task'):
                try:
                    task_title = request.POST.get('follow_up_task_title', '').strip()
                    if not task_title:
                        default_title = f"Follow up on meeting: {specialized_activity.title or 'Meeting Activity'}"
                        task_title = default_title[:255]
                        
                    due_date_str = request.POST.get('follow_up_due_date')
                    due_time_str = request.POST.get('follow_up_due_time')
                    
                    due_datetime = None
                    if due_date_str:
                        try:
                            due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                            due_time = timezone.datetime.strptime(due_time_str or '09:00', '%H:%M').time()
                            due_datetime = timezone.make_aware(timezone.datetime.combine(due_date, due_time))
                        except ValueError:
                            due_datetime = timezone.now() + timedelta(days=1)
                            due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                    else:
                        due_datetime = timezone.now() + timedelta(days=1)
                        due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                    
                    task_notes = request.POST.get('follow_up_task_notes', '').strip()
                    base_description = f"Follow-up task automatically created for edited Meeting Activity ID: {activity.id}"
                    task_description = f"{task_notes}\n\n---\n{base_description}" if task_notes else base_description
                    
                    task = TaskActivity.objects.create(
                        company=activity.company,
                        performed_by=request.user,
                        activity_type='task',
                        title=task_title,
                        description=task_description,
                        due_datetime=due_datetime,
                        assigned_to=request.user,
                        status='not_started',
                        priority='medium',
                        related_activity=activity # Link task to the original meeting activity
                    )
                    
                    # Add attendees to the follow-up task
                    for contact in specialized_activity.contact_attendees.all():
                        task.contacts.add(contact)
                    for user in specialized_activity.user_attendees.all():
                        task.users.add(user)
                    
                    if is_ajax:
                        return JsonResponse({'success': True, 'message': 'Meeting activity updated successfully with follow-up task', 'reload_page': True})
                    else:
                        messages.success(request, 'Meeting activity updated successfully with follow-up task')
                        return redirect('crm:company_detail', pk=activity.company.id)
                except Exception as task_error:
                    logging.error(f"Error creating follow-up task for edited meeting {activity.id}: {task_error}", exc_info=True)
                    if is_ajax:
                        return JsonResponse({'success': True, 'message': f'Meeting updated, but failed to create follow-up task: {task_error}', 'reload_page': True})
                    else:
                        messages.warning(request, f'Meeting updated, but failed to create follow-up task: {task_error}')
                        return redirect('crm:company_detail', pk=activity.company.id)
            
            # Return success response for meeting update without task
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Meeting activity updated successfully', 'reload_page': True})
            else:
                messages.success(request, 'Meeting activity updated successfully')
                return redirect('crm:company_detail', pk=activity.company.id)
        
        elif activity_type == 'note':
            # Get form data for note
            subject_id = request.POST.get('subject')
            content = request.POST.get('content', '')
            is_important = request.POST.get('is_important') == 'on'
            
            # Update basic fields
            specialized_activity.content = content
            specialized_activity.description = content # Keep description synced with content
            specialized_activity.is_important = is_important
            
            # Update subject
            if subject_id:
                try:
                    note_subject = NoteSubject.objects.get(id=subject_id)
                    specialized_activity.subject = note_subject
                except NoteSubject.DoesNotExist:
                    specialized_activity.subject = None # Set to null if subject not found
            else:
                specialized_activity.subject = None # Set to null if no subject selected
                
            # +++ ADDED: Update associated contacts +++
            contact_input_ids = request.POST.getlist('contacts')
            contact_ids = []
            for contact_id_str in contact_input_ids:
                if contact_id_str.startswith('contact_'):
                    contact_ids.append(contact_id_str.replace('contact_', ''))
                elif contact_id_str.isdigit():
                    contact_ids.append(contact_id_str)
            
            selected_contacts = Contact.objects.filter(id__in=contact_ids, company=activity.company)
            specialized_activity.contacts.set(selected_contacts) # Use set() to update M2M
            # --- END --- 
            
            # Save the specialized activity changes first
            specialized_activity.save()
            
            # Update edit tracking fields on base activity
            activity.last_edited_at = timezone.now()
            activity.last_edited_by = request.user
            activity.save(update_fields=['last_edited_at', 'last_edited_by'])
            
            # Handle follow-up task creation for note
            if request.POST.get('create_follow_up_task'):
                try:
                    task_title = request.POST.get('follow_up_task_title', '').strip()
                    if not task_title:
                        default_title = f"Follow up on note: {specialized_activity.content[:50]}..." if len(specialized_activity.content) > 50 else f"Follow up on note: {specialized_activity.content}"
                        task_title = default_title[:255]
                        
                    due_date_str = request.POST.get('follow_up_due_date')
                    due_time_str = request.POST.get('follow_up_due_time')
                    
                    due_datetime = None
                    if due_date_str:
                        try:
                            due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                            due_time = timezone.datetime.strptime(due_time_str or '09:00', '%H:%M').time()
                            due_datetime = timezone.make_aware(timezone.datetime.combine(due_date, due_time))
                        except ValueError:
                            due_datetime = timezone.now() + timedelta(days=1)
                            due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                    else:
                        due_datetime = timezone.now() + timedelta(days=1)
                        due_datetime = due_datetime.replace(hour=9, minute=0, second=0)
                    
                    task_notes = request.POST.get('follow_up_task_notes', '').strip()
                    base_description = f"Follow-up task automatically created for edited Note Activity ID: {activity.id}"
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
                        related_activity=activity # Link task to the original note activity
                    )
                    
                    if is_ajax:
                        return JsonResponse({'success': True, 'message': 'Note activity updated successfully with follow-up task', 'reload_page': True})
                    else:
                        messages.success(request, 'Note activity updated successfully with follow-up task')
                        return redirect('crm:company_detail', pk=activity.company.id)
                except Exception as task_error:
                    logging.error(f"Error creating follow-up task for edited note {activity.id}: {task_error}", exc_info=True)
                    if is_ajax:
                        return JsonResponse({'success': True, 'message': f'Note updated, but failed to create follow-up task: {task_error}', 'reload_page': True})
                    else:
                        messages.warning(request, f'Note updated, but failed to create follow-up task: {task_error}')
                        return redirect('crm:company_detail', pk=activity.company.id)
            
            # Return success response for note update without task
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Note activity updated successfully', 'reload_page': True})
            else:
                messages.success(request, 'Note activity updated successfully')
                return redirect('crm:company_detail', pk=activity.company.id)
        
        elif activity_type == 'task':
            # Get form data for task
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            priority = request.POST.get('priority', 'medium')
            status = request.POST.get('status', 'not_started')
            assignee_id = request.POST.get('assignee')
            related_item_ids = request.POST.getlist('related_contacts', [])
            
            # Update basic fields
            specialized_activity.title = title
            specialized_activity.description = description
            specialized_activity.priority = priority
            specialized_activity.status = status
            
            # Update assignee
            if assignee_id:
                try:
                    assignee = User.objects.get(id=assignee_id)
                    specialized_activity.assigned_to = assignee
                except User.DoesNotExist:
                    specialized_activity.assigned_to = None
            else:
                specialized_activity.assigned_to = None # Allow unassigning
            
            # Update due date/time
            due_date_str = request.POST.get('due_date')
            due_time_str = request.POST.get('due_time')
            # Reset due_datetime to None if date/time strings are empty
            if not due_date_str and not due_time_str:
                specialized_activity.due_datetime = None
            elif due_date_str and due_time_str:
                try:
                    due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                    due_time = timezone.datetime.strptime(due_time_str, '%H:%M').time()
                    naive_datetime = timezone.datetime.combine(due_date, due_time)
                    specialized_activity.due_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
                except ValueError:
                    # Keep existing datetime if parsing fails
                    pass 
            
            # +++ UPDATED: Update related contacts and users (M2M) +++
            related_item_ids = request.POST.getlist('related_contacts') # Get combined list
            # +++ DEBUG LOGGING +++
            logging.debug(f"[EDIT TASK - POST] Received related_item_ids: {related_item_ids}")
            # --- END DEBUG ---
            contact_ids = []
            user_ids = []
            for item_id in related_item_ids:
                if item_id.startswith('contact_'):
                    contact_ids.append(item_id.replace('contact_', ''))
                elif item_id.startswith('user_'):
                    user_ids.append(item_id.replace('user_', ''))
            
            # Update M2M fields using set()
            selected_contacts = Contact.objects.filter(id__in=contact_ids)
            selected_users = User.objects.filter(id__in=user_ids)
            specialized_activity.contacts.set(selected_contacts)
            specialized_activity.users.set(selected_users)
            # --- END --- 
            
            # Removed old logic for single contact FK
            # selected_contact_id = None
            # for item_id in related_item_ids:
            #     if item_id.startswith('contact_'):
            #         selected_contact_id = item_id.replace('contact_', '')
            #         break 
            # 
            # if selected_contact_id:
            #     try:
            #         contact_obj = Contact.objects.get(id=selected_contact_id)
            #         specialized_activity.contact = contact_obj
            #     except Contact.DoesNotExist:
            #         specialized_activity.contact = None
            # else:
            #     specialized_activity.contact = None
            
            # Save the specialized activity changes first
            specialized_activity.save()
            
            # Update edit tracking fields on base activity
            activity.last_edited_at = timezone.now()
            activity.last_edited_by = request.user
            activity.save(update_fields=['last_edited_at', 'last_edited_by'])
            
            # Return success response
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Task activity updated successfully', 'reload_page': True})
            else:
                messages.success(request, 'Task activity updated successfully')
                return redirect('crm:company_detail', pk=activity.company.id)
        
        elif activity_type == 'waiver_favour':
            # Get form data for waiver/favour
            type_id = request.POST.get('type')
            contact_ids = request.POST.getlist('contacts', []) # Expecting contact_XXX format
            amount_str = request.POST.get('amount')
            reason = request.POST.get('reason', '')
            approved_by_id = request.POST.get('approved_by')
            
            # Update basic fields
            specialized_activity.reason = reason
            specialized_activity.description = reason # Keep description synced
            
            # Update type
            if type_id:
                try:
                    waiver_type = WaiverFavourType.objects.get(id=type_id)
                    specialized_activity.type = waiver_type
                except WaiverFavourType.DoesNotExist:
                    # Maybe raise an error or set to None if type is mandatory?
                    # For now, let's assume it can be cleared if type not found
                    specialized_activity.type = None 
            else:
                 # If type is mandatory, we might need validation here
                 specialized_activity.type = None
                 
            # Update amount
            if amount_str:
                try:
                    specialized_activity.amount = Decimal(amount_str)
                except (ValueError, InvalidOperation):
                    specialized_activity.amount = None # Clear if invalid
            else:
                specialized_activity.amount = None # Clear if empty
            
            # Update approved_by
            if approved_by_id:
                try:
                    approver = User.objects.get(id=approved_by_id)
                    specialized_activity.approved_by = approver
                except User.DoesNotExist:
                    specialized_activity.approved_by = None
            else:
                specialized_activity.approved_by = None # Clear approval
                
            # Update contacts (replace existing)
            specialized_activity.contacts.clear()
            for contact_id_str in contact_ids:
                if contact_id_str.startswith('contact_'):
                    contact_id = contact_id_str.replace('contact_', '')
                    try:
                        contact = Contact.objects.get(id=contact_id)
                        specialized_activity.contacts.add(contact)
                    except Contact.DoesNotExist:
                        pass # Ignore if a contact ID is invalid
            
            # Save the specialized activity changes first
            specialized_activity.save()
            
            # Update edit tracking fields on base activity
            activity.last_edited_at = timezone.now()
            activity.last_edited_by = request.user
            activity.save(update_fields=['last_edited_at', 'last_edited_by', 'description'])
            
            # Return success response
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Waiver & Favour activity updated successfully', 'reload_page': True})
            else:
                messages.success(request, 'Waiver & Favour activity updated successfully')
                return redirect('crm:company_detail', pk=activity.company.id)
    
    # Prepare the form for GET requests
    if specialized_activity:
        # Prepare context data specific to the activity type
        context_data = {}
        if activity_type == 'email':
            current_recipients = []
            for contact in specialized_activity.contact_recipients.all():
                current_recipients.append({
                    'id': f'contact_{contact.id}',
                    'text': contact.get_full_name()
                })
            for user in specialized_activity.user_recipients.all():
                current_recipients.append({
                    'id': f'user_{user.id}',
                    'text': user.get_full_name()
                })
            context_data['current_recipients'] = current_recipients
        elif activity_type == 'call':
            # For call, we don't need special data beyond activity_details
            # TomSelect initialization will handle the single contact selection
            pass
        elif activity_type == 'meeting':
            # Prepare attendees data for meeting edit form
            current_attendees = []
            for contact in specialized_activity.contact_attendees.all():
                current_attendees.append({
                    'id': f'contact_{contact.id}',
                    'text': contact.get_full_name()
                })
            for user in specialized_activity.user_attendees.all():
                current_attendees.append({
                    'id': f'user_{user.id}',
                    'text': user.get_full_name()
                })
            context_data['current_attendees'] = current_attendees
        elif activity_type == 'note':
            # Fetch NoteSubject choices for the dropdown
            context_data['subjects'] = NoteSubject.objects.all()
            # +++ ADDED: Prepare current contacts for note edit TomSelect +++
            current_contacts = []
            for contact in specialized_activity.contacts.all():
                current_contacts.append({
                    'id': f'contact_{contact.id}',
                    'text': contact.get_full_name()
                })
            context_data['current_contacts'] = current_contacts
            # --- END --- 
        elif activity_type == 'task':
            # Fetch users for assignee dropdown
            context_data['users'] = User.objects.filter(is_active=True)
            # +++ UPDATED: Prepare related items for task edit TomSelect (M2M) +++
            current_related_items = []
            for contact in specialized_activity.contacts.all():
                current_related_items.append({
                    'id': f'contact_{contact.id}',
                    'text': contact.get_full_name(),
                    'type': 'contact' # Add type for rendering
                })
            for user in specialized_activity.users.all():
                 current_related_items.append({
                    'id': f'user_{user.id}',
                    'text': user.get_full_name(),
                    'type': 'user' # Add type for rendering
                })
            context_data['current_related_items'] = current_related_items
            # Removed old single contact context
            # context_data['current_related_contact'] = specialized_activity.contact
            # --- END --- 
        elif activity_type == 'waiver_favour':
            # Fetch WaiverFavourType choices
            context_data['waiver_types'] = WaiverFavourType.objects.all()
            # Fetch Users for approved_by dropdown
            context_data['users'] = User.objects.filter(is_active=True)
            # Prepare current contacts for TomSelect
            current_contacts = []
            for contact in specialized_activity.contacts.all():
                current_contacts.append({
                    'id': f'contact_{contact.id}', # Use prefixed ID for consistency
                    'text': contact.get_full_name()
                })
            context_data['current_contacts'] = current_contacts
        
        context = {
            'activity': activity,
            'activity_details': specialized_activity,
            'company': activity.company,
            **context_data # Add type-specific context data
        }
        
        if is_ajax:
            html = render_to_string(template_name, context, request=request)
            return HttpResponse(html)
        else:
            return render(request, template_name, context)
    
    # Fallback if we couldn't find the specialized activity
    messages.error(request, f"Could not find {activity_type} activity with ID {activity_id}")
    return redirect('crm:company_detail', pk=activity.company.id)

@login_required
def delete_activity(request, activity_id):
    # Only handle POST requests from the confirmation modal form
    if request.method != 'POST':
        # If accessed via GET or other methods, redirect with info message
        # Avoid showing a confirmation page here, rely on the modal
        activity = get_object_or_404(Activity, id=activity_id)
        messages.info(request, 'Please use the confirmation dialog in the side panel to delete activities.')
        return redirect('crm:company_detail', pk=activity.company.id)

    # Permission Check: Allow only superuser and admin
    if not request.user.is_superuser and request.user.role != 'admin':
        messages.error(request, 'You do not have permission to delete activities.')
        # Need company_id for redirect, try getting it from the activity first
        try:
            activity = Activity.objects.get(id=activity_id)
            company_id = activity.company.id
        except Activity.DoesNotExist:
             # Fallback: If activity doesn't exist, maybe redirect to a general dashboard or list view
             # Or try getting company ID differently if possible. For now, let's redirect to company list.
             # This case is unlikely if the delete button was shown.
             return redirect('crm:company_list') # Adjust target as needed
        return redirect('crm:company_detail', pk=company_id)

    # Get IDs from POST data
    activity_id_to_delete = request.POST.get('activity_id_to_delete')
    confirm_id_typed = request.POST.get('confirm_activity_id')

    # Verify the hidden ID matches the URL ID (as a safeguard)
    if str(activity_id_to_delete) != str(activity_id):
        messages.error(request, 'An error occurred (ID mismatch). Please try again.')
        # Try to get company ID for redirect
        try:
            activity = Activity.objects.get(id=activity_id)
            company_id = activity.company.id
        except Activity.DoesNotExist:
            return redirect('crm:company_list') # Adjust target
        return redirect('crm:company_detail', pk=company_id)

    # Get the activity instance
    activity = get_object_or_404(Activity, id=activity_id)
    company_id = activity.company.id # Store company ID before deleting activity

    # Check if the typed confirmation ID matches the actual activity ID
    if str(confirm_id_typed) == str(activity.id):
        try:
            activity_description = f"{activity.get_activity_type_display()} on {activity.performed_at.strftime('%b %d')}"
            activity.delete()
            messages.success(request, f'Activity (ID: {activity_id}) "{activity_description}" deleted successfully.')
        except Exception as e:
            logging.error(f"Error deleting activity ID {activity_id}: {str(e)}", exc_info=True)
            messages.error(request, f'An error occurred while deleting the activity: {str(e)}')
    else:
        messages.error(request, f'Confirmation failed. The entered ID "{confirm_id_typed}" did not match the activity ID "{activity.id}".')

    # Redirect back to the company detail page
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