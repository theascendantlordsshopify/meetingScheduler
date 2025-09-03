from django.contrib import admin
from .models import (
    NotificationTemplate, Notification, NotificationPreference,
    NotificationQueue, NotificationBatch
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'channel', 'is_active', 'is_system_template', 'created_at')
    list_filter = ('template_type', 'channel', 'is_active', 'is_system_template', 'created_at')
    search_fields = ('name', 'subject', 'body_template')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'category', 'priority', 'status', 'channel', 'created_at')
    list_filter = ('category', 'priority', 'status', 'channel', 'created_at')
    search_fields = ('title', 'message', 'recipient__email', 'recipient__first_name', 'recipient__last_name')
    readonly_fields = ('sent_at', 'delivered_at', 'read_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('recipient', 'template', 'title', 'message', 'html_content')
        }),
        ('Classification', {
            'fields': ('category', 'priority', 'channel')
        }),
        ('Delivery', {
            'fields': ('status', 'scheduled_at', 'sent_at', 'delivered_at', 'read_at')
        }),
        ('Related Objects', {
            'fields': ('meeting', 'event_type', 'metadata')
        }),
        ('Error Handling', {
            'fields': ('error_message', 'retry_count', 'max_retries')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_enabled', 'sms_enabled', 'in_app_enabled', 'push_enabled', 'created_at')
    list_filter = ('email_enabled', 'sms_enabled', 'in_app_enabled', 'push_enabled', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


@admin.register(NotificationQueue)
class NotificationQueueAdmin(admin.ModelAdmin):
    list_display = ('notification', 'attempts', 'next_attempt_at', 'priority_score', 'created_at')
    list_filter = ('attempts', 'next_attempt_at', 'created_at')
    search_fields = ('notification__title', 'notification__recipient__email')


@admin.register(NotificationBatch)
class NotificationBatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'total_recipients', 'sent_count', 'failed_count', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'created_by__email')
    filter_horizontal = ('recipients',)