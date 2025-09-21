from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('management/', views.management_dashboard, name='management_dashboard'),
    path('project-user/', views.project_user_dashboard, name='project_user_dashboard'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('reports/', views.reports_view, name='reports'),
    
    # API endpoints
    path('api/calendar-events/', views.calendar_events_api, name='calendar_events_api'),
    path('api/user-projects/', views.user_projects_api, name='user_projects_api'),
]