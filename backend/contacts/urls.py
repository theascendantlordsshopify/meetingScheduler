from django.urls import path
from . import views

urlpatterns = [
    # Contacts
    path('', views.ContactListCreateView.as_view(), name='contact-list-create'),
    path('<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
    path('search/', views.search_contacts, name='contact-search'),
    path('stats/', views.contact_stats, name='contact-stats'),
    path('export/', views.export_contacts, name='contact-export'),
    
    # Bulk operations
    path('bulk-import/', views.bulk_import_contacts, name='bulk-import-contacts'),
    path('bulk-tag/', views.bulk_tag_contacts, name='bulk-tag-contacts'),
    path('bulk-delete/', views.bulk_delete_contacts, name='bulk-delete-contacts'),
    path('merge/', views.merge_contacts, name='merge-contacts'),
    
    # Contact Tags
    path('tags/', views.ContactTagListCreateView.as_view(), name='contact-tag-list'),
    path('tags/<int:pk>/', views.ContactTagDetailView.as_view(), name='contact-tag-detail'),
    
    # Contact Groups
    path('groups/', views.ContactGroupListCreateView.as_view(), name='contact-group-list'),
    path('groups/<int:pk>/', views.ContactGroupDetailView.as_view(), name='contact-group-detail'),
    
    # Contact Interactions
    path('<int:contact_id>/interactions/', views.ContactInteractionListCreateView.as_view(), name='contact-interaction-list'),
    
    # Custom Fields
    path('custom-fields/', views.ContactCustomFieldListCreateView.as_view(), name='contact-custom-field-list'),
    path('custom-fields/<int:pk>/', views.ContactCustomFieldDetailView.as_view(), name='contact-custom-field-detail'),
]