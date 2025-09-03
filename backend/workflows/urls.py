from django.urls import path
from . import views

urlpatterns = [
    # Workflows
    path('', views.WorkflowListCreateView.as_view(), name='workflow-list-create'),
    path('<int:pk>/', views.WorkflowDetailView.as_view(), name='workflow-detail'),
    path('<int:pk>/duplicate/', views.duplicate_workflow, name='workflow-duplicate'),
    path('<int:pk>/activate/', views.activate_workflow, name='workflow-activate'),
    path('<int:pk>/pause/', views.pause_workflow, name='workflow-pause'),
    path('<int:pk>/test/', views.test_workflow, name='workflow-test'),
    path('<int:pk>/analytics/', views.workflow_analytics, name='workflow-analytics'),
    
    # Workflow Executions
    path('<int:workflow_id>/executions/', views.WorkflowExecutionListView.as_view(), name='workflow-execution-list'),
    
    # Templates and Components
    path('templates/', views.WorkflowTemplateListView.as_view(), name='workflow-template-list'),
    path('templates/create/', views.create_workflow_from_template, name='workflow-from-template'),
    path('actions/', views.WorkflowActionListView.as_view(), name='workflow-action-list'),
    path('triggers/', views.WorkflowTriggerListView.as_view(), name='workflow-trigger-list'),
    
    # Statistics
    path('stats/', views.workflow_stats, name='workflow-stats'),
]