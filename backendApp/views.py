import copy
import uuid
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests
import requests
from .models import AdminSettings
from .serializers import (
    PostSerializer,
    CommentSerializer,
    LikeSerializer,
    FollowRequestSerializer,
    AuthorSerializer,
    InboxSerializer,PublicAuthorSerializer,
)
from .models import Author, Post, Comment, Like, FollowRequest, Inbox , ToWhichItsConnected,GitHubPost

from .authentication import NodeBasicAuthentication
from .permissions import IsAuthenticatedOrNode
from .utils import make_node_request

# from .utils import connect_to_remote_node
from django.shortcuts import get_object_or_404
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
from datetime import datetime

from rest_framework.test import APIRequestFactory
from django.urls import reverse


def defaultPath(request):
    return render(request, "index.html")


@swagger_auto_schema(
    method="post",
    operation_summary="Create a new post for a specific author",
    operation_description="""
    Use this endpoint to create a new post for the author specified by `author_serial`. 
    Send a POST request with the post data in the request body. 
    Required fields: title, content. Optional field: published.
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "title": openapi.Schema(
                type=openapi.TYPE_STRING, description="Title of the post (Required)"
            ),
            "content": openapi.Schema(
                type=openapi.TYPE_STRING, description="Content of the post (Required)"
            ),
            "published": openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                description="Date and time when the post was published (Optional)",
            ),
        },
        required=["title", "content"],  # Specify required fields
    ),
    responses={
        201: openapi.Response(
            "Created",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Post ID"
                    ),
                    "author_id": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Author ID"
                    ),
                    "title": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Title of the post"
                    ),
                    "content": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Content of the post"
                    ),
                    "published": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATETIME,
                        description="Date and time when the post was published",
                    ),
                },
            ),
        ),
        400: openapi.Response(
            "Bad Request",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "errors": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        additional_properties=openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                        ),
                    )
                },
            ),
        ),
    },
    tags=["Posts"],
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

    if "content" in data:
        data["content"] = markdown2.markdown(
            data["content"], extras=["fenced-code-blocks", "tables"]
        )

    if "title" in data:
        data["title"] = markdown2.markdown(
            data["title"], extras=["fenced-code-blocks", "tables"]
        )

    if "description" in data:
        data["description"] = markdown2.markdown(
            data["description"], extras=["fenced-code-blocks", "tables"]
        )
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
    method="GET",
    operation_summary="Retrieve a specific post",
    operation_description="Retrieve details of a post specified by post_serial for the given author.",
    responses={
        200: openapi.Response(
            description="Post details",
            schema=PostSerializer(),
        ),
        404: "Post not found",
    },
    tags=["Posts"],
)
@swagger_auto_schema(
    method="DELETE",
    operation_summary="Delete a specific post",
    operation_description="Delete a post specified by post_serial for the given author.",
    responses={204: "Post deleted successfully", 404: "Post not found"},
    tags=["Posts"],
)
@swagger_auto_schema(
    method="PUT",
    operation_summary="Update a specific post",
    operation_description="Update details of a post specified by post_serial for the given author.",
    request_body=PostSerializer,
    responses={
        200: openapi.Response(
            description="Post updated",
            schema=PostSerializer(),
        ),
        400: "Invalid request data",
        404: "Post not found",
    },
    tags=["Posts"],
)
@swagger_auto_schema(
    method="POST",
    operation_summary="Like or comment on a post",
    operation_description="Like a post or add a comment to it, depending on the action specified in the URL.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "author_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="ID of the author"
            ),
            "post_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="ID of the post"
            ),
            "content": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Content of the comment (if applicable)",
            ),
        },
        required=["author_id", "post_id"],
    ),
    responses={
        201: openapi.Response(
            description="Like created or comment added",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
        400: "Invalid request data",
    },
    tags=["Posts"],
)

@api_view(["GET", "DELETE", "PUT", "POST"])
def post_detail(request, author_serial, post_serial):
    segments = post_serial.split("/")
    post_id = segments[0]
    action = segments[1] if len(segments) > 1 else None
    parsed_author_id = urlparse(author_serial).path.split("/")[-1]

    # Get the author and post objects
    author = get_object_or_404(Author, uuid=parsed_author_id)
    post = get_object_or_404(Post, author=author, id=post_id)

    # Handle GET request for post details
    if request.method == "GET" and not action:
        comments = Comment.objects.filter(post=post).order_by("-published")
        comment_serializer = CommentSerializer(comments, many=True)

        post_serializer = PostSerializer(post)
        return Response({
            "type": "post_detail",
            "post": post_serializer.data,
            "comments": {
                "type": "comments",
                "page": f"http://{request.get_host()}/posts/{post_id}/comments/",
                "id": f"http://{request.get_host()}/posts/{post_id}/comments/",
                "page_number": 1,
                "size": len(comments),
                "count": comments.count(),
                "src": comment_serializer.data,
            },
            "likes": {
                "type": "likes",
                "page": f"http://{request.get_host()}/posts/{post_id}/likes/",
                "id": f"http://{request.get_host()}/posts/{post_id}/likes/",
                "page_number": 1,
                "size": Like.objects.filter(post=post).count(),
                "count": Like.objects.filter(post=post).count(),
                "src": LikeSerializer(
                    Like.objects.filter(post=post).order_by("-published")[:5], many=True
                ).data,
            }
        }, status=status.HTTP_200_OK)

    # Handle POST request for adding comments or likes
    if action == "comments" and request.method == "POST":
        data = request.data.copy()
        data["author_id"] = str(request.user.id)
        data["post_id"] = str(post.id)

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif action == "like" and request.method == "POST":
        data = request.data.copy()
        data["author_id"] = str(request.user.id)
        data["post_id"] = str(post.id)

        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle DELETE request for deleting the post
    if request.method == "DELETE" and not action:
        post.delete()
        return Response({"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    # Handle PUT request for updating the post
    if request.method == "PUT" and not action:
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

    # If the action is unrecognized
    return Response({"detail": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    operation_summary="Post a comment on a specific post",
    operation_description="API to handle posting a comment for a specific post by post_id.",
    manual_parameters=[
        openapi.Parameter(
            "post_id",
            openapi.IN_PATH,
            description="UUID of the post to comment on",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "content": openapi.Schema(
                type=openapi.TYPE_STRING, description="Content of the comment"
            ),
            "contentType": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Type of content (e.g., text/plain)",
            ),
        },
        required=["content", "contentType"],
    ),
    responses={
        201: openapi.Response(
            description="Comment posted successfully.", schema=CommentSerializer()
        ),
        400: openapi.Response(
            description="Invalid input data.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    ),
                    "content": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                    ),
                    # Add other fields as needed based on your serializer errors
                },
            ),
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Comments"],
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_comment(request, comment_id):
    """
    API to handle liking a specific comment by comment_id.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    author = request.user

    # Check if the user has already liked the comment
    if Like.objects.filter(comment=comment, author=author).exists():
        return Response(
            {"detail": "You have already liked this comment."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = {
        "author_id": str(author.id),
        "comment_id": str(comment.id),
    }

    serializer = LikeSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def comment_likes(request, comment_id):
    """
    API to fetch likes for a specific comment by comment_id.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    likes = Like.objects.filter(comment=comment).order_by("-published")
    serializer = LikeSerializer(likes, many=True)
    return Response({
        "type": "likes",
        "page": f"http://{request.get_host()}/comments/{comment_id}/likes",
        "id": f"http://{request.get_host()}/comments/{comment_id}/likes",
        "page_number": 1,
        "size": len(likes),
        "count": likes.count(),
        "src": serializer.data,
    })


@swagger_auto_schema(
    method="post",
    operation_summary="Like a specific post",
    operation_description="API to handle liking a specific post by post_id.",
    manual_parameters=[
        openapi.Parameter(
            "post_id",
            openapi.IN_PATH,
            description="UUID of the post to like",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "author_id": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="ID of the author liking the post",
                read_only=True,
            ),
            "post_id": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="ID of the post being liked",
                read_only=True,
            ),
            "post": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Reference to the post",
                read_only=True,
            ),
        },
        required=["author_id", "post_id", "post"],
    ),
    responses={
        201: openapi.Response(
            description="Post liked successfully.", schema=LikeSerializer()
        ),
        400: openapi.Response(
            description="Invalid input data or already liked post.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Likes"],
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
    method="get",
    operation_summary="Fetch comments for a specific post",
    operation_description="API to fetch comments for a specific post by post_id.",
    manual_parameters=[
        openapi.Parameter(
            "post_id",
            openapi.IN_PATH,
            description="UUID of the post to fetch comments for",
            type=openapi.TYPE_STRING,
            required=True,
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
                        "id": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Comment ID"
                        ),
                        "author_id": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="ID of the comment author",
                        ),
                        "post_id": openapi.Schema(
                            type=openapi.TYPE_STRING, description="ID of the post"
                        ),
                        "content": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Comment content"
                        ),
                        "published": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            description="Timestamp of when the comment was published",
                        ),
                    },
                ),
            ),
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Comments"],
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
    method="get",
    operation_summary="Fetch likes for a specific post",
    operation_description="API to fetch likes for a specific post by post_id.",
    manual_parameters=[
        openapi.Parameter(
            "post_id",
            openapi.IN_PATH,
            description="UUID of the post to fetch likes for",
            type=openapi.TYPE_STRING,
            required=True,
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
                        "id": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Like ID"
                        ),
                        "author_id": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="ID of the user who liked the post",
                        ),
                        "post_id": openapi.Schema(
                            type=openapi.TYPE_STRING, description="ID of the post"
                        ),
                        "published": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            description="Timestamp of when the like was made",
                        ),
                    },
                ),
            ),
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Likes"],
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
    method="GET",
    operation_summary="Retrieve all posts for a specific author",
    operation_description="Fetch all posts created by the author specified by author_serial.",
    manual_parameters=[
        openapi.Parameter(
            "author_serial",
            openapi.IN_PATH,
            description="UUID of the author whose posts you want to retrieve",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="A list of posts for the specified author",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "type": openapi.Schema(type=openapi.TYPE_STRING, example="posts"),
                    "items": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(
                                    type=openapi.TYPE_STRING, example="post_id_here"
                                ),
                                "author_id": openapi.Schema(
                                    type=openapi.TYPE_STRING, example="author_id_here"
                                ),
                                "title": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="Sample Post Title",
                                ),
                                "content": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="Post content goes here...",
                                ),
                                "published": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="2023-01-01T00:00:00Z",
                                ),
                            },
                        ),
                    ),
                },
            ),
        ),
        404: "Author not found",
    },
    tags=["Posts"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_all_posts(request, author_serial):
    print("(((((((((((((((((((((((((((((())))))))))))))))))))))))))))))")
    author_serial = unquote(author_serial)
    author = get_object_or_404(Author, uuid=author_serial)
    posts = Post.objects.filter(author=author).order_by("-edited_at")

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 100  # Adjust as needed
    result_page = paginator.paginate_queryset(posts, request)

    serializer = PostSerializer(result_page, many=True)

    return paginator.get_paginated_response({"type": "posts", "items": serializer.data})


@swagger_auto_schema(
    method="POST",
    operation_summary="Send a follow request to an author",
    operation_description="Send a follow request from the currently authenticated user to the specified author.",
    manual_parameters=[
        openapi.Parameter(
            "author_uuid",
            openapi.IN_PATH,
            description="UUID of the author to whom the follow request is sent",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        201: openapi.Response(
            description="Follow request sent successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, example="Follow request sent."
                    )
                },
            ),
        ),
        400: openapi.Response(
            description="Bad Request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="You are already following this author.",
                    )
                },
            ),
        ),
        404: "Author not found",
    },
    tags=["Follow Requests"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_follow_request(request, author_uuid):
    current_author = request.user  # The one sending the request
    # The one receiving the request
    target_author = get_object_or_404(Author, uuid=author_uuid)

    my_host = request.build_absolute_uri('/').rstrip('/')
    target_host = target_author.host.rstrip('/')
    print("yes>>>>>>>>>>>>>>>>>>>>" , my_host , target_host)

    # Check if already following
    if current_author in target_author.followers.all():
        return Response(
            {"detail": "You are already following this author."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if a pending request already exists
    existing_request = FollowRequest.objects.filter(
        actor=current_author, object=target_author, accepted=False
    ).exists()

    if existing_request:
        return Response(
            {"detail": "A follow request is already pending."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create new follow request
    follow_request = FollowRequest.objects.create(
        actor=current_author, object=target_author
    )

    # Notify through WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{target_author.uuid}",
        {
            "type": "follow_request_notification",
            "count": FollowRequest.objects.filter(
                object=target_author, accepted=False
            ).count(),
            "message": f"{current_author.displayName} sent you a follow request",
        },
    )

    return Response({"detail": "Follow request sent."}, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method="POST",
    operation_summary="Accept a follow request from an author",
    operation_description="Accept a follow request from the specified author.",
    manual_parameters=[
        openapi.Parameter(
            "author_uuid",
            openapi.IN_PATH,
            description="UUID of the author who sent the follow request",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Follow request accepted successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, example="Follow request accepted."
                    )
                },
            ),
        ),
        400: openapi.Response(
            description="Bad Request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="This author is already following you.",
                    )
                },
            ),
        ),
        404: openapi.Response(
            description="Follow request not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Follow request no longer exists or has already been resolved.",
                    )
                },
            ),
        ),
    },
    tags=["Follow Requests"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_follow_request(request, author_uuid):
    current_author = request.user  # The one accepting
    requesting_author = get_object_or_404(
        Author, uuid=author_uuid
    )  # The one who sent request

    # Check if request still exists and hasn't been resolved
    follow_request = FollowRequest.objects.filter(
        actor=requesting_author, object=current_author, accepted=False
    ).first()

    if not follow_request:
        return Response(
            {"detail": "Follow request no longer exists or has already been resolved."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Check if already following
    if requesting_author in current_author.followers.all():
        follow_request.delete()
        return Response(
            {"detail": "This author is already following you."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    post_data = construct_posts_data(current_author)
    print(post_data , requesting_author.host , current_author.host)
    if requesting_author.host != current_author.host:
        # post_data = construct_posts_data(current_author)

        # Send the constructed object to the remote node
        send_data_to_remote_node(requesting_author.host, post_data)

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
            "type": "follow_request_notification",
            "message": f"{current_author.displayName} accepted your follow request",
            "status": "accepted",
        },
    )

    return Response({"detail": "Follow request accepted."}, status=status.HTTP_200_OK)
def send_data_to_remote_node(url, data):
    """
    Send data to the remote node with authentication using the ToWhichItsConnected model.
    """
    # Find the remote node that matches the base URL
    matched_node = None
    for node in ToWhichItsConnected.objects.filter(active=True):
        if url.startswith(node.url):  # Check if the base URL matches
            matched_node = node
            break

    if not matched_node:
        raise ValueError("No matching remote node found for the provided URL.")

    # Extract credentials from the matched node
    username = matched_node.username
    password = matched_node.password

    if not username or not password:
        raise ValueError(f"Username or password not found for node {matched_node.url}.")

    # Set up headers with Basic Authentication
    headers = {
        'Authorization': f'Basic {username}:{password}',  # Use basic auth format
    }

    new_url = url + "inbox/"

    try:
        # Send the POST request to the remote node
        response = requests.post(new_url, json=data, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to send data to {matched_node.url}: {e}")

    return response

@swagger_auto_schema(
    method="POST",
    operation_summary="Decline a follow request from an author",
    operation_description="Decline a follow request from the specified author.",
    manual_parameters=[
        openapi.Parameter(
            "author_uuid",
            openapi.IN_PATH,
            description="UUID of the author who sent the follow request",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Follow request declined successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, example="Follow request declined."
                    )
                },
            ),
        ),
        404: openapi.Response(
            description="Follow request not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Follow request no longer exists or has already been resolved.",
                    )
                },
            ),
        ),
    },
    tags=["Follow Requests"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def decline_follow_request(request, author_uuid):
    current_author = request.user
    requesting_author = get_object_or_404(Author, uuid=author_uuid)

    # Check if request still exists and hasn't been resolved
    follow_requests = FollowRequest.objects.filter(
        actor=requesting_author, object=current_author, accepted=False
    )

    if not follow_requests.exists():
        return Response(
            {"detail": "Follow request no longer exists or has already been resolved."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Delete all pending requests from this user
    follow_requests.delete()

    # Notify the requesting author through WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{requesting_author.uuid}",
        {
            "type": "follow_request_notification",
            "count": FollowRequest.objects.filter(
                object=requesting_author, accepted=False
            ).count(),
            "message": "Follow request declined",
        },
    )

    return Response({"detail": "Follow request declined."}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="GET",
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
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                        "actor": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "uuid": openapi.Schema(
                                    type=openapi.TYPE_STRING, example="author-uuid"
                                ),
                                "displayName": openapi.Schema(
                                    type=openapi.TYPE_STRING, example="Author Name"
                                ),
                            },
                        ),
                        "object": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "uuid": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="current-author-uuid",
                                ),
                                "displayName": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="Current Author Name",
                                ),
                            },
                        ),
                        "accepted": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN, example=False
                        ),
                        "created_at": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            example="2024-01-01T12:00:00Z",
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
    },
    tags=["Follow Requests"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_follow_requests(request):
    current_author = request.user
    # Filter to only show pending follow requests
    pending_requests = FollowRequest.objects.filter(
        object=current_author, accepted=False
    )
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
                    )
                },
            ),
        ),
    },
    tags=["Authors"],
)
@api_view(["GET"])
@authentication_classes([JWTAuthentication, NodeBasicAuthentication])
@permission_classes([IsAuthenticatedOrNode])
def get_all_authors(request):
    try:
        current_author = request.user

        # Exclude the current user, admin users, and superusers
        authors = Author.objects.exclude(id=current_author.id).filter(
            is_staff=False, is_superuser=False
        )

        author_data = []
        for author in authors:
            # Serialize the author data
            serialized_author = AuthorSerializer(author).data

            # Add followers data
            followers = author.followers.all()
            serialized_author["followers"] = [
                str(follower.uuid) for follower in followers
            ]

            author_data.append(serialized_author)

        return Response(author_data)
    except Exception as e:
        import traceback

        print(f"Error in get_all_authors: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method="get",
    operation_summary="Fetch the stream of posts for a specific author",
    operation_description="API to retrieve a stream of posts based on the following relationships of the author.",
    manual_parameters=[
        openapi.Parameter(
            "author_id",
            openapi.IN_PATH,
            description="UUID of the author to fetch the stream for",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully fetched posts.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "count": openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="Total number of posts"
                    ),
                    "next": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="URL to the next page of results",
                    ),
                    "previous": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="URL to the previous page of results",
                    ),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(
                                    type=openapi.TYPE_STRING, description="Post ID"
                                ),
                                "author": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    description="Post author details",
                                    properties={
                                        "id": openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Author ID",
                                        ),
                                        "displayName": openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="Author display name",
                                        ),
                                        "profileImage": openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description="URL to author profile image",
                                        ),
                                    },
                                ),
                                "title": openapi.Schema(
                                    type=openapi.TYPE_STRING, description="Post title"
                                ),
                                "description": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Post description",
                                ),
                                "contentType": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Content type of the post",
                                ),
                                "content": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Main content of the post",
                                ),
                                "visibility": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Visibility of the post",
                                ),
                                "published": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME,
                                    description="Post publication timestamp",
                                ),
                                "repost_count": openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="Count of reposts",
                                ),
                            },
                        ),
                    ),
                },
            ),
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
    },
    tags=["Stream"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stream_page(request, author_id):
    # Get the current author
    current_author = get_object_or_404(Author, uuid=author_id)

    # Authors that the current author is following
    following_authors = current_author.following.all()

    # Authors who are following the current author
    followers = current_author.followers.all()

    # Mutual friends: authors with a mutual following relationship
    mutual_friends = following_authors.filter(id__in=followers.values("id"))

    # Posts from mutual friends with visibility PUBLIC, PRIVATE, UNLISTED, FRIENDS
    mutual_friends_posts = Post.objects.filter(
        author__in=mutual_friends,
        visibility__in=["PUBLIC", "PRIVATE", "UNLISTED", "FRIENDS"],
    )

    # Posts from authors the current author is following (but not mutual friends) with visibility PUBLIC and UNLISTED
    other_following_authors = following_authors.exclude(
        id__in=mutual_friends.values("id")
    )
    other_following_posts = Post.objects.filter(
        author__in=other_following_authors, visibility__in=["PUBLIC", "UNLISTED"]
    )

    # Public posts from any author (visible to everyone)
    public_posts = Post.objects.filter(visibility="PUBLIC")

    # Current author's own posts (including private)
    personal_posts = Post.objects.filter(author=current_author)

    # Combine all posts and avoid duplicates

    all_posts = (
        (public_posts | mutual_friends_posts | other_following_posts | personal_posts)
        .distinct()
        .order_by("-edited_at")
    )

    # Paginate and return response
    paginator = PageNumberPagination()
    paginator.page_size = 100
    result_page = paginator.paginate_queryset(all_posts, request)
    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@swagger_auto_schema(
    method="POST",
    operation_summary="User Signup",
    operation_description="Creates a new user account. The user data must include the necessary fields as defined in the AuthorSerializer.",
    request_body=AuthorSerializer,
    responses={
        201: openapi.Response(
            description="User created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "refresh": openapi.Schema(
                        type=openapi.TYPE_STRING, example="refresh-token"
                    ),
                    "access": openapi.Schema(
                        type=openapi.TYPE_STRING, example="access-token"
                    ),
                    "user": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(
                                type=openapi.TYPE_STRING, example="user-id"
                            ),
                            "username": openapi.Schema(
                                type=openapi.TYPE_STRING, example="username"
                            ),
                            "email": openapi.Schema(
                                type=openapi.TYPE_STRING, example="user@example.com"
                            ),
                            # Add other fields from AuthorSerializer as necessary
                        },
                    ),
                },
            ),
        ),
        400: openapi.Response(
            description="Invalid input",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "errors": openapi.Schema(
                        type=openapi.TYPE_OBJECT
                    )  # Detailed error messages
                },
            ),
        ),
    },
    tags=["Authentication"],
)
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])

def signup(request):
    serializer = AuthorSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Fetch the toggle setting from the database
        settings = AdminSettings.objects.first()
        if settings and not settings.user_approval_required:
            user.is_approved = True  # Automatically approve the user
        else:
            user.is_approved = False  # Require admin approval

        user.save()
        print("user saved")

        # Notify the user about their approval status
        if user.is_approved:
            print("user approved")
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "User created and approved.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": AuthorSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "User created. Your account is pending admin approval.",
                "user": AuthorSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="POST",
    operation_summary="User Login",
    operation_description="Authenticates a user and returns JWT tokens if successful.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(
                type=openapi.TYPE_STRING, example="example_username"
            ),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING, example="example_password"
            ),
        },
        required=["username", "password"],
    ),
    responses={
        200: openapi.Response(
            description="Login successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "refresh": openapi.Schema(
                        type=openapi.TYPE_STRING, example="refresh-token"
                    ),
                    "access": openapi.Schema(
                        type=openapi.TYPE_STRING, example="access-token"
                    ),
                    "user": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(
                                type=openapi.TYPE_STRING, example="user-id"
                            ),
                            "username": openapi.Schema(
                                type=openapi.TYPE_STRING, example="example_username"
                            ),
                            "email": openapi.Schema(
                                type=openapi.TYPE_STRING, example="user@example.com"
                            ),
                            # Add other fields from AuthorSerializer as necessary
                        },
                    ),
                },
            ),
        ),
        401: openapi.Response(
            description="Invalid credentials",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, example="Invalid Credentials"
                    )
                },
            ),
        ),
    },
    tags=["Authentication"],
)
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" , username , password)
    user = authenticate(username=username, password=password)

    print("This is the user:" , user , username , password)

    if user:
        if not user.is_approved:
            return Response(
                {"error": "Your account is pending admin approval."},
                status=status.HTTP_403_FORBIDDEN,
            )

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


@swagger_auto_schema(
    method="get",
    operation_summary="Get all pending outgoing follow requests",
    operation_description="Get all pending follow requests sent by the current user.",
    responses={
        200: openapi.Response(
            description="A list of pending follow requests",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Unique identifier for the follow request",
                        ),
                        "actor": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "uuid": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="UUID of the actor",
                                ),
                                "displayName": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Display name of the actor",
                                ),
                            },
                        ),
                        "object": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "uuid": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="UUID of the target author",
                                ),
                                "displayName": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Display name of the target author",
                                ),
                            },
                        ),
                        "accepted": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            description="Indicates if the follow request is accepted",
                        ),
                    },
                ),
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Follow Requests"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_requests(request):
    """Get all pending follow requests sent by the current user"""
    current_author = request.user
    pending_requests = FollowRequest.objects.filter(
        actor=current_author, accepted=False
    )
    serializer = FollowRequestSerializer(pending_requests, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="delete",
    operation_summary="Remove a follow request",
    operation_description="Remove a pending follow request.",
    manual_parameters=[
        openapi.Parameter(
            "author_uuid",
            openapi.IN_PATH,
            description="UUID of the author whose follow request is to be removed",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Follow request successfully removed.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Confirmation message"
                    )
                },
            ),
        ),
        404: openapi.Response(
            description="No follow request found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Follow Requests"],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_follow_request(request, author_uuid):
    """Remove a pending follow request"""
    current_author = request.user
    target_author = get_object_or_404(Author, uuid=author_uuid)

    follow_requests = FollowRequest.objects.filter(
        actor=current_author, object=target_author, accepted=False
    )

    if not follow_requests.exists():
        return Response(
            {"detail": "No follow request found."}, status=status.HTTP_404_NOT_FOUND
        )

    # Delete all pending requests from this user
    follow_requests.delete()

    # Notify the target author through WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{target_author.uuid}",
        {
            "type": "follow_request_notification",
            "count": FollowRequest.objects.filter(
                object=target_author, accepted=False
            ).count(),
            "message": f"{current_author.displayName} removed their follow request",
        },
    )

    return Response({"detail": "Follow request removed."}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="delete",
    operation_summary="Unfollow an Author",
    operation_description="Unfollow an author.",
    manual_parameters=[
        openapi.Parameter(
            "author_id",
            openapi.IN_PATH,
            description="UUID of the author to unfollow",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully unfollowed the author.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Success message"
                    )
                },
            ),
        ),
        400: openapi.Response(
            description="You are not following this author.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Follow Requests"],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def unfollow_author(request, author_id):
    try:
        target_author = get_object_or_404(Author, uuid=author_id)
        current_author = request.user  # Since your user model is Author

        # Remove from followers
        if current_author in target_author.followers.all():
            target_author.followers.remove(current_author)
            target_author.save()

            # Notify through WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{target_author.uuid}",
                {
                    "type": "follow_request_notification",
                    "count": FollowRequest.objects.filter(
                        object=target_author, accepted=False
                    ).count(),
                    "message": f"{current_author.displayName} unfollowed you",
                },
            )

            return Response(
                {"detail": f"Successfully unfollowed {target_author.displayName}"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "You are not following this author"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Author.DoesNotExist:
        return Response(
            {"detail": "Author not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="Check Relationship Status",
    operation_description="Check the relationship status between the current user and a target author.",
    manual_parameters=[
        openapi.Parameter(
            "author_uuid",
            openapi.IN_PATH,
            description="UUID of the author to check the relationship with",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Relationship status retrieved successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "is_following": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="True if the current user is following the target author",
                    ),
                    "is_followed_by": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="True if the target author is following the current user",
                    ),
                    "is_friend": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="True if both users are following each other",
                    ),
                },
            ),
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Relationships"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_relationship_status(request, author_uuid):
    """Check complete relationship status between current user and target author"""
    try:
        current_author = request.user
        target_author = get_object_or_404(Author, uuid=author_uuid)

        is_following = target_author.followers.filter(id=current_author.id).exists()
        is_followed_by = current_author.followers.filter(id=target_author.id).exists()
        is_friend = is_following and is_followed_by

        return Response(
            {
                "is_following": is_following,
                "is_followed_by": is_followed_by,
                "is_friend": is_friend,
            }
        )
    except Author.DoesNotExist:
        return Response({"error": "Author not found"}, status=404)


@swagger_auto_schema(
    method="get",
    operation_summary="Get Author Statistics",
    operation_description="Retrieve statistics about the specified author's relationships.",
    manual_parameters=[
        openapi.Parameter(
            "author_uuid",
            openapi.IN_PATH,
            description="UUID of the author for whom to retrieve statistics",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Author statistics retrieved successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "followers": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Total number of followers",
                    ),
                    "following": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Total number of users the author is following",
                    ),
                    "friends": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Total number of mutual followers (friends)",
                    ),
                },
            ),
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Author Stats"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_author_stats(request, author_uuid):
    try:
        author = get_object_or_404(Author, uuid=author_uuid)
        followers_count = author.followers.count()
        following_count = author.following.count()
        friends_count = author.followers.filter(
            id__in=author.following.values("id")
        ).count()

        return Response(
            {
                "followers": followers_count,
                "following": following_count,
                "friends": friends_count,
            }
        )
    except Author.DoesNotExist:
        return Response({"error": "Author not found"}, status=404)


@swagger_auto_schema(
    method="post",
    operation_summary="Repost a Post",
    operation_description="Create a repost of an existing post. The original post must be public.",
    manual_parameters=[
        openapi.Parameter(
            "post_id",
            openapi.IN_PATH,
            description="ID of the post to repost",
            type=openapi.TYPE_INTEGER,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Post reposted successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Success message"
                    ),
                    "repost_count": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Updated repost count of the original post",
                    ),
                },
            ),
        ),
        400: openapi.Response(
            description="You have already reposted this post.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        403: openapi.Response(
            description="Post is not public.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Posts"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def repost_post(request, post_id):
    reposted_post = get_object_or_404(Post, id=post_id)

    # Determine the original post
    if reposted_post.is_repost:
        original_post = get_object_or_404(Post, id=reposted_post.original_post_id)
    else:
        original_post = reposted_post

    # Check if the original post is public
    if original_post.visibility != "PUBLIC":
        return Response({"error": "Post is not public."}, status=403)

    # Check if the user has already reposted the original post
    if request.user in original_post.reposted_by.all():
        return Response({"error": "You have already reposted this post."}, status=400)

    # Create a new post for the repost
    new_repost = Post(
        author=request.user,
        title=f"Reposted: {original_post.author.displayName} {original_post.title}",
        description=original_post.description,
        content=original_post.content,
        contentType=original_post.contentType,
        visibility="PUBLIC",
        published=timezone.now(),
        is_repost=True,
        original_post_id=original_post.id,  # Reference the original post ID
    )
    new_repost.save()

    # Track the repost and increment the count
    original_post.reposted_by.add(request.user)
    original_post.repost_count += 1
    original_post.save()

    return Response(
        {
            "message": "Post reposted successfully.",
            "repost_count": original_post.repost_count,
        },
        status=200,
    )


@swagger_auto_schema(
    method="get",
    operation_summary="Get Author Followers",
    operation_description="Retrieve the list of followers for a specific author.",
    manual_parameters=[
        openapi.Parameter(
            "author_uuid",
            openapi.IN_PATH,
            description="UUID of the author to retrieve followers for",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully retrieved followers.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="ID of the author"
                        ),
                        "uuid": openapi.Schema(
                            type=openapi.TYPE_STRING, description="UUID of the author"
                        ),
                        "host": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Host of the author"
                        ),
                        "displayName": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Display name of the author",
                        ),
                        "github": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="GitHub URL of the author",
                        ),
                        "profileImage": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Profile image URL of the author",
                        ),
                        "page": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Page URL of the author",
                        ),
                        "username": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Username of the author",
                        ),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Email of the author"
                        ),
                    },
                ),
            ),
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Authors"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_author_followers(request, author_uuid):
    try:
        author = get_object_or_404(Author, uuid=author_uuid)
        followers = author.followers.all()
        serializer = AuthorSerializer(followers, many=True)
        return Response(serializer.data)
    except Author.DoesNotExist:
        return Response({"error": "Author not found"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def followers_handler(request, author_serial):
    """Get a list of authors who are followers"""
    try:
        author = get_object_or_404(Author, uuid=author_serial)
        followers = author.followers.all()
        serializer = AuthorSerializer(followers, many=True)
        
        response_data = {
            "type": "followers",
            "followers": serializer.data
        }
        return Response(response_data)
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def specific_follower_handler(request, author_serial, foreign_author_fqid):
    """Handle specific follower operations"""
    try:
        author = get_object_or_404(Author, uuid=author_serial)
        # Decode the URL-encoded foreign author ID
        decoded_fqid = unquote(foreign_author_fqid)
        foreign_author = get_object_or_404(Author, id=decoded_fqid)

        if request.method == 'GET':
            # Check if foreign_author is a follower
            if not author.followers.filter(id=foreign_author.id).exists():
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = AuthorSerializer(foreign_author)
            return Response(serializer.data)

        elif request.method == 'PUT':
            # Add as follower (accept follow request)
            author.followers.add(foreign_author)
            
            # Notify through WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{author.uuid}",
                {
                    'type': 'follow_request_notification',
                    'message': f'{foreign_author.displayName} is now following you'
                }
            )
            
            return Response(status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            # Remove follower
            author.followers.remove(foreign_author)
            
            # Notify through WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{author.uuid}",
                {
                    'type': 'follow_request_notification',
                    'message': f'{foreign_author.displayName} has unfollowed you'
                }
            )
            
            return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
@swagger_auto_schema(
    method="get",
    operation_summary="Get Authors Following",
    operation_description="Retrieve the list of authors that a specific author is following.",
    manual_parameters=[
        openapi.Parameter(
            "author_uuid",
            openapi.IN_PATH,
            description="UUID of the author to retrieve following authors for",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully retrieved following authors.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="ID of the author"
                        ),
                        "uuid": openapi.Schema(
                            type=openapi.TYPE_STRING, description="UUID of the author"
                        ),
                        "host": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Host of the author"
                        ),
                        "displayName": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Display name of the author",
                        ),
                        "github": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="GitHub URL of the author",
                        ),
                        "profileImage": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Profile image URL of the author",
                        ),
                        "page": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Page URL of the author",
                        ),
                        "username": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Username of the author",
                        ),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Email of the author"
                        ),
                    },
                ),
            ),
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Authors"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_author_following(request, author_uuid):
    try:
        author = get_object_or_404(Author, uuid=author_uuid)
        following = author.following.all()
        serializer = AuthorSerializer(following, many=True)
        return Response(serializer.data)
    except Author.DoesNotExist:
        return Response({"error": "Author not found"}, status=404)


@swagger_auto_schema(
    method="get",
    operation_summary="Get Author Friends",
    operation_description="Retrieve the list of friends for a specific author. Friends are defined as those who are both following and followed by the author.",
    manual_parameters=[
        openapi.Parameter(
            "author_uuid",
            openapi.IN_PATH,
            description="UUID of the author to retrieve friends for",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully retrieved friends of the author.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="ID of the friend author",
                        ),
                        "uuid": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="UUID of the friend author",
                        ),
                        "host": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Host of the friend author",
                        ),
                        "displayName": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Display name of the friend author",
                        ),
                        "github": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="GitHub URL of the friend author",
                        ),
                        "profileImage": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Profile image URL of the friend author",
                        ),
                        "page": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Page URL of the friend author",
                        ),
                        "username": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Username of the friend author",
                        ),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Email of the friend author",
                        ),
                    },
                ),
            ),
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Authors"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_author_friends(request, author_uuid):
    try:
        author = get_object_or_404(Author, uuid=author_uuid)
        followers = author.followers.all()
        following = author.following.all()
        friends = followers.filter(id__in=following.values("id"))
        serializer = AuthorSerializer(friends, many=True)
        return Response(serializer.data)
    except Author.DoesNotExist:
        return Response({"error": "Author not found"}, status=404)


@swagger_auto_schema(
    method="post",
    operation_summary="Update Author Profile",
    operation_description="Update the profile of the specified author. Only the author can update their profile.",
    manual_parameters=[
        openapi.Parameter(
            "author_uuid",
            openapi.IN_PATH,
            description="UUID of the author whose profile is to be updated",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "host": openapi.Schema(
                type=openapi.TYPE_STRING, description="Host of the author"
            ),
            "displayName": openapi.Schema(
                type=openapi.TYPE_STRING, description="Display name of the author"
            ),
            "github": openapi.Schema(
                type=openapi.TYPE_STRING, description="GitHub URL of the author"
            ),
            "profileImage": openapi.Schema(
                type=openapi.TYPE_STRING, description="Profile image URL of the author"
            ),
            "page": openapi.Schema(
                type=openapi.TYPE_STRING, description="Page URL of the author"
            ),
            "username": openapi.Schema(
                type=openapi.TYPE_STRING, description="Username of the author"
            ),
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, description="Email of the author"
            ),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Password of the author (if updating)",
                write_only=True,
            ),
        },
        required=[],  # Specify fields that are required if any
    ),
    responses={
        200: openapi.Response(
            description="Successfully updated the author's profile.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="ID of the author"
                    ),
                    "uuid": openapi.Schema(
                        type=openapi.TYPE_STRING, description="UUID of the author"
                    ),
                    "host": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Host of the author"
                    ),
                    "displayName": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Display name of the author",
                    ),
                    "github": openapi.Schema(
                        type=openapi.TYPE_STRING, description="GitHub URL of the author"
                    ),
                    "profileImage": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Profile image URL of the author",
                    ),
                    "page": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Page URL of the author"
                    ),
                    "username": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Username of the author"
                    ),
                    "email": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Email of the author"
                    ),
                },
            ),
        ),
        403: openapi.Response(
            description="Permission denied.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        400: openapi.Response(
            description="Invalid input data.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Authors"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_author_profile(request, author_uuid):
    try:
        author = Author.objects.get(uuid=author_uuid)
        if request.user != author:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Author.DoesNotExist:
        return Response({"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method="get",
    operation_summary="Fetch a Post by ID",
    operation_description="Retrieve a post by its ID. The post must be either public or unlisted.",
    manual_parameters=[
        openapi.Parameter(
            "post_id",
            openapi.IN_PATH,
            description="ID of the post to retrieve",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Post retrieved successfully.",
            schema=PostSerializer(),  # Use the PostSerializer schema
        ),
        403: openapi.Response(
            description="You are not authorized to view this post.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Error message"
                    )
                },
            ),
        ),
    },
    tags=["Posts"],
)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_post_by_link(request, post_id):
    """
    Fetch a post by ID if it's either public or unlisted.
    """
    post = get_object_or_404(Post, id=post_id)

    # Check if the post is public or unlisted
    if post.visibility in ["PUBLIC", "UNLISTED"]:
        serializer = PostSerializer(post)
        return Response(serializer.data, status=200)

    # If the post is private or friends-only, return a 403 Forbidden
    return Response({"detail": "You are not authorized to view this post."}, status=403)


GITHUB_API_URL = "https://api.github.com/users/{}/events/public"


def fetch_and_create_github_posts():
    authors = Author.objects.filter(github__isnull=False)
    for author in authors:
        github_username = author.github.split("/")[-1]
        if github_username:
            response = requests.get(GITHUB_API_URL.format(github_username))
            if response.status_code == 200:
                events = response.json()
                for event in events:
                    if not GitHubPost.objects.filter(
                        github_event_id=event["id"]
                    ).exists():
                        github_post = GitHubPost.objects.create(
                            author=author,
                            activity_type=event["type"],
                            activity_data=event,
                            github_event_id=event["id"],
                        )
                        create_public_post_from_github_activity(author, github_post)
            else:
                print(
                    f"Failed to fetch events for {github_username}: {response.status_code}"
                )


def create_public_post_from_github_activity(author, github_post):
    event_type = github_post.activity_type
    event_data = github_post.activity_data
    title = f"{author.displayName} performed a {event_type} on GitHub"
    content = f"Event data: {event_data}"

    Post.objects.create(
        title=title,
        description=f"GitHub activity: {event_type}",
        contentType="text/plain",
        content="",
        author=author,
        published=timezone.now(),
        visibility="PUBLIC",
    )


# class TestRemoteNodeConnectionView(APIView):
#     def post(self, request, pk):
#         try:
#             node = RemoteNode.objects.get(pk=pk)
#             success = connect_to_remote_node(node)
#             return Response({"connected": success}, status=status.HTTP_200_OK)
#         except RemoteNode.DoesNotExist:
#             return Response(
#                 {"error": "Node not found"}, status=status.HTTP_404_NOT_FOUND
#             )


class PublicAuthorProfileView(APIView):
    # permission_classes = []  # Allow all users to access this view

    def get(self, request, author_uuid):
        try:
            # Fetch the author using UUID
            author = Author.objects.get(uuid=author_uuid)
            serializer = PublicAuthorSerializer(author)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Author.DoesNotExist:
            return Response(
                {"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND
            )


class PublicAuthorStatsView(APIView):
    # permission_classes = []  # Allow all users to access this view

    def get(self, request, author_uuid):
        try:
            # Fetch the author using UUID
            author = Author.objects.get(uuid=author_uuid)
            stats = {
                "followers": author.followers.count(),
                "following": author.following.count(),
                "friends": author.followers.filter(
                    id__in=author.following.values("id")
                ).count(),
            }
            return Response(stats, status=status.HTTP_200_OK)
        except Author.DoesNotExist:
            return Response(
                {"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND
            )


class PublicPostsView(APIView):
    def get(self, request, author_uuid):
        try:
            # Ensure author_uuid is properly handled as a UUID
            posts = Post.objects.filter(
                author__uuid=author_uuid, visibility="PUBLIC"
            ).order_by("-published")
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response(
                {"detail": "No public posts found for this author."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )




@api_view(['GET'])
@authentication_classes([NodeBasicAuthentication])
@permission_classes([IsAuthenticatedOrNode])
def verify_node_connection(request):
    try:
        # Log incoming request details
        return Response({
            "status": "success",
            "message": "Connection verified",
            "node": request.user.url if hasattr(request.user, 'url') else str(request.user)
        })
    except Exception as e:
        # Log any exceptions
        return Response({
            "status": "error",
            "message": str(e)
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def test_node_connection(request):
    try:

        # Get all remote nodes
        remote_nodes = ToWhichItsConnected.objects.filter(active=True)
        if not remote_nodes:
            return Response({
                "status": "error",
                "message": "No remote nodes found in database. Please create one in the admin panel."
            }, status=status.HTTP_404_NOT_FOUND)

        results = []
        for node in remote_nodes:
            try:
                 # Test outgoing connection (us -> them)
                outgoing_url = f"{node.url}"
                # endpoint = 'service/api/authors/931b3149-9101-4bb6-a78d-3350fdb70615/posts/all/'
                endpoint = 'service/api/authors/931b3149-9101-4bb6-a78d-3350fdb70615/posts/all'
                outgoing_response = make_node_request(base_url=outgoing_url, endpoint=endpoint)
                
                results.append({
                    "node_url": node.url,
                    "outgoing_test": {
                        "status": "success",
                        "status_code": outgoing_response.status_code,
                        "response": outgoing_response.json() if outgoing_response.status_code == 200 else outgoing_response.text
                    }
                })
                
            except requests.RequestException as e:
                results.append({
                    "node_url": node.url,
                    "status": "error",
                    "error_type": str(type(e).__name__),
                    "error_message": str(e)
                })
        
        return Response({
            "status": "completed",
            "test_results": results
        })
        
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            "type": str(type(e))
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST', 'GET', 'DELETE'])
@authentication_classes([NodeBasicAuthentication])
@permission_classes([IsAuthenticatedOrNode])
def inbox_handler(request, author_serial):
    """
    Handles inbox activities for a given author. Supports POST (to add activities),
    GET (to retrieve inbox contents), and DELETE (to clear the inbox).
    """
    # Retrieve the author based on UUID
    author = get_object_or_404(Author, uuid=author_serial)
    # Get or create the inbox for the author
    inbox, created = Inbox.objects.get_or_create(author=author)
    

    if request.method == 'GET':
        # Serialize and return the inbox data
        serializer = InboxSerializer(inbox)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data
        item_type = data.get('type', '').lower()

        try:
            if item_type == "posts":
                # Handle multiple posts
                posts_data = data.get('src', [])
                for post_data in posts_data:
                    # Process each post individually
                    # First, get or create the author
                    author_data = post_data.get('author', {})
                    author_id = author_data.get('id')
                    if not author_id:
                        continue  # Skip posts without author ID

                    # Parse author UUID from the author_id URL
                    author_uuid = author_id.rstrip('/').split('/')[-1]

                    # Get or create the author
                    author, created = Author.objects.get_or_create(
                        uuid=author_uuid,
                        defaults={
                            'displayName': author_data.get('displayName', ''),
                            'host': author_data.get('host', ''),
                            'page': author_data.get('page', ''),
                            'github': author_data.get('github', ''),
                            'profileImage': author_data.get('profileImage', ''),
                        }
                    )

                    # If the author exists, update their info
                    if not created:
                        author.displayName = author_data.get('displayName', author.displayName)
                        author.host = author_data.get('host', author.host)
                        author.page = author_data.get('page', author.page)
                        author.github = author_data.get('github', author.github)
                        author.profileImage = author_data.get('profileImage', author.profileImage)
                        author.save()

                    # Now, process the post
                    post_id = post_data.get('id')
                    if not post_id:
                        continue  # Skip posts without ID

                    # Parse post UUID from the post_id URL
                    post_uuid = post_id.rstrip('/').split('/')[-1]

                    # Get or create the post
                    post, post_created = Post.objects.get_or_create(
                        id=post_uuid,
                        defaults={
                            'author': author,
                            'title': post_data.get('title', ''),
                            'description': post_data.get('description', ''),
                            'contentType': post_data.get('contentType', 'text/plain'),
                            'content': post_data.get('content', ''),
                            'published': post_data.get('published', timezone.now()),
                            'visibility': post_data.get('visibility', 'PUBLIC'),
                            'page': post_data.get('page', ''),
                        }
                    )

                    # If the post exists, update its info
                    if not post_created:
                        post.title = post_data.get('title', post.title)
                        post.description = post_data.get('description', post.description)
                        post.contentType = post_data.get('contentType', post.contentType)
                        post.content = post_data.get('content', post.content)
                        post.published = post_data.get('published', post.published)
                        post.visibility = post_data.get('visibility', post.visibility)
                        post.page = post_data.get('page', post.page)
                        post.save()

                    # Now handle comments
                    comments_data = post_data.get('comments', {}).get('src', [])
                    for comment_data in comments_data:
                        # Process each comment
                        comment_author_data = comment_data.get('author', {})
                        comment_author_id = comment_author_data.get('id')
                        if not comment_author_id:
                            continue  # Skip comments without author ID

                        # Parse comment author UUID
                        comment_author_uuid = comment_author_id.rstrip('/').split('/')[-1]

                        # Get or create the comment author
                        comment_author, ca_created = Author.objects.get_or_create(
                            uuid=comment_author_uuid,
                            defaults={
                                'displayName': comment_author_data.get('displayName', ''),
                                'host': comment_author_data.get('host', ''),
                                'page': comment_author_data.get('page', ''),
                                'github': comment_author_data.get('github', ''),
                                'profileImage': comment_author_data.get('profileImage', ''),
                            }
                        )

                        # If the author exists, update their info
                        if not ca_created:
                            comment_author.displayName = comment_author_data.get('displayName', comment_author.displayName)
                            comment_author.host = comment_author_data.get('host', comment_author.host)
                            comment_author.page = comment_author_data.get('page', comment_author.page)
                            comment_author.github = comment_author_data.get('github', comment_author.github)
                            comment_author.profileImage = comment_author_data.get('profileImage', comment_author.profileImage)
                            comment_author.save()

                        # Process the comment
                        comment_id = comment_data.get('id')
                        if not comment_id:
                            continue  # Skip comments without ID

                        # Parse comment UUID
                        comment_uuid = comment_id.rstrip('/').split('/')[-1]

                        # Get or create the comment
                        comment, comment_created = Comment.objects.get_or_create(
                            id=comment_uuid,
                            defaults={
                                'post': post,
                                'author': comment_author,
                                'content': comment_data.get('comment', ''),
                                'contentType': comment_data.get('contentType', 'text/plain'),
                                'published': comment_data.get('published', timezone.now()),
                            }
                        )

                        # If the comment exists, update its info
                        if not comment_created:
                            comment.content = comment_data.get('comment', comment.content)
                            comment.contentType = comment_data.get('contentType', comment.contentType)
                            comment.published = comment_data.get('published', comment.published)
                            comment.save()

                        # Handle likes on comments
                        comment_likes_data = comment_data.get('likes', {}).get('src', [])
                        for like_data in comment_likes_data:
                            # Process each like
                            like_author_data = like_data.get('author', {})
                            like_author_id = like_author_data.get('id')
                            if not like_author_id:
                                continue  # Skip likes without author ID

                            # Parse like author UUID
                            like_author_uuid = like_author_id.rstrip('/').split('/')[-1]

                            # Get or create the like author
                            like_author, la_created = Author.objects.get_or_create(
                                uuid=like_author_uuid,
                                defaults={
                                    'displayName': like_author_data.get('displayName', ''),
                                    'host': like_author_data.get('host', ''),
                                    'page': like_author_data.get('page', ''),
                                    'github': like_author_data.get('github', ''),
                                    'profileImage': like_author_data.get('profileImage', ''),
                                }
                            )

                            if not la_created:
                                like_author.displayName = like_author_data.get('displayName', like_author.displayName)
                                like_author.host = like_author_data.get('host', like_author.host)
                                like_author.page = like_author_data.get('page', like_author.page)
                                like_author.github = like_author_data.get('github', like_author.github)
                                like_author.profileImage = like_author_data.get('profileImage', like_author.profileImage)
                                like_author.save()

                            # Process the like
                            like_id = like_data.get('id')
                            if not like_id:
                                continue  # Skip likes without ID

                            # Parse like UUID
                            like_uuid = like_id.rstrip('/').split('/')[-1]

                            # Get or create the like
                            like, like_created = Like.objects.get_or_create(
                                id=like_uuid,
                                defaults={
                                    'author': like_author,
                                    'comment': comment,
                                    'published': like_data.get('published', timezone.now()),
                                }
                            )

                            if not like_created:
                                like.published = like_data.get('published', like.published)
                                like.save()

                    # Now handle likes on posts
                    likes_data = post_data.get('likes', {}).get('src', [])
                    for like_data in likes_data:
                        # Process each like
                        like_author_data = like_data.get('author', {})
                        like_author_id = like_author_data.get('id')
                        if not like_author_id:
                            continue  # Skip likes without author ID

                        # Parse like author UUID
                        like_author_uuid = like_author_id.rstrip('/').split('/')[-1]

                        # Get or create the like author
                        like_author, la_created = Author.objects.get_or_create(
                            uuid=like_author_uuid,
                            defaults={
                                'displayName': like_author_data.get('displayName', ''),
                                'host': like_author_data.get('host', ''),
                                'page': like_author_data.get('page', ''),
                                'github': like_author_data.get('github', ''),
                                'profileImage': like_author_data.get('profileImage', ''),
                            }
                        )

                        if not la_created:
                            like_author.displayName = like_author_data.get('displayName', like_author.displayName)
                            like_author.host = like_author_data.get('host', like_author.host)
                            like_author.page = like_author_data.get('page', like_author.page)
                            like_author.github = like_author_data.get('github', like_author.github)
                            like_author.profileImage = like_author_data.get('profileImage', like_author.profileImage)
                            like_author.save()

                        # Process the like
                        like_id = like_data.get('id')
                        if not like_id:
                            continue  # Skip likes without ID

                        # Parse like UUID
                        like_uuid = like_id.rstrip('/').split('/')[-1]

                        # Get or create the like
                        like, like_created = Like.objects.get_or_create(
                            id=like_uuid,
                            defaults={
                                'author': like_author,
                                'post': post,
                                'published': like_data.get('published', timezone.now()),
                            }
                        )

                        if not like_created:
                            like.published = like_data.get('published', like.published)
                            like.save()

                return Response({'message': 'Posts added to inbox and created locally.'}, status=status.HTTP_201_CREATED)

            if item_type == 'post':
                # to create a post, basically call this url: service/api/authors/<path:author_serial>/posts/
                # i need the author_serial from data
                auth_serial = data.get("author_id")
                hostname = data["author"]["host"]
                print("THIS IS THE HOSTNAME: " , hostname , auth_serial)

                api_url = f"{hostname}service/api/authors/{auth_serial}/posts/"
                print("complete url:" , api_url)

                # Prepare the body for creating a post
                post_data = {
                    'title': data.get('title'),
                    'description': data.get('description', ''),
                    'contentType': data.get('contentType', 'text/plain'),
                    'visibility': data.get('visibility', 'PUBLIC'),
                    'content': data.get('content', ''),
                }

                # Check if there is an image to upload
                if 'image' in data:
                    post_data['image'] = data['image']  # Assuming the image is included in the data

                response = requests.post(api_url, json=post_data, headers={
                    'Authorization': f"Token {data.get('token')}",  # Ensure this line is correctly indented
                    'Content-Type': 'application/json'
                })

                return Response({'message': 'Post added to inbox and created locally.'}, status=status.HTTP_201_CREATED)

            elif item_type == 'like':
                pass

            elif item_type == 'comment':
                pass

            elif item_type == 'follow':
                # Handle Follow Activity
                print("Handling follow request.")

                # Get the target author's UUID from the request data
                target_uuid = data.get('object', {}).get('id')
                if not target_uuid:
                    return Response({'error': 'Target UUID for follow is missing.'}, status=status.HTTP_400_BAD_REQUEST)

                django_request = request._request  # Get the underlying Django HttpRequest

                # Call the existing send_follow_request function
                response = send_follow_request(django_request, target_uuid)

                if response.status_code == status.HTTP_201_CREATED:
                    print("Follow request created successfully.")

                    # Get the most recent follow request
                    follow_request = FollowRequest.objects.filter(
                        actor=request.user,
                        object=author,
                        accepted=False
                    ).latest('created_at')

                    print(f"Adding follow request {follow_request.id} to inbox.")
                    # Add to inbox if not already added
                    if not inbox.follow_requests.filter(id=follow_request.id).exists():
                        inbox.follow_requests.add(follow_request)
                        print(f"Follow request {follow_request.id} added to inbox of author {author_serial}.")
                    else:
                        print(f"Follow request {follow_request.id} already in inbox of author {author_serial}.")

                    # **Process the follow request by calling the local API endpoint**
                    response = process_follow_request(request, follow_request)
                    if response.status_code != status.HTTP_200_OK:
                        return Response({'error': 'Failed to process follow request locally.'}, status=status.HTTP_400_BAD_REQUEST)

                    return Response({'message': 'Follow request added to inbox and processed locally.'}, status=status.HTTP_201_CREATED)

                # If there was an error, return the original response
                print(f"send_follow_request response status: {response.status_code}")
                return response

            else:
                # Unsupported activity type
                print(f"Unsupported activity type: {item_type}")
                return Response({'error': f"Unsupported activity type: {item_type}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error in inbox_handler: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Clear all activities from the inbox
        inbox.posts.clear()
        inbox.likes.clear()
        inbox.comments.clear()
        inbox.follow_requests.clear()
        print(f"Inbox for author {author_serial} has been cleared.")
        return Response({'message': 'Inbox cleared.'}, status=status.HTTP_204_NO_CONTENT)
def create_local_post(request, post):
    """
    Processes a post activity by creating a local post via the API.
    """
    try:
        factory = APIRequestFactory()
        api_request = factory.post(
            reverse('post-list'),  # Ensure this URL name matches your URL configuration
            data={
                'type': post.type,
                'title': post.title,
                'id': post.id,
                'page': post.page,
                'description': post.description,
                'contentType': post.contentType,
                'content': post.content,
                'published': post.published,
                'visibility': post.visibility,
                'author': post.author.id,  # Assuming author is referenced by ID
            },
            format='json'
        )
        api_request.user = request.user
        response = create_post(api_request)  # Call your post creation view
        return response
    except Exception as e:
        print(f"Error creating local post: {e}")
        return Response({'error': 'Failed to create local post.'}, status=status.HTTP_400_BAD_REQUEST)

def create_local_comment(request, comment):
    """
    Processes a comment activity by creating a local comment via the API.
    """
    try:
        factory = APIRequestFactory()
        api_request = factory.post(
            reverse('comment-list'),  # Ensure this URL name matches your URL configuration
            data={
                'type': comment.type,
                'id': comment.id,
                'author': comment.author.id,
                'post': comment.post,
                'comment': comment.comment,
                'contentType': comment.contentType,
                'published': comment.published,
            },
            format='json'
        )
        api_request.user = request.user
        response = post_comment(api_request)  # Call your comment creation view
        return response
    except Exception as e:
        print(f"Error creating local comment: {e}")
        return Response({'error': 'Failed to create local comment.'}, status=status.HTTP_400_BAD_REQUEST)

def process_follow_request(request, follow_request):
    """
    Processes a follow request by accepting it via the API.
    """
    try:
        factory = APIRequestFactory()
        api_request = factory.post(
            reverse('follow-request-accept', args=[follow_request.id]),  # Ensure this URL name matches your URL configuration
            data={},  # If your accept_follow_request view requires additional data, include it here
            format='json'
        )
        api_request.user = request.user
        response = accept_follow_request(api_request, follow_request.id)  # Call your follow request acceptance view
        return response
    except Exception as e:
        print(f"Error processing follow request: {e}")
        return Response({'error': 'Failed to process follow request.'}, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_remote_authors(request):
    try:
        # Get all active remote nodes
        remote_nodes = ToWhichItsConnected.objects.filter(active=True)
        if not remote_nodes:
            return Response({
                "status": "error",
                "message": "No remote nodes found in the database. Please create one in the admin panel."
            }, status=status.HTTP_404_NOT_FOUND)

        results = []
        for node in remote_nodes:
            node_result = {
                "node_url": node.url,
                "authors_synced": 0,
                "errors": []
            }

            try:
                # Fetch all authors from the remote node
                base_url = node.url
                endpoint = 'service/api/authors/'

                response = make_node_request(
                    base_url=base_url,
                    endpoint=endpoint,
                )

                if response.status_code == 200:
                    data = response.json()
                    # Adjust based on the remote node's response structure
                    remote_authors = data

                    # Iterate over authors and save them to the local database
                    for author_data in remote_authors:
                        try:
                            # Get or create the author
                            author_id = author_data.get('id')
                            if not author_id:
                                continue  # Skip if author ID is missing

                            # Ensure username is unique
                            # unique_username = f"{author_data.get('displayName', '').lower()}_{author_id.split('/')[-1][:8]}"

                            author_defaults = {
                                'uuid': author_data.get('uuid'),
                                'host': author_data.get('host', base_url),
                                'displayName': author_data.get('displayName', ''),
                                'github': author_data.get('github', ''),
                                'profileImage': author_data.get('profileImage', ''),
                                'username': author_data.get('username',''),  # Ensure unique usernames
                                'email': '',  # Email might not be available
                                'is_active': False,  # Remote authors are not local users
                            }

                            author, created = Author.objects.update_or_create(
                                id=author_id,
                                defaults=author_defaults
                            )
                            node_result['authors_synced'] += 1

                        except Exception as e:
                            error_message = f"Error processing author {author_data.get('id')}: {e}"
                            node_result['errors'].append(error_message)
                            continue  # Skip to the next author
                    results.append(node_result)
                else:
                    error_message = f"Failed to fetch authors from {node.url}: Status {response.status_code}"
                    node_result['errors'].append(error_message)
                    results.append(node_result)
            except requests.RequestException as e:
                error_message = f"Connection error with {node.url}: {e}"
                node_result['errors'].append(error_message)
                results.append(node_result)

        return Response({
            "status": "completed",
            "sync_results": results
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            "type": str(type(e).__name__)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def construct_posts_data(author):
    # Get all public and friends-only posts of the author
    posts = Post.objects.filter(author=author, visibility__in=['PUBLIC', 'FRIENDS']).order_by('-published')

    posts_data = {
        "type": "posts",
        "page_number": 1,
        "size": len(posts),
        "count": posts.count(),
        "src": []
    }

    for post in posts:
        post_data = {
            "type": "post",
            "title": post.title,
            "id": f"{post.author.host}authors/{post.author.uuid}/posts/{post.id}",
            "page": f"{post.author.page}/posts/{post.id}",
            "description": post.description,
            "contentType": post.contentType,
            "content": post.content,
            "author": {
                "type": "author",
                "id": f"{post.author.host}authors/{post.author.uuid}",
                "host": post.author.host,
                "displayName": post.author.displayName,
                "page": post.author.page,
                "github": post.author.github,
                "profileImage": post.author.profileImage,
            },
            "published": post.published.isoformat(),
            "visibility": post.visibility,
            "comments": construct_comments_data(post),
            "likes": construct_likes_data(post),
        }
        posts_data["src"].append(post_data)

    return posts_data
def construct_comments_data(post):
    comments = Comment.objects.filter(post=post).order_by('-published')[:5]
    comments_data = {
        "type": "comments",
        "page": f"{post.author.page}/posts/{post.id}",
        "id": f"{post.author.host}authors/{post.author.uuid}/posts/{post.id}/comments",
        "page_number": 1,
        "size": 5,
        "count": post.comments.count(),
        "src": []
    }

    for comment in comments:
        comment_data = {
            "type": "comment",
            "author": {
                "type": "author",
                "id": f"{comment.author.host}authors/{comment.author.uuid}",
                "page": comment.author.page,
                "host": comment.author.host,
                "displayName": comment.author.displayName,
                "github": comment.author.github,
                "profileImage": comment.author.profileImage
            },
            "comment": comment.content,
            "contentType": comment.contentType,
            "published": comment.published.isoformat(),
            "id": f"{comment.post.author.host}authors/{comment.post.author.uuid}/comments/{comment.id}",
            "post": f"{post.author.host}authors/{post.author.uuid}/posts/{post.id}",
            "page": f"{comment.author.page}/posts/{post.id}",
            "likes": construct_comment_likes_data(comment),
        }
        comments_data["src"].append(comment_data)

    return comments_data
def construct_likes_data(post):
    likes = Like.objects.filter(post=post).order_by('-published')[:5]
    likes_data = {
        "type": "likes",
        "page": f"{post.author.page}/posts/{post.id}",
        "id": f"{post.author.host}authors/{post.author.uuid}/posts/{post.id}/likes",
        "page_number": 1,
        "size": 5,
        "count": post.likes.count(),
        "src": []
    }

    for like in likes:
        like_data = {
            "type": "like",
            "author": {
                "type": "author",
                "id": f"{like.author.host}authors/{like.author.uuid}",
                "page": like.author.page,
                "host": like.author.host,
                "displayName": like.author.displayName,
                "github": like.author.github,
                "profileImage": like.author.profileImage
            },
            "published": like.published.isoformat(),
            "id": f"{like.author.host}authors/{like.author.uuid}/liked/{like.id}",
            "object": f"{post.author.page}/posts/{post.id}"
        }
        likes_data["src"].append(like_data)

    return likes_data
def construct_comment_likes_data(comment):
    likes = Like.objects.filter(comment=comment).order_by('-published')[:5]
    likes_data = {
        "type": "likes",
        "id": f"{comment.post.author.host}authors/{comment.post.author.uuid}/comments/{comment.id}/likes",
        "page": f"{comment.author.page}/comments/{comment.id}/likes",
        "page_number": 1,
        "size": 5,
        "count": likes.count(),
        "src": []
    }

    for like in likes:
        like_data = {
            "type": "like",
            "author": {
                "type": "author",
                "id": f"{like.author.host}authors/{like.author.uuid}",
                "page": like.author.page,
                "host": like.author.host,
                "displayName": like.author.displayName,
                "github": like.author.github,
                "profileImage": like.author.profileImage
            },
            "published": like.published.isoformat(),
            "id": f"{like.author.host}authors/{like.author.uuid}/liked/{like.id}",
            "object": f"{comment.post.author.page}/comments/{comment.id}"
        }
        likes_data["src"].append(like_data)

    return likes_data
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def send_follow_request_to_remote_authors(request, author_serial):
    """
    Send a follow request to an author on a connected remote node.
    """
    try:
        # Extract the follow activity from the request data
        print("Incoming request data: ", request.data)
        follow_activity = request.data

        # Validate required fields in the follow activity
        actor = follow_activity.get('actor')
        object_author = follow_activity.get('object')
        if not actor or not object_author:
            return Response({
                "status": "error",
                "message": "Both 'actor' and 'object' are required in the follow activity."
            }, status=status.HTTP_400_BAD_REQUEST)

        author_uuid = object_author.get('uuid') or object_author.get('id').split('/')[-1]
        if not author_uuid:
            return Response({
                "status": "error",
                "message": "Author UUID is required in the 'object'."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get all active remote nodes
        remote_nodes = ToWhichItsConnected.objects.filter(active=True)
        if not remote_nodes:
            return Response({
                "status": "error",
                "message": "No remote nodes found in the database. Please create one in the admin panel."
            }, status=status.HTTP_404_NOT_FOUND)

        results = []
        for node in remote_nodes:
            node_result = {
                "node_url": node.url,
                "follow_request_sent": False,
                "errors": []
            }

            try:
                print("Preparing follow activity for node:", node.url)

                # Make a deep copy of the follow activity to avoid mutating the original data
                follow_activity_copy = copy.deepcopy(follow_activity)

                # Update the 'object' field with the correct author URL for the target node
                follow_activity_copy['object']['id'] = f"{node.url.rstrip('/')}/authors/{author_uuid}"

                # Update the 'object' field's host if necessary
                follow_activity_copy['object']['host'] = node.url.rstrip('/')

                # Define the endpoint for the target node's inbox
                endpoint = f"/service/api/authors/{object_author.get('uuid')}/inbox/"

                # Send the follow request to the remote node's inbox using make_node_request
                response = make_node_request(
                    base_url=node.url.rstrip('/'),
                    endpoint=endpoint,
                    method='POST',
                    data=follow_activity_copy
                )

                print("Response from node:", response.status_code, response.text)

                if response.status_code in [200, 201]:
                    node_result['follow_request_sent'] = True
                else:
                    error_message = f"Failed to send follow request to {node.url}: Status {response.status_code}, Response: {response.text}"
                    node_result['errors'].append(error_message)
                    print(error_message)

            except Exception as e:
                error_message = f"Connection error with {node.url}: {e}"
                node_result['errors'].append(error_message)
                print(error_message)

            results.append(node_result)

        return Response({
            "status": "completed",
            "results": results
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print("Exception occurred: ", str(e))
        return Response({
            "status": "error",
            "message": str(e),
            "type": type(e).__name__
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
def connected_nodes(request):
    nodes = ToWhichItsConnected.objects.all()
    data = [
        {
            'url': node.url,
            'username': node.username,
            'password': node.password,
        }
        for node in nodes
    ]
    return Response(data)