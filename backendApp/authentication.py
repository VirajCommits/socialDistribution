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
            print("username is: ", username)
            print("password is: ", password)
        except:
            raise exceptions.AuthenticationFailed('Invalid basic auth credentials')

        try:
            print("going inside try:, username: ", username)
            # Check if node exists and credentials match
            all_nodes = RemoteNode.objects.all()
            for node in all_nodes:
                print("ALLL NODES:", f"ID: {node.id}, Username: {node.username}, URL: {node.url}, Active: {node.active}, Password: {node.password}")
            remotenode = RemoteNode.objects.get(username=username, password=password, active=True)
        except RemoteNode.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such node exists')

        return (remotenode, None)