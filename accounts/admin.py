# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Business, BusinessDomain

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
    list_display = ('email', 'first_name', 'last_name', 'business', 'is_active', 'date_joined')
    list_filter = ('is_active', 'business', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
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