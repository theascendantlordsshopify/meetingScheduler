from rest_framework import serializers
from .models import (
    IntegrationProvider, UserIntegration, IntegrationWebhook,
    IntegrationLog, IntegrationTemplate, IntegrationSync
)


class IntegrationProviderSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    auth_type_display = serializers.CharField(source='get_auth_type_display', read_only=True)
    
    class Meta:
        model = IntegrationProvider
        fields = [
            'id', 'name', 'slug', 'category', 'category_display', 'description',
            'website_url', 'logo_url', 'documentation_url', 'auth_type',
            'auth_type_display', 'features', 'is_active', 'is_popular'
        ]


class IntegrationWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationWebhook
        fields = '__all__'
        read_only_fields = ('integration', 'created_at', 'updated_at')


class IntegrationLogSerializer(serializers.ModelSerializer):
    log_type_display = serializers.CharField(source='get_log_type_display', read_only=True)
    
    class Meta:
        model = IntegrationLog
        fields = [
            'id', 'log_type', 'log_type_display', 'message', 'details',
            'is_error', 'created_at'
        ]


class IntegrationSyncSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = IntegrationSync
        fields = '__all__'

    def get_duration(self, obj):
        if obj.completed_at and obj.started_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None


class UserIntegrationSerializer(serializers.ModelSerializer):
    provider_details = IntegrationProviderSerializer(source='provider', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_token_expired = serializers.ReadOnlyField()
    recent_logs = serializers.SerializerMethodField()
    recent_syncs = serializers.SerializerMethodField()
    
    class Meta:
        model = UserIntegration
        fields = [
            'id', 'provider', 'provider_details', 'external_id', 'external_email',
            'external_name', 'settings', 'status', 'status_display', 'last_sync_at',
            'sync_error_message', 'api_calls_count', 'last_api_call_at',
            'is_token_expired', 'recent_logs', 'recent_syncs', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'user', 'access_token', 'refresh_token', 'token_expires_at',
            'api_key', 'api_calls_count', 'last_api_call_at', 'created_at', 'updated_at'
        )

    def get_recent_logs(self, obj):
        recent = obj.logs.all()[:5]
        return IntegrationLogSerializer(recent, many=True).data

    def get_recent_syncs(self, obj):
        recent = obj.sync_jobs.all()[:3]
        return IntegrationSyncSerializer(recent, many=True).data


class UserIntegrationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing integrations"""
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_category = serializers.CharField(source='provider.category', read_only=True)
    provider_logo = serializers.CharField(source='provider.logo_url', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_token_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = UserIntegration
        fields = [
            'id', 'provider', 'provider_name', 'provider_category', 'provider_logo',
            'external_name', 'status', 'status_display', 'last_sync_at',
            'is_token_expired', 'created_at'
        ]


class IntegrationTemplateSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = IntegrationTemplate
        fields = '__all__'


class IntegrationConnectSerializer(serializers.Serializer):
    """Serializer for connecting to an integration"""
    provider_id = serializers.IntegerField()
    auth_code = serializers.CharField(required=False, allow_blank=True)
    api_key = serializers.CharField(required=False, allow_blank=True)
    settings = serializers.JSONField(required=False, default=dict)

    def validate_provider_id(self, value):
        try:
            IntegrationProvider.objects.get(id=value, is_active=True)
        except IntegrationProvider.DoesNotExist:
            raise serializers.ValidationError("Provider not found or inactive")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        provider = IntegrationProvider.objects.get(id=validated_data['provider_id'])
        
        # Check if integration already exists
        existing = UserIntegration.objects.filter(user=user, provider=provider).first()
        if existing:
            raise serializers.ValidationError("Integration already exists")
        
        # Create integration
        integration = UserIntegration.objects.create(
            user=user,
            provider=provider,
            api_key=validated_data.get('api_key', ''),
            settings=validated_data.get('settings', {}),
            status='connected'
        )
        
        # TODO: Handle OAuth flow if auth_code is provided
        # TODO: Validate API key if provided
        
        return integration


class IntegrationDisconnectSerializer(serializers.Serializer):
    """Serializer for disconnecting an integration"""
    confirm = serializers.BooleanField(default=False)

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError("Please confirm disconnection")
        return value


class IntegrationSyncTriggerSerializer(serializers.Serializer):
    """Serializer for triggering a sync"""
    sync_type = serializers.CharField(required=False, default='full')
    force = serializers.BooleanField(default=False)

    def validate_sync_type(self, value):
        allowed_types = ['full', 'incremental', 'calendar', 'contacts']
        if value not in allowed_types:
            raise serializers.ValidationError(f"Invalid sync type. Allowed: {allowed_types}")
        return value