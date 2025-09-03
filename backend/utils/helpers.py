from django.utils import timezone
from datetime import datetime, timedelta
import uuid
import secrets
import string


def generate_confirmation_token():
    """Generate a secure confirmation token"""
    return str(uuid.uuid4())


def generate_meeting_id():
    """Generate a unique meeting ID"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))


def generate_api_key():
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def format_duration(minutes):
    """Format duration in minutes to human readable format"""
    if minutes < 60:
        return f"{minutes} min"
    elif minutes == 60:
        return "1 hour"
    elif minutes % 60 == 0:
        hours = minutes // 60
        return f"{hours} hours"
    else:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"


def get_time_slots(start_time, end_time, duration_minutes, buffer_minutes=0):
    """Generate available time slots between start and end time"""
    slots = []
    current_time = start_time
    slot_duration = timedelta(minutes=duration_minutes + buffer_minutes)
    
    while current_time + timedelta(minutes=duration_minutes) <= end_time:
        slots.append({
            'start_time': current_time,
            'end_time': current_time + timedelta(minutes=duration_minutes)
        })
        current_time += slot_duration
    
    return slots


def is_business_day(date):
    """Check if date is a business day (Monday-Friday)"""
    return date.weekday() < 5


def get_next_business_day(date):
    """Get the next business day after the given date"""
    next_day = date + timedelta(days=1)
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
    return next_day


def convert_timezone(dt, from_tz, to_tz):
    """Convert datetime from one timezone to another"""
    import pytz
    
    if isinstance(from_tz, str):
        from_tz = pytz.timezone(from_tz)
    if isinstance(to_tz, str):
        to_tz = pytz.timezone(to_tz)
    
    # Localize if naive
    if dt.tzinfo is None:
        dt = from_tz.localize(dt)
    
    return dt.astimezone(to_tz)


def get_user_local_time(user, dt=None):
    """Get current time or specific datetime in user's timezone"""
    if dt is None:
        dt = timezone.now()
    
    user_tz = user.timezone
    return convert_timezone(dt, 'UTC', str(user_tz))


def validate_meeting_time_slot(start_time, end_time, user, exclude_meeting_id=None):
    """Validate that a meeting time slot doesn't conflict with existing meetings"""
    from meetings.models import Meeting
    
    conflicts = Meeting.objects.filter(
        organizer=user,
        status__in=['confirmed', 'pending'],
        start_time__lt=end_time,
        end_time__gt=start_time
    )
    
    if exclude_meeting_id:
        conflicts = conflicts.exclude(id=exclude_meeting_id)
    
    return not conflicts.exists()


def send_notification_email(user, subject, message, html_content=None):
    """Send notification email to user"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def create_calendar_event_data(meeting):
    """Create calendar event data from meeting object"""
    return {
        'summary': meeting.title,
        'description': meeting.description,
        'start': {
            'dateTime': meeting.start_time.isoformat(),
            'timeZone': meeting.timezone,
        },
        'end': {
            'dateTime': meeting.end_time.isoformat(),
            'timeZone': meeting.timezone,
        },
        'attendees': [
            {'email': meeting.invitee_email, 'displayName': meeting.invitee_name},
            {'email': meeting.organizer.email, 'displayName': meeting.organizer.full_name}
        ],
        'location': meeting.location_details,
        'conferenceData': {
            'createRequest': {
                'requestId': meeting.meeting_id or generate_meeting_id()
            }
        } if meeting.location_type in ['zoom', 'google_meet'] else None
    }


def parse_custom_questions(questions_json):
    """Parse and validate custom questions JSON"""
    if not questions_json:
        return []
    
    if isinstance(questions_json, str):
        import json
        try:
            questions_json = json.loads(questions_json)
        except json.JSONDecodeError:
            return []
    
    if not isinstance(questions_json, list):
        return []
    
    parsed_questions = []
    for question in questions_json:
        if isinstance(question, dict) and 'question' in question:
            parsed_questions.append({
                'question': question['question'],
                'type': question.get('type', 'text'),
                'required': question.get('required', False),
                'options': question.get('options', [])
            })
    
    return parsed_questions


def get_available_time_zones():
    """Get list of common time zones"""
    import pytz
    
    common_timezones = [
        'UTC',
        'US/Eastern',
        'US/Central',
        'US/Mountain',
        'US/Pacific',
        'Europe/London',
        'Europe/Paris',
        'Europe/Berlin',
        'Asia/Tokyo',
        'Asia/Shanghai',
        'Asia/Kolkata',
        'Australia/Sydney',
        'America/New_York',
        'America/Chicago',
        'America/Denver',
        'America/Los_Angeles',
    ]
    
    return [(tz, tz.replace('_', ' ')) for tz in common_timezones]