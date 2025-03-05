from django.urls import path
from . import views

app_name = 'agent_support'

urlpatterns = [
    path('', views.agent_support_view, name='agent_support_view'),
    path('supplier-contacts/', views.supplier_contacts, name='supplier_contacts'),
    path('add-supplier/', views.add_agent_supplier, name='add_agent_supplier'),
    path('edit-supplier/<int:pk>/', views.edit_agent_supplier, name='edit_agent_supplier'),
    path('delete-supplier/<int:supplier_id>/', views.delete_agent_supplier, name='delete_agent_supplier'),
    path('add-attachment/<int:supplier_id>/', views.add_attachment, name='add_attachment'),
    path('delete-attachment/<int:pk>/', views.delete_attachment, name='delete_attachment'),
]