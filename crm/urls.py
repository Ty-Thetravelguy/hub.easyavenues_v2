from django.urls import path
from . import views
from .views import activity_views
from .views import company_views
from .views import contact_views
from .views import document_views
from .views import travel_policy_views
from .views import hubspot_views
from .views import admin_views

app_name = 'crm'

urlpatterns = [
    path('companies/', company_views.company_list, name='company_list'),
    path('companies/<int:pk>/', company_views.company_detail, name='company_detail'),
    path('companies/<int:pk>/update/', company_views.CompanyUpdateView.as_view(), name='company_update'),
    path('companies/create/', company_views.CompanyCreateWizardView.as_view(), name='company_create'),
    path('companies/<int:company_id>/contacts/create/', contact_views.ContactCreateView.as_view(), name='contact_create'),
    path('contacts/', contact_views.ContactListView.as_view(), name='contact_list'),
    path('contacts/<int:pk>/', contact_views.ContactDetailView.as_view(), name='contact_detail'),
    path('contacts/<int:pk>/update/', contact_views.ContactUpdateView.as_view(), name='contact_update'),
    path('contacts/<int:pk>/add-note/', contact_views.contact_add_note, name='contact_add_note'),
    path('contacts/<int:pk>/delete/', contact_views.contact_delete, name='contact_delete'),
    path('contacts/create/<int:company_id>/', contact_views.ContactCreateView.as_view(), name='contact_create'),
    path('company/<int:company_id>/update-invoice-references/', company_views.update_invoice_references, name='update_invoice_references'),
    path('company/<int:company_id>/relationships/', company_views.manage_company_relationships, name='manage_company_relationships'),
    path('company/relationship/<int:relationship_id>/delete/', company_views.delete_company_relationship, name='delete_company_relationship'),
    
    # Document Management
    path('company/<int:company_id>/documents/upload/', document_views.document_upload, name='document_upload'),
    path('documents/<int:document_id>/delete/', document_views.document_delete, name='document_delete'),
    path('documents/<int:document_id>/', document_views.document_detail, name='document_detail'),
    path('documents/<int:document_id>/update/', document_views.document_update, name='document_update'),
    
    # Travel Policy Management
    path('company/<int:company_id>/travel-policy/create/', travel_policy_views.travel_policy_create, name='travel_policy_create'),
    path('travel-policy/<int:policy_id>/', travel_policy_views.travel_policy_detail, name='travel_policy_detail'),
    path('travel-policy/<int:policy_id>/update/', travel_policy_views.travel_policy_update, name='travel_policy_update'),
    path('travel-policy/<int:policy_id>/delete/', travel_policy_views.travel_policy_delete, name='travel_policy_delete'),
    
    # Activity Logging - Legacy paths (keep for backward compatibility)
    path('company/<int:company_id>/log/email/', activity_views.log_email_activity, name='log_email'),
    path('company/<int:company_id>/log/call/', activity_views.log_call_activity, name='log_call'),
    path('company/<int:company_id>/log/meeting/', activity_views.log_meeting_activity, name='log_meeting'),
    path('company/<int:company_id>/log/note/', activity_views.log_note_activity, name='log_note'),
    path('company/<int:company_id>/log/waiver-favor/', activity_views.log_waiver_activity, name='log_waiver_favor'),
    
    # Activity Management - New routes using activity_views
    path('activity/<int:activity_id>/details/', activity_views.get_activity_details, name='activity_details'),
    path('activity/<int:activity_id>/edit/', activity_views.edit_activity, name='edit_activity'),
    path('activity/<int:activity_id>/delete/', activity_views.delete_activity, name='delete_activity'),
    path('api/search-recipients/', activity_views.search_recipients, name='search_recipients'),
    
    # HubSpot Integration
    path('hubspot/search/', hubspot_views.hubspot_search, name='hubspot_search'),
    path('hubspot/company/<str:hubspot_id>/', hubspot_views.hubspot_company_detail, name='hubspot_company_detail'),
    path('hubspot/import/<str:hubspot_id>/', hubspot_views.import_hubspot_company, name='import_hubspot_company'),
    path('hubspot/api-test/', hubspot_views.hubspot_api_test, name='hubspot_api_test'),
    path('hubspot/setup-guide/', hubspot_views.hubspot_setup_guide, name='hubspot_setup_guide'),
    
    # Activity URLs - New activity framework
    path('activity/<str:activity_type>/form/', activity_views.activity_form, name='activity_form'),
    path('company/<int:company_id>/activities/', activity_views.company_activities, name='company_activities'),
    path('company/<int:company_id>/activities-json/', activity_views.company_activities_json, name='company_activities_json'),
    path('activity/email/', activity_views.log_email_activity, name='log_email_activity'),
    path('activity/call/', activity_views.log_call_activity, name='log_call_activity'),
    path('activity/meeting/', activity_views.log_meeting_activity, name='log_meeting_activity'),
    path('activity/note/', activity_views.log_note_activity, name='log_note_activity'),
    path('activity/waiver/', activity_views.log_waiver_activity, name='log_waiver_activity'),
    path('activity/task/', activity_views.log_task_activity, name='log_task_activity'),
    path('activity/details/<int:activity_id>/', activity_views.activity_details, name='activity_view'),
    
    # --- Admin/Settings Management --- 
    path(
        'manage/note-subjects/',
        admin_views.NoteSubjectListView.as_view(),
        name='manage_note_subject_list'
    ),
    path(
        'manage/note-subjects/create/',
        admin_views.NoteSubjectCreateView.as_view(),
        name='manage_note_subject_create'
    ),
    path(
        'manage/note-subjects/<int:pk>/update/',
        admin_views.NoteSubjectUpdateView.as_view(),
        name='manage_note_subject_update'
    ),
    path(
        'manage/note-subjects/<int:pk>/delete/',
        admin_views.NoteSubjectDeleteView.as_view(),
        name='manage_note_subject_delete'
    ),
    # --- End Admin/Settings Management --- 
]
    