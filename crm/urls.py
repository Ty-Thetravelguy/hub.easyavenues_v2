from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('companies/<int:pk>/update/', views.CompanyUpdateView.as_view(), name='company_update'),
    path('companies/create/', views.CompanyCreateWizardView.as_view(), name='company_create'),
    path('companies/<int:company_id>/contacts/create/', views.ContactCreateView.as_view(), name='contact_create'),
    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact_detail'),
    path('contacts/<int:pk>/update/', views.ContactUpdateView.as_view(), name='contact_update'),
    path('contacts/<int:pk>/add-note/', views.contact_add_note, name='contact_add_note'),
    path('contacts/create/<int:company_id>/', views.ContactCreateView.as_view(), name='contact_create'),
    path('company/<int:company_id>/update-invoice-references/', views.update_invoice_references, name='update_invoice_references'),
    path('company/<int:company_id>/relationships/', views.manage_company_relationships, name='manage_company_relationships'),
    path('company/relationship/<int:relationship_id>/delete/', views.delete_company_relationship, name='delete_company_relationship'),
    
    # HubSpot Integration
    path('hubspot/search/', views.hubspot_search, name='hubspot_search'),
    path('hubspot/company/<str:hubspot_id>/', views.hubspot_company_detail, name='hubspot_company_detail'),
    path('hubspot/import/<str:hubspot_id>/', views.import_hubspot_company, name='import_hubspot_company'),
    path('hubspot/api-test/', views.hubspot_api_test, name='hubspot_api_test'),
    path('hubspot/setup-guide/', views.hubspot_setup_guide, name='hubspot_setup_guide'),
]
    