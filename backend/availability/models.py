from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from timezone_field import TimeZoneField

User = get_user_model()


class WeeklyAvailability(models.Model):
    """User's weekly availability schedule"""
    
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_availability')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'weekday', 'start_time', 'end_time']
        ordering = ['weekday', 'start_time']

    def __str__(self):
        weekday_name = dict(self.WEEKDAY_CHOICES)[self.weekday]
        status = "Available" if self.is_available else "Unavailable"
        return f"{self.user.full_name} - {weekday_name} {self.start_time}-{self.end_time} ({status})"


class DateOverride(models.Model):
    """Override availability for specific dates"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='date_overrides')
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    is_available = models.BooleanField(default=False)
    reason = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date', 'start_time', 'end_time']
        ordering = ['date', 'start_time']

    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        if self.start_time and self.end_time:
            return f"{self.user.full_name} - {self.date} {self.start_time}-{self.end_time} ({status})"
        return f"{self.user.full_name} - {self.date} ({status})"


class BufferTime(models.Model):
    """Buffer time settings for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buffer_time')
    
    # Buffer times in minutes
    before_meeting = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Buffer time before meetings (minutes)"
    )
    after_meeting = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Buffer time after meetings (minutes)"
    )
    
    # Lunch break
    lunch_break_enabled = models.BooleanField(default=False)
    lunch_start_time = models.TimeField(blank=True, null=True)
    lunch_end_time = models.TimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Buffer settings for {self.user.full_name}"


class TimeZoneSettings(models.Model):
    """Time zone settings for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='timezone_settings')
    timezone = TimeZoneField(default='UTC')
    auto_detect = models.BooleanField(default=True, help_text="Auto-detect timezone from browser")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Timezone settings for {self.user.full_name} - {self.timezone}"


class CalendarIntegration(models.Model):
    """Calendar integration settings"""
    
    PROVIDER_CHOICES = [
        ('google', 'Google Calendar'),
        ('outlook', 'Outlook Calendar'),
        ('apple', 'Apple Calendar'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendar_integrations')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    calendar_id = models.CharField(max_length=255)
    calendar_name = models.CharField(max_length=100)
    
    # Integration settings
    is_primary = models.BooleanField(default=False)
    sync_enabled = models.BooleanField(default=True)
    check_conflicts = models.BooleanField(default=True)
    
    # OAuth tokens (encrypted in production)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    
    # Sync status
    last_sync_at = models.DateTimeField(blank=True, null=True)
    sync_status = models.CharField(max_length=20, default='active', choices=[
        ('active', 'Active'),
        ('error', 'Error'),
        ('disabled', 'Disabled'),
    ])
    sync_error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'provider', 'calendar_id']

    def __str__(self):
        return f"{self.user.full_name} - {self.get_provider_display()} ({self.calendar_name})"


class AvailabilityRule(models.Model):
    """Advanced availability rules"""
    
    RULE_TYPE_CHOICES = [
        ('minimum_notice', 'Minimum Notice Time'),
        ('maximum_advance', 'Maximum Advance Booking'),
        ('daily_limit', 'Daily Meeting Limit'),
        ('weekly_limit', 'Weekly Meeting Limit'),
        ('time_between_meetings', 'Time Between Meetings'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_rules')
    rule_type = models.CharField(max_length=30, choices=RULE_TYPE_CHOICES)
    
    # Rule parameters (stored as JSON for flexibility)
    parameters = models.JSONField(default=dict)
    
    # Rule conditions
    applies_to_event_types = models.ManyToManyField('events.EventType', blank=True)
    applies_to_weekdays = models.JSONField(default=list, help_text="List of weekday numbers (0=Monday)")
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rule_type']

    def __str__(self):
        return f"{self.user.full_name} - {self.get_rule_type_display()}"