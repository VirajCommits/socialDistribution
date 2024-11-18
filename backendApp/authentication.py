from rest_framework import authentication
from rest_framework import exceptions
from .models import RemoteNode

class NodeBasicAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Get credentials from header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Basic '):
            return None

        import base64
        try:
            # Decode base64 credentials
            auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = auth_decoded.split(':')
        except:
            raise exceptions.AuthenticationFailed('Invalid basic auth credentials')

        try:
            # Check if node exists and credentials match
            node = RemoteNode.objects.get(username=username, password=password, active=True)
        except RemoteNode.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such node exists')

        return (node, None)