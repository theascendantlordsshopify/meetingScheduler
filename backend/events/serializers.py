from rest_framework import serializers
from .models import EventType, EventTypeAvailability, BookingPage


class EventTypeAvailabilitySerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    
    class Meta:
        model = EventTypeAvailability
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class BookingPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingPage
        fields = '__all__'
        read_only_fields = ('event_type', 'created_at', 'updated_at')


class EventTypeSerializer(serializers.ModelSerializer):
    custom_availability = EventTypeAvailabilitySerializer(many=True, read_only=True)
    booking_page = BookingPageSerializer(read_only=True)
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)
    location_type_display = serializers.CharField(source='get_location_type_display', read_only=True)
    total_duration_with_buffer = serializers.ReadOnlyField()
    
    class Meta:
        model = EventType
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class EventTypeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = [
            'name', 'description', 'duration', 'location_type', 'location_details',
            'buffer_time_before', 'buffer_time_after', 'max_bookings_per_day',
            'min_notice_time', 'max_advance_time', 'color', 'image', 'custom_questions'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        event_type = EventType.objects.create(**validated_data)
        
        # Create default booking page
        BookingPage.objects.create(
            event_type=event_type,
            page_title=f"Book a {event_type.name}",
            welcome_message=f"Schedule a {event_type.name} with {event_type.user.full_name}",
            thank_you_message="Thank you for booking! You'll receive a confirmation email shortly."
        )
        
        return event_type


class EventTypeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = [
            'name', 'description', 'duration', 'location_type', 'location_details',
            'buffer_time_before', 'buffer_time_after', 'max_bookings_per_day',
            'min_notice_time', 'max_advance_time', 'color', 'image', 'custom_questions',
            'is_active'
        ]


class EventTypeListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing event types"""
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)
    location_type_display = serializers.CharField(source='get_location_type_display', read_only=True)
    
    class Meta:
        model = EventType
        fields = [
            'id', 'name', 'description', 'duration', 'duration_display',
            'location_type', 'location_type_display', 'color', 'image',
            'is_active', 'created_at', 'updated_at'
        ]