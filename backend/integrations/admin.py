from django.contrib import admin
from .models import (
    IntegrationProvider, UserIntegration, IntegrationWebhook,
    IntegrationLog, IntegrationTemplate, IntegrationSync
)


@admin.register(IntegrationProvider)
class IntegrationProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'auth_type', 'is_active', 'is_popular', 'created_at')
    list_filter = ('category', 'auth_type', 'is_active', 'is_popular', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'is_active', 'is_popular')
        }),
        ('URLs', {
            'fields': ('website_url', 'logo_url', 'documentation_url')
        }),
        ('Authentication', {
            'fields': ('auth_type', 'client_id', 'client_secret', 'auth_url', 'token_url', 'scopes')
        }),
        ('API Configuration', {
            'fields': ('base_url', 'api_version', 'features')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserIntegration)
class UserIntegrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'external_name', 'status', 'last_sync_at', 'created_at')
    list_filter = ('provider', 'status', 'created_at', 'last_sync_at')
    search_fields = ('user__email', 'provider__name', 'external_name', 'external_email')
    readonly_fields = ('access_token', 'refresh_token', 'api_calls_count', 'created_at', 'updated_at')


@admin.register(IntegrationWebhook)
class IntegrationWebhookAdmin(admin.ModelAdmin):
    list_display = ('integration', 'webhook_url', 'is_active', 'last_received_at', 'created_at')
    list_filter = ('is_active', 'created_at', 'last_received_at')
    search_fields = ('integration__provider__name', 'webhook_url')


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ('integration', 'log_type', 'message', 'is_error', 'created_at')
    list_filter = ('log_type', 'is_error', 'created_at')
    search_fields = ('integration__provider__name', 'message')
    readonly_fields = ('created_at',)


@admin.register(IntegrationTemplate)
class IntegrationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'is_recommended', 'usage_count', 'created_at')
    list_filter = ('provider', 'is_recommended', 'created_at')
    search_fields = ('name', 'description', 'provider__name')
    readonly_fields = ('usage_count', 'created_at')


@admin.register(IntegrationSync)
class IntegrationSyncAdmin(admin.ModelAdmin):
    list_display = ('integration', 'sync_type', 'status', 'items_processed', 'started_at', 'completed_at')
    list_filter = ('sync_type', 'status', 'started_at')
    search_fields = ('integration__provider__name', 'sync_type')
    readonly_fields = ('started_at', 'created_at')