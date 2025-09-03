from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count
from .models import Meeting, MeetingNote, MeetingAttachment, MeetingRescheduleRequest
from .serializers import (
    MeetingSerializer, MeetingCreateSerializer, MeetingUpdateSerializer,
    MeetingListSerializer, MeetingNoteSerializer, MeetingAttachmentSerializer,
    MeetingRescheduleRequestSerializer, PublicMeetingBookingSerializer
)
from events.models import EventType


class MeetingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'event_type', 'is_today']
    search_fields = ['title', 'invitee_name', 'invitee_email']
    ordering_fields = ['start_time', 'created_at', 'status']
    ordering = ['-start_time']

    def get_queryset(self):
        return Meeting.objects.filter(organizer=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MeetingCreateSerializer
        return MeetingListSerializer


class MeetingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Meeting.objects.filter(organizer=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MeetingUpdateSerializer
        return MeetingSerializer


class UpcomingMeetingsView(generics.ListAPIView):
    serializer_class = MeetingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Meeting.objects.filter(
            organizer=self.request.user,
            start_time__gte=timezone.now(),
            status__in=['pending', 'confirmed']
        ).order_by('start_time')[:10]


class TodaysMeetingsView(generics.ListAPIView):
    serializer_class = MeetingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        today = timezone.now().date()
        return Meeting.objects.filter(
            organizer=self.request.user,
            start_time__date=today,
            status__in=['pending', 'confirmed']
        ).order_by('start_time')


class MeetingNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = MeetingNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        meeting_id = self.kwargs.get('meeting_id')
        return MeetingNote.objects.filter(
            meeting_id=meeting_id,
            meeting__organizer=self.request.user
        )

    def perform_create(self, serializer):
        meeting_id = self.kwargs.get('meeting_id')
        meeting = Meeting.objects.get(id=meeting_id, organizer=self.request.user)
        serializer.save(meeting=meeting, author=self.request.user)


class MeetingAttachmentListCreateView(generics.ListCreateAPIView):
    serializer_class = MeetingAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        meeting_id = self.kwargs.get('meeting_id')
        return MeetingAttachment.objects.filter(
            meeting_id=meeting_id,
            meeting__organizer=self.request.user
        )

    def perform_create(self, serializer):
        meeting_id = self.kwargs.get('meeting_id')
        meeting = Meeting.objects.get(id=meeting_id, organizer=self.request.user)
        serializer.save(meeting=meeting, uploaded_by=self.request.user)


class PublicBookingView(generics.CreateAPIView):
    """Public endpoint for booking meetings (no authentication required)"""
    serializer_class = PublicMeetingBookingSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = serializer.save()
        
        # TODO: Send confirmation email to invitee
        # TODO: Send notification to organizer
        
        return Response({
            'meeting_id': meeting.id,
            'confirmation_token': meeting.confirmation_token,
            'message': 'Meeting booked successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_meeting(request, pk):
    """Cancel a meeting"""
    try:
        meeting = Meeting.objects.get(pk=pk, organizer=request.user)
        
        if meeting.status == 'cancelled':
            return Response(
                {'error': 'Meeting is already cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        meeting.status = 'cancelled'
        meeting.cancellation_reason = request.data.get('reason', '')
        meeting.cancelled_at = timezone.now()
        meeting.save()
        
        # TODO: Send cancellation email to invitee
        
        return Response({
            'message': 'Meeting cancelled successfully',
            'meeting': MeetingSerializer(meeting).data
        })
        
    except Meeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_meeting(request, pk):
    """Confirm a pending meeting"""
    try:
        meeting = Meeting.objects.get(pk=pk, organizer=request.user)
        
        if meeting.status != 'pending':
            return Response(
                {'error': 'Only pending meetings can be confirmed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        meeting.status = 'confirmed'
        meeting.confirmation_sent = True
        meeting.save()
        
        # TODO: Send confirmation email to invitee
        
        return Response({
            'message': 'Meeting confirmed successfully',
            'meeting': MeetingSerializer(meeting).data
        })
        
    except Meeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def meeting_stats(request):
    """Get meeting statistics for the user"""
    user = request.user
    meetings = Meeting.objects.filter(organizer=user)
    
    # Basic counts
    total_meetings = meetings.count()
    confirmed_meetings = meetings.filter(status='confirmed').count()
    pending_meetings = meetings.filter(status='pending').count()
    cancelled_meetings = meetings.filter(status='cancelled').count()
    completed_meetings = meetings.filter(status='completed').count()
    
    # Today's meetings
    today = timezone.now().date()
    todays_meetings = meetings.filter(
        start_time__date=today,
        status__in=['confirmed', 'pending']
    ).count()
    
    # Upcoming meetings
    upcoming_meetings = meetings.filter(
        start_time__gte=timezone.now(),
        status__in=['confirmed', 'pending']
    ).count()
    
    # This month's meetings
    current_month = timezone.now().replace(day=1)
    this_month_meetings = meetings.filter(
        start_time__gte=current_month,
        status='confirmed'
    ).count()
    
    return Response({
        'total_meetings': total_meetings,
        'confirmed_meetings': confirmed_meetings,
        'pending_meetings': pending_meetings,
        'cancelled_meetings': cancelled_meetings,
        'completed_meetings': completed_meetings,
        'todays_meetings': todays_meetings,
        'upcoming_meetings': upcoming_meetings,
        'this_month_meetings': this_month_meetings,
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_event_availability(request, event_type_id):
    """Get available time slots for public booking"""
    try:
        event_type = EventType.objects.get(id=event_type_id, is_active=True)
        
        # TODO: Implement availability calculation logic
        # This would check the organizer's availability, existing meetings, etc.
        
        return Response({
            'event_type': {
                'id': event_type.id,
                'name': event_type.name,
                'duration': event_type.duration,
                'description': event_type.description,
            },
            'available_slots': [],  # TODO: Calculate available slots
        })
        
    except EventType.DoesNotExist:
        return Response(
            {'error': 'Event type not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )