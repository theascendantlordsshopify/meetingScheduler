from django.contrib.auth.models import AbstractUser
from django.db import models
from timezone_field import TimeZoneField


class User(AbstractUser):
    """Custom User model for MeetXccelerate"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    timezone = TimeZoneField(default='UTC')
    phone_number = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    # Scheduling preferences
    default_meeting_duration = models.IntegerField(default=30)  # in minutes
    buffer_time_before = models.IntegerField(default=0)  # in minutes
    buffer_time_after = models.IntegerField(default=0)  # in minutes
    
    # Account settings
    is_email_verified = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(models.Model):
    """Extended profile information for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Social links
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # Preferences
    date_format = models.CharField(max_length=20, default='MM/DD/YYYY')
    time_format = models.CharField(max_length=10, default='12h', choices=[('12h', '12 Hour'), ('24h', '24 Hour')])
    week_start = models.CharField(max_length=10, default='monday', choices=[
        ('monday', 'Monday'),
        ('sunday', 'Sunday'),
        ('saturday', 'Saturday')
    ])
    
    # Branding
    brand_color = models.CharField(max_length=7, default='#1D9CA4')  # Hex color
    custom_logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.full_name}"