from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.CompanyListView.as_view(), name='company_list'),
    path('company/create/', views.CompanyCreateWizardView.as_view(), name='company_create'),
    path('company/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('company/<int:pk>/update/', views.CompanyUpdateView.as_view(), name='company_update'),
    path('company/<int:company_pk>/contact/create/', views.ContactCreateView.as_view(), name='contact_create'),
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
    