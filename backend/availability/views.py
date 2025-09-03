from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from .models import (
    WeeklyAvailability, DateOverride, BufferTime, 
    TimeZoneSettings, CalendarIntegration, AvailabilityRule
)
from .serializers import (
    WeeklyAvailabilitySerializer, DateOverrideSerializer, BufferTimeSerializer,
    TimeZoneSettingsSerializer, CalendarIntegrationSerializer, 
    CalendarIntegrationCreateSerializer, AvailabilityRuleSerializer,
    AvailabilityOverviewSerializer, BulkWeeklyAvailabilitySerializer
)


class WeeklyAvailabilityListCreateView(generics.ListCreateAPIView):
    serializer_class = WeeklyAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['weekday', 'is_available']
    ordering = ['weekday', 'start_time']

    def get_queryset(self):
        return WeeklyAvailability.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WeeklyAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WeeklyAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WeeklyAvailability.objects.filter(user=self.request.user)


class DateOverrideListCreateView(generics.ListCreateAPIView):
    serializer_class = DateOverrideSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_available', 'date']
    ordering = ['date', 'start_time']

    def get_queryset(self):
        return DateOverride.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DateOverrideDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DateOverrideSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DateOverride.objects.filter(user=self.request.user)


class BufferTimeView(generics.RetrieveUpdateAPIView):
    serializer_class = BufferTimeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        buffer_time, created = BufferTime.objects.get_or_create(user=self.request.user)
        return buffer_time


class TimeZoneSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = TimeZoneSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        timezone_settings, created = TimeZoneSettings.objects.get_or_create(
            user=self.request.user
        )
        return timezone_settings


class CalendarIntegrationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['provider', 'sync_status', 'is_primary']
    ordering = ['-is_primary', 'provider']

    def get_queryset(self):
        return CalendarIntegration.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CalendarIntegrationCreateSerializer
        return CalendarIntegrationSerializer


class CalendarIntegrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CalendarIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CalendarIntegration.objects.filter(user=self.request.user)


class AvailabilityRuleListCreateView(generics.ListCreateAPIView):
    serializer_class = AvailabilityRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['rule_type', 'is_active']
    ordering = ['rule_type']

    def get_queryset(self):
        return AvailabilityRule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AvailabilityRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AvailabilityRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AvailabilityRule.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def availability_overview(request):
    """Get complete availability overview for the user"""
    user = request.user
    
    data = {
        'weekly_availability': WeeklyAvailabilitySerializer(
            user.weekly_availability.all(), many=True
        ).data,
        'date_overrides': DateOverrideSerializer(
            user.date_overrides.filter(date__gte=timezone.now().date()), many=True
        ).data,
        'buffer_time': None,
        'timezone_settings': None,
        'calendar_integrations': CalendarIntegrationSerializer(
            user.calendar_integrations.all(), many=True
        ).data,
        'availability_rules': AvailabilityRuleSerializer(
            user.availability_rules.filter(is_active=True), many=True
        ).data,
    }
    
    # Get buffer time settings
    try:
        buffer_time = BufferTime.objects.get(user=user)
        data['buffer_time'] = BufferTimeSerializer(buffer_time).data
    except BufferTime.DoesNotExist:
        pass
    
    # Get timezone settings
    try:
        timezone_settings = TimeZoneSettings.objects.get(user=user)
        data['timezone_settings'] = TimeZoneSettingsSerializer(timezone_settings).data
    except TimeZoneSettings.DoesNotExist:
        pass
    
    return Response(data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_weekly_availability(request):
    """Bulk update weekly availability"""
    serializer = BulkWeeklyAvailabilitySerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def sync_calendar(request, integration_id):
    """Manually sync a calendar integration"""
    try:
        integration = CalendarIntegration.objects.get(
            id=integration_id, 
            user=request.user
        )
        
        # TODO: Implement actual calendar sync logic
        integration.last_sync_at = timezone.now()
        integration.sync_status = 'active'
        integration.sync_error_message = ''
        integration.save()
        
        return Response({
            'message': 'Calendar synced successfully',
            'last_sync_at': integration.last_sync_at
        })
        
    except CalendarIntegration.DoesNotExist:
        return Response(
            {'error': 'Calendar integration not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_availability(request):
    """Check availability for a specific date and time range"""
    date_str = request.GET.get('date')
    start_time_str = request.GET.get('start_time')
    end_time_str = request.GET.get('end_time')
    
    if not all([date_str, start_time_str, end_time_str]):
        return Response(
            {'error': 'date, start_time, and end_time parameters are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from datetime import datetime, date, time
        
        check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        # TODO: Implement availability checking logic
        # This would check weekly availability, date overrides, existing meetings, etc.
        
        is_available = True  # Placeholder
        conflicts = []  # Placeholder
        
        return Response({
            'is_available': is_available,
            'conflicts': conflicts,
            'date': check_date,
            'start_time': start_time,
            'end_time': end_time,
        })
        
    except ValueError as e:
        return Response(
            {'error': f'Invalid date/time format: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def availability_stats(request):
    """Get availability statistics"""
    user = request.user
    
    # Count availability slots
    total_weekly_slots = WeeklyAvailability.objects.filter(
        user=user, is_available=True
    ).count()
    
    # Count date overrides
    future_overrides = DateOverride.objects.filter(
        user=user, 
        date__gte=timezone.now().date()
    ).count()
    
    # Count calendar integrations
    active_integrations = CalendarIntegration.objects.filter(
        user=user, 
        sync_status='active'
    ).count()
    
    # Count availability rules
    active_rules = AvailabilityRule.objects.filter(
        user=user, 
        is_active=True
    ).count()
    
    return Response({
        'total_weekly_slots': total_weekly_slots,
        'future_overrides': future_overrides,
        'active_integrations': active_integrations,
        'active_rules': active_rules,
    })