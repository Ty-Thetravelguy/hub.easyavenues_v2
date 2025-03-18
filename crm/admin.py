from django.contrib import admin
from .models import Company, Contact, ClientProfile, SupplierProfile, ClientInvoiceReference, CompanyRelationship

# Register your models here.

@admin.register(CompanyRelationship)
class CompanyRelationshipAdmin(admin.ModelAdmin):
    list_display = ('from_company', 'relationship_type', 'to_company', 'established_date', 'is_active')
    list_filter = ('relationship_type', 'is_active', 'established_date')
    search_fields = ('from_company__company_name', 'to_company__company_name', 'description')
    date_hierarchy = 'established_date'
    raw_id_fields = ('from_company', 'to_company', 'created_by')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "to_company":
            kwargs["queryset"] = Company.objects.all().order_by('company_name')
        if db_field.name == "from_company":
            kwargs["queryset"] = Company.objects.all().order_by('company_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
