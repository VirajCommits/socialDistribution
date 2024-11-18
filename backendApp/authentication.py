from rest_framework import authentication
from rest_framework import exceptions
from .models import RemoteNode

class NodeBasicAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        print("Authenticate is called.")
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
        except:
            raise exceptions.AuthenticationFailed('Invalid basic auth credentials')

        try:
            print("going inside try:, username: ", username)
            # Check if node exists and credentials match
            all_nodes = RemoteNode.objects.all()
            for node in all_nodes:
                print("ALLL NODES:", node)
            node = RemoteNode.objects.get(username=username, password=password, active=True)
            print("Node: ", node)
        except RemoteNode.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such node exists')

        return (node, None)