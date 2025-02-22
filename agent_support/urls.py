from django.urls import path
from . import views

app_name = 'agent_support'

urlpatterns = [
    path('', views.agent_support_view, name='agent_support_view'),
    path('add-agent-supplier/', views.add_agent_supplier, name='add_agent_supplier'),
    path('edit/<int:supplier_id>/', views.edit_agent_supplier, name='edit_agent_supplier'),
    path('delete/<int:supplier_id>/', views.delete_agent_supplier, name='delete_agent_supplier'),
]