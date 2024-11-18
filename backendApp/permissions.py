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
        if request.user and request.user.is_authenticated:
            return True
            
        # Allow if request comes from authenticated node
        return isinstance(request.user, RemoteNode)