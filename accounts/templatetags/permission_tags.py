from django import template

register = template.Library()

@register.filter
def has_permission(user, permission_name):
    """Check if user has specific permission"""
    if not user.is_authenticated:
        return False
    
    # Admin and management users have all permissions
    if user.is_admin or user.is_management:
        return True
    
    # Project users check specific permissions
    if user.is_project_user:
        return getattr(user, permission_name, False)
    
    return False

@register.simple_tag
def user_can(user, permission_name):
    """Simple tag version for checking permissions"""
    return has_permission(user, permission_name)

@register.inclusion_tag('partials/permission_badge.html')
def permission_status(user, permission_name, label):
    """Show permission status badge for management interface"""
    has_perm = has_permission(user, permission_name)
    return {
        'has_permission': has_perm,
        'permission_name': permission_name,
        'label': label,
        'user': user
    }