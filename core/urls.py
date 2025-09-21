from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Project URLs
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('my-projects/', views.my_projects, name='my_projects'),
    
    # Event URLs
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/quick-decisions/', views.quick_add_decisions, name='quick_add_decisions'),
    path('my-events/', views.my_events, name='my_events'),
    
    # Decision URLs
    path('decisions/', views.decision_list, name='decision_list'),
    path('decisions/create/', views.decision_create, name='decision_create'),
    path('decisions/<int:pk>/', views.decision_detail, name='decision_detail'),
    path('decisions/<int:pk>/edit/', views.decision_edit, name='decision_edit'),
    path('my-decisions/', views.my_decisions, name='my_decisions'),
    
    # Deliverable URLs
    path('deliverables/', views.deliverable_list, name='deliverable_list'),
    path('deliverables/create/', views.deliverable_create, name='deliverable_create'),
    path('deliverables/<int:pk>/', views.deliverable_detail, name='deliverable_detail'),
    path('deliverables/<int:pk>/update/', views.deliverable_update, name='deliverable_update'),
    path('deliverables/<int:pk>/quick-update/', views.quick_progress_update, name='quick_progress_update'),
    path('my-deliverables/', views.my_deliverables, name='my_deliverables'),
    path('assigned-deliverables/', views.assigned_deliverables, name='assigned_deliverables'),
    
    # Invitation URLs
    path('invitations/', views.invitation_list, name='invitation_list'),
    path('invitations/create/', views.invitation_create, name='invitation_create'),
    path('invitations/<int:pk>/respond/', views.invitation_respond, name='invitation_respond'),
    path('invitations/<int:pk>/respond-ajax/', views.invitation_respond_ajax, name='invitation_respond_ajax'),
    path('my-invitations/', views.my_invitations, name='my_invitations'),
    
    # Management User URLs
    path('management/team-overview/', views.team_overview, name='team_overview'),
    path('management/workload/', views.workload_distribution, name='workload_distribution'),
    
    # Project User URLs
    path('user/task-progress/', views.task_progress, name='task_progress'),
    path('user/time-tracker/', views.time_tracker, name='time_tracker'),
    
    # Permission Management URLs
    path('permissions/', views.manage_user_permissions, name='manage_user_permissions'),
    path('permissions/user/<int:user_id>/', views.user_permissions_detail, name='user_permissions_detail'),
    path('permissions/toggle/', views.toggle_user_permission, name='toggle_user_permission'),
    
    # Notification URLs
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/count/', views.notification_count, name='notification_count'),
    path('notifications/dropdown/', views.notification_dropdown, name='notification_dropdown'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]