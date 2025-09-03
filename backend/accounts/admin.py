from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'created_at', 'timezone')
    search_fields = ('email', 'first_name', 'last_name', 'company')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Personal Info', {
            'fields': ('profile_picture', 'timezone', 'phone_number', 'company', 'job_title', 'bio', 'website')
        }),
        ('Scheduling Preferences', {
            'fields': ('default_meeting_duration', 'buffer_time_before', 'buffer_time_after')
        }),
        ('Notification Settings', {
            'fields': ('is_email_verified', 'email_notifications', 'sms_notifications')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_format', 'time_format', 'week_start', 'created_at')
    list_filter = ('date_format', 'time_format', 'week_start', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')