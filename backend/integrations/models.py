from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class IntegrationProvider(models.Model):
    """Available integration providers"""
    
    CATEGORY_CHOICES = [
        ('calendar', 'Calendar'),
        ('video', 'Video Conferencing'),
        ('communication', 'Communication'),
        ('crm', 'CRM'),
        ('productivity', 'Productivity'),
        ('automation', 'Automation'),
        ('payment', 'Payment'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    
    # Provider details
    website_url = models.URLField()
    logo_url = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)
    
    # Integration configuration
    auth_type = models.CharField(max_length=20, choices=[
        ('oauth2', 'OAuth 2.0'),
        ('api_key', 'API Key'),
        ('webhook', 'Webhook'),
        ('custom', 'Custom'),
    ], default='oauth2')
    
    # OAuth configuration
    client_id = models.CharField(max_length=255, blank=True)
    client_secret = models.CharField(max_length=255, blank=True)
    auth_url = models.URLField(blank=True)
    token_url = models.URLField(blank=True)
    scopes = models.JSONField(default=list, help_text="Required OAuth scopes")
    
    # API configuration
    base_url = models.URLField(blank=True)
    api_version = models.CharField(max_length=20, blank=True)
    
    # Features
    features = models.JSONField(default=list, help_text="List of supported features")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_popular', 'name']

    def __str__(self):
        return self.name


class UserIntegration(models.Model):
    """User's connected integrations"""
    
    STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integrations')
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE)
    
    # Connection details
    external_id = models.CharField(max_length=255, blank=True, help_text="External account ID")
    external_email = models.EmailField(blank=True)
    external_name = models.CharField(max_length=255, blank=True)
    
    # Authentication
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True)
    
    # Configuration
    settings = models.JSONField(default=dict, help_text="Integration-specific settings")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='connected')
    last_sync_at = models.DateTimeField(blank=True, null=True)
    sync_error_message = models.TextField(blank=True)
    
    # Usage statistics
    api_calls_count = models.PositiveIntegerField(default=0)
    last_api_call_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'provider']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.provider.name}"

    @property
    def is_token_expired(self):
        """Check if the access token is expired"""
        if not self.token_expires_at:
            return False
        from django.utils import timezone
        return timezone.now() >= self.token_expires_at


class IntegrationWebhook(models.Model):
    """Webhook endpoints for integrations"""
    
    integration = models.ForeignKey(UserIntegration, on_delete=models.CASCADE, related_name='webhooks')
    
    # Webhook details
    webhook_url = models.URLField()
    webhook_secret = models.CharField(max_length=255, blank=True)
    events = models.JSONField(default=list, help_text="List of events to listen for")
    
    # Status
    is_active = models.BooleanField(default=True)
    last_received_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Webhook for {self.integration}"


class IntegrationLog(models.Model):
    """Log of integration activities"""
    
    LOG_TYPES = [
        ('auth', 'Authentication'),
        ('api_call', 'API Call'),
        ('webhook', 'Webhook'),
        ('sync', 'Sync'),
        ('error', 'Error'),
    ]
    
    integration = models.ForeignKey(UserIntegration, on_delete=models.CASCADE, related_name='logs')
    
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    
    # Request/Response data (for debugging)
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    
    # Status
    is_error = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.integration} - {self.get_log_type_display()}"


class IntegrationTemplate(models.Model):
    """Pre-configured integration templates"""
    
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE, related_name='templates')
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Template configuration
    default_settings = models.JSONField(default=dict)
    required_scopes = models.JSONField(default=list)
    
    # Usage
    usage_count = models.PositiveIntegerField(default=0)
    is_recommended = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_recommended', 'name']

    def __str__(self):
        return f"{self.provider.name} - {self.name}"


class IntegrationSync(models.Model):
    """Track synchronization jobs"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    integration = models.ForeignKey(UserIntegration, on_delete=models.CASCADE, related_name='sync_jobs')
    
    sync_type = models.CharField(max_length=50, help_text="Type of sync (e.g., 'calendar_events', 'contacts')")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Results
    items_processed = models.PositiveIntegerField(default=0)
    items_created = models.PositiveIntegerField(default=0)
    items_updated = models.PositiveIntegerField(default=0)
    items_failed = models.PositiveIntegerField(default=0)
    
    # Error handling
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.integration} - {self.sync_type} ({self.status})"