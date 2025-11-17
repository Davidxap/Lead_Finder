# leads/admin.py
from django.contrib import admin
from django.utils.html import format_html
from typing import Any
from .models import Lead, LeadList, LeadListItem


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Admin interface for Lead model."""
    
    list_display = [
        'full_name',
        'current_title',
        'current_company',
        'location_display',
        'email_display',
        'linkedin_display',
        'created_at',
    ]
    
    list_filter = [
        'seniority_level',
        'country',
        'industry',
        'created_at',
    ]
    
    search_fields = [
        'first_name',
        'last_name',
        'full_name',
        'email',
        'current_company',
        'location',
    ]
    
    readonly_fields = [
        'external_id',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'first_name',
                'last_name',
                'full_name',
            )
        }),
        ('Contact Information', {
            'fields': (
                'email',
                'phone',
                'linkedin_url',
                'photo_url',
            )
        }),
        ('Professional Information', {
            'fields': (
                'current_title',
                'current_company',
                'company_linkedin_url',
                'headline',
                'seniority_level',
            )
        }),
        ('Location', {
            'fields': (
                'location',
                'country',
            )
        }),
        ('Company Details', {
            'fields': (
                'industry',
                'company_size',
            )
        }),
        ('Additional Information', {
            'fields': (
                'skills',
                'bio',
            )
        }),
        ('Metadata', {
            'fields': (
                'external_id',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def location_display(self, obj: Lead) -> str:
        """Display location with country"""
        if obj.country:
            return f"{obj.location}, {obj.country}"
        return obj.location
    
    def email_display(self, obj: Lead) -> str:
        """Display email as link"""
        if obj.email:
            return format_html(
                '<a href="mailto:{}">{}</a>',
                obj.email,
                obj.email
            )
        return '-'
    
    def linkedin_display(self, obj: Lead) -> str:
        """Display LinkedIn as clickable link"""
        if obj.linkedin_url:
            return format_html(
                '<a href="https://{}" target="_blank">View Profile</a>',
                obj.linkedin_url
            )
        return '-'


# Set display names manually (workaround for type checkers)
if hasattr(LeadAdmin.location_display, '__func__'):
    LeadAdmin.location_display.__func__.short_description = 'Location'  # type: ignore
if hasattr(LeadAdmin.email_display, '__func__'):
    LeadAdmin.email_display.__func__.short_description = 'Email'  # type: ignore
if hasattr(LeadAdmin.linkedin_display, '__func__'):
    LeadAdmin.linkedin_display.__func__.short_description = 'LinkedIn'  # type: ignore


@admin.register(LeadList)
class LeadListAdmin(admin.ModelAdmin):
    """Admin interface for LeadList model."""
    
    list_display = [
        'name',
        'lead_count_display',
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'name',
        'description',
    ]
    
    readonly_fields = [
        'slug',
        'created_at',
        'updated_at',
        'lead_count_display',
    ]
    
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'slug',
            )
        }),
        ('Statistics', {
            'fields': (
                'lead_count_display',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def lead_count_display(self, obj: LeadList) -> str:
        """Display number of leads"""
        count = obj.get_lead_count()
        return f"{count} lead{'s' if count != 1 else ''}"


if hasattr(LeadListAdmin.lead_count_display, '__func__'):
    LeadListAdmin.lead_count_display.__func__.short_description = 'Total Leads'  # type: ignore


@admin.register(LeadListItem)
class LeadListItemAdmin(admin.ModelAdmin):
    """Admin interface for LeadListItem model."""
    
    list_display = [
        'lead_display',
        'lead_list',
        'added_at',
    ]
    
    list_filter = [
        'lead_list',
        'added_at',
    ]
    
    search_fields = [
        'lead__first_name',
        'lead__last_name',
        'lead__email',
        'lead_list__name',
    ]
    
    readonly_fields = [
        'added_at',
    ]
    
    def lead_display(self, obj: LeadListItem) -> str:
        """Display lead name and company"""
        return f"{obj.lead.get_full_name()} ({obj.lead.current_company})"


if hasattr(LeadListItemAdmin.lead_display, '__func__'):
    LeadListItemAdmin.lead_display.__func__.short_description = 'Lead'  # type: ignore