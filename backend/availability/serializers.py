from rest_framework import serializers
from .models import (
    WeeklyAvailability, DateOverride, BufferTime, 
    TimeZoneSettings, CalendarIntegration, AvailabilityRule
)


class WeeklyAvailabilitySerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    
    class Meta:
        model = WeeklyAvailability
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class DateOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = DateOverride
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class BufferTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BufferTime
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class TimeZoneSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeZoneSettings
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class CalendarIntegrationSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    sync_status_display = serializers.CharField(source='get_sync_status_display', read_only=True)
    
    class Meta:
        model = CalendarIntegration
        fields = [
            'id', 'provider', 'provider_display', 'calendar_id', 'calendar_name',
            'is_primary', 'sync_enabled', 'check_conflicts', 'last_sync_at',
            'sync_status', 'sync_status_display', 'sync_error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('user', 'last_sync_at', 'created_at', 'updated_at')


class CalendarIntegrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarIntegration
        fields = [
            'provider', 'calendar_id', 'calendar_name', 'is_primary',
            'sync_enabled', 'check_conflicts'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AvailabilityRuleSerializer(serializers.ModelSerializer):
    rule_type_display = serializers.CharField(source='get_rule_type_display', read_only=True)
    
    class Meta:
        model = AvailabilityRule
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class AvailabilityOverviewSerializer(serializers.Serializer):
    """Serializer for availability overview"""
    weekly_availability = WeeklyAvailabilitySerializer(many=True, read_only=True)
    date_overrides = DateOverrideSerializer(many=True, read_only=True)
    buffer_time = BufferTimeSerializer(read_only=True)
    timezone_settings = TimeZoneSettingsSerializer(read_only=True)
    calendar_integrations = CalendarIntegrationSerializer(many=True, read_only=True)
    availability_rules = AvailabilityRuleSerializer(many=True, read_only=True)


class BulkWeeklyAvailabilitySerializer(serializers.Serializer):
    """Serializer for bulk updating weekly availability"""
    availability_data = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of availability objects"
    )

    def validate_availability_data(self, value):
        """Validate the availability data structure"""
        for item in value:
            if 'weekday' not in item or 'start_time' not in item or 'end_time' not in item:
                raise serializers.ValidationError(
                    "Each availability item must have weekday, start_time, and end_time"
                )
            
            weekday = item.get('weekday')
            if not isinstance(weekday, int) or weekday < 0 or weekday > 6:
                raise serializers.ValidationError("Weekday must be an integer between 0 and 6")
        
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        availability_data = validated_data['availability_data']
        
        # Clear existing availability
        WeeklyAvailability.objects.filter(user=user).delete()
        
        # Create new availability
        availability_objects = []
        for item in availability_data:
            availability_objects.append(
                WeeklyAvailability(
                    user=user,
                    weekday=item['weekday'],
                    start_time=item['start_time'],
                    end_time=item['end_time'],
                    is_available=item.get('is_available', True)
                )
            )
        
        WeeklyAvailability.objects.bulk_create(availability_objects)
        return {'message': 'Availability updated successfully'}