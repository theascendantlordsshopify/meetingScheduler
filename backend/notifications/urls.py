from django.urls import path
from . import views

urlpatterns = [
    # Notifications
    path('', views.NotificationListCreateView.as_view(), name='notification-list-create'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('unread/', views.UnreadNotificationsView.as_view(), name='unread-notifications'),
    path('categories/', views.notification_categories, name='notification-categories'),
    
    # Notification actions
    path('<int:pk>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete-notification'),
    path('mark-all-read/', views.mark_all_read, name='mark-all-notifications-read'),
    
    # Bulk operations
    path('bulk-send/', views.send_bulk_notification, name='send-bulk-notification'),
    
    # Preferences
    path('preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
    
    # Templates
    path('templates/', views.NotificationTemplateListView.as_view(), name='notification-template-list'),
    
    # Statistics
    path('stats/', views.notification_stats, name='notification-stats'),
]