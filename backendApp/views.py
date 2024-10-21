from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer
from .models import Author , Post
from django.shortcuts import get_object_or_404
from urllib.parse import urlparse
# from django.utils import timezone
from django.shortcuts import render
from urllib.parse import unquote
from rest_framework.pagination import PageNumberPagination

from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import AuthorSerializer

def defaultPath(request):
    return render(request, "index.html")
@api_view(['POST'])
def create_post(request, author_serial):
    """
    Create a new post for a specific author.

    When to Use:
    - Use this endpoint to create a new post for the author specified by author_serial.

    How to Use:
    - Send a POST request with the post data in the request body.

    Why to Use:
    - To add new content created by an author to the database.

    Why Not to Use:
    - If the author does not exist or if required fields are missing from the request.
    
    Request Body:
    {
      "title": "string",         # Title of the post (Required)
      "content": "string",       # Content of the post (Required)
      "published": "datetime"    # Date and time when the post was published (Optional)
    }

    Response:
    - 201 Created:
    {
      "id": "string",
      "author_id": "string",
      "title": "string",
      "content": "string",
      "published": "datetime"
    }
    - 400 Bad Request:
    {
      "errors": {
        "field": ["error message"]
      }
    }
    """
    author_serial = unquote(author_serial)
    print("This is serial author --------------------  " , author_serial)
    
    data = request.data.copy()
    
    # Fetch the author instance
    author = get_object_or_404(Author, uuid=author_serial)
    
    # Set the 'author_id' field to the author's ID (URL)
    data['author_id'] = author.uuid  # This will be accepted by the serializer
    
    # Remove fields that are generated automatically and 'author' if present
    data.pop('id', None)
    data.pop('page', None)
    data.pop('published', None)
    data.pop('type', None)
    data.pop('author', None)
    
    serializer = PostSerializer(data=data)
    
    if serializer.is_valid():
        post = serializer.save()
        response_serializer = PostSerializer(post)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    else:
        print(serializer.errors)  # For debugging purposes
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
def vueTest(request):
    return render(request, "index.html")


@api_view(['GET' , 'DELETE' , 'PUT'])
def post_detail(request , author_serial , post_serial):
    """
    Retrieve, update, or delete a specific post.

    When to Use:
    - Use this endpoint to manage individual posts based on their unique identifiers.

    How to Use:
    - Send a GET request to retrieve the post.
    - Send a PUT request with updated data to modify the post.
    - Send a DELETE request to remove the post.

    Why to Use:
    - To manage posts effectively.

    Why Not to Use:
    - If the post or author does not exist.

    Response:
    - 200 OK for GET and PUT:
    {
      "id": "string",
      "author_id": "string",
      "title": "string",
      "content": "string",
      "published": "datetime"
    }
    - 204 No Content for DELETE
    """
    print("GET POST DETAILS>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" , author_serial , post_serial)

    # Get the author object or return 404 if not found
    author = get_object_or_404(Author, uuid=author_serial)
    
    # Get the post object or return 404 if not found
    post = get_object_or_404(Post, author=author, id=post_serial)

    print("FOUND AURTHOR AND POSTTTT")

    print(" --------- " , request.method)
    # Handle GET request
    if request.method == 'GET':
        # Directly allow access to public and friends-only posts
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # Handle DELETE request
    elif request.method == 'DELETE':
        # Directly delete the post without requiring authentication
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    # Handle PUT request
    elif request.method == 'PUT':
        # Directly update the post without requiring authentication
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_posts(request, author_serial):
    """
    Retrieve all posts for a specific author.

    When to Use:
    - Use this endpoint to list all posts made by a specific author.

    How to Use:
    - Send a GET request.

    Why to Use:
    - To fetch all posts related to an author.

    Why Not to Use:
    - If the author does not exist.

    Response:
    {
      "type": "posts",
      "items": [
        {
          "id": "string",
          "author_id": "string",
          "title": "string",
          "content": "string",
          "published": "datetime"
        }
      ]
    }
    """
    print(" ----------- >>>>" , author_serial)
    author_serial = unquote(author_serial)
    author = get_object_or_404(Author, uuid=author_serial)
    posts = Post.objects.filter(author=author).order_by('-published')

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Adjust as needed
    result_page = paginator.paginate_queryset(posts, request)

    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response({'type': 'posts', 'items': serializer.data})
class SignupView(APIView):
    """
    Create a new author account.

    When to Use:
    - Use this endpoint to register a new author.

    How to Use:
    - Send a POST request with user data.

    Why to Use:
    - To allow new authors to register.

    Why Not to Use:
    - If required fields are missing or if the user already exists.

    Request Body:
    {
      "username": "string",  # Unique username (Required)
      "password": "string",  # User's password (Required)
      "email": "string"      # User's email address (Required)
    }

    Response:
    - 201 Created:
    {
      "refresh": "string",   # Refresh token for authentication
      "access": "string",     # Access token for authentication
      "user": {
        "id": "string",
        "username": "string",
        "email": "string"
      }
    }
    - 400 Bad Request:
    {
      "errors": {
        "field": ["error message"]
      }
    }
    """
    def post(self, request):
        serializer = AuthorSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': AuthorSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    Authenticate an existing author.

    When to Use:
    - Use this endpoint for user login.

    How to Use:
    - Send a POST request with credentials.

    Why to Use:
    - To log in and receive authentication tokens.

    Why Not to Use:
    - If credentials are invalid.

    Request Body:
    {
      "username": "string",  # User's username (Required)
      "password": "string"   # User's password (Required)
    }

    Response:
    - 200 OK:
    {
      "refresh": "string",   # Refresh token for authentication
      "access": "string",     # Access token for authentication
      "user": {
        "id": "string",
        "username": "string",
        "email": "string"
      }
    }
    - 401 Unauthorized:
    {
      "error": "Invalid Credentials"
    }
    """
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': AuthorSerializer(user).data
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
