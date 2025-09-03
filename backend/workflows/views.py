from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import Workflow, WorkflowExecution, WorkflowTemplate, WorkflowAction, WorkflowTrigger
from .serializers import (
    WorkflowSerializer, WorkflowCreateSerializer, WorkflowListSerializer,
    WorkflowExecutionSerializer, WorkflowTemplateSerializer,
    WorkflowActionSerializer, WorkflowTriggerSerializer,
    WorkflowFromTemplateSerializer
)


class WorkflowListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'trigger_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'last_executed_at', 'execution_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return Workflow.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkflowCreateSerializer
        return WorkflowListSerializer


class WorkflowDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Workflow.objects.filter(user=self.request.user)


class WorkflowExecutionListView(generics.ListAPIView):
    serializer_class = WorkflowExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'workflow']
    ordering = ['-started_at']

    def get_queryset(self):
        workflow_id = self.kwargs.get('workflow_id')
        return WorkflowExecution.objects.filter(
            workflow_id=workflow_id,
            workflow__user=self.request.user
        )


class WorkflowTemplateListView(generics.ListAPIView):
    queryset = WorkflowTemplate.objects.filter(is_active=True)
    serializer_class = WorkflowTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category']
    ordering = ['-is_popular', 'name']


class WorkflowActionListView(generics.ListAPIView):
    queryset = WorkflowAction.objects.filter(is_active=True)
    serializer_class = WorkflowActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['action_type', 'requires_integration']
    ordering = ['name']


class WorkflowTriggerListView(generics.ListAPIView):
    queryset = WorkflowTrigger.objects.filter(is_active=True)
    serializer_class = WorkflowTriggerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['trigger_type']
    ordering = ['name']


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_workflow_from_template(request):
    """Create a workflow from a template"""
    serializer = WorkflowFromTemplateSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        workflow = serializer.save()
        return Response(
            WorkflowSerializer(workflow).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def duplicate_workflow(request, pk):
    """Duplicate an existing workflow"""
    try:
        original = Workflow.objects.get(pk=pk, user=request.user)
        
        duplicate = Workflow.objects.create(
            user=request.user,
            name=f"{original.name} (Copy)",
            description=original.description,
            trigger_type=original.trigger_type,
            trigger_conditions=original.trigger_conditions,
            actions=original.actions,
            status='draft'
        )
        
        return Response(
            WorkflowSerializer(duplicate).data,
            status=status.HTTP_201_CREATED
        )
        
    except Workflow.DoesNotExist:
        return Response(
            {'error': 'Workflow not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def activate_workflow(request, pk):
    """Activate a workflow"""
    try:
        workflow = Workflow.objects.get(pk=pk, user=request.user)
        workflow.status = 'active'
        workflow.is_active = True
        workflow.save()
        
        return Response({
            'message': 'Workflow activated successfully',
            'workflow': WorkflowSerializer(workflow).data
        })
        
    except Workflow.DoesNotExist:
        return Response(
            {'error': 'Workflow not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def pause_workflow(request, pk):
    """Pause a workflow"""
    try:
        workflow = Workflow.objects.get(pk=pk, user=request.user)
        workflow.status = 'paused'
        workflow.save()
        
        return Response({
            'message': 'Workflow paused successfully',
            'workflow': WorkflowSerializer(workflow).data
        })
        
    except Workflow.DoesNotExist:
        return Response(
            {'error': 'Workflow not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_workflow(request, pk):
    """Test a workflow with sample data"""
    try:
        workflow = Workflow.objects.get(pk=pk, user=request.user)
        
        # Create a test execution
        test_execution = WorkflowExecution.objects.create(
            workflow=workflow,
            trigger_data=request.data.get('test_data', {}),
            status='running'
        )
        
        # TODO: Implement actual workflow execution logic
        # For now, just mark as completed
        test_execution.status = 'completed'
        test_execution.completed_at = timezone.now()
        test_execution.actions_completed = len(workflow.actions)
        test_execution.execution_log = [
            {'step': 'test', 'message': 'Workflow test completed successfully'}
        ]
        test_execution.save()
        
        return Response({
            'message': 'Workflow test completed',
            'execution': WorkflowExecutionSerializer(test_execution).data
        })
        
    except Workflow.DoesNotExist:
        return Response(
            {'error': 'Workflow not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def workflow_stats(request):
    """Get workflow statistics"""
    user = request.user
    workflows = Workflow.objects.filter(user=user)
    
    total_workflows = workflows.count()
    active_workflows = workflows.filter(status='active').count()
    paused_workflows = workflows.filter(status='paused').count()
    draft_workflows = workflows.filter(status='draft').count()
    
    # Execution statistics
    executions = WorkflowExecution.objects.filter(workflow__user=user)
    total_executions = executions.count()
    successful_executions = executions.filter(status='completed').count()
    failed_executions = executions.filter(status='failed').count()
    
    # Recent activity
    recent_executions = executions.order_by('-started_at')[:5]
    
    return Response({
        'total_workflows': total_workflows,
        'active_workflows': active_workflows,
        'paused_workflows': paused_workflows,
        'draft_workflows': draft_workflows,
        'total_executions': total_executions,
        'successful_executions': successful_executions,
        'failed_executions': failed_executions,
        'success_rate': round((successful_executions / total_executions * 100), 2) if total_executions > 0 else 0,
        'recent_executions': WorkflowExecutionSerializer(recent_executions, many=True).data,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def workflow_analytics(request, pk):
    """Get analytics for a specific workflow"""
    try:
        workflow = Workflow.objects.get(pk=pk, user=request.user)
        executions = workflow.executions.all()
        
        # Execution statistics
        total_executions = executions.count()
        successful_executions = executions.filter(status='completed').count()
        failed_executions = executions.filter(status='failed').count()
        
        # Performance metrics
        completed_executions = executions.filter(
            status='completed',
            completed_at__isnull=False
        )
        
        avg_duration = None
        if completed_executions.exists():
            durations = [
                (exec.completed_at - exec.started_at).total_seconds()
                for exec in completed_executions
            ]
            avg_duration = sum(durations) / len(durations)
        
        # Recent executions
        recent_executions = executions.order_by('-started_at')[:10]
        
        return Response({
            'workflow': WorkflowListSerializer(workflow).data,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': round((successful_executions / total_executions * 100), 2) if total_executions > 0 else 0,
            'average_duration': avg_duration,
            'recent_executions': WorkflowExecutionSerializer(recent_executions, many=True).data,
        })
        
    except Workflow.DoesNotExist:
        return Response(
            {'error': 'Workflow not found'},
            status=status.HTTP_404_NOT_FOUND
        )