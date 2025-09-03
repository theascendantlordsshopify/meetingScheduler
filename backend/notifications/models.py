from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""
    
    TEMPLATE_TYPES = [
        ('meeting_confirmation', 'Meeting Confirmation'),
        ('meeting_reminder', 'Meeting Reminder'),
        ('meeting_cancellation', 'Meeting Cancellation'),
        ('meeting_reschedule', 'Meeting Reschedule'),
        ('system_alert', 'System Alert'),
        ('workflow_notification', 'Workflow Notification'),
    ]
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    
    # Template content
    subject = models.CharField(max_length=200, blank=True)
    body_template = models.TextField(help_text="Template with variables like {{user_name}}, {{meeting_title}}")
    html_template = models.TextField(blank=True, help_text="HTML version of the template")
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_system_template = models.BooleanField(default=False, help_text="System templates cannot be deleted")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['template_type', 'channel']
        ordering = ['template_type', 'channel']

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()} - {self.get_channel_display()})"


class Notification(models.Model):
    """Individual notifications sent to users"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    CATEGORY_CHOICES = [
        ('meeting_updates', 'Meeting Updates'),
        ('reminders', 'Reminders'),
        ('cancellations', 'Cancellations'),
        ('system_alerts', 'System Alerts'),
        ('workflow', 'Workflow'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Classification
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='system_alerts')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Delivery
    channel = models.CharField(max_length=20, choices=NotificationTemplate.CHANNEL_CHOICES, default='in_app')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Scheduling
    scheduled_at = models.DateTimeField(blank=True, null=True, help_text="When to send the notification")
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    # Related objects
    meeting = models.ForeignKey('meetings.Meeting', on_delete=models.CASCADE, blank=True, null=True)
    event_type = models.ForeignKey('events.EventType', on_delete=models.CASCADE, blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional data for the notification")
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['recipient', 'category']),
            models.Index(fields=['scheduled_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.full_name} ({self.status})"

    def mark_as_read(self):
        """Mark notification as read"""
        if self.status in ['sent', 'delivered']:
            self.status = 'read'
            self.read_at = timezone.now()
            self.save()

    @property
    def is_overdue(self):
        """Check if scheduled notification is overdue"""
        if self.scheduled_at and self.status == 'pending':
            from django.utils import timezone
            return timezone.now() > self.scheduled_at
        return False


class NotificationPreference(models.Model):
    """User preferences for notifications"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_meeting_confirmations = models.BooleanField(default=True)
    email_meeting_reminders = models.BooleanField(default=True)
    email_meeting_cancellations = models.BooleanField(default=True)
    email_system_alerts = models.BooleanField(default=True)
    email_workflow_notifications = models.BooleanField(default=True)
    
    # SMS preferences
    sms_enabled = models.BooleanField(default=False)
    sms_meeting_reminders = models.BooleanField(default=False)
    sms_urgent_alerts = models.BooleanField(default=False)
    
    # In-app preferences
    in_app_enabled = models.BooleanField(default=True)
    in_app_meeting_updates = models.BooleanField(default=True)
    in_app_system_alerts = models.BooleanField(default=True)
    
    # Push notification preferences
    push_enabled = models.BooleanField(default=True)
    push_meeting_reminders = models.BooleanField(default=True)
    push_urgent_alerts = models.BooleanField(default=True)
    
    # Timing preferences
    reminder_time_before = models.IntegerField(default=15, help_text="Minutes before meeting to send reminder")
    quiet_hours_start = models.TimeField(blank=True, null=True)
    quiet_hours_end = models.TimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification preferences for {self.user.full_name}"


class NotificationQueue(models.Model):
    """Queue for processing notifications"""
    
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, related_name='queue_item')
    
    # Processing
    attempts = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField()
    
    # Priority queue
    priority_score = models.IntegerField(default=0, help_text="Higher scores are processed first")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority_score', 'next_attempt_at']

    def __str__(self):
        return f"Queue item for {self.notification.title}"


class NotificationBatch(models.Model):
    """Batch notifications for bulk sending"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Recipients
    recipients = models.ManyToManyField(User, related_name='notification_batches')
    
    # Content
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_recipients = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    
    # Scheduling
    scheduled_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notification_batches')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status})"