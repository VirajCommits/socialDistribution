from rest_framework import authentication
from rest_framework import exceptions
from .models import RemoteNode

class NodeBasicAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for RemoteNode using Basic Authentication.
    Requires Basic Authentication - will fail if not provided.
    """
    def authenticate(self, request):
        # Get credentials from header
        print("REQUEST IN NODE BASIC AUTHENTICATIONjknefknlknvelke: " , request)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        # Fail if no authorization header or not Basic auth
        if not auth_header or not auth_header.startswith('Basic '):
            raise exceptions.AuthenticationFailed('Basic authentication credentials required')

        import base64
        try:
            # Decode base64 credentials
            auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = auth_decoded.split(':', 1)
            
            # Fetch the RemoteNode instance
            remotenode = RemoteNode.objects.get(username=username, password=password, active=True)
            
            # If we get here, authentication was successful
            return (remotenode, None)
            
        except (base64.binascii.Error, ValueError):
            raise exceptions.AuthenticationFailed('Invalid basic auth credentials')
        except RemoteNode.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such node exists')