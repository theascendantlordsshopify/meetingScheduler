from rest_framework import serializers
from .models import (
    NotificationTemplate, Notification, NotificationPreference,
    NotificationQueue, NotificationBatch
)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('recipient', 'sent_at', 'delivered_at', 'read_at', 'created_at', 'updated_at')


class NotificationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing notifications"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'category', 'category_display',
            'priority', 'status', 'status_display', 'channel',
            'read_at', 'time_ago', 'created_at'
        ]

    def get_time_ago(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            return f"{diff.seconds // 60}m ago"
        elif diff < timedelta(days=1):
            return f"{diff.seconds // 3600}h ago"
        elif diff < timedelta(days=7):
            return f"{diff.days}d ago"
        else:
            return obj.created_at.strftime("%b %d, %Y")


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'html_content', 'category', 'priority',
            'channel', 'scheduled_at', 'meeting', 'event_type', 'metadata'
        ]

    def create(self, validated_data):
        validated_data['recipient'] = self.context['request'].user
        return super().create(validated_data)


class NotificationBatchSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationBatch
        fields = '__all__'
        read_only_fields = ('created_by', 'total_recipients', 'sent_count', 'failed_count', 'created_at')

    def get_success_rate(self, obj):
        if obj.total_recipients == 0:
            return 0
        return round((obj.sent_count / obj.total_recipients) * 100, 2)

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer for sending bulk notifications"""
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of user IDs to send notifications to"
    )
    title = serializers.CharField(max_length=200)
    message = serializers.TextField()
    category = serializers.ChoiceField(choices=Notification.CATEGORY_CHOICES)
    priority = serializers.ChoiceField(choices=Notification.PRIORITY_CHOICES, default='normal')
    channel = serializers.ChoiceField(choices=NotificationTemplate.CHANNEL_CHOICES, default='in_app')
    scheduled_at = serializers.DateTimeField(required=False)

    def validate_recipient_ids(self, value):
        """Validate that all recipient IDs exist"""
        existing_ids = User.objects.filter(id__in=value).values_list('id', flat=True)
        missing_ids = set(value) - set(existing_ids)
        
        if missing_ids:
            raise serializers.ValidationError(f"Users not found: {list(missing_ids)}")
        
        return value

    def create(self, validated_data):
        recipient_ids = validated_data.pop('recipient_ids')
        recipients = User.objects.filter(id__in=recipient_ids)
        
        notifications = []
        for recipient in recipients:
            notification = Notification(
                recipient=recipient,
                **validated_data
            )
            notifications.append(notification)
        
        created_notifications = Notification.objects.bulk_create(notifications)
        return {
            'message': f'Created {len(created_notifications)} notifications',
            'notification_count': len(created_notifications)
        }