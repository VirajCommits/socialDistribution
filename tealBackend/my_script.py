# create_token.py

import os
import django

# Set the environment variable to your Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tealBackend.settings')  # Replace with your actual project name

# Set up Django
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Get the user instance
user = User.objects.get(username='your_username')  # Replace 'your_username' with the actual username

# Create or get the token
token, created = Token.objects.get_or_create(user=user)

# Print the token key
print(f'Token for user {user.username}: {token.key}')
