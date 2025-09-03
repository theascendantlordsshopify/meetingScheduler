from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from .models import Contact, ContactTag, ContactGroup, ContactInteraction, ContactCustomField
from .serializers import (
    ContactSerializer, ContactListSerializer, ContactCreateSerializer,
    ContactTagSerializer, ContactGroupSerializer, ContactInteractionSerializer,
    ContactCustomFieldSerializer, BulkContactImportSerializer
)


class ContactListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tags', 'company', 'preferred_contact_method', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'company', 'job_title']
    ordering_fields = ['first_name', 'last_name', 'company', 'created_at', 'last_contacted_at']
    ordering = ['first_name', 'last_name']

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user).prefetch_related('tags')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContactCreateSerializer
        return ContactListSerializer


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


class ContactTagListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['name']

    def get_queryset(self):
        return ContactTag.objects.filter(user=self.request.user)


class ContactTagDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactTagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ContactTag.objects.filter(user=self.request.user)


class ContactGroupListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['name']

    def get_queryset(self):
        return ContactGroup.objects.filter(user=self.request.user).prefetch_related('contacts')


class ContactGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ContactGroup.objects.filter(user=self.request.user)


class ContactInteractionListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['interaction_type', 'contact']
    ordering = ['-interaction_date']

    def get_queryset(self):
        contact_id = self.kwargs.get('contact_id')
        return ContactInteraction.objects.filter(
            contact_id=contact_id,
            contact__user=self.request.user
        )

    def perform_create(self, serializer):
        contact_id = self.kwargs.get('contact_id')
        contact = Contact.objects.get(id=contact_id, user=self.request.user)
        serializer.save(contact=contact, user=self.request.user)


class ContactCustomFieldListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactCustomFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['field_type', 'is_active', 'is_required']
    ordering = ['name']

    def get_queryset(self):
        return ContactCustomField.objects.filter(user=self.request.user)


class ContactCustomFieldDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactCustomFieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ContactCustomField.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_import_contacts(request):
    """Bulk import contacts from CSV or JSON data"""
    serializer = BulkContactImportSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_tag_contacts(request):
    """Add tags to multiple contacts"""
    contact_ids = request.data.get('contact_ids', [])
    tag_ids = request.data.get('tag_ids', [])
    
    if not contact_ids or not tag_ids:
        return Response(
            {'error': 'contact_ids and tag_ids are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify contacts belong to user
    contacts = Contact.objects.filter(
        id__in=contact_ids,
        user=request.user
    )
    
    if contacts.count() != len(contact_ids):
        return Response(
            {'error': 'Some contacts not found or not owned by user'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify tags belong to user
    tags = ContactTag.objects.filter(
        id__in=tag_ids,
        user=request.user
    )
    
    if tags.count() != len(tag_ids):
        return Response(
            {'error': 'Some tags not found or not owned by user'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Add tags to contacts
    for contact in contacts:
        contact.tags.add(*tags)
    
    return Response({
        'message': f'Tags added to {contacts.count()} contacts',
        'contacts_updated': contacts.count()
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def bulk_delete_contacts(request):
    """Delete multiple contacts"""
    contact_ids = request.data.get('contact_ids', [])
    
    if not contact_ids:
        return Response(
            {'error': 'contact_ids are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify contacts belong to user
    contacts = Contact.objects.filter(
        id__in=contact_ids,
        user=request.user
    )
    
    deleted_count = contacts.count()
    contacts.delete()
    
    return Response({
        'message': f'{deleted_count} contacts deleted',
        'deleted_count': deleted_count
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def contact_stats(request):
    """Get contact statistics"""
    user = request.user
    
    total_contacts = Contact.objects.filter(user=user).count()
    active_contacts = Contact.objects.filter(user=user, is_active=True).count()
    
    # Contacts by company
    companies = Contact.objects.filter(user=user).exclude(
        company=''
    ).values('company').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Contacts by tag
    tags = ContactTag.objects.filter(user=user).annotate(
        contact_count=Count('contacts')
    ).order_by('-contact_count')[:5]
    
    # Recent contacts
    recent_contacts = Contact.objects.filter(user=user).order_by('-created_at')[:5]
    
    return Response({
        'total_contacts': total_contacts,
        'active_contacts': active_contacts,
        'top_companies': list(companies),
        'top_tags': ContactTagSerializer(tags, many=True).data,
        'recent_contacts': ContactListSerializer(recent_contacts, many=True).data,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_contacts(request):
    """Advanced contact search"""
    query = request.GET.get('q', '')
    
    if not query:
        return Response({'contacts': []})
    
    contacts = Contact.objects.filter(
        user=request.user
    ).filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(company__icontains=query) |
        Q(job_title__icontains=query)
    )[:10]
    
    return Response({
        'contacts': ContactListSerializer(contacts, many=True).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def merge_contacts(request):
    """Merge duplicate contacts"""
    primary_contact_id = request.data.get('primary_contact_id')
    duplicate_contact_ids = request.data.get('duplicate_contact_ids', [])
    
    if not primary_contact_id or not duplicate_contact_ids:
        return Response(
            {'error': 'primary_contact_id and duplicate_contact_ids are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        primary_contact = Contact.objects.get(
            id=primary_contact_id,
            user=request.user
        )
        
        duplicate_contacts = Contact.objects.filter(
            id__in=duplicate_contact_ids,
            user=request.user
        )
        
        # Merge interactions
        ContactInteraction.objects.filter(
            contact__in=duplicate_contacts
        ).update(contact=primary_contact)
        
        # Merge tags
        for duplicate in duplicate_contacts:
            primary_contact.tags.add(*duplicate.tags.all())
        
        # Delete duplicates
        duplicate_contacts.delete()
        
        return Response({
            'message': f'Merged {len(duplicate_contact_ids)} contacts into primary contact',
            'primary_contact': ContactSerializer(primary_contact).data
        })
        
    except Contact.DoesNotExist:
        return Response(
            {'error': 'Primary contact not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_contacts(request):
    """Export contacts to CSV format"""
    contacts = Contact.objects.filter(user=request.user)
    
    # Apply filters if provided
    tag_ids = request.GET.getlist('tags')
    if tag_ids:
        contacts = contacts.filter(tags__id__in=tag_ids).distinct()
    
    company = request.GET.get('company')
    if company:
        contacts = contacts.filter(company__icontains=company)
    
    # TODO: Generate CSV export
    # This would typically use Django's CSV response or a task queue for large exports
    
    return Response({
        'message': 'Export functionality would be implemented here',
        'contact_count': contacts.count(),
        'export_url': None  # Would contain download URL
    })