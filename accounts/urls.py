from django.urls import path
from .views import (
    CustomLoginView, custom_logout_view, register, profile,
    user_management, UserCreateView, UserRoleUpdateView, UserDetailView,
    toggle_user_status, system_settings
)

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    
    # Admin user management
    path('admin/users/', user_management, name='user_management'),
    path('admin/users/create/', UserCreateView.as_view(), name='user_create'),
    path('admin/users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('admin/users/<int:pk>/role/', UserRoleUpdateView.as_view(), name='user_role_update'),
    path('admin/users/<int:user_id>/toggle-status/', toggle_user_status, name='toggle_user_status'),
    path('admin/settings/', system_settings, name='system_settings'),
]