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
        # Log the request user for debugging
        print("request user:", request.user)
        
        # Check if the user is a RemoteNode
        if isinstance(request.user, RemoteNode):
            print("Authenticated as RemoteNode")
            return True
        
        
        # If neither, deny access
        print("Access denied")
        return False