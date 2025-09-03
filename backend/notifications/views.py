from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count
from .models import (
    NotificationTemplate, Notification, NotificationPreference,
    NotificationQueue, NotificationBatch
)
from .serializers import (
    NotificationTemplateSerializer, NotificationSerializer, NotificationListSerializer,
    NotificationPreferenceSerializer, NotificationCreateSerializer,
    NotificationBatchSerializer, BulkNotificationSerializer
)


class NotificationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'priority', 'status', 'channel']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'priority', 'scheduled_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotificationCreateSerializer
        return NotificationListSerializer


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class UnreadNotificationsView(generics.ListAPIView):
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
            read_at__isnull=True,
            status__in=['sent', 'delivered']
        ).order_by('-created_at')


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences


class NotificationTemplateListView(generics.ListAPIView):
    queryset = NotificationTemplate.objects.filter(is_active=True)
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['template_type', 'channel']


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
        notification.mark_as_read()
        
        return Response({
            'message': 'Notification marked as read',
            'notification': NotificationSerializer(notification).data
        })
        
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read for the user"""
    updated_count = Notification.objects.filter(
        recipient=request.user,
        read_at__isnull=True,
        status__in=['sent', 'delivered']
    ).update(
        status='read',
        read_at=timezone.now()
    )
    
    return Response({
        'message': f'Marked {updated_count} notifications as read',
        'updated_count': updated_count
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_notification(request, pk):
    """Delete a specific notification"""
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
        notification.delete()
        
        return Response({
            'message': 'Notification deleted successfully'
        })
        
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_bulk_notification(request):
    """Send notifications to multiple users"""
    serializer = BulkNotificationSerializer(data=request.data)
    
    if serializer.is_valid():
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_stats(request):
    """Get notification statistics for the user"""
    user = request.user
    notifications = Notification.objects.filter(recipient=user)
    
    total_notifications = notifications.count()
    unread_notifications = notifications.filter(read_at__isnull=True).count()
    
    # Category breakdown
    category_stats = notifications.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent notifications
    recent_notifications = notifications.order_by('-created_at')[:5]
    
    # This week's notifications
    from datetime import timedelta
    week_ago = timezone.now() - timedelta(days=7)
    this_week_count = notifications.filter(created_at__gte=week_ago).count()
    
    return Response({
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'this_week_count': this_week_count,
        'category_stats': list(category_stats),
        'recent_notifications': NotificationListSerializer(recent_notifications, many=True).data,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_categories(request):
    """Get notifications grouped by category"""
    user = request.user
    
    categories = {}
    for category_code, category_name in Notification.CATEGORY_CHOICES:
        notifications = Notification.objects.filter(
            recipient=user,
            category=category_code
        ).order_by('-created_at')[:10]
        
        categories[category_code] = {
            'name': category_name,
            'count': notifications.count(),
            'notifications': NotificationListSerializer(notifications, many=True).data
        }
    
    return Response(categories)