from django.urls import path
from . import views

urlpatterns = [
    # Meetings
    path('', views.MeetingListCreateView.as_view(), name='meeting-list-create'),
    path('<int:pk>/', views.MeetingDetailView.as_view(), name='meeting-detail'),
    path('<int:pk>/cancel/', views.cancel_meeting, name='meeting-cancel'),
    path('<int:pk>/confirm/', views.confirm_meeting, name='meeting-confirm'),
    
    # Meeting views
    path('upcoming/', views.UpcomingMeetingsView.as_view(), name='upcoming-meetings'),
    path('today/', views.TodaysMeetingsView.as_view(), name='todays-meetings'),
    path('stats/', views.meeting_stats, name='meeting-stats'),
    
    # Meeting notes
    path('<int:meeting_id>/notes/', views.MeetingNoteListCreateView.as_view(), name='meeting-notes'),
    
    # Meeting attachments
    path('<int:meeting_id>/attachments/', views.MeetingAttachmentListCreateView.as_view(), name='meeting-attachments'),
    
    # Public booking
    path('book/', views.PublicBookingView.as_view(), name='public-booking'),
    path('availability/<int:event_type_id>/', views.public_event_availability, name='public-availability'),
]