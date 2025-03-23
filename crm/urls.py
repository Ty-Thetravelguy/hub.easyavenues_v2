from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('companies/', views.company_list, name='company_list'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('companies/<int:pk>/update/', views.CompanyUpdateView.as_view(), name='company_update'),
    path('companies/create/', views.CompanyCreateWizardView.as_view(), name='company_create'),
    path('companies/<int:company_id>/contacts/create/', views.ContactCreateView.as_view(), name='contact_create'),
    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact_detail'),
    path('contacts/<int:pk>/update/', views.ContactUpdateView.as_view(), name='contact_update'),
    path('contacts/<int:pk>/add-note/', views.contact_add_note, name='contact_add_note'),
    path('contacts/<int:pk>/delete/', views.contact_delete, name='contact_delete'),
    path('contacts/create/<int:company_id>/', views.ContactCreateView.as_view(), name='contact_create'),
    path('company/<int:company_id>/update-invoice-references/', views.update_invoice_references, name='update_invoice_references'),
    path('company/<int:company_id>/relationships/', views.manage_company_relationships, name='manage_company_relationships'),
    path('company/relationship/<int:relationship_id>/delete/', views.delete_company_relationship, name='delete_company_relationship'),
    
    # Document Management
    path('company/<int:company_id>/documents/upload/', views.document_upload, name='document_upload'),
    path('documents/<int:document_id>/delete/', views.document_delete, name='document_delete'),
    
    # Travel Policy Management
    path('company/<int:company_id>/travel-policy/create/', views.travel_policy_create, name='travel_policy_create'),
    path('travel-policy/<int:policy_id>/', views.travel_policy_detail, name='travel_policy_detail'),
    path('travel-policy/<int:policy_id>/update/', views.travel_policy_update, name='travel_policy_update'),
    path('travel-policy/<int:policy_id>/delete/', views.travel_policy_delete, name='travel_policy_delete'),
    
    # Activity Logging
    path('companies/<int:company_id>/log-activity/<str:activity_type>/', views.log_activity, name='log_activity'),
    path('contacts/<int:contact_id>/log-activity/<str:activity_type>/', views.log_contact_activity, name='log_contact_activity'),
    path('activity/<int:activity_id>/details/', views.get_activity_details, name='activity_details'),
    path('activity/<int:activity_id>/edit/', views.edit_activity, name='edit_activity'),
    path('activity/<int:activity_id>/delete/', views.delete_activity, name='delete_activity'),
    
    # HubSpot Integration
    path('hubspot/search/', views.hubspot_search, name='hubspot_search'),
    path('hubspot/company/<str:hubspot_id>/', views.hubspot_company_detail, name='hubspot_company_detail'),
    path('hubspot/import/<str:hubspot_id>/', views.import_hubspot_company, name='import_hubspot_company'),
    path('hubspot/api-test/', views.hubspot_api_test, name='hubspot_api_test'),
    path('hubspot/setup-guide/', views.hubspot_setup_guide, name='hubspot_setup_guide'),
]
    