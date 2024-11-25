import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')  # Replace 'your_project_name' with your actual project name

# Setup Django
django.setup()

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Create or retrieve token for a specific user (replace 'admin' with the correct username)
user = User.objects.get(username='admin')
token, created = Token.objects.get_or_create(user=user)
print(token.key)