from rest_framework import serializers
from django.utils import timezone
from .models import Meeting, MeetingNote, MeetingAttachment, MeetingRescheduleRequest
from events.serializers import EventTypeListSerializer


class MeetingNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    
    class Meta:
        model = MeetingNote
        fields = '__all__'
        read_only_fields = ('meeting', 'author', 'created_at', 'updated_at')


class MeetingAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = MeetingAttachment
        fields = '__all__'
        read_only_fields = ('meeting', 'uploaded_by', 'filename', 'file_size', 'content_type', 'created_at')


class MeetingRescheduleRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = MeetingRescheduleRequest
        fields = '__all__'
        read_only_fields = ('meeting', 'requested_by', 'created_at', 'updated_at')


class MeetingSerializer(serializers.ModelSerializer):
    event_type_details = EventTypeListSerializer(source='event_type', read_only=True)
    organizer_name = serializers.CharField(source='organizer.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_today = serializers.ReadOnlyField()
    notes = MeetingNoteSerializer(many=True, read_only=True)
    attachments = MeetingAttachmentSerializer(many=True, read_only=True)
    reschedule_requests = MeetingRescheduleRequestSerializer(many=True, read_only=True)
    
    class Meta:
        model = Meeting
        fields = '__all__'
        read_only_fields = ('organizer', 'confirmation_token', 'created_at', 'updated_at', 'cancelled_at')

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError("End time must be after start time")
            
            if start_time < timezone.now():
                raise serializers.ValidationError("Meeting cannot be scheduled in the past")
        
        return attrs


class MeetingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = [
            'event_type', 'title', 'description', 'start_time', 'end_time',
            'timezone', 'location_type', 'location_details', 'meeting_url',
            'meeting_id', 'meeting_password', 'invitee_name', 'invitee_email',
            'invitee_phone', 'invitee_timezone', 'custom_responses'
        ]

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError("End time must be after start time")
            
            if start_time < timezone.now():
                raise serializers.ValidationError("Meeting cannot be scheduled in the past")
        
        return attrs


class MeetingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = [
            'title', 'description', 'start_time', 'end_time', 'timezone',
            'location_type', 'location_details', 'meeting_url', 'meeting_id',
            'meeting_password', 'status', 'cancellation_reason'
        ]

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError("End time must be after start time")
        
        return attrs


class MeetingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing meetings"""
    event_type_name = serializers.CharField(source='event_type.name', read_only=True)
    organizer_name = serializers.CharField(source='organizer.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_today = serializers.ReadOnlyField()
    
    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'start_time', 'end_time', 'timezone', 'status',
            'status_display', 'invitee_name', 'invitee_email', 'event_type_name',
            'organizer_name', 'duration_minutes', 'is_upcoming', 'is_today',
            'created_at', 'updated_at'
        ]


class PublicMeetingBookingSerializer(serializers.ModelSerializer):
    """Serializer for public booking (no authentication required)"""
    class Meta:
        model = Meeting
        fields = [
            'event_type', 'title', 'description', 'start_time', 'timezone',
            'invitee_name', 'invitee_email', 'invitee_phone', 'invitee_timezone',
            'custom_responses'
        ]

    def create(self, validated_data):
        event_type = validated_data['event_type']
        validated_data['organizer'] = event_type.user
        validated_data['location_type'] = event_type.location_type
        validated_data['location_details'] = event_type.location_details
        
        # Calculate end time
        from datetime import timedelta
        start_time = validated_data['start_time']
        validated_data['end_time'] = start_time + timedelta(minutes=event_type.duration)
        
        return super().create(validated_data)

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        
        if start_time and start_time < timezone.now():
            raise serializers.ValidationError("Meeting cannot be scheduled in the past")
        
        return attrs