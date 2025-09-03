from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import EventType, EventTypeAvailability, BookingPage
from .serializers import (
    EventTypeSerializer, EventTypeCreateSerializer, EventTypeUpdateSerializer,
    EventTypeListSerializer, EventTypeAvailabilitySerializer, BookingPageSerializer
)


class EventTypeListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['duration', 'location_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'duration', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return EventType.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EventTypeCreateSerializer
        return EventTypeListSerializer


class EventTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventType.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EventTypeUpdateSerializer
        return EventTypeSerializer


class EventTypeAvailabilityListCreateView(generics.ListCreateAPIView):
    serializer_class = EventTypeAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        event_type_id = self.kwargs.get('event_type_id')
        return EventTypeAvailability.objects.filter(
            event_type_id=event_type_id,
            event_type__user=self.request.user
        )

    def perform_create(self, serializer):
        event_type_id = self.kwargs.get('event_type_id')
        event_type = EventType.objects.get(id=event_type_id, user=self.request.user)
        serializer.save(event_type=event_type)


class EventTypeAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventTypeAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventTypeAvailability.objects.filter(
            event_type__user=self.request.user
        )


class BookingPageDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = BookingPageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        event_type_id = self.kwargs.get('event_type_id')
        event_type = EventType.objects.get(id=event_type_id, user=self.request.user)
        booking_page, created = BookingPage.objects.get_or_create(event_type=event_type)
        return booking_page


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def duplicate_event_type(request, pk):
    """Duplicate an existing event type"""
    try:
        original = EventType.objects.get(pk=pk, user=request.user)
        
        # Create a copy
        duplicate = EventType.objects.create(
            user=request.user,
            name=f"{original.name} (Copy)",
            description=original.description,
            duration=original.duration,
            location_type=original.location_type,
            location_details=original.location_details,
            buffer_time_before=original.buffer_time_before,
            buffer_time_after=original.buffer_time_after,
            max_bookings_per_day=original.max_bookings_per_day,
            min_notice_time=original.min_notice_time,
            max_advance_time=original.max_advance_time,
            color=original.color,
            custom_questions=original.custom_questions,
        )
        
        # Copy custom availability
        for availability in original.custom_availability.all():
            EventTypeAvailability.objects.create(
                event_type=duplicate,
                weekday=availability.weekday,
                start_time=availability.start_time,
                end_time=availability.end_time,
                is_available=availability.is_available,
            )
        
        # Copy booking page
        if hasattr(original, 'booking_page'):
            original_page = original.booking_page
            BookingPage.objects.create(
                event_type=duplicate,
                welcome_message=original_page.welcome_message,
                thank_you_message=original_page.thank_you_message,
                background_color=original_page.background_color,
                text_color=original_page.text_color,
                accent_color=original_page.accent_color,
                page_title=f"Book a {duplicate.name}",
                meta_description=original_page.meta_description,
                show_event_details=original_page.show_event_details,
                show_organizer_info=original_page.show_organizer_info,
                require_confirmation=original_page.require_confirmation,
            )
        
        serializer = EventTypeSerializer(duplicate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except EventType.DoesNotExist:
        return Response(
            {'error': 'Event type not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def event_type_stats(request):
    """Get statistics for user's event types"""
    user = request.user
    event_types = EventType.objects.filter(user=user)
    
    total_event_types = event_types.count()
    active_event_types = event_types.filter(is_active=True).count()
    
    # Get booking statistics
    from meetings.models import Meeting
    total_bookings = Meeting.objects.filter(event_type__user=user).count()
    confirmed_bookings = Meeting.objects.filter(
        event_type__user=user, 
        status='confirmed'
    ).count()
    
    return Response({
        'total_event_types': total_event_types,
        'active_event_types': active_event_types,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
    })