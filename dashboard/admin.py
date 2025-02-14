# dashboard/admin.py

from django.contrib import admin
from .models import CompanyUpdate, UpdateAttachment

class UpdateAttachmentInline(admin.TabularInline):
    model = UpdateAttachment
    extra = 1

@admin.register(CompanyUpdate)
class CompanyUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'update_type', 'author', 'created_at')
    list_filter = ('update_type', 'created_at', 'author')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    inlines = [UpdateAttachmentInline]

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new object
            obj.author = request.user
        super().save_model(request, obj, form, change)
