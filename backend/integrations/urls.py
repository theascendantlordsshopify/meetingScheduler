from django.urls import path
from . import views

urlpatterns = [
    # Integration Providers
    path('providers/', views.IntegrationProviderListView.as_view(), name='integration-provider-list'),
    path('providers/popular/', views.popular_integrations, name='popular-integrations'),
    
    # User Integrations
    path('', views.UserIntegrationListCreateView.as_view(), name='user-integration-list'),
    path('<int:pk>/', views.UserIntegrationDetailView.as_view(), name='user-integration-detail'),
    path('recently-connected/', views.recently_connected, name='recently-connected-integrations'),
    
    # Integration Actions
    path('connect/', views.connect_integration, name='connect-integration'),
    path('<int:pk>/disconnect/', views.disconnect_integration, name='disconnect-integration'),
    path('<int:pk>/sync/', views.sync_integration, name='sync-integration'),
    path('<int:pk>/test/', views.test_integration, name='test-integration'),
    
    # Integration Logs and Syncs
    path('<int:integration_id>/logs/', views.IntegrationLogListView.as_view(), name='integration-log-list'),
    path('<int:integration_id>/syncs/', views.IntegrationSyncListView.as_view(), name='integration-sync-list'),
    
    # Templates
    path('templates/', views.IntegrationTemplateListView.as_view(), name='integration-template-list'),
    
    # Statistics
    path('stats/', views.integration_stats, name='integration-stats'),
    
    # Webhooks
    path('webhook/<int:integration_id>/<slug:provider_slug>/', views.webhook_handler, name='integration-webhook'),
]