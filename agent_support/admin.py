from django.contrib import admin
from .models import AgentSupportSupplier

@admin.register(AgentSupportSupplier)
class AgentSupportSupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_name', 'supplier_type', 'has_scribe_content']
    search_fields = ['supplier_name']
    
    fieldsets = (
        (None, {
            'fields': ('supplier_name', 'supplier_type')
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'general_email', 'group_phone', 'group_email')
        }),
        ('Account Manager', {
            'fields': ('account_manager_name', 'account_manager_email', 'account_manager_phone')
        }),
        ('Additional Information', {
            'fields': ('agent_websites', 'other_notes')
        }),
        ('Scribe Content', {
            'fields': ('scribe_html',),
            'classes': ('wide',)
        }),
    )

    def has_scribe_content(self, obj):
        return bool(obj.scribe_html)
    has_scribe_content.boolean = True
    has_scribe_content.short_description = "Has Scribe Content"
