from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import (
    IntegrationProvider, UserIntegration, IntegrationWebhook,
    IntegrationLog, IntegrationTemplate, IntegrationSync
)
from .serializers import (
    IntegrationProviderSerializer, UserIntegrationSerializer,
    UserIntegrationListSerializer, IntegrationTemplateSerializer,
    IntegrationLogSerializer, IntegrationSyncSerializer,
    IntegrationConnectSerializer, IntegrationDisconnectSerializer,
    IntegrationSyncTriggerSerializer
)


class IntegrationProviderListView(generics.ListAPIView):
    queryset = IntegrationProvider.objects.filter(is_active=True)
    serializer_class = IntegrationProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'auth_type', 'is_popular']
    search_fields = ['name', 'description']
    ordering = ['-is_popular', 'name']


class UserIntegrationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['provider__category', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return UserIntegration.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return IntegrationConnectSerializer
        return UserIntegrationListSerializer

    def perform_create(self, serializer):
        serializer.save()


class UserIntegrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserIntegration.objects.filter(user=self.request.user)


class IntegrationTemplateListView(generics.ListAPIView):
    serializer_class = IntegrationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['provider__category', 'is_recommended']
    ordering = ['-is_recommended', 'name']

    def get_queryset(self):
        return IntegrationTemplate.objects.filter(provider__is_active=True)


class IntegrationLogListView(generics.ListAPIView):
    serializer_class = IntegrationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['log_type', 'is_error']
    ordering = ['-created_at']

    def get_queryset(self):
        integration_id = self.kwargs.get('integration_id')
        return IntegrationLog.objects.filter(
            integration_id=integration_id,
            integration__user=self.request.user
        )


class IntegrationSyncListView(generics.ListAPIView):
    serializer_class = IntegrationSyncSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'sync_type']
    ordering = ['-started_at']

    def get_queryset(self):
        integration_id = self.kwargs.get('integration_id')
        return IntegrationSync.objects.filter(
            integration_id=integration_id,
            integration__user=self.request.user
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_integration(request):
    """Connect to a new integration"""
    serializer = IntegrationConnectSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        integration = serializer.save()
        
        # Log the connection
        IntegrationLog.objects.create(
            integration=integration,
            log_type='auth',
            message=f'Connected to {integration.provider.name}',
            details={'action': 'connect'}
        )
        
        return Response(
            UserIntegrationSerializer(integration).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def disconnect_integration(request, pk):
    """Disconnect an integration"""
    try:
        integration = UserIntegration.objects.get(pk=pk, user=request.user)
        
        serializer = IntegrationDisconnectSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Log the disconnection
        IntegrationLog.objects.create(
            integration=integration,
            log_type='auth',
            message=f'Disconnected from {integration.provider.name}',
            details={'action': 'disconnect'}
        )
        
        # Update status instead of deleting (for audit trail)
        integration.status = 'disconnected'
        integration.access_token = ''
        integration.refresh_token = ''
        integration.api_key = ''
        integration.save()
        
        return Response({
            'message': 'Integration disconnected successfully'
        })
        
    except UserIntegration.DoesNotExist:
        return Response(
            {'error': 'Integration not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def sync_integration(request, pk):
    """Trigger a sync for an integration"""
    try:
        integration = UserIntegration.objects.get(pk=pk, user=request.user)
        
        if integration.status != 'connected':
            return Response(
                {'error': 'Integration is not connected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = IntegrationSyncTriggerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        sync_type = serializer.validated_data['sync_type']
        force = serializer.validated_data['force']
        
        # Check if there's already a running sync
        if not force:
            running_sync = integration.sync_jobs.filter(status='running').first()
            if running_sync:
                return Response(
                    {'error': 'Sync already in progress'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create sync job
        sync_job = IntegrationSync.objects.create(
            integration=integration,
            sync_type=sync_type,
            status='pending'
        )
        
        # TODO: Trigger actual sync process (usually via Celery task)
        # For now, just mark as completed
        sync_job.status = 'completed'
        sync_job.completed_at = timezone.now()
        sync_job.items_processed = 10  # Placeholder
        sync_job.save()
        
        # Update integration sync timestamp
        integration.last_sync_at = timezone.now()
        integration.save()
        
        # Log the sync
        IntegrationLog.objects.create(
            integration=integration,
            log_type='sync',
            message=f'Sync triggered for {integration.provider.name}',
            details={'sync_type': sync_type, 'force': force}
        )
        
        return Response({
            'message': 'Sync triggered successfully',
            'sync_job': IntegrationSyncSerializer(sync_job).data
        })
        
    except UserIntegration.DoesNotExist:
        return Response(
            {'error': 'Integration not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_integration(request, pk):
    """Test an integration connection"""
    try:
        integration = UserIntegration.objects.get(pk=pk, user=request.user)
        
        if integration.status != 'connected':
            return Response(
                {'error': 'Integration is not connected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement actual connection test based on provider
        # For now, just simulate a successful test
        test_result = {
            'success': True,
            'message': f'Connection to {integration.provider.name} is working',
            'details': {
                'provider': integration.provider.name,
                'external_id': integration.external_id,
                'last_sync': integration.last_sync_at,
            }
        }
        
        # Log the test
        IntegrationLog.objects.create(
            integration=integration,
            log_type='api_call',
            message=f'Connection test for {integration.provider.name}',
            details=test_result
        )
        
        return Response(test_result)
        
    except UserIntegration.DoesNotExist:
        return Response(
            {'error': 'Integration not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def integration_stats(request):
    """Get integration statistics"""
    user = request.user
    integrations = UserIntegration.objects.filter(user=user)
    
    total_integrations = integrations.count()
    connected_integrations = integrations.filter(status='connected').count()
    error_integrations = integrations.filter(status='error').count()
    
    # Category breakdown
    categories = integrations.values('provider__category').distinct()
    category_stats = []
    for cat in categories:
        category = cat['provider__category']
        count = integrations.filter(provider__category=category).count()
        category_stats.append({
            'category': category,
            'count': count
        })
    
    # Recent activity
    recent_logs = IntegrationLog.objects.filter(
        integration__user=user
    ).order_by('-created_at')[:10]
    
    # API usage
    total_api_calls = sum(integrations.values_list('api_calls_count', flat=True))
    
    return Response({
        'total_integrations': total_integrations,
        'connected_integrations': connected_integrations,
        'error_integrations': error_integrations,
        'category_stats': category_stats,
        'total_api_calls': total_api_calls,
        'recent_activity': IntegrationLogSerializer(recent_logs, many=True).data,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def popular_integrations(request):
    """Get popular integrations"""
    popular = IntegrationProvider.objects.filter(
        is_active=True,
        is_popular=True
    ).order_by('name')
    
    return Response({
        'integrations': IntegrationProviderSerializer(popular, many=True).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recently_connected(request):
    """Get recently connected integrations"""
    recent = UserIntegration.objects.filter(
        user=request.user,
        status='connected'
    ).order_by('-created_at')[:5]
    
    return Response({
        'integrations': UserIntegrationListSerializer(recent, many=True).data
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def webhook_handler(request, integration_id, provider_slug):
    """Handle incoming webhooks from integration providers"""
    try:
        integration = UserIntegration.objects.get(
            id=integration_id,
            provider__slug=provider_slug,
            status='connected'
        )
        
        # TODO: Verify webhook signature
        # TODO: Process webhook data based on provider
        
        # Log the webhook
        IntegrationLog.objects.create(
            integration=integration,
            log_type='webhook',
            message=f'Webhook received from {integration.provider.name}',
            details={'headers': dict(request.headers)},
            request_data=request.data
        )
        
        return Response({'status': 'received'})
        
    except UserIntegration.DoesNotExist:
        return Response(
            {'error': 'Integration not found'},
            status=status.HTTP_404_NOT_FOUND
        )