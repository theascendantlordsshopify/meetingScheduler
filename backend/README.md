# MeetXccelerate Backend

A Django REST API backend for the MeetXccelerate scheduling platform.

## Features

- **User Management**: Custom user model with profiles and preferences
- **Event Types**: Create and manage different types of bookable events
- **Meetings**: Schedule, manage, and track meetings
- **Availability**: Set weekly schedules, buffer times, and date overrides
- **Contacts**: Manage contacts with tags, groups, and interactions
- **Workflows**: Automate actions based on meeting events
- **Integrations**: Connect with external services (Google Calendar, Zoom, Slack, etc.)
- **Notifications**: Comprehensive notification system with preferences

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database Setup**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py loaddata fixtures/initial_data.json
   ```

4. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `GET /api/auth/dashboard/stats/` - Dashboard statistics

### Event Types
- `GET /api/events/` - List event types
- `POST /api/events/` - Create event type
- `GET /api/events/{id}/` - Get event type details
- `PUT /api/events/{id}/` - Update event type
- `DELETE /api/events/{id}/` - Delete event type

### Meetings
- `GET /api/meetings/` - List meetings
- `POST /api/meetings/` - Create meeting
- `GET /api/meetings/{id}/` - Get meeting details
- `POST /api/meetings/{id}/confirm/` - Confirm meeting
- `POST /api/meetings/{id}/cancel/` - Cancel meeting

### Availability
- `GET /api/availability/weekly/` - Get weekly availability
- `POST /api/availability/weekly/` - Set weekly availability
- `GET /api/availability/overrides/` - Get date overrides
- `GET /api/availability/overview/` - Complete availability overview

### Contacts
- `GET /api/contacts/` - List contacts
- `POST /api/contacts/` - Create contact
- `GET /api/contacts/{id}/` - Get contact details
- `POST /api/contacts/bulk-import/` - Bulk import contacts

### Workflows
- `GET /api/workflows/` - List workflows
- `POST /api/workflows/` - Create workflow
- `GET /api/workflows/{id}/` - Get workflow details
- `POST /api/workflows/{id}/activate/` - Activate workflow

### Integrations
- `GET /api/integrations/providers/` - List integration providers
- `GET /api/integrations/` - List user integrations
- `POST /api/integrations/connect/` - Connect integration
- `POST /api/integrations/{id}/sync/` - Sync integration

### Notifications
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/unread/` - Get unread notifications
- `POST /api/notifications/{id}/read/` - Mark as read
- `POST /api/notifications/mark-all-read/` - Mark all as read

## Project Structure

```
backend/
├── meetxccelerate/          # Main project settings
├── accounts/                # User management
├── events/                  # Event types and booking pages
├── meetings/                # Meeting management
├── availability/            # Availability and scheduling
├── contacts/                # Contact management
├── workflows/               # Workflow automation
├── integrations/            # Third-party integrations
├── notifications/           # Notification system
├── api/                     # API utilities
├── utils/                   # Shared utilities
└── fixtures/                # Initial data

```

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Interface
Access the admin interface at `http://localhost:8000/admin/`

### API Documentation
API documentation will be available at `http://localhost:8000/api/docs/` (when DRF documentation is configured)

## Deployment

For production deployment:

1. Set `DEBUG=False` in settings
2. Configure a production database (PostgreSQL recommended)
3. Set up Redis for Celery
4. Configure email backend
5. Set up static file serving
6. Configure CORS for frontend domain

## Background Tasks

The project uses Celery for background tasks:

```bash
# Start Celery worker
celery -A meetxccelerate worker -l info

# Start Celery beat (for scheduled tasks)
celery -A meetxccelerate beat -l info
```

## Environment Variables

Key environment variables (see `.env.example`):

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `DATABASE_URL` - Database connection
- `CELERY_BROKER_URL` - Redis URL for Celery
- `EMAIL_HOST_USER` - Email configuration
- Integration API keys for Google, Zoom, Slack, etc.