# backendApp/authentication.py

from rest_framework import authentication
from rest_framework import exceptions
from .models import RemoteNode

class RemoteNodeUser:
    """
    A wrapper class to make RemoteNode compatible with Django's authentication system.
    """
    def __init__(self, node):
        self.node = node

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __getattr__(self, attr):
        return getattr(self.node, attr)

class NodeBasicAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for RemoteNode using Basic Authentication.
    """
    def authenticate(self, request):
        # Get credentials from header
        print("WE INSIDE AUTHENTICATE -------------------------------------------------------------------- ")
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Basic '):
            return False  # Return None to allow other authentication classes to attempt

        import base64
        try:
            # Decode base64 credentials
            auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = auth_decoded.split(':', 1)
            print("Username:", username)
            print("Password:", password)
        except (base64.binascii.Error, ValueError):
            raise exceptions.AuthenticationFailed('Invalid basic auth credentials')

        try:
            print("Authenticating user:", username)
            # Fetch the RemoteNode instance
            remotenode = RemoteNode.objects.get(username=username, password=password, active=True)
        except RemoteNode.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such node exists')

        # Wrap the RemoteNode instance
        user = RemoteNodeUser(remotenode)
        return (user, None)
