from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.CompanyListView.as_view(), name='company_list'),
    path('company/create/', views.CompanyCreateWizardView.as_view(), name='company_create'),
    path('company/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('company/<int:pk>/update/', views.CompanyUpdateView.as_view(), name='company_update'),
    path('company/<int:company_pk>/contact/create/', views.ContactCreateView.as_view(), name='contact_create'),
]
    