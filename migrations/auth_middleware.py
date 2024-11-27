from django.http import JsonResponse
from django.contrib.auth import authenticate, login

class HeaderAuthenticationMiddleware:
    """
    Middleware to authenticate a user based on username and password in headers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the headers contain the username and password
        username = request.headers.get('X-Username')
        password = request.headers.get('X-Password')

        if username and password:
            # Attempt to authenticate the user
            user = authenticate(username=username, password=password)
            if user:
                # Log in the user for this request
                login(request, user)
            else:
                # Authentication failed, return a 401 response
                return JsonResponse({"error": "Invalid credentials"}, status=401)

        # Proceed to the view if authentication succeeded or no credentials were provided
        response = self.get_response(request)
        return response
