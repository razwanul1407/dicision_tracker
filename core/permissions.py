from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        elif hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        
        return False


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsManagementUser(permissions.BasePermission):
    """
    Allows access to admin and management users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'management']
        )


class IsProjectUser(permissions.BasePermission):
    """
    Allows access to all authenticated users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'management', 'project_user']
        )


class CanManageProject(permissions.BasePermission):
    """
    Allows project management only to creator or admin.
    """

    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_admin:
            return True
        
        # Management users can only manage their own projects
        if request.user.is_management:
            return obj.created_by == request.user
        
        # Project users can only view
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False


class CanManageEvent(permissions.BasePermission):
    """
    Allows event management to organizer, project creator, or admin.
    """

    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_admin:
            return True
        
        # Event organizer can manage
        if obj.organizer == request.user:
            return True
        
        # Project creator can manage events in their project
        if request.user.is_management and obj.project.created_by == request.user:
            return True
        
        # Project users can only view
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False


class CanUpdateDeliverable(permissions.BasePermission):
    """
    Allows deliverable updates by assigned user, decision creator, or admin.
    """

    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_admin:
            return True
        
        # Assigned user can update progress and notes
        if obj.assigned_to == request.user:
            return True
        
        # Decision creator can manage deliverable
        if obj.decision.created_by == request.user:
            return True
        
        # Project creator can manage deliverables in their project
        if (request.user.is_management and 
            obj.decision.event.project.created_by == request.user):
            return True
        
        # Others can only view
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False