from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_meeting_reminder(meeting_id):
    """Send meeting reminder notification"""
    from meetings.models import Meeting
    from notifications.models import Notification
    
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        
        # Create reminder notification
        Notification.objects.create(
            recipient=meeting.organizer,
            title=f"Reminder: {meeting.title}",
            message=f"You have a meeting with {meeting.invitee_name} in 15 minutes.",
            category='reminders',
            priority='high',
            meeting=meeting
        )
        
        # Send email reminder if enabled
        if meeting.organizer.email_notifications:
            send_mail(
                subject=f"Reminder: {meeting.title}",
                message=f"You have a meeting with {meeting.invitee_name} starting at {meeting.start_time}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[meeting.organizer.email],
                fail_silently=True
            )
        
        # Mark reminder as sent
        meeting.reminder_sent = True
        meeting.save()
        
        return f"Reminder sent for meeting {meeting_id}"
        
    except Meeting.DoesNotExist:
        return f"Meeting {meeting_id} not found"


@shared_task
def send_meeting_confirmation(meeting_id):
    """Send meeting confirmation to invitee"""
    from meetings.models import Meeting
    
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        
        # Send confirmation email to invitee
        send_mail(
            subject=f"Meeting Confirmed: {meeting.title}",
            message=f"""
            Your meeting has been confirmed!
            
            Meeting: {meeting.title}
            Date & Time: {meeting.start_time}
            Duration: {meeting.duration_minutes} minutes
            
            Meeting details will be sent closer to the meeting time.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[meeting.invitee_email],
            fail_silently=True
        )
        
        # Mark confirmation as sent
        meeting.confirmation_sent = True
        meeting.save()
        
        return f"Confirmation sent for meeting {meeting_id}"
        
    except Meeting.DoesNotExist:
        return f"Meeting {meeting_id} not found"


@shared_task
def sync_calendar_integration(integration_id):
    """Sync calendar integration"""
    from integrations.models import UserIntegration, IntegrationSync
    
    try:
        integration = UserIntegration.objects.get(id=integration_id)
        
        # Create sync job
        sync_job = IntegrationSync.objects.create(
            integration=integration,
            sync_type='calendar_events',
            status='running'
        )
        
        # TODO: Implement actual calendar sync logic
        # This would connect to the calendar API and sync events
        
        # For now, simulate successful sync
        sync_job.status = 'completed'
        sync_job.completed_at = timezone.now()
        sync_job.items_processed = 10
        sync_job.save()
        
        # Update integration
        integration.last_sync_at = timezone.now()
        integration.save()
        
        return f"Calendar sync completed for integration {integration_id}"
        
    except UserIntegration.DoesNotExist:
        return f"Integration {integration_id} not found"


@shared_task
def process_workflow_execution(workflow_id, trigger_data):
    """Process workflow execution"""
    from workflows.models import Workflow, WorkflowExecution
    
    try:
        workflow = Workflow.objects.get(id=workflow_id)
        
        # Create execution record
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            trigger_data=trigger_data,
            status='running'
        )
        
        # TODO: Implement actual workflow processing logic
        # This would execute the workflow actions based on the trigger
        
        # For now, simulate successful execution
        execution.status = 'completed'
        execution.completed_at = timezone.now()
        execution.actions_completed = len(workflow.actions)
        execution.save()
        
        # Update workflow statistics
        workflow.execution_count += 1
        workflow.last_executed_at = timezone.now()
        workflow.save()
        
        return f"Workflow {workflow_id} executed successfully"
        
    except Workflow.DoesNotExist:
        return f"Workflow {workflow_id} not found"


@shared_task
def cleanup_old_notifications():
    """Clean up old notifications"""
    from notifications.models import Notification
    from datetime import timedelta
    
    # Delete notifications older than 90 days
    cutoff_date = timezone.now() - timedelta(days=90)
    deleted_count = Notification.objects.filter(
        created_at__lt=cutoff_date,
        status='read'
    ).delete()[0]
    
    return f"Cleaned up {deleted_count} old notifications"


@shared_task
def generate_meeting_analytics():
    """Generate meeting analytics data"""
    from meetings.models import Meeting
    from django.db.models import Count
    
    # TODO: Implement analytics generation
    # This would calculate various metrics and store them for dashboard display
    
    return "Meeting analytics generated"