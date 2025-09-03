from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class EventType(models.Model):
    """Event types that users can create for scheduling"""
    
    DURATION_CHOICES = [
        (15, '15 minutes'),
        (30, '30 minutes'),
        (45, '45 minutes'),
        (60, '1 hour'),
        (90, '1.5 hours'),
        (120, '2 hours'),
        (180, '3 hours'),
    ]
    
    LOCATION_CHOICES = [
        ('zoom', 'Zoom'),
        ('google_meet', 'Google Meet'),
        ('microsoft_teams', 'Microsoft Teams'),
        ('phone', 'Phone Call'),
        ('in_person', 'In Person'),
        ('custom', 'Custom'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_types')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.IntegerField(choices=DURATION_CHOICES, default=30)
    location_type = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='zoom')
    location_details = models.TextField(blank=True, help_text="Additional location information")
    
    # Scheduling settings
    buffer_time_before = models.IntegerField(default=0, help_text="Buffer time before meeting (minutes)")
    buffer_time_after = models.IntegerField(default=0, help_text="Buffer time after meeting (minutes)")
    max_bookings_per_day = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(50)])
    
    # Booking settings
    min_notice_time = models.IntegerField(default=60, help_text="Minimum notice time in minutes")
    max_advance_time = models.IntegerField(default=10080, help_text="Maximum advance booking time in minutes (default: 1 week)")
    
    # Customization
    color = models.CharField(max_length=7, default='#1D9CA4', help_text="Hex color code")
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    
    # Questions for invitees
    custom_questions = models.JSONField(default=list, blank=True, help_text="Custom questions for invitees")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} ({self.duration} min) - {self.user.full_name}"

    @property
    def total_duration_with_buffer(self):
        """Total duration including buffer times"""
        return self.duration + self.buffer_time_before + self.buffer_time_after


class EventTypeAvailability(models.Model):
    """Custom availability for specific event types"""
    
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='custom_availability')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['event_type', 'weekday', 'start_time', 'end_time']
        ordering = ['weekday', 'start_time']

    def __str__(self):
        weekday_name = dict(self.WEEKDAY_CHOICES)[self.weekday]
        return f"{self.event_type.name} - {weekday_name} {self.start_time}-{self.end_time}"


class BookingPage(models.Model):
    """Customizable booking page for event types"""
    
    event_type = models.OneToOneField(EventType, on_delete=models.CASCADE, related_name='booking_page')
    
    # Page customization
    welcome_message = models.TextField(blank=True)
    thank_you_message = models.TextField(blank=True)
    
    # Branding
    logo = models.ImageField(upload_to='booking_logos/', blank=True, null=True)
    background_color = models.CharField(max_length=7, default='#FFFFFF')
    text_color = models.CharField(max_length=7, default='#000000')
    accent_color = models.CharField(max_length=7, default='#1D9CA4')
    
    # SEO
    page_title = models.CharField(max_length=100, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Settings
    show_event_details = models.BooleanField(default=True)
    show_organizer_info = models.BooleanField(default=True)
    require_confirmation = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking page for {self.event_type.name}"