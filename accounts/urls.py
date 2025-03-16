# account/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='account_signup'),
    
    # Admin section
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:user_id>/toggle-active/', views.admin_toggle_user_active, name='admin_toggle_user_active'),
    
    # Team management
    path('admin/teams/', views.admin_team_list, name='admin_team_list'),
    path('admin/teams/create/', views.admin_team_create, name='admin_team_create'),
    path('admin/teams/<int:team_id>/edit/', views.admin_team_edit, name='admin_team_edit'),
    path('admin/teams/<int:team_id>/members/', views.admin_team_members, name='admin_team_members'),
    path('admin/teams/<int:team_id>/delete/', views.admin_team_delete, name='admin_team_delete'),

    # Admin Invoice Remarks
    path('admin/invoice-remarks/', views.admin_invoice_remark_list, name='admin_invoice_remark_list'),
    path('admin/invoice-remarks/create/', views.admin_invoice_remark_create, name='admin_invoice_remark_create'),
    path('admin/invoice-remarks/<int:remark_id>/edit/', views.admin_invoice_remark_edit, name='admin_invoice_remark_edit'),
    path('admin/invoice-remarks/<int:remark_id>/delete/', views.admin_invoice_remark_delete, name='admin_invoice_remark_delete'),
]
