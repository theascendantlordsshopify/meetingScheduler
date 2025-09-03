from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time


def validate_future_datetime(value):
    """Validate that datetime is in the future"""
    if value <= timezone.now():
        raise ValidationError('Date and time must be in the future.')


def validate_business_hours(value):
    """Validate that time is within business hours (6 AM - 10 PM)"""
    if not isinstance(value, time):
        return
    
    start_time = time(6, 0)  # 6:00 AM
    end_time = time(22, 0)   # 10:00 PM
    
    if not (start_time <= value <= end_time):
        raise ValidationError('Time must be between 6:00 AM and 10:00 PM.')


def validate_meeting_duration(value):
    """Validate meeting duration is reasonable"""
    if value < 5:
        raise ValidationError('Meeting duration must be at least 5 minutes.')
    if value > 480:  # 8 hours
        raise ValidationError('Meeting duration cannot exceed 8 hours.')


def validate_buffer_time(value):
    """Validate buffer time is reasonable"""
    if value < 0:
        raise ValidationError('Buffer time cannot be negative.')
    if value > 120:  # 2 hours
        raise ValidationError('Buffer time cannot exceed 2 hours.')


def validate_hex_color(value):
    """Validate hex color format"""
    import re
    if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
        raise ValidationError('Enter a valid hex color code (e.g., #1D9CA4).')


def validate_timezone(value):
    """Validate timezone string"""
    import pytz
    try:
        pytz.timezone(value)
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValidationError('Enter a valid timezone.')


def validate_phone_number(value):
    """Basic phone number validation"""
    import re
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', value)
    
    if len(digits_only) < 10:
        raise ValidationError('Phone number must have at least 10 digits.')
    if len(digits_only) > 15:
        raise ValidationError('Phone number cannot have more than 15 digits.')


def validate_json_schema(value):
    """Validate that value is valid JSON"""
    import json
    try:
        json.loads(json.dumps(value))
    except (TypeError, ValueError):
        raise ValidationError('Enter valid JSON data.')