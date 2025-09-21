from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def role_required(roles):
    """
    Decorator to check if user has required role
    Args:
        roles: list of roles or single role string
    """
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard:index')
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator for admin-only views"""
    return role_required('admin')(view_func)


def management_required(view_func):
    """Decorator for management and admin users"""
    return role_required(['admin', 'management'])(view_func)


def require_management_or_admin(view_func):
    """Alias for management_required for clarity"""
    return management_required(view_func)


def project_user_required(view_func):
    """Decorator for all authenticated users"""
    return role_required(['admin', 'management', 'project_user'])(view_func)


class RolePermissionMixin:
    """Mixin for class-based views to check user roles"""
    
    required_roles = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if self.required_roles:
            if isinstance(self.required_roles, str):
                required_roles = [self.required_roles]
            else:
                required_roles = self.required_roles
            
            if request.user.role not in required_roles:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard:index')
        
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RolePermissionMixin):
    """Mixin for admin-only views"""
    required_roles = ['admin']


class ManagementRequiredMixin(RolePermissionMixin):
    """Mixin for management and admin users"""
    required_roles = ['admin', 'management']


class ProjectUserRequiredMixin(RolePermissionMixin):
    """Mixin for all authenticated users"""
    required_roles = ['admin', 'management', 'project_user']