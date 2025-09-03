from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'version': '1.0.0'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_version(request):
    """API version information"""
    return Response({
        'version': '1.0.0',
        'name': 'MeetXccelerate API',
        'description': 'Smart scheduling and meeting management platform',
        'documentation_url': '/api/docs/',
        'debug': settings.DEBUG
    })