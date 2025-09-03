from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Workflow(models.Model):
    """Automated workflows for meeting-related actions"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('draft', 'Draft'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflows')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Workflow configuration
    trigger_type = models.CharField(max_length=50)  # e.g., 'meeting_created', 'meeting_cancelled'
    trigger_conditions = models.JSONField(default=dict, help_text="Conditions for triggering the workflow")
    
    # Actions to perform
    actions = models.JSONField(default=list, help_text="List of actions to perform")
    
    # Status and settings
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    
    # Statistics
    execution_count = models.PositiveIntegerField(default=0)
    last_executed_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.full_name})"


class WorkflowExecution(models.Model):
    """Track workflow executions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='executions')
    
    # Trigger information
    trigger_data = models.JSONField(default=dict, help_text="Data that triggered the workflow")
    
    # Execution details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Results
    actions_completed = models.PositiveIntegerField(default=0)
    actions_failed = models.PositiveIntegerField(default=0)
    execution_log = models.JSONField(default=list, help_text="Log of execution steps")
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.workflow.name} execution - {self.status}"


class WorkflowTemplate(models.Model):
    """Pre-built workflow templates"""
    
    CATEGORY_CHOICES = [
        ('meeting', 'Meeting Management'),
        ('notification', 'Notifications'),
        ('integration', 'Integrations'),
        ('automation', 'Automation'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Template configuration
    trigger_type = models.CharField(max_length=50)
    trigger_conditions = models.JSONField(default=dict)
    actions = models.JSONField(default=list)
    
    # Template metadata
    is_popular = models.BooleanField(default=False)
    usage_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_popular', 'name']

    def __str__(self):
        return self.name


class WorkflowAction(models.Model):
    """Available workflow actions"""
    
    ACTION_TYPES = [
        ('send_email', 'Send Email'),
        ('send_sms', 'Send SMS'),
        ('create_calendar_event', 'Create Calendar Event'),
        ('send_slack_message', 'Send Slack Message'),
        ('webhook', 'Webhook'),
        ('delay', 'Delay'),
        ('conditional', 'Conditional'),
    ]
    
    name = models.CharField(max_length=100)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    
    # Configuration schema
    config_schema = models.JSONField(default=dict, help_text="JSON schema for action configuration")
    
    # Integration requirements
    requires_integration = models.CharField(max_length=50, blank=True, help_text="Required integration type")
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkflowTrigger(models.Model):
    """Available workflow triggers"""
    
    TRIGGER_TYPES = [
        ('meeting_created', 'Meeting Created'),
        ('meeting_updated', 'Meeting Updated'),
        ('meeting_cancelled', 'Meeting Cancelled'),
        ('meeting_completed', 'Meeting Completed'),
        ('meeting_reminder', 'Meeting Reminder'),
        ('contact_created', 'Contact Created'),
        ('event_type_booked', 'Event Type Booked'),
        ('schedule', 'Scheduled'),
    ]
    
    name = models.CharField(max_length=100)
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    description = models.TextField()
    
    # Configuration schema
    config_schema = models.JSONField(default=dict, help_text="JSON schema for trigger configuration")
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name