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
    

class IsNode(permissions.BasePermission):
    def has_permission(self, request, view):
        # Log the request user for debugging
        
        # Check if the user is a RemoteNode
        if isinstance(request.user, RemoteNode):
            return True
        
        # If neither, deny access
        return False