from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import PostSerializer, FollowRequestSerializer
from .models import Author, Post, FollowRequest

from .serializers import PostSerializer,CommentSerializer,LikeSerializer
from .models import Author, Post,Comment,Like

from django.shortcuts import get_object_or_404
from urllib.parse import urlparse
from django.shortcuts import render
from urllib.parse import unquote
import re
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import AuthorSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

def defaultPath(request):
    return render(request, "index.html")


@api_view(["POST"])
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
    print("This is serial author --------------------  ", author_serial)

    data = request.data.copy()

    # Fetch the author instance
    author = get_object_or_404(Author, uuid=author_serial)

    # Set the 'author_id' field to the author's ID (URL)
    data["author_id"] = author.uuid  # This will be accepted by the serializer

    # Remove fields that are generated automatically and 'author' if present
    data.pop("id", None)
    data.pop("page", None)
    data.pop("published", None)
    data.pop("type", None)
    data.pop("author", None)

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

@api_view(["GET", "DELETE", "PUT", "POST"])
def post_detail(request, author_serial, post_serial):
    """
    Retrieve, update, delete, or interact with a specific post.

    When to Use:
    - Use this endpoint to manage individual posts and their likes or comments.

    How to Use:
    - Send a GET request to retrieve the post.
    - Send a DELETE request to remove the post.
    - Send a PUT request to update the post.
    - Send a POST request with "like" or "comments" action to interact with likes or comments.

    Why to Use:
    - To manage posts and their interactions effectively.

    Why Not to Use:
    - If the post or author does not exist, or if the action is not recognized.
    """
    # print("Request received")
    # Strip the trailing slash and check for any segments like "like" or "comments"
    segments = post_serial.split("/")
    post_id = segments[0]  # This should be the UUID part
    action = segments[1] if len(segments) > 1 else None
    parsed_author_id = urlparse(author_serial).path.split("/")[-1]

    # Get the author and post objects
    author = get_object_or_404(Author, uuid=parsed_author_id)
    post = get_object_or_404(Post, author=author, id=post_id)

   
    if request.method == "GET" and not action:
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if action == "like":
        if request.method == "POST":
            # Handle like creation directly here
            data = request.data.copy()
            data["author_id"] = str(author.id)
            data["post_id"] = str(post.id)
            data["post"] = post.id

            serializer = LikeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print("Serializer errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if action == "likes":
        if request.method == "GET":
            likes = Like.objects.filter(post=post).order_by("-published")
            serializer = LikeSerializer(likes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # Handle comments if specified in the URL
    elif action == "comments":
        print("Handling comments")
        if request.method == "GET":
            comments = Comment.objects.filter(post=post).order_by("-published")
            serializer = CommentSerializer(
                comments, many=True, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "POST":
            # Handle comment creation directly here
            data = request.data.copy()
            data["author_id"] = str(author.id)
            data["post_id"] = str(post.id)

            serializer = CommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print("Serializer errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle DELETE request
    elif request.method == "DELETE" and not action:
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Handle PUT request for updating the post
    elif request.method == "PUT" and not action:
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # If the action doesn't match any known value
    return Response({"detail": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_all_posts(request, author_serial):
    """
    Retrieve all posts by a specific author.

    When to Use:
    - Use this endpoint to view all posts associated with an author.

    How to Use:
    - Send a GET request.

    Response:
    - 200 OK:
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

    Pagination:
    - The response is paginated. Use the `page` query parameter to navigate through pages.
    """
    print(" ----------- >>>>", author_serial)
    author_serial = unquote(author_serial)
    author = get_object_or_404(Author, uuid=author_serial)
    posts = Post.objects.filter(author=author).order_by("-edited_at")

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Adjust as needed
    result_page = paginator.paginate_queryset(posts, request)

    serializer = PostSerializer(result_page, many=True)

    return paginator.get_paginated_response({'type': 'posts', 'items': serializer.data})


# Follow Request Actions
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_follow_request(request, author_uuid):
    """
    Send a follow request to another author.

    When to Use:
    - Use this endpoint to establish a follow relationship.

    How to Use:
    - Send a POST request with no additional data.

    Why to Use:
    - To request to follow another author.

    Why Not to Use:
    - If you are trying to follow yourself or if a request has already been sent.

    Response:
    - 201 Created:
    {
      "actor": "string",
      "object": "string",
      "summary": "string"
    }
    - 400 Bad Request:
    {
      "detail": "Error message"
    }
    """
    current_author = request.user
    target_author = get_object_or_404(Author, uuid=author_uuid)

    if current_author == target_author:
        return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

    if FollowRequest.objects.filter(actor=current_author, object=target_author).exists():
        return Response({'detail': 'Follow request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

    follow_request = FollowRequest.objects.create(
        actor=current_author,
        object=target_author,
        summary=f"{current_author.displayName} wants to follow {target_author.displayName}"
    )
    return Response(FollowRequestSerializer(follow_request).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_follow_request(request, author_uuid):
    """
    Accept a follow request.

    When to Use:
    - Use this endpoint to confirm a follow relationship.

    How to Use:
    - Send a POST request.

    Response:
    - 200 OK:
    {
      "detail": "Follow request accepted."
    }
    """
    current_author = request.user
    print("This is the current author:", current_author)
    requesting_author = get_object_or_404(Author, uuid=author_uuid)

    follow_request = get_object_or_404(FollowRequest, actor=requesting_author, object=current_author)
    current_author.followers.add(requesting_author)  # Add to followers
    follow_request.delete()  # Remove the follow request
    return Response({'detail': 'Follow request accepted.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decline_follow_request(request, author_uuid):
    """
    Decline a follow request.

    When to Use:
    - Use this endpoint to reject a follow relationship.

    How to Use:
    - Send a POST request.

    Response:
    - 200 OK:
    {
      "detail": "Follow request declined."
    }
    """
    current_author = request.user
    requesting_author = get_object_or_404(Author, uuid=author_uuid)

    follow_request = get_object_or_404(FollowRequest, actor=requesting_author, object=current_author)
    follow_request.delete()  # Remove the follow request
    return Response({'detail': 'Follow request declined.'}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_follow_requests(request):
    """
    Retrieve follow requests sent to the current author.

    When to Use:
    - Use this endpoint to view incoming follow requests.

    How to Use:
    - Send a GET request.

    Response:
    - 200 OK:
    [
      {
        "actor": "string",
        "object": "string",
        "summary": "string"
      }
    ]
    """
    current_author = request.user
    requests = FollowRequest.objects.filter(object=current_author)
    serializer = FollowRequestSerializer(requests, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_authors(request):
    """
    Retrieve all authors except the current user.

    When to Use:
    - Use this endpoint to view all authors in the system.

    How to Use:
    - Send a GET request.

    Response:
    - 200 OK:
    [
      {
        "id": "string",
        "username": "string",
        "email": "string"
      }
    ]
    """
    current_author = request.user
    authors = Author.objects.exclude(id=current_author.id)
    serializer = AuthorSerializer(authors, many=True)
    return Response(serializer.data)


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
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": AuthorSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
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
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": AuthorSerializer(user).data,
                }
            )
        return Response(
            {"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

