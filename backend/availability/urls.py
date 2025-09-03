from django.urls import path
from . import views

urlpatterns = [
    # Weekly Availability
    path('weekly/', views.WeeklyAvailabilityListCreateView.as_view(), name='weekly-availability-list'),
    path('weekly/<int:pk>/', views.WeeklyAvailabilityDetailView.as_view(), name='weekly-availability-detail'),
    path('weekly/bulk-update/', views.bulk_update_weekly_availability, name='bulk-update-weekly-availability'),
    
    # Date Overrides
    path('overrides/', views.DateOverrideListCreateView.as_view(), name='date-override-list'),
    path('overrides/<int:pk>/', views.DateOverrideDetailView.as_view(), name='date-override-detail'),
    
    # Buffer Time
    path('buffer-time/', views.BufferTimeView.as_view(), name='buffer-time'),
    
    # Timezone Settings
    path('timezone/', views.TimeZoneSettingsView.as_view(), name='timezone-settings'),
    
    # Calendar Integrations
    path('calendars/', views.CalendarIntegrationListCreateView.as_view(), name='calendar-integration-list'),
    path('calendars/<int:pk>/', views.CalendarIntegrationDetailView.as_view(), name='calendar-integration-detail'),
    path('calendars/<int:integration_id>/sync/', views.sync_calendar, name='sync-calendar'),
    
    # Availability Rules
    path('rules/', views.AvailabilityRuleListCreateView.as_view(), name='availability-rule-list'),
    path('rules/<int:pk>/', views.AvailabilityRuleDetailView.as_view(), name='availability-rule-detail'),
    
    # Overview and utilities
    path('overview/', views.availability_overview, name='availability-overview'),
    path('check/', views.check_availability, name='check-availability'),
    path('stats/', views.availability_stats, name='availability-stats'),
]