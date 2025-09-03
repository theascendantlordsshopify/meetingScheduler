from rest_framework import serializers
from .models import Workflow, WorkflowExecution, WorkflowTemplate, WorkflowAction, WorkflowTrigger


class WorkflowActionSerializer(serializers.ModelSerializer):
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = WorkflowAction
        fields = '__all__'


class WorkflowTriggerSerializer(serializers.ModelSerializer):
    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    
    class Meta:
        model = WorkflowTrigger
        fields = '__all__'


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowExecution
        fields = '__all__'

    def get_duration(self, obj):
        if obj.completed_at and obj.started_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = WorkflowTemplate
        fields = '__all__'


class WorkflowSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    recent_executions = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Workflow
        fields = '__all__'
        read_only_fields = ('user', 'execution_count', 'last_executed_at', 'created_at', 'updated_at')

    def get_recent_executions(self, obj):
        recent = obj.executions.all()[:5]
        return WorkflowExecutionSerializer(recent, many=True).data

    def get_success_rate(self, obj):
        total_executions = obj.executions.count()
        if total_executions == 0:
            return 0
        
        successful_executions = obj.executions.filter(status='completed').count()
        return round((successful_executions / total_executions) * 100, 2)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WorkflowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = [
            'name', 'description', 'trigger_type', 'trigger_conditions', 
            'actions', 'status'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WorkflowListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing workflows"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    last_execution_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'trigger_type', 'status', 'status_display',
            'is_active', 'execution_count', 'last_executed_at', 'last_execution_status',
            'created_at', 'updated_at'
        ]

    def get_last_execution_status(self, obj):
        last_execution = obj.executions.first()
        return last_execution.status if last_execution else None


class WorkflowFromTemplateSerializer(serializers.Serializer):
    """Serializer for creating workflow from template"""
    template_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_template_id(self, value):
        try:
            WorkflowTemplate.objects.get(id=value)
        except WorkflowTemplate.DoesNotExist:
            raise serializers.ValidationError("Template not found")
        return value

    def create(self, validated_data):
        template = WorkflowTemplate.objects.get(id=validated_data['template_id'])
        user = self.context['request'].user
        
        workflow = Workflow.objects.create(
            user=user,
            name=validated_data['name'],
            description=validated_data.get('description', template.description),
            trigger_type=template.trigger_type,
            trigger_conditions=template.trigger_conditions,
            actions=template.actions,
            status='draft'
        )
        
        # Increment template usage count
        template.usage_count += 1
        template.save()
        
        return workflow


class WorkflowExecutionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowExecution
        fields = ['workflow', 'trigger_data']

    def create(self, validated_data):
        # This would typically be called by the workflow engine
        return super().create(validated_data)