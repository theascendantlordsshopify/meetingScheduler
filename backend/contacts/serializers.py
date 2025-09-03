from rest_framework import serializers
from .models import Contact, ContactTag, ContactGroup, ContactInteraction, ContactCustomField, ContactCustomFieldValue


class ContactTagSerializer(serializers.ModelSerializer):
    contact_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactTag
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

    def get_contact_count(self, obj):
        return obj.contacts.count()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ContactCustomFieldValueSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='custom_field.name', read_only=True)
    field_type = serializers.CharField(source='custom_field.field_type', read_only=True)
    
    class Meta:
        model = ContactCustomFieldValue
        fields = ['id', 'custom_field', 'field_name', 'field_type', 'value', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')


class ContactInteractionSerializer(serializers.ModelSerializer):
    interaction_type_display = serializers.CharField(source='get_interaction_type_display', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = ContactInteraction
        fields = '__all__'
        read_only_fields = ('contact', 'user', 'created_at', 'updated_at')


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    tags = ContactTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=ContactTag.objects.none(),
        source='tags',
        write_only=True
    )
    custom_field_values = ContactCustomFieldValueSerializer(many=True, read_only=True)
    recent_interactions = serializers.SerializerMethodField()
    total_meetings = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('request'):
            user = self.context['request'].user
            self.fields['tag_ids'].queryset = ContactTag.objects.filter(user=user)

    def get_recent_interactions(self, obj):
        recent = obj.interactions.all()[:3]
        return ContactInteractionSerializer(recent, many=True).data

    def get_total_meetings(self, obj):
        from meetings.models import Meeting
        return Meeting.objects.filter(invitee_email=obj.email).count()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ContactListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing contacts"""
    full_name = serializers.ReadOnlyField()
    tags = ContactTagSerializer(many=True, read_only=True)
    total_meetings = serializers.SerializerMethodField()
    last_meeting_date = serializers.SerializerMethodField()
    upcoming_meeting = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = [
            'id', 'full_name', 'email', 'company', 'job_title', 'phone',
            'tags', 'total_meetings', 'last_meeting_date', 'upcoming_meeting',
            'last_contacted_at', 'created_at', 'updated_at'
        ]

    def get_total_meetings(self, obj):
        from meetings.models import Meeting
        return Meeting.objects.filter(invitee_email=obj.email).count()

    def get_last_meeting_date(self, obj):
        from meetings.models import Meeting
        last_meeting = Meeting.objects.filter(
            invitee_email=obj.email,
            status='completed'
        ).order_by('-start_time').first()
        return last_meeting.start_time.date() if last_meeting else None

    def get_upcoming_meeting(self, obj):
        from meetings.models import Meeting
        from django.utils import timezone
        
        upcoming = Meeting.objects.filter(
            invitee_email=obj.email,
            start_time__gte=timezone.now(),
            status__in=['confirmed', 'pending']
        ).order_by('start_time').first()
        
        if upcoming:
            return {
                'date': upcoming.start_time.date(),
                'title': upcoming.title
            }
        return None


class ContactCreateSerializer(serializers.ModelSerializer):
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=ContactTag.objects.none(),
        source='tags',
        required=False
    )
    
    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'company', 'job_title',
            'department', 'website', 'linkedin_url', 'notes', 'address_line1',
            'address_line2', 'city', 'state', 'postal_code', 'country',
            'preferred_contact_method', 'timezone', 'language', 'tag_ids'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('request'):
            user = self.context['request'].user
            self.fields['tag_ids'].queryset = ContactTag.objects.filter(user=user)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ContactGroupSerializer(serializers.ModelSerializer):
    contact_count = serializers.ReadOnlyField()
    contacts = ContactListSerializer(many=True, read_only=True)
    contact_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Contact.objects.none(),
        source='contacts',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ContactGroup
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('request'):
            user = self.context['request'].user
            self.fields['contact_ids'].queryset = Contact.objects.filter(user=user)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ContactCustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactCustomField
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BulkContactImportSerializer(serializers.Serializer):
    """Serializer for bulk importing contacts"""
    contacts_data = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of contact objects"
    )

    def validate_contacts_data(self, value):
        """Validate the contacts data structure"""
        required_fields = ['first_name', 'last_name', 'email']
        
        for i, contact_data in enumerate(value):
            for field in required_fields:
                if field not in contact_data or not contact_data[field]:
                    raise serializers.ValidationError(
                        f"Contact {i+1}: {field} is required"
                    )
            
            # Validate email format
            email = contact_data.get('email')
            if email:
                from django.core.validators import validate_email
                try:
                    validate_email(email)
                except:
                    raise serializers.ValidationError(
                        f"Contact {i+1}: Invalid email format"
                    )
        
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        contacts_data = validated_data['contacts_data']
        
        created_contacts = []
        errors = []
        
        for i, contact_data in enumerate(contacts_data):
            try:
                # Check if contact already exists
                existing = Contact.objects.filter(
                    user=user, 
                    email=contact_data['email']
                ).first()
                
                if existing:
                    errors.append(f"Contact {i+1}: Email already exists")
                    continue
                
                contact = Contact.objects.create(
                    user=user,
                    **contact_data
                )
                created_contacts.append(contact)
                
            except Exception as e:
                errors.append(f"Contact {i+1}: {str(e)}")
        
        return {
            'created_count': len(created_contacts),
            'error_count': len(errors),
            'errors': errors,
            'contacts': ContactListSerializer(created_contacts, many=True).data
        }