"""
URL configuration for MeetXccelerate project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/events/', include('events.urls')),
    path('api/meetings/', include('meetings.urls')),
    path('api/availability/', include('availability.urls')),
    path('api/contacts/', include('contacts.urls')),
    path('api/workflows/', include('workflows.urls')),
    path('api/integrations/', include('integrations.urls')),
    path('api/notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)