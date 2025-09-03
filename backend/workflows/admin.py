from django.contrib import admin
from .models import Workflow, WorkflowExecution, WorkflowTemplate, WorkflowAction, WorkflowTrigger


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'trigger_type', 'status', 'execution_count', 'last_executed_at', 'created_at')
    list_filter = ('status', 'trigger_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'user__email')
    readonly_fields = ('execution_count', 'last_executed_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'status', 'is_active')
        }),
        ('Trigger Configuration', {
            'fields': ('trigger_type', 'trigger_conditions')
        }),
        ('Actions', {
            'fields': ('actions',)
        }),
        ('Statistics', {
            'fields': ('execution_count', 'last_executed_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'status', 'started_at', 'completed_at', 'actions_completed', 'actions_failed')
    list_filter = ('status', 'started_at', 'completed_at')
    search_fields = ('workflow__name', 'workflow__user__email')
    readonly_fields = ('started_at', 'created_at')


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'trigger_type', 'is_popular', 'usage_count', 'created_at')
    list_filter = ('category', 'trigger_type', 'is_popular', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('usage_count', 'created_at', 'updated_at')


@admin.register(WorkflowAction)
class WorkflowActionAdmin(admin.ModelAdmin):
    list_display = ('name', 'action_type', 'requires_integration', 'is_active', 'created_at')
    list_filter = ('action_type', 'requires_integration', 'is_active', 'created_at')
    search_fields = ('name', 'description')


@admin.register(WorkflowTrigger)
class WorkflowTriggerAdmin(admin.ModelAdmin):
    list_display = ('name', 'trigger_type', 'is_active', 'created_at')
    list_filter = ('trigger_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')