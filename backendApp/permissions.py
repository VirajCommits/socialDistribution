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
        print("Checking permissions...")
        
        # Allow if user is authenticated normally
        if request.user.is_authenticated:
            return True
        
        # Allow if the request is coming from a RemoteNode
        # Assuming you have a way to identify the RemoteNode, e.g., through a specific header or attribute
        # This part needs to be defined based on your application's logic
        if hasattr(request, 'remote_node') and isinstance(request.remote_node, RemoteNode):
            return True
            
        return False