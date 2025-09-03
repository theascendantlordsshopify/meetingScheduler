from django.urls import path
from . import views

urlpatterns = [
    # Event Types
    path('', views.EventTypeListCreateView.as_view(), name='event-type-list-create'),
    path('<int:pk>/', views.EventTypeDetailView.as_view(), name='event-type-detail'),
    path('<int:pk>/duplicate/', views.duplicate_event_type, name='event-type-duplicate'),
    path('stats/', views.event_type_stats, name='event-type-stats'),
    
    # Event Type Availability
    path('<int:event_type_id>/availability/', views.EventTypeAvailabilityListCreateView.as_view(), name='event-type-availability-list'),
    path('availability/<int:pk>/', views.EventTypeAvailabilityDetailView.as_view(), name='event-type-availability-detail'),
    
    # Booking Pages
    path('<int:event_type_id>/booking-page/', views.BookingPageDetailView.as_view(), name='booking-page-detail'),
]