# permissions.py
    
from rest_framework import permissions
from .models import RemoteNode
from rest_framework.permissions import BasePermission


class AllowAuthenticatedOrAllowAny(BasePermission):
    """
    Custom permission to allow authenticated and unauthenticated users.
    """

    def has_permission(self, request, view):
        # Allow access for all users, regardless of authentication
        return True  # This will always return True
    

class IsAuthenticatedOrNode(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow if user is authenticated normally
        if isinstance(request.user, RemoteNode):
            return True
        
        # Then check for regular authenticated user
        if hasattr(request.user, 'is_authenticated'):
            return request.user.is_authenticated
            
        return False