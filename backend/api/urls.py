from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API documentation and health check
urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('version/', views.api_version, name='api-version'),
]