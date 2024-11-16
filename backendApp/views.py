from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import AdminSettings
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from .models import Author, Post, Comment, Like, FollowRequest, RemoteNode
from django.shortcuts import get_object_or_404
from .utils import connect_to_remote_node
from urllib.parse import urlparse
from django.shortcuts import render
from urllib.parse import unquote
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import AuthorSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import markdown2
from .serializers import FollowRequestSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
import threading
import time
import requests
from django.utils import timezone
from .models import Author, GitHubPost, Post

def defaultPath(request):
    return render(request, "index.html")

@swagger_auto_schema(
    method='post',
    operation_summary="Create a new post for a specific author",
    operation_description="""
    Use this endpoint to create a new post for the author specified by `author_serial`. 
    Send a POST request with the post data in the request body. 
    Required fields: title, content. Optional field: published.
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the post (Required)'),
            'content': openapi.Schema(type=openapi.TYPE_STRING, description='Content of the post (Required)'),
            'published': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Date and time when the post was published (Optional)'),
        },
        required=['title', 'content'],  # Specify required fields
    ),
    responses={
        201: openapi.Response(
            'Created',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, description='Post ID'),
                    'author_id': openapi.Schema(type=openapi.TYPE_STRING, description='Author ID'),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the post'),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, description='Content of the post'),
                    'published': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Date and time when the post was published'),
                },
            )
        ),
        400: openapi.Response(
            'Bad Request',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'errors': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        additional_properties=openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                    )
                }
            )
        ),
    },
    tags=["Posts"]
)
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

    data = request.data.copy()

    # Fetch the author instance
    author = get_object_or_404(Author, uuid=author_serial)

    # Set the 'author_id' field to the author's ID (URL)
    data["author_id"] = author.uuid  # This will be accepted by the serializer

    if 'content' in data:
        data['content'] = markdown2.markdown(
            data['content'], extras=["fenced-code-blocks", "tables"])

    if 'title' in data:
        data['title'] = markdown2.markdown(
            data['title'], extras=["fenced-code-blocks", "tables"])

    if 'description' in data:
        data['description'] = markdown2.markdown(data['description'], extras=[
                                                 "fenced-code-blocks", "tables"])
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def vueTest(request):
    return render(request, "index.html")

@swagger_auto_schema(
    method='GET',
    operation_summary="Retrieve a specific post",
    operation_description="Retrieve details of a post specified by post_serial for the given author.",
    responses={
        200: openapi.Response(
            description="Post details",
            schema=PostSerializer(),
        ),
        404: "Post not found"
    },
    tags=["Posts"]
)
@swagger_auto_schema(
    method='DELETE',
    operation_summary="Delete a specific post",
    operation_description="Delete a post specified by post_serial for the given author.",
    responses={
        204: "Post deleted successfully",
        404: "Post not found"
    },
    tags=["Posts"]
)
@swagger_auto_schema(
    method='PUT',
    operation_summary="Update a specific post",
    operation_description="Update details of a post specified by post_serial for the given author.",
    request_body=PostSerializer,
    responses={
        200: openapi.Response(
            description="Post updated",
            schema=PostSerializer(),
        ),
        400: "Invalid request data",
        404: "Post not found"
    },
    tags=["Posts"]
)
@swagger_auto_schema(
    method='POST',
    operation_summary="Like or comment on a post",
    operation_description="Like a post or add a comment to it, depending on the action specified in the URL.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'author_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the author'),
            'post_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the post'),
            'content': openapi.Schema(type=openapi.TYPE_STRING, description='Content of the comment (if applicable)'),
        },
        required=['author_id', 'post_id']
    ),
    responses={
        201: openapi.Response(
            description="Like created or comment added",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
        ),
        400: "Invalid request data"
    },
    tags=["Posts"]
)
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

    # If the request is a GET and no action is specified, return the post details
    if request.method == "GET" and not action:
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Handle "like" action for POST request
    if action == "like":
        if request.method == "POST":
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

    # Handle fetching likes
    if action == "likes":
        if request.method == "GET":
            likes = Like.objects.filter(post=post).order_by("-published")
            serializer = LikeSerializer(likes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # Handle comments if specified in the URL
    elif action == "comments":
        if request.method == "GET":
            # Filter comments based on visibility rules
            current_user = request.user
            if post.visibility == "FRIENDS":
                # Check if the current user is a friend or the post's author
                is_friend = (
                    current_user in author.followers.all()
                    and current_user in author.following.all()
                )
                if not (is_friend or current_user == author):
                    # If the current user is not a friend or the post's author, filter out comments
                    return Response(
                        {"detail": "You are not authorized to view these comments."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # Return all comments, as visibility rules are satisfied
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
        data = request.data
        if "content" in data:
            markdown_content = data["content"]
            html_content = markdown2.markdown(
                markdown_content, extras=["fenced-code-blocks", "tables"]
            )
            # Replace Markdown with HTML for saving
            data["content"] = html_content

        serializer = PostSerializer(post, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # If the action doesn't match any known value, return an error
    return Response({"detail": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Post a comment on a specific post",
    operation_description="API to handle posting a comment for a specific post by post_id.",
    manual_parameters=[
        openapi.Parameter(
            'post_id',
            openapi.IN_PATH,
            description="UUID of the post to comment on",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'content': openapi.Schema(type=openapi.TYPE_STRING, description='Content of the comment'),
            'contentType': openapi.Schema(type=openapi.TYPE_STRING, description='Type of content (e.g., text/plain)'),
        },
        required=['content', 'contentType']
    ),
    responses={
        201: openapi.Response(
            description="Comment posted successfully.",
            schema=CommentSerializer()
        ),
        400: openapi.Response(
            description="Invalid input data.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                    'content': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                    # Add other fields as needed based on your serializer errors
                }
            )
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Comments"]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_comment(request, post_id):
    """
    API to handle posting a comment for a specific post by post_id.
    """
    post = get_object_or_404(Post, id=post_id)
    author = request.user

    data = request.data.copy()
    data["author_id"] = str(author.id)
    data["post_id"] = str(post.id)

    serializer = CommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Like a specific post",
    operation_description="API to handle liking a specific post by post_id.",
    manual_parameters=[
        openapi.Parameter(
            'post_id',
            openapi.IN_PATH,
            description="UUID of the post to like",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'author_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the author liking the post', read_only=True),
            'post_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the post being liked', read_only=True),
            'post': openapi.Schema(type=openapi.TYPE_STRING, description='Reference to the post', read_only=True),
        },
        required=['author_id', 'post_id', 'post']
    ),
    responses={
        201: openapi.Response(
            description="Post liked successfully.",
            schema=LikeSerializer()
        ),
        400: openapi.Response(
            description="Invalid input data or already liked post.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Likes"]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    """
    API to handle liking a specific post by post_id.
    """
    post = get_object_or_404(Post, id=post_id)
    author = request.user

    # Check if the user has already liked the post
    existing_like = Like.objects.filter(post=post, author=author).first()
    if existing_like:
        return Response(
            {"detail": "You have already liked this post."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = {
        "author_id": str(author.id),
        "post_id": str(post.id),
        "post": post.id,
    }

    serializer = LikeSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_summary="Fetch comments for a specific post",
    operation_description="API to fetch comments for a specific post by post_id.",
    manual_parameters=[
        openapi.Parameter(
            'post_id',
            openapi.IN_PATH,
            description="UUID of the post to fetch comments for",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully fetched comments.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, description='Comment ID'),
                        'author_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the comment author'),
                        'post_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the post'),
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description='Comment content'),
                        'published': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Timestamp of when the comment was published'),
                    }
                )
            )
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Comments"]
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stream_page_comments(request, post_id):
    """
    API to fetch comments for a specific post by post_id.
    """
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by("-published")
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data, status=200)

@swagger_auto_schema(
    method='get',
    operation_summary="Fetch likes for a specific post",
    operation_description="API to fetch likes for a specific post by post_id.",
    manual_parameters=[
        openapi.Parameter(
            'post_id',
            openapi.IN_PATH,
            description="UUID of the post to fetch likes for",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully fetched likes.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, description='Like ID'),
                        'author_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the user who liked the post'),
                        'post_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the post'),
                        'published': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Timestamp of when the like was made'),
                    }
                )
            )
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Likes"]
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stream_page_likes(request, post_id):
    """
    API to fetch likes for a specific post by post_id.
    """
    post = get_object_or_404(Post, id=post_id)
    likes = Like.objects.filter(post=post).order_by("-published")
    serializer = LikeSerializer(likes, many=True)
    return Response(serializer.data, status=200)


@swagger_auto_schema(
    method='GET',
    operation_summary="Retrieve all posts for a specific author",
    operation_description="Fetch all posts created by the author specified by author_serial.",
    manual_parameters=[
        openapi.Parameter(
            'author_serial',
            openapi.IN_PATH,
            description="UUID of the author whose posts you want to retrieve",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="A list of posts for the specified author",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'type': openapi.Schema(type=openapi.TYPE_STRING, example='posts'),
                    'items': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                            'id': openapi.Schema(type=openapi.TYPE_STRING, example='post_id_here'),
                            'author_id': openapi.Schema(type=openapi.TYPE_STRING, example='author_id_here'),
                            'title': openapi.Schema(type=openapi.TYPE_STRING, example='Sample Post Title'),
                            'content': openapi.Schema(type=openapi.TYPE_STRING, example='Post content goes here...'),
                            'published': openapi.Schema(type=openapi.TYPE_STRING, example='2023-01-01T00:00:00Z'),
                        })
                    )
                }
            )
        ),
        404: "Author not found"
    },
    tags=["Posts"]
)
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


@swagger_auto_schema(
    method='POST',
    operation_summary="Send a follow request to an author",
    operation_description="Send a follow request from the currently authenticated user to the specified author.",
    manual_parameters=[
        openapi.Parameter(
            'author_uuid',
            openapi.IN_PATH,
            description="UUID of the author to whom the follow request is sent",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        201: openapi.Response(
            description="Follow request sent successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, example='Follow request sent.')
                }
            )
        ),
        400: openapi.Response(
            description="Bad Request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, example='You are already following this author.')
                }
            )
        ),
        404: "Author not found"
    },
    tags=["Follow Requests"]
)
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

    # Check if already following
    if current_author in target_author.followers.all():
        return Response(
            {'detail': 'You are already following this author.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if a pending request already exists
    existing_request = FollowRequest.objects.filter(
        actor=current_author,
        object=target_author,
        accepted=False
    ).exists()

    if existing_request:
        return Response(
            {'detail': 'A follow request is already pending.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create new follow request
    follow_request = FollowRequest.objects.create(
        actor=current_author,
        object=target_author
    )

    # Notify through WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{target_author.uuid}",
        {
            'type': 'follow_request_notification',
            'count': FollowRequest.objects.filter(
                object=target_author,
                accepted=False
            ).count(),
            'message': f'{current_author.displayName} sent you a follow request'
        }
    )

    return Response({'detail': 'Follow request sent.'}, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='POST',
    operation_summary="Accept a follow request from an author",
    operation_description="Accept a follow request from the specified author.",
    manual_parameters=[
        openapi.Parameter(
            'author_uuid',
            openapi.IN_PATH,
            description="UUID of the author who sent the follow request",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Follow request accepted successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, example='Follow request accepted.')
                }
            )
        ),
        400: openapi.Response(
            description="Bad Request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, example='This author is already following you.')
                }
            )
        ),
        404: openapi.Response(
            description="Follow request not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, example='Follow request no longer exists or has already been resolved.')
                }
            )
        )
    },
    tags=["Follow Requests"]
)
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

    # Check if request still exists and hasn't been resolved
    follow_request = FollowRequest.objects.filter(
        actor=requesting_author,
        object=current_author,
        accepted=False
    ).first()

    if not follow_request:
        return Response(
            {'detail': 'Follow request no longer exists or has already been resolved.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if already following
    if requesting_author in current_author.followers.all():
        follow_request.delete()
        return Response(
            {'detail': 'This author is already following you.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Accept the request
    follow_request.accepted = True
    follow_request.save()

    # Add to followers
    current_author.followers.add(requesting_author)
    current_author.save()

    # Notify the requesting author through WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{requesting_author.uuid}",
        {
            'type': 'follow_request_notification',
            'message': f'{current_author.displayName} accepted your follow request',
            'status': 'accepted'
        }
    )

    return Response({'detail': 'Follow request accepted.'}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='POST',
    operation_summary="Decline a follow request from an author",
    operation_description="Decline a follow request from the specified author.",
    manual_parameters=[
        openapi.Parameter(
            'author_uuid',
            openapi.IN_PATH,
            description="UUID of the author who sent the follow request",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Follow request declined successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, example='Follow request declined.')
                }
            )
        ),
        404: openapi.Response(
            description="Follow request not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, example='Follow request no longer exists or has already been resolved.')
                }
            )
        )
    },
    tags=["Follow Requests"]
)
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

    # Check if request still exists and hasn't been resolved
    follow_requests = FollowRequest.objects.filter(
        actor=requesting_author,
        object=current_author,
        accepted=False
    )

    if not follow_requests.exists():
        return Response(
            {'detail': 'Follow request no longer exists or has already been resolved.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Delete all pending requests from this user
    follow_requests.delete()

    # Notify the requesting author through WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{requesting_author.uuid}",
        {
            'type': 'follow_request_notification',
            'count': FollowRequest.objects.filter(object=requesting_author, accepted=False).count(),
            'message': 'Follow request declined'
        }
    )

    return Response({'detail': 'Follow request declined.'}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='GET',
    operation_summary="Retrieve pending follow requests",
    operation_description="Get all follow requests that are pending for the authenticated user.",
    responses={
        200: openapi.Response(
            description="List of pending follow requests",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                        'actor': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                            'uuid': openapi.Schema(type=openapi.TYPE_STRING, example='author-uuid'),
                            'displayName': openapi.Schema(type=openapi.TYPE_STRING, example='Author Name')
                        }),
                        'object': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                            'uuid': openapi.Schema(type=openapi.TYPE_STRING, example='current-author-uuid'),
                            'displayName': openapi.Schema(type=openapi.TYPE_STRING, example='Current Author Name')
                        }),
                        'accepted': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, example='2024-01-01T12:00:00Z')
                    }
                )
            )
        ),
        401: openapi.Response(
            description="Unauthorized access",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, example='Authentication credentials were not provided.')
                }
            )
        )
    },
    tags=["Follow Requests"]
)
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
    # Filter to only show pending follow requests
    pending_requests = FollowRequest.objects.filter(
        object=current_author, accepted=False)
    serializer = FollowRequestSerializer(pending_requests, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="GET",
    operation_summary="Retrieve all authors excluding the current user",
    operation_description="Fetch a list of all authors, excluding the currently authenticated user. Each author object will include their followers.",
    responses={
        200: openapi.Response(
            description="List of authors excluding the current user",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "uuid": openapi.Schema(
                            type=openapi.TYPE_STRING, example="author-uuid"
                        ),
                        "displayName": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Author Name"
                        ),
                        "followers": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_STRING, example="follower-uuid"
                            ),
                        ),
                    },
                ),
            ),
        ),
        401: openapi.Response(
            description="Unauthorized access",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Authentication credentials were not provided.",
                    )
                },
            ),
        ),
        500: openapi.Response(
            description="Internal server error",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="An error occurred while fetching authors.",
                    )
                },
            ),
        ),
    },
    tags=["Authors"],
)
@api_view(["GET"])
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

