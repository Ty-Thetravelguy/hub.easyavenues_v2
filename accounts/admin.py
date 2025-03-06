# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Business, BusinessDomain
from users.models import RecentlyViewed, PageBookmark

class BusinessDomainInline(admin.TabularInline):
    model = BusinessDomain
    extra = 1  # Number of empty forms to display

class CustomUserInline(admin.TabularInline):
    model = CustomUser
    extra = 0
    fields = ('email', 'first_name', 'last_name', 'is_active')
    readonly_fields = ('email',)

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'main_contact', 'main_contact_email', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('business_name', 'main_contact', 'main_contact_email')
    inlines = [BusinessDomainInline, CustomUserInline]
    ordering = ('-created_at',)

@admin.register(BusinessDomain)
class BusinessDomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'business', 'active', 'created_at')
    list_filter = ('active', 'created_at', 'business')
    search_fields = ('domain', 'business__business_name')
    ordering = ('business', 'domain')

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'role')
    list_filter = ('is_staff', 'is_active', 'role')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    def view_on_site(self, obj):
        return '/'  # This will take you to the main site
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    def get_deleted_objects(self, objs, request):
        # Get the standard deleted objects
        deleted_objects, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        
        # Create a new list of deleted objects
        filtered_deleted = []
        
        # Only include items that are directly related to the user being deleted
        for obj in deleted_objects:
            # Skip if it's not a model instance
            if not hasattr(obj, '_meta'):
                continue
                
            if isinstance(obj, (RecentlyViewed, PageBookmark)):
                if obj.user in objs:
                    filtered_deleted.append(obj)
            else:
                filtered_deleted.append(obj)
        
        # Update model count to reflect filtered items
        model_count = {}
        for obj in filtered_deleted:
            if hasattr(obj, '_meta'):
                model_name = obj._meta.model_name
                model_count[model_name] = model_count.get(model_name, 0) + 1
        
        return filtered_deleted, model_count, perms_needed, protected

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'business')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'business'),
        }),
    )

    # These are the fields used for searching in admin
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)