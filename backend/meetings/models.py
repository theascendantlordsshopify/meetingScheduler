from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from events.models import EventType

User = get_user_model()


class Meeting(models.Model):
    """Meeting/Appointment model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    # Basic information
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='meetings')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings')
    
    # Meeting details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Location
    location_type = models.CharField(max_length=20, default='zoom')
    location_details = models.TextField(blank=True)
    meeting_url = models.URLField(blank=True, null=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    
    # Invitee information
    invitee_name = models.CharField(max_length=100)
    invitee_email = models.EmailField()
    invitee_phone = models.CharField(max_length=20, blank=True)
    invitee_timezone = models.CharField(max_length=50, default='UTC')
    
    # Custom responses
    custom_responses = models.JSONField(default=dict, blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmation_token = models.CharField(max_length=100, unique=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Notifications
    reminder_sent = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')} ({self.status})"

    @property
    def duration_minutes(self):
        """Duration of the meeting in minutes"""
        if self.end_time and self.start_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return self.event_type.duration

    @property
    def is_upcoming(self):
        """Check if the meeting is in the future"""
        return self.start_time > timezone.now()

    @property
    def is_today(self):
        """Check if the meeting is today"""
        return self.start_time.date() == timezone.now().date()

    def save(self, *args, **kwargs):
        # Generate confirmation token if not exists
        if not self.confirmation_token:
            import uuid
            self.confirmation_token = str(uuid.uuid4())
        
        # Set end time based on start time and duration
        if not self.end_time and self.start_time:
            from datetime import timedelta
            self.end_time = self.start_time + timedelta(minutes=self.event_type.duration)
        
        # Set cancellation timestamp
        if self.status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        
        super().save(*args, **kwargs)


class MeetingNote(models.Model):
    """Notes for meetings"""
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_private = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.meeting.title} by {self.author.full_name}"


class MeetingAttachment(models.Model):
    """File attachments for meetings"""
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='meeting_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} - {self.meeting.title}"

    def save(self, *args, **kwargs):
        if self.file:
            self.filename = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class MeetingRescheduleRequest(models.Model):
    """Reschedule requests for meetings"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='reschedule_requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # New proposed time
    new_start_time = models.DateTimeField()
    new_end_time = models.DateTimeField()
    reason = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Reschedule request for {self.meeting.title} - {self.status}"