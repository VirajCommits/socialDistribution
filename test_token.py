import os
import django
from django.core.management import call_command
from rest_framework_simplejwt.tokens import AccessToken
from backendApp.models import Author

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tealBackend.settings")
django.setup()

# Ensure migrations are applied
call_command("migrate", verbosity=0)

# Create a test user dynamically
test_user = Author.objects.create_user(username="testuser", password="password123")

# Generate a fresh token
token = AccessToken.for_user(test_user)  # Keep it as an AccessToken object


