from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom User model with role-based permissions"""
    
    USER_ROLES = [
        ('admin', 'Admin'),
        ('management', 'Management User'),
        ('project_user', 'Project User'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=USER_ROLES, 
        default='project_user'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Project User Permissions (controlled by management)
    can_view_projects = models.BooleanField(default=True, help_text="Can view assigned projects")
    can_view_events = models.BooleanField(default=True, help_text="Can view and participate in events")
    can_view_decisions = models.BooleanField(default=False, help_text="Can view project decisions")
    can_manage_deliverables = models.BooleanField(default=True, help_text="Can manage assigned deliverables")
    can_track_progress = models.BooleanField(default=True, help_text="Can track task progress")
    can_use_time_tracker = models.BooleanField(default=False, help_text="Can use time tracking features")
    can_view_reports = models.BooleanField(default=False, help_text="Can view personal reports")
    can_view_calendar = models.BooleanField(default=True, help_text="Can access calendar view")
    can_manage_invitations = models.BooleanField(default=True, help_text="Can manage event invitations")
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_management(self):
        return self.role == 'management'
    
    @property
    def is_project_user(self):
        return self.role == 'project_user'
    
    def has_permission(self, permission_name):
        """Check if user has specific permission"""
        if self.is_admin or self.is_management:
            return True  # Admin and management have all permissions
        
        if self.is_project_user:
            return getattr(self, permission_name, False)
        
        return False
    
    def grant_permission(self, permission_name):
        """Grant a specific permission to project user"""
        if hasattr(self, permission_name):
            setattr(self, permission_name, True)
            self.save()
            return True
        return False
    
    def revoke_permission(self, permission_name):
        """Revoke a specific permission from project user"""
        if hasattr(self, permission_name):
            setattr(self, permission_name, False)
            self.save()
            return True
        return False
    
    class Meta:
        db_table = 'auth_user'
