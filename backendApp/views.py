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
from rest_framework_simplejwt.authentication import JWTAuthentication



def defaultPath(request):
    return render(request, "index.html")


@swagger_auto_schema(
    method="post",
    operation_summary="Create a new post for a specific author",
    operation_description="""
    Use this endpoint to create a new post for the author specified by the author's unique serial identifier (author_serial). 
    This should be used when you want to add a new post to the system for a specific author. A new post will be created 
    with the provided title and content. Optionally, you can provide a published date to set the date and time 
    when the post is considered published.

    **When to use:**
    - Use this endpoint when you need to create a new post for a specific author.
    - Required fields for this operation are `title` and `content`.

    **How to use:**
    - Send a `POST` request with the author's serial identifier in the URL.
    - Include the `title` and `content` in the request body as required fields.
    - The optional field `published` can be provided to specify when the post was published, in `YYYY-MM-DDTHH:MM:SS` format.

    **Why use or not use:**
    - This endpoint should be used when you are adding a new post to an author's profile.
    - Do not use this endpoint if the post data is incomplete (missing required fields like `title` or `content`).
    - Make sure the author exists before creating a post for them.
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

    print("YES CR4EATING POSTS")

    if serializer.is_valid():
        post = serializer.save()
        response_serializer = PostSerializer(post)
        print("POSTS CREATED SUCCESFULLY")

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def vueTest(request):
    return render(request, "index.html")


@swagger_auto_schema(
    method="GET",
    operation_summary="Retrieve a specific post",
    operation_description="""
    Use this endpoint to retrieve details of a specific post for the given author. 
    This will include the post details, comments, and likes.

    **When to use:**
    - Use this endpoint when you want to fetch details of a post for a specific author.
    - The post is identified by the post_serial, which includes both the post ID and, optionally, an action for comments or likes.

    **How to use:**
    - Send a `GET` request to the endpoint with the `author_serial` and `post_serial` in the URL.
    - The response will return the post details, associated comments, and likes information.

    **Why use or not use:**
    - This endpoint should be used when retrieving post details along with its comments and likes.
    - Do not use this endpoint for modifying or deleting a post—use the corresponding PUT or DELETE endpoints for those actions.
    """,
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
    operation_description="""
    Use this endpoint to delete a specific post for the given author. 
    The post is identified by the post_serial.

    **When to use:**
    - Use this endpoint when you want to permanently delete a post.
    - The post is identified by the `post_serial`, which includes both the post ID and the author's serial ID.

    **How to use:**
    - Send a `DELETE` request to the endpoint with the `author_serial` and `post_serial` in the URL.

    **Why use or not use:**
    - This endpoint should be used to permanently delete a post from the system.
    - Do not use this endpoint if the post should remain in the system, as deletion is permanent.
    """,
    responses={204: "Post deleted successfully", 404: "Post not found"},
    tags=["Posts"],
)
@swagger_auto_schema(
    method="PUT",
    operation_summary="Update a specific post",
    operation_description="""
    Use this endpoint to update the details of a specific post for the given author. 
    The post is identified by the post_serial.

    **When to use:**
    - Use this endpoint when you need to update an existing post for a specific author.
    - The post to be updated is identified by the `post_serial`.

    **How to use:**
    - Send a `PUT` request to the endpoint with the `author_serial` and `post_serial` in the URL, along with the data you wish to update in the request body.
    - The request body can include fields like `title` and `content`, where `content` is parsed as markdown and converted to HTML.

    **Why use or not use:**
    - This endpoint should be used when modifying the content or other attributes of an existing post.
    - Do not use this endpoint if the post data is invalid or missing required fields.
    """,
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
    operation_description="""
    Use this endpoint to either like a post or add a comment to it. The action is specified in the URL path (either `like` or `comments`).

    **When to use:**
    - Use this endpoint when you want to interact with a post by either liking it or commenting on it.
    - Specify the action (`like` or `comments`) in the URL to determine whether you're liking or commenting.

    **How to use:**
    - Send a `POST` request to the endpoint with the `author_id`, `post_id`, and optional `content` (for comments) in the request body.
    - The `author_id` should be the ID of the user performing the action, and the `post_id` should be the ID of the post being interacted with.

    **Why use or not use:**
    - This endpoint should be used when you need to either add a like or post a comment on a post.
    - Do not use this endpoint for other actions, such as updating or deleting a post—use the corresponding PUT or DELETE endpoints for those actions.
    """,
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
    operation_description="""
    Use this endpoint to post a comment on a specific post identified by its post_id. 
    The comment will be associated with the authenticated user as the author.

    **When to use:**
    - Use this endpoint when you need to post a comment on an existing post.
    - The post to which you are commenting is identified by the `post_id` in the URL.

    **How to use:**
    - Send a `POST` request to this endpoint with the `post_id` in the URL path, along with the `content` and `contentType` of the comment in the request body.
    - `content` refers to the actual text or content of the comment, while `contentType` specifies the format of the comment (e.g., `text/plain`).
    - The request requires authentication to ensure that the user posting the comment is authenticated.

    **Why use or not use:**
    - This endpoint should be used when you want to allow a user to add a comment to a post.
    - Do not use this endpoint if the post does not exist or if the user is not authenticated.
    - Make sure to include all required fields (`content` and `contentType`) in the request.
    """,
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


@swagger_auto_schema(
    method="post",
    operation_summary="Like a specific comment",
    operation_description="""
    Use this endpoint to like a specific comment identified by its comment_id. 
    The like will be associated with the authenticated user as the author.

    **When to use:**
    - Use this endpoint when you need to like a comment on a post.
    - The comment to be liked is identified by the `comment_id` in the URL.
    - The user must be authenticated.

    **How to use:**
    - Send a `POST` request to this endpoint with the `comment_id` in the URL path.
    - The request body is not required since the like will be automatically associated with the authenticated user.
    - The user will be added as the `author` of the like, and the comment will be identified by `comment_id`.

    **Why use or not use:**
    - This endpoint should be used when you want to allow a user to like a specific comment.
    - Do not use this endpoint if the user is not authenticated or if the comment does not exist.
    - The user cannot like the same comment multiple times; an error will be returned if they attempt to do so.
    - Ensure that the user has not already liked the comment, as repeated likes are not allowed.
    """,
    manual_parameters=[
        openapi.Parameter(
            "comment_id",
            openapi.IN_PATH,
            description="UUID of the comment to like",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    request_body=None,
    responses={
        201: openapi.Response(
            description="Comment liked successfully.", schema=LikeSerializer()
        ),
        400: openapi.Response(
            description="Invalid input data or comment already liked.",
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
            description="Comment not found.",
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


@swagger_auto_schema(
    method="get",
    operation_summary="Fetch likes for a specific comment",
    operation_description="""
    Use this endpoint to fetch all likes associated with a specific comment identified by its comment_id. 
    The response will include a list of likes for the comment.

    **When to use:**
    - Use this endpoint when you need to retrieve all the likes for a specific comment.
    - The comment whose likes you are fetching is identified by the `comment_id` in the URL.

    **How to use:**
    - Send a `GET` request to this endpoint with the `comment_id` in the URL path.
    - The response will include details of all the likes for the specified comment, including the number of likes and the serialized data of the likes.

    **Why use or not use:**
    - This endpoint should be used when you want to view the likes associated with a comment.
    - Do not use this endpoint if the comment does not exist, as a 404 error will be returned.
    - This endpoint can be used by anyone, as it is accessible without authentication (i.e., `AllowAny` permission).
    """,
    manual_parameters=[
        openapi.Parameter(
            "comment_id",
            openapi.IN_PATH,
            description="UUID of the comment to fetch likes for",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    request_body=None,
    responses={
        200: openapi.Response(
            description="Likes fetched successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "type": openapi.Schema(type=openapi.TYPE_STRING, description="The type of resource (likes)"),
                    "page": openapi.Schema(type=openapi.TYPE_STRING, description="URL for the current page"),
                    "id": openapi.Schema(type=openapi.TYPE_STRING, description="URL of the resource"),
                    "page_number": openapi.Schema(type=openapi.TYPE_INTEGER, description="Current page number"),
                    "size": openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of likes on this page"),
                    "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of likes"),
                    "src": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                            "author_id": openapi.Schema(type=openapi.TYPE_STRING, description="ID of the author of the like"),
                            "comment_id": openapi.Schema(type=openapi.TYPE_STRING, description="ID of the commented post"),
                            "published": openapi.Schema(type=openapi.TYPE_STRING, description="Timestamp when the like was published"),
                        }),
                        description="List of likes",
                    ),
                },
            ),
        ),
        404: openapi.Response(
            description="Comment not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                },
            ),
        ),
    },
    tags=["Likes"],
)
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
    operation_description="""
    Use this endpoint to like a specific post identified by its post_id. The request must include the post ID and the authenticated user's ID to track the like.

    **When to use:**
    - Use this endpoint when you want to like a specific post identified by `post_id`.
    - This operation is only available to authenticated users. 

    **How to use:**
    - Send a `POST` request to this endpoint with the `post_id` in the URL path, and the `author_id`, `post_id`, and `post` fields in the request body.
    - The `author_id` is the ID of the authenticated user who is liking the post, and `post_id` refers to the specific post being liked.
    - The `post` field is a reference to the post being liked.

    **Why to use or not use:**
    - This endpoint should be used when you want to register a like on a post.
    - Do not use this endpoint if you are not authenticated, or if you have already liked the post.
    - Ensure the post exists before attempting to like it.
    """,
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
    operation_description="""
    This endpoint allows you to retrieve all comments for a given post, identified by its `post_id`.

    **When to use:**
    - Use this endpoint when you want to fetch all the comments associated with a specific post.
    - This is useful for viewing the conversation or discussions related to a post.

    **How to use:**
    - Send a `GET` request to this endpoint with the `post_id` as part of the URL path.
    - The `post_id` is the unique identifier for the post whose comments you want to fetch.

    **Why to use or not use:**
    - Use this endpoint to retrieve the list of comments related to a post. 
    - This is a read-only operation, so it’s suitable for users who want to view comments.
    - You should not use this endpoint if you need to add, update, or delete comments (use the respective `POST`, `PUT`, or `DELETE` endpoints for those operations).
    - If the post is not found, a `404` error will be returned.
    - Ensure that the post exists before attempting to fetch comments.
    """,
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
    operation_description="""
    This endpoint allows you to retrieve all likes for a specific post, identified by its `post_id`.

    **When to use:**
    - Use this endpoint when you want to retrieve all the likes associated with a specific post.
    - This is useful for seeing how many users have liked a post or for viewing the users who liked the post.

    **How to use:**
    - Send a `GET` request to this endpoint with the `post_id` as part of the URL path.
    - The `post_id` is the unique identifier for the post whose likes you want to fetch.

    **Why to use or not use:**
    - Use this endpoint if you want to view the list of likes for a post.
    - This is a read-only operation, intended to fetch the likes, not modify them.
    - If you want to like a post, use the `POST` method at the appropriate endpoint for liking a post.
    - If the post is not found, a `404` error will be returned, so ensure the post exists before trying to fetch its likes.
    """,
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
    operation_description="""
    Fetch all posts created by the author specified by the `author_serial` UUID.

    **When to use:**
    - Use this endpoint when you need to retrieve all posts created by a specific author.
    - It is helpful when displaying a list of posts for a given author or fetching a specific author's content.

    **How to use:**
    - Send a `GET` request to this endpoint, including the `author_serial` parameter in the URL path.
    - The `author_serial` parameter should be the unique UUID identifier for the author whose posts you want to fetch.
    - You can paginate the response to limit the number of posts returned at once.

    **Why to use or not use:**
    - Use this endpoint to get a complete list of posts for an author.
    - This is a read-only operation, meaning you can view the posts but cannot modify them.
    - If the author does not exist, you will receive a `404` error.
    - This API supports pagination to handle large datasets. Be sure to check the paginated results.
    """,
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
    operation_description="""
    Send a follow request from the currently authenticated user to the specified author.

    **When to use:**
    - Use this endpoint when you want to send a follow request to an author you are not yet following.
    - It is used in scenarios where a user wants to request to follow another user (author).

    **How to use:**
    - Send a `POST` request to this endpoint, including the `author_uuid` parameter in the URL path.
    - The `author_uuid` should be the UUID of the author you wish to send a follow request to.
    - If you are already following the author, or if a request is already pending, you will receive an error message.

    **Why to use or not use:**
    - Use this API to initiate a follow request. If accepted, this will allow the requesting user to follow the target author.
    - If you are already following the author, you will receive a `400` response indicating that you are already following them.
    - If a follow request is already pending, you will receive a `400` response indicating that the request is already in progress.
    - This is a one-time operation, as follow requests are typically only created once and do not require repeated submissions.
    """,
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
    operation_description="""
    Use this endpoint to accept a follow request from an author specified by their unique UUID. 
    This should be used when an author receives a follow request and wishes to accept it. 
    When the follow request is accepted, the requesting author will be added as a follower.

    **When to use:**
    - Use this endpoint when you want to accept a follow request from an author.
    - The `author_uuid` in the path must correspond to the author who sent the follow request.

    **How to use:**
    - Send a `POST` request with the author's UUID (`author_uuid`) in the URL path.
    - The request will be processed to check whether the follow request exists and has not already been accepted or resolved.
    - If the request is valid, the author will be added as a follower.

    **Why use or not use:**
    - This endpoint should be used when you are accepting a follow request and you want the requesting author to become your follower.
    - Do not use this endpoint if the follow request no longer exists or has already been accepted.
    - Ensure that the follow request has not already been resolved or that the requesting author is not already following you.
    """,
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


        print("ACCEPTED NOW SENDING DATA" , post_data)
        # post_data = construct_posts_data(current_author)

        # Send the constructed object to the remote node
        send_data_to_remote_node(requesting_author.host, post_data , requesting_author.uuid)

        print("DATA SENT TO REMOTE NODE: ============================== ")


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
def send_data_to_remote_node(url, data , uuid):
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

    # The endpoint is 'inbox/'
    print("This is the data i got:(Viraj) " , data)
    endpoint = f'api/authors/{uuid}/inbox/'

    # Send the POST request via make_node_request
    response = make_node_request(
        base_url=matched_node.url,
        endpoint=endpoint,
        method='POST',
        data=data
    )

    return response


@swagger_auto_schema(
    method="POST",
    operation_summary="Decline a follow request from an author",
    operation_description="""
    Use this endpoint to decline a follow request from the author specified by their unique UUID. 
    This should be used when an author wants to reject a follow request from another author. 
    When the follow request is declined, the requesting author will not be added as a follower.

    **When to use:**
    - Use this endpoint when you want to decline a follow request from a specific author.
    - The `author_uuid` in the path must correspond to the author who sent the follow request.

    **How to use:**
    - Send a `POST` request with the author's UUID (`author_uuid`) in the URL path.
    - The system will check if the follow request is valid and has not already been resolved or accepted.
    - If the request is valid, the request will be declined, and the requesting author will be notified.

    **Why use or not use:**
    - This endpoint should be used when you wish to reject a follow request from an author.
    - Do not use this endpoint if the follow request no longer exists or has already been accepted.
    - Make sure you are declining the correct request and that the request is still pending.
    """,
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
    operation_description="""
    Use this endpoint to retrieve all follow requests that are pending for the authenticated user. 
    This should be used when you want to check all incoming follow requests that have not been accepted or declined yet.

    **When to use:**
    - Use this endpoint when you need to see all the pending follow requests for your account.
    - This will return requests where the authenticated user is the object (the one receiving the follow request) and the request is still pending.

    **How to use:**
    - Send a `GET` request to the endpoint with proper authentication.
    - The server will return all pending follow requests directed towards the authenticated user.

    **Why use or not use:**
    - This endpoint should be used when you need to view all the incoming follow requests that have not been resolved yet (i.e., those that are still pending).
    - Do not use this endpoint if you are not authenticated or do not have the correct credentials, as it will return an unauthorized error.
    """,
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
    operation_description="""
    Use this endpoint to fetch a list of all authors, excluding the currently authenticated user. 
    Each author object will include details about their followers, but the authenticated user will not be included in the list.

    **When to use:**
    - Use this endpoint when you want to retrieve a list of authors who are not the currently authenticated user.
    - This is useful for displaying a list of other authors that the current user can interact with or follow.

    **How to use:**
    - Send a `GET` request to the endpoint with the appropriate authentication credentials.
    - The response will return a list of authors excluding the current user, as well as their followers' UUIDs.

    **Why use or not use:**
    - This endpoint should be used when you need to fetch a list of authors other than the current user, along with their follower information.
    - Do not use this endpoint if you are not authenticated, as it will return an unauthorized error.
    - Avoid using this endpoint if you need data about the current user, as they will not be included in the response.
    """,
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
            serialized_author["type"] = "author"

            author_data.append(serialized_author)
        response_data = {}
        response_data["type"] = "authors"
        response_data["authors"] = author_data
        


        return Response(response_data)
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
    operation_description="""
    Use this endpoint to retrieve a stream of posts based on the following relationships of a specified author. 
    The posts included in the stream are from the author's mutual friends, authors they follow, their followers, 
    and public posts. The stream is paginated for better performance and scalability.

    **When to use:**
    - Use this endpoint when you want to retrieve a stream of posts from the author specified by `author_id`.
    - The stream will include posts from mutual friends, followed authors, followers, and public posts.
    - This endpoint is useful for displaying the most relevant posts for the user, based on their social connections.

    **How to use:**
    - Send a `GET` request with the `author_id` as a URL parameter, which represents the UUID of the author.
    - The response will return a paginated list of posts with details like the post title, content, visibility, and repost count.
    - The stream includes posts from mutual friends, followed authors, followers, and public posts. Posts are filtered based on visibility and relationship.
    - Pagination is used to limit the number of posts per page. You can navigate through pages using the `next` and `previous` fields in the response.

    **Why use or not use:**
    - This endpoint should be used when you need to show a dynamic stream of posts based on an author's network and social relationships.
    - Do not use this endpoint if you are looking for posts that are specific to a single author, as this stream includes posts from multiple authors.
    - Avoid using this endpoint if you do not have the `author_id` parameter or if the provided `author_id` does not correspond to an existing author.
    """,
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
    operation_description="""
    Creates a new user account. The user data must include the necessary fields as defined in the `AuthorSerializer`. 
    During signup, the system will check whether the user needs to be approved by an administrator based on settings. 
    If admin approval is not required, the user will be automatically approved.

    **When to use:**
    - Use this endpoint when creating a new user account for the system.
    - Typically used during registration or user onboarding.

    **How to use:**
    - Send a `POST` request with the user details in the request body, including fields such as `username`, `email`, and any other required information.
    - The user details are validated using the `AuthorSerializer`.
    - If admin approval is not required, the user will be automatically approved and can log in immediately after receiving the `access` and `refresh` tokens.
    - If admin approval is required, the user account will be marked as pending, and an administrator will need to approve the account before full access is granted.
    - On successful creation, the system returns the newly created user's information along with a pair of JWT tokens: `access` and `refresh`.

    **Why use or not use:**
    - Use this endpoint to allow users to create an account and initiate the approval or approval-free signup process.
    - This endpoint should not be used for updating existing user details. For that, use the update endpoint instead.
    """,
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
@authentication_classes([])
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
    operation_description="""
    Authenticates a user based on the provided credentials (username and password). 
    If the credentials are valid, the system returns JWT tokens (refresh and access tokens) along with the user's basic information.

    **When to use:**
    - Use this endpoint for authenticating users when they log into the system.
    - The authentication process will return JWT tokens to allow users to interact with other protected API endpoints.

    **How to use:**
    - Send a `POST` request with the `username` and `password` in the request body.
    - The `username` should match the user's registered username, and the `password` should be the correct password for the account.
    - If the credentials are valid, the system returns the user's basic information (e.g., `id`, `username`, and `email`), along with a pair of JWT tokens: `access` and `refresh`.
    - The `access` token is used for accessing protected resources, while the `refresh` token can be used to obtain a new access token once it expires.
    - If the account is pending approval, the response will indicate that the user is awaiting admin approval.
    - If the credentials are incorrect, the response will indicate "Invalid Credentials."

    **Why use or not use:**
    - Use this endpoint to authenticate users and generate JWT tokens that can be used for further interactions with the system.
    - This endpoint should not be used for new user registration or account management (use a separate registration endpoint for that).
    """,
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
    operation_description="""
    Use this endpoint to retrieve all follow requests sent by the current user that are still pending approval. 
    This includes requests that have not yet been accepted or rejected by the target authors.

    **When to use:**
    - Use this endpoint when you want to retrieve all follow requests you have sent that are still pending approval.
    - This is useful for tracking follow requests you've made to other users and monitoring their approval status.

    **How to use:**
    - Send a `GET` request to this endpoint, which will automatically retrieve all pending follow requests sent by the currently authenticated user.
    - The response will include details about each pending request, such as the `actor` (the user who sent the request) and the `object` (the target of the follow request).
    - Pending requests are filtered by the actor (the current user) and only those that have not been accepted will be returned.

    **Why use or not use:**
    - Use this endpoint to check the status of follow requests you’ve sent but have not yet been accepted.
    - Do not use this endpoint to manage incoming follow requests or check requests sent by other users.
    """,
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
    operation_description="""
    Removes a pending follow request sent by the current user to a specified author.
    This action deletes the follow request and notifies the target author through a WebSocket message.

    **When to use:**
    - Use this endpoint when you want to cancel a pending follow request that you have sent to another author.
    - This is useful for users who wish to retract a follow request before it is accepted.

    **How to use:**
    - Send a `DELETE` request to this endpoint with the `author_uuid` of the target author whose follow request you want to remove.
    - The `author_uuid` should be provided as a path parameter and corresponds to the UUID of the author.
    - If the follow request exists and is still pending, it will be removed from the system.
    - If the follow request is successfully removed, a confirmation message will be returned.
    - If no pending follow request is found, an error message will be returned indicating that no follow request was found.
    - The target author will also be notified through WebSocket about the removal of the follow request.

    **Why use or not use:**
    - Use this endpoint if you need to cancel a follow request you have sent and retract your follow attempt before it is accepted.
    - This endpoint should not be used for managing incoming follow requests or removing accepted follow requests.
    """,
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
    operation_description="""
    Unfollows an author, removing the current user from the target author's list of followers.
    This action is useful when a user wants to stop following another author, retracting any previous follow action.

    **When to use:**
    - Use this endpoint when you want to unfollow an author you are currently following.
    - This is useful for managing your list of followed authors and stopping notifications from them.

    **How to use:**
    - Send a `DELETE` request to this endpoint with the `author_id` of the target author whom you wish to unfollow.
    - The `author_id` should be provided as a path parameter and corresponds to the UUID of the author you wish to unfollow.
    - If you are currently following the author, the system will remove you from the author's followers and return a success message.
    - If you are not following the author, the system will return an error message indicating that you are not following the target author.
    - If the specified author does not exist, the system will return an error message indicating that the author was not found.
    - The target author will be notified via WebSocket about the unfollow action.

    **Why use or not use:**
    - Use this endpoint if you wish to stop following an author and no longer receive updates or notifications from them.
    - This endpoint should not be used to manage follow requests or incoming followers. For follow request management, use the appropriate endpoints for follow request actions.
    """,
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
    operation_description="""
    Checks the relationship status between the current user and a target author.
    This includes determining whether the current user is following the author, whether the author is following the current user,
    and whether both users are following each other, making them "friends".

    **When to use:**
    - Use this endpoint when you want to check the relationship status between the current user and another author.
    - This can be helpful for displaying follow status, mutual friendships, or determining how users are connected within the platform.

    **How to use:**
    - Send a `GET` request to this endpoint with the `author_uuid` of the target author whose relationship status you want to check.
    - The `author_uuid` should be provided as a path parameter and corresponds to the UUID of the author.
    - The response will include three boolean values:
        - `is_following`: True if the current user is following the target author.
        - `is_followed_by`: True if the target author is following the current user.
        - `is_friend`: True if both users are following each other.
    - If the specified author does not exist, an error message will be returned with a `404` status.

    **Why use or not use:**
    - Use this endpoint to quickly assess the relationship between two authors (e.g., for displaying follow status or mutual connections).
    - This endpoint should not be used for managing follow actions (use appropriate endpoints for following or unfollowing).
    """,
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
    operation_description="""
    Retrieves statistics about the specified author's relationships. This includes the total number of followers, the total number of users
    the author is following, and the number of mutual followers (friends). These metrics provide insights into the author's social connections.

    **When to use:**
    - Use this endpoint when you want to retrieve key statistics about an author's relationships with others on the platform.
    - This can be useful for displaying basic social metrics, such as follower counts or mutual followers, on an author's profile.

    **How to use:**
    - Send a `GET` request to this endpoint with the `author_uuid` of the author whose statistics you want to retrieve.
    - The `author_uuid` should be provided as a path parameter and corresponds to the UUID of the target author.
    - The response will include the following fields:
        - `followers`: The total number of followers the author has.
        - `following`: The total number of users the author is following.
        - `friends`: The total number of mutual followers (friends) between the author and others.
    - If the specified author does not exist, an error message will be returned with a `404` status.

    **Why use or not use:**
    - Use this endpoint to get a quick overview of an author's social connections and their standing within the platform.
    - Do not use this endpoint to manipulate relationships or follow/unfollow users. For managing relationships, use other appropriate endpoints.
    """,
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
        followers = author.followers.all()
        
        # Format each follower according to the specification
        formatted_followers = []
        for follower in followers:
            formatted_followers.append({
                "type": "author",
                "id": follower.id,
                "host": follower.host,
                "displayName": follower.displayName,
                "page": follower.page,
                "github": follower.github,
                "profileImage": follower.profileImage
            })
        
        response_data = {
            "type": "followers",
            "followers": formatted_followers
        }
        return Response(response_data)
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@swagger_auto_schema(
    method="post",
    operation_summary="Repost a Post",
    operation_description="""
    Allows a user to create a repost of an existing post. The original post must be public for reposting. 
    This action will create a new post that references the original post, incrementing its repost count.
    
    **When to use:**
    - Use this endpoint when you want to repost a public post to your profile. 
    - This is helpful for users who want to share content from others with their followers.
    
    **How to use:**
    - Send a `POST` request to this endpoint with the `post_id` of the original post that you wish to repost.
    - The `post_id` should be provided as a path parameter and corresponds to the ID of the post you wish to repost.
    - The request will check if the post is public and whether the current user has already reposted it. If either condition is not met, an appropriate error will be returned.
    - If the repost is successful, a new post will be created on your profile referencing the original post, and the repost count of the original post will be updated.
    
    **Why use or not use:**
    - Use this endpoint to share public posts from others and increase visibility for that post.
    - Do not use this endpoint for reposting private posts, as only public posts can be reposted. 
    - Avoid reposting a post you have already reposted, as it will trigger an error.
    """,
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
    operation_description="""
    Retrieve a list of followers for a specific author based on their UUID. This endpoint will return 
    the details of each follower, such as their username, display name, and other public information.

    **When to use:**
    - Use this endpoint when you need to fetch the followers of a specific author.
    - This can be useful for displaying the list of people following an author or for gathering information 
      about the author's audience.

    **How to use:**
    - Send a `GET` request to this endpoint with the `author_uuid` as a path parameter.
    - The `author_uuid` represents the UUID of the author whose followers you want to retrieve.
    - If the author exists, the system will return a list of followers with details like `id`, `uuid`, `displayName`, 
      `email`, and other public information of each follower.
    - If the author does not exist or if the request is unauthorized, the system will return an appropriate error message.
    
    **Why use or not use:**
    - Use this endpoint to retrieve a list of followers for a given author to analyze their network or display the followers.
    - Do not use this endpoint to access a list of users who are following a specific author if you do not have the correct 
      authorization or if the author is not found.
    """,
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
    
    
@swagger_auto_schema(
    method="get",
    operation_summary="Get a list of followers for a specific author",
    operation_description="""
    Use this endpoint to retrieve the list of followers for a specific author identified by their `author_serial` (UUID).
    The response will include the details of all the followers associated with the author.

    **When to use:**
    - Use this endpoint when you need to fetch the list of followers for a specific author.
    - The author is identified by the `author_serial` (UUID) in the URL path.

    **How to use:**
    - Send a `GET` request to this endpoint with the `author_serial` in the URL path.
    - The response will include details of all the followers of the author, including their serialized data.

    **Why use or not use:**
    - This endpoint should be used when you want to view all the followers of a specific author.
    - Do not use this endpoint if the author does not exist or the `author_serial` is invalid.
    - The user must be authenticated to access this data (i.e., authentication is required).
    """,
    manual_parameters=[
        openapi.Parameter(
            "author_serial",
            openapi.IN_PATH,
            description="UUID of the author whose followers are to be fetched",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    request_body=None,
    responses={
        200: openapi.Response(
            description="Followers fetched successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "type": openapi.Schema(type=openapi.TYPE_STRING, description="The type of resource (followers)"),
                    "followers": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                            "uuid": openapi.Schema(type=openapi.TYPE_STRING, description="UUID of the author"),
                            "name": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the follower"),
                            # Add other fields you need from AuthorSerializer
                        }),
                        description="List of followers",
                    ),
                },
            ),
        ),
        400: openapi.Response(
            description="Bad request or error fetching followers.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                },
            ),
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Followers"],
)
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


@swagger_auto_schema(
    method="get",
    operation_summary="Get specific follower details",
    operation_description="""
    Use this endpoint to fetch the details of a specific follower of an author identified by `author_serial`.
    The `foreign_author_fqid` refers to the follower's unique identifier.

    **When to use:**
    - Use this endpoint when you need to fetch details about a specific follower of an author.
    - The author and the follower are identified by `author_serial` and `foreign_author_fqid` respectively.
    - The follower must already exist for the author.

    **How to use:**
    - Send a `GET` request to this endpoint with the `author_serial` and `foreign_author_fqid` in the URL path.
    - The response will return the details of the `foreign_author` if they are a follower of the specified author.

    **Why use or not use:**
    - This endpoint is useful when you want to check if a particular author follows a specific user and retrieve their details.
    - Do not use this endpoint if the foreign author is not following the specified author, as the response will be a `404` error.
    - Authentication is required to ensure the user is authorized to check followers.
    """,
    manual_parameters=[
        openapi.Parameter(
            "author_serial",
            openapi.IN_PATH,
            description="UUID of the author whose followers are being queried",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "foreign_author_fqid",
            openapi.IN_PATH,
            description="URL-encoded ID of the follower to fetch details for",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    request_body=None,
    responses={
        200: openapi.Response(
            description="Follower details fetched successfully.",
            schema=AuthorSerializer(),
        ),
        404: openapi.Response(
            description="Follower not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Followers"],
)
@swagger_auto_schema(
    method="put",
    operation_summary="Add a specific follower",
    operation_description="""
    Use this endpoint to add a specific follower to an author's list of followers.

    **When to use:**
    - Use this endpoint when you want to accept a follow request and add the `foreign_author` as a follower of the specified `author`.
    - The `foreign_author_fqid` identifies the follower being added.

    **How to use:**
    - Send a `PUT` request to this endpoint with the `author_serial` and `foreign_author_fqid` in the URL path.
    - The `foreign_author` will be added to the author's followers.

    **Why use or not use:**
    - This endpoint should be used when you want to allow an author to accept a follow request and add a follower.
    - Do not use if the author does not exist, or if the foreign author is already following the author.
    - Ensure that the user is authenticated as only authenticated users can perform this operation.
    """,
    manual_parameters=[
        openapi.Parameter(
            "author_serial",
            openapi.IN_PATH,
            description="UUID of the author whose followers are being modified",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "foreign_author_fqid",
            openapi.IN_PATH,
            description="URL-encoded ID of the follower to add",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    request_body=None,
    responses={
        201: openapi.Response(
            description="Follower added successfully.",
        ),
        400: openapi.Response(
            description="Bad request or already following.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Followers"],
)
@swagger_auto_schema(
    method="delete",
    operation_summary="Remove a specific follower",
    operation_description="""
    Use this endpoint to remove a specific follower from an author's list of followers.

    **When to use:**
    - Use this endpoint when you want to remove a follower from an author's list.
    - The `foreign_author_fqid` identifies the follower to be removed.

    **How to use:**
    - Send a `DELETE` request to this endpoint with the `author_serial` and `foreign_author_fqid` in the URL path.
    - The `foreign_author` will be removed from the author's followers.

    **Why use or not use:**
    - This endpoint should be used when an author wants to remove a follower from their list.
    - Do not use this endpoint if the foreign author is not a follower of the author.
    - Ensure that the user is authenticated to perform this operation.
    """,
    manual_parameters=[
        openapi.Parameter(
            "author_serial",
            openapi.IN_PATH,
            description="UUID of the author whose followers are being modified",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "foreign_author_fqid",
            openapi.IN_PATH,
            description="URL-encoded ID of the follower to remove",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    request_body=None,
    responses={
        204: openapi.Response(
            description="Follower removed successfully.",
        ),
        404: openapi.Response(
            description="Follower not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                },
            ),
        ),
        401: "Unauthorized",
    },
    tags=["Followers"],
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
    operation_description="""
    Retrieve a list of authors that a specific author is following based on their UUID. This endpoint will return 
    the details of each author being followed, such as their username, display name, and other public information.

    **When to use:**
    - Use this endpoint when you need to fetch the list of authors that a particular author is following.
    - This can be useful for understanding the author's network or displaying the authors they are following.

    **How to use:**
    - Send a `GET` request to this endpoint with the `author_uuid` as a path parameter.
    - The `author_uuid` represents the UUID of the author whose following list you want to retrieve.
    - If the author exists, the system will return a list of authors they are following, with details such as `id`, `uuid`, 
      `displayName`, `email`, and other public information of each followed author.
    - If the author does not exist or if the request is unauthorized, the system will return an appropriate error message.
    
    **Why use or not use:**
    - Use this endpoint to retrieve a list of authors that a specific author is following to explore their connections or display their network.
    - Do not use this endpoint to fetch the followers of an author or if you do not have the appropriate authorization.
    """,
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
    operation_description="""
    Retrieve a list of friends for a specific author based on their UUID. Friends are defined as authors who are 
    both following and followed by the current author.

    **When to use:**
    - Use this endpoint when you need to retrieve a list of mutual followers between the current author and 
      another author, also referred to as friends.
    - This is useful when displaying a list of friends or mutual connections.

    **How to use:**
    - Send a `GET` request to this endpoint with the `author_uuid` as a path parameter.
    - The `author_uuid` represents the UUID of the author whose friends you want to retrieve.
    - If the author exists, the system will return a list of authors who are both following and followed by the given 
      author.
    - The response will include details of each friend, such as `id`, `uuid`, `displayName`, and other public 
      information of each friend author.
    - If the author does not exist or if the request is unauthorized, the system will return an appropriate error message.
    
    **Why use or not use:**
    - Use this endpoint to identify and display mutual followers (friends) of a specific author.
    - Do not use this endpoint if you are looking for non-mutual followers or if the authorization is insufficient.
    """,
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
    operation_description="""
    Update the profile of a specified author. This operation allows an author to update their own profile information, 
    such as display name, email, and other optional details. Only the author themselves is authorized to make these changes.
    
    **When to use:**
    - Use this endpoint when an authenticated author wants to update their own profile information.
    - This can be useful for updating personal details such as `displayName`, `email`, `profileImage`, `username`, and other fields.

    **How to use:**
    - Send a `POST` request to this endpoint with the `author_uuid` as a path parameter.
    - Include the fields to be updated in the request body. The fields are optional, so you can update only the ones you wish to modify.
    - If the `password` is included, it will be updated; otherwise, no change to the password will occur.
    - The request body should be in JSON format and include any of the fields such as `displayName`, `github`, `profileImage`, `email`, etc.
    - You must be authenticated, and only the specified author can update their profile. If you attempt to update someone else's profile, the server will return a `403 Permission Denied` error.
    
    **Why use or not use:**
    - Use this endpoint to modify the profile details of the authenticated user.
    - Do not use this endpoint to modify other authors' profiles; this is strictly for the author's own account.
    - Avoid submitting invalid data or empty fields if they are not meant to be updated, as it will result in a `400 Invalid input` error.
    """,
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
    operation_description="""
    Fetch a post by its ID. This operation retrieves the details of a post by its unique identifier. The post must have 
    a visibility status of either 'PUBLIC' or 'UNLISTED' in order for the request to succeed. Posts with 'PRIVATE' or 
    'FRIENDS_ONLY' visibility will not be accessible by non-authorized users.
    
    **When to use:**
    - Use this endpoint to retrieve details of a post by its unique ID.
    - This can be helpful if you are trying to view a post that is public or unlisted, where visibility settings allow broad access.
    - Ideal for fetching posts when the visibility status of the post is either `PUBLIC` or `UNLISTED`.

    **How to use:**
    - Send a `GET` request to this endpoint with the `post_id` as a path parameter.
    - The `post_id` refers to the unique identifier of the post you want to retrieve.
    - If the post visibility is `PUBLIC` or `UNLISTED`, the post data will be returned in the response body using the `PostSerializer`.
    - If the post visibility is `PRIVATE` or `FRIENDS_ONLY`, the server will respond with a `403 Forbidden` error and a message indicating that you are not authorized to view the post.

    **Why use or not use:**
    - Use this endpoint to access public or unlisted posts by ID.
    - Do not use this endpoint for private posts or posts that are visible only to specific groups (e.g., friends-only posts). If you are not authorized to view the post, a `403 Forbidden` will be returned.
    - Avoid unauthorized access attempts to private posts, as this would violate the privacy settings and security of the application.
    """,
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


@swagger_auto_schema(
    method="get",
    operation_summary="Verify the connection for the Node user",
    operation_description="""
    Use this endpoint to verify the connection for a Node user. It returns a success message along with the user's connection details.

    **When to use:**
    - Use this endpoint when you need to verify the connection of a Node user.
    - The response will confirm the connection status and provide details about the authenticated user.

    **How to use:**
    - Send a `GET` request to this endpoint.
    - The response will indicate the connection status and return the user's URL if available, or the user’s identifier.

    **Why use or not use:**
    - This endpoint is useful when checking if the Node user is successfully connected or authenticated.
    - Do not use if the user is not authenticated or doesn't have a valid Node connection.
    """,
    request_body=None,
    responses={
        200: openapi.Response(
            description="Connection successfully verified.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, description="Status of the request"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
                    "node": openapi.Schema(type=openapi.TYPE_STRING, description="URL or identifier of the authenticated user"),
                },
            ),
        ),
        401: "Unauthorized - The user must be authenticated.",
        400: openapi.Response(
            description="Error occurred during the connection verification.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, description="Error status"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                },
            ),
        ),
    },
    tags=["Node Connection"],
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


@swagger_auto_schema(
    method="get",
    operation_summary="Test outgoing connections to remote nodes",
    operation_description="""
    Use this endpoint to test outgoing connections to remote nodes by making requests to their endpoints.

    **When to use:**
    - Use this endpoint when you want to test if the outgoing connections from your system to remote nodes are functioning.
    - This is particularly useful for verifying the availability and connectivity of remote nodes linked to your system.

    **How to use:**
    - Send a `GET` request to this endpoint.
    - The endpoint will check the connectivity to all active remote nodes and provide the results of the connection tests.

    **Why use or not use:**
    - This endpoint is useful for administrators or systems integrators who need to ensure that all remote nodes are reachable and that the outgoing connections to those nodes work.
    - Do not use if there are no active remote nodes in the database or if the remote node endpoints are not configured properly.
    """,
    request_body=None,
    responses={
        200: openapi.Response(
            description="Test completed successfully. Returns the results of the connection tests.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, description="Status of the overall operation"),
                    "test_results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "node_url": openapi.Schema(type=openapi.TYPE_STRING, description="URL of the remote node"),
                                "outgoing_test": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "status": openapi.Schema(type=openapi.TYPE_STRING, description="Status of the outgoing test"),
                                        "status_code": openapi.Schema(type=openapi.TYPE_INTEGER, description="HTTP status code of the response"),
                                        "response": openapi.Schema(type=openapi.TYPE_STRING, description="Response body or error message from the remote node"),
                                    }
                                ),
                            }
                        ),
                    ),
                },
            ),
        ),
        404: openapi.Response(
            description="No remote nodes found in database.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, description="Error status"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                },
            ),
        ),
        500: openapi.Response(
            description="Internal server error during the test.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, description="Error status"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                    "type": openapi.Schema(type=openapi.TYPE_STRING, description="Error type (exception name)"),
                },
            ),
        ),
    },
    tags=["Node Connection"],
)
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
                # endpoint = 'api/authors/931b3149-9101-4bb6-a78d-3350fdb70615/posts/all/'
                endpoint = 'api/authors/931b3149-9101-4bb6-a78d-3350fdb70615/posts/all'
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


@swagger_auto_schema(
    method="get",
    operation_summary="Retrieve the inbox contents for a given author",
    operation_description="""
    Use this endpoint to retrieve the inbox contents of a specific author identified by their UUID.

    **When to use:**
    - Use this endpoint to get the inbox data for an author, which includes posts, likes, comments, and follow requests.
    - It is useful for checking activities related to a specific author.

    **How to use:**
    - Send a `GET` request to this endpoint with the `author_serial` as part of the URL.
    - The inbox contents for the specified author will be returned.

    **Why use or not use:**
    - This endpoint should be used when you need to retrieve the activities for a specific author.
    - Do not use this endpoint if you are not authenticated or if the author UUID does not exist.
    """,
    responses={
        200: openapi.Response(
            description="Inbox retrieved successfully.",
            schema=InboxSerializer()
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Inbox"],
)
@swagger_auto_schema(
    method="post",
    operation_summary="Add activity to the author's inbox",
    operation_description="""
    Use this endpoint to add activities such as posts, likes, comments, and follow requests to an author's inbox.

    **When to use:**
    - Use this endpoint to add activities like posts, likes, comments, or follow requests to the author's inbox.
    - The request body must specify the type of activity (`post`, `like`, `comment`, or `follow`).

    **How to use:**
    - Send a `POST` request to this endpoint with the `author_serial` as part of the URL.
    - The request body should include the activity type and necessary data (e.g., post content, target UUID for follow request).
    - Depending on the activity type, the corresponding action will be performed (e.g., creating a post, processing a follow request).

    **Why use or not use:**
    - This endpoint should be used when you want to add activities to an author's inbox, such as posts or follow requests.
    - Do not use if the activity type is unsupported or if the required data (e.g., `author_id`, `content`, etc.) is missing.
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "type": openapi.Schema(type=openapi.TYPE_STRING, description="Type of activity (e.g., post, like, comment, follow)"),
            "author_id": openapi.Schema(type=openapi.TYPE_STRING, description="UUID of the author performing the activity (used for posts and follow requests)"),
            "author": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "host": openapi.Schema(type=openapi.TYPE_STRING, description="Host URL of the author performing the activity"),
                }
            ),
            "content": openapi.Schema(type=openapi.TYPE_STRING, description="Content of the activity (e.g., post content)"),
            "visibility": openapi.Schema(type=openapi.TYPE_STRING, description="Visibility of the post (optional)"),
            "title": openapi.Schema(type=openapi.TYPE_STRING, description="Title of the post (optional)"),
            "description": openapi.Schema(type=openapi.TYPE_STRING, description="Description of the post (optional)"),
            "contentType": openapi.Schema(type=openapi.TYPE_STRING, description="Content type of the post (optional)"),
            "image": openapi.Schema(type=openapi.TYPE_STRING, description="Image URL for the post (optional)"),
            "object": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_STRING, description="UUID of the target user (used for follow requests)"),
                }
            ),
        },
        required=["type"],
    ),
    responses={
        201: openapi.Response(
            description="Activity added to inbox successfully.",
            schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Success message")
            }),
        ),
        400: openapi.Response(
            description="Invalid input data or unsupported activity type.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            )
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Inbox"],
)
@swagger_auto_schema(
    method="delete",
    operation_summary="Clear all activities from the author's inbox",
    operation_description="""
    Use this endpoint to clear all activities from a given author's inbox.

    **When to use:**
    - Use this endpoint to clear all posts, likes, comments, and follow requests from the inbox of the specified author.
    - This is useful for managing inbox contents or clearing outdated activities.

    **How to use:**
    - Send a `DELETE` request to this endpoint with the `author_serial` as part of the URL.
    - This will clear all activities from the author's inbox.

    **Why use or not use:**
    - This endpoint should be used when you want to reset or clear the inbox of an author.
    - Do not use if you want to retain the inbox contents.
    """,
    responses={
        204: openapi.Response(
            description="Inbox cleared successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING, description="Success message")
                }
            ),
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Inbox"],
)

@csrf_exempt
@authentication_classes([NodeBasicAuthentication])
@permission_classes([IsAuthenticatedOrNode])
@api_view(['POST', 'GET', 'DELETE'])
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
        print("AAAAAAAAAAAAA")
        data = request.data
        item_type = data.get('type', '').lower()

        try:
            if item_type == "posts":

                print("WE ARE INSIDE INBOX POSTS")
                # Handle multiple posts
                print("Handling multiple posts.")
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
                print("WE ARE INSIDE SINGLE POST HANDLER")
                # Handle a single post
                author_data = data.get('author', {})
                author_id = author_data.get('id')
                if not author_id:
                    return Response({'error': 'Author ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

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

                # Now process the post
                post_id = data.get('id')
                if not post_id:
                    return Response({'error': 'Post ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

                # Parse post UUID from the post_id URL
                post_uuid = post_id.rstrip('/').split('/')[-1]

                # Get or create the post
                post, post_created = Post.objects.get_or_create(
                    id=post_uuid,
                    defaults={
                        'author': author,
                        'title': data.get('title', ''),
                        'description': data.get('description', ''),
                        'contentType': data.get('contentType', 'text/plain'),
                        'content': data.get('content', ''),
                        'published': data.get('published', timezone.now()),
                        'visibility': data.get('visibility', 'PUBLIC'),
                        'page': data.get('page', ''),
                    }
                )

                # If the post exists, update its info
                if not post_created:
                    post.title = data.get('title', post.title)
                    post.description = data.get('description', post.description)
                    post.contentType = data.get('contentType', post.contentType)
                    post.content = data.get('content', post.content)
                    post.published = data.get('published', post.published)
                    post.visibility = data.get('visibility', post.visibility)
                    post.page = data.get('page', post.page)
                    post.save()

                # Handle comments if any
                comments_data = data.get('comments', {}).get('src', [])
                for comment_data in comments_data:
                    # Process each comment (similar logic as before)
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

                return Response({'message': 'Post added to inbox and created locally.'}, status=status.HTTP_201_CREATED)
            elif item_type == 'like':
                print("WE ARE INSIDE THE LIKE SECTION ...IMPLEMENT THE INBOX!")
                return Response({'message': 'Comment added to inbox and created locally.'}, status=status.HTTP_201_CREATED)
                pass

            elif item_type == 'comment':
                data = request.data

                try:
                    # Extract necessary data
                    comment_data = request.data
                    
                    # Get or create the comment author
                    author_data = comment_data.get('author', {})
                    author_id = author_data.get('id')
                    author_uuid = author_id.rstrip('/').split('/')[-1]
                    
                    author, _ = Author.objects.get_or_create(
                        uuid=author_uuid,
                        defaults={
                            'displayName': author_data.get('displayName', ''),
                            'host': author_data.get('host', ''),
                            'page': author_data.get('page', ''),
                            'github': author_data.get('github', ''),
                            'profileImage': author_data.get('profileImage', '')
                        }
                    )

                    # Get the post
                    post_data = comment_data.get('post', {})
                    post_id = post_data.get('id')
                    post = get_object_or_404(Post, id=post_id)

                    # Create the comment
                    comment, created = Comment.objects.get_or_create(
                        id=comment_data.get('id'),
                        defaults={
                            'post': post,
                            'author': author,
                            'content': comment_data.get('content', ''),
                            'contentType': comment_data.get('contentType', 'text/plain'),
                            'published': comment_data.get('published', timezone.now())
                        }
                    )

                    # Add to inbox
                    inbox.comments.add(comment)

                    return Response(
                        {'message': 'Comment added to inbox successfully.'}, 
                        status=status.HTTP_201_CREATED
                    )

                except Post.DoesNotExist:
                    return Response(
                        {'error': 'Referenced post does not exist'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                except Exception as e:
                    return Response(
                        {'error': str(e)}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            elif item_type == 'follow':
                # Handle Follow Activity
                print("Handling follow request.")
                    # Extract actor and object data
                actor_data = data.get('actor', {})
                object_data = data.get('object', {})

                # Get or create the actor (follower)
                actor_id = actor_data.get('id')
                actor_uuid = actor_id.rstrip('/').split('/')[-1]
                actor, created = Author.objects.get_or_create(
                    uuid=actor_uuid,
                    defaults={
                        'displayName': actor_data.get('displayName', ''),
                        'host': actor_data.get('host', ''),
                        'page': actor_data.get('url', ''),
                        'github': actor_data.get('github', ''),
                        'profileImage': actor_data.get('profileImage', ''),
                    }
                )

                # Get or create the object (target author)
                object_id = object_data.get('id')
                object_uuid = object_id.rstrip('/').split('/')[-1]
                target_author, created = Author.objects.get_or_create(
                    uuid=object_uuid,
                    defaults={
                        'displayName': object_data.get('displayName', ''),
                        'host': object_data.get('host', ''),
                        'page': object_data.get('page', ''),
                        'github': object_data.get('github', ''),
                        'profileImage': object_data.get('profileImage', ''),
                    }
                )

                # Create a follow request
                follow_request, created = FollowRequest.objects.get_or_create(
                    actor=actor,
                    object=target_author,
                    defaults={'summary': data.get('summary', '')}
                )
                if created:
                    return Response({"status": "success", "message": "Follow request sent successfully."}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"status": "info", "message": "Follow request already exists."}, status=status.HTTP_200_OK)

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
    
    
@swagger_auto_schema(
    method="get",
    operation_summary="Sync remote authors from active remote nodes",
    operation_description="""
    Use this endpoint to synchronize authors from active remote nodes.

    **When to use:**
    - Use this endpoint to fetch authors from connected remote nodes and sync them with your local database.
    - This is useful when you want to keep the list of authors in your local system up to date with remote nodes.

    **How to use:**
    - Send a `GET` request to this endpoint to start the synchronization process.
    - The system will attempt to fetch all authors from the active remote nodes and add them to the local database.
    - The response will include the synchronization status and any errors encountered during the process.

    **Why use or not use:**
    - This endpoint should be used when you need to update the list of remote authors in your local system.
    - If no remote nodes are active or if the network is unreachable, the synchronization will fail.
    """,
    responses={
        200: openapi.Response(
            description="Authors synchronized successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, description="Sync status"),
                    "sync_results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "node_url": openapi.Schema(type=openapi.TYPE_STRING, description="Remote node URL"),
                                "authors_synced": openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of authors successfully synced"),
                                "errors": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(type=openapi.TYPE_STRING, description="Error messages")
                                ),
                            }
                        ),
                    ),
                }
            )
        ),
        404: openapi.Response(
            description="No remote nodes found in the database.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, description="Error status"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            )
        ),
        500: openapi.Response(
            description="Internal server error during sync.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, description="Error status"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                    "type": openapi.Schema(type=openapi.TYPE_STRING, description="Error type")
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Sync"],
)
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_remote_authors(request):

    print("INCOMING REQUEST BODY:" , request)
    try:
        # Get all active remote nodes
        remote_nodes = ToWhichItsConnected.objects.filter(active=True)
        if not remote_nodes:
            return Response({
                "status": "error",
                "message": "No remote nodes found in the database. Please create one in the admin panel."
            }, status=status.HTTP_404_NOT_FOUND)
        print(remote_nodes)
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
                endpoint = 'api/authors/'

                response = make_node_request(
                    base_url=base_url,
                    endpoint=endpoint,
                )

                print("****************" , response.data)

                if response.status_code == 200:
                    print(response)
                    data = response.data.authors.json()
                    print(data)
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
                                'is_active': True,  # Remote authors are not local users
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

        # Get the target host from object_author
        target_host = object_author.get('host')
        if not target_host:
            # Extract the host from the 'id' field if 'host' is not provided
            target_host = '/'.join(object_author.get('id').split('/')[:3])
        target_host = target_host.rstrip('/')

        # Get the remote node corresponding to the target host
        try:
            node = ToWhichItsConnected.objects.get(url__contains=target_host, active=True)
        except ToWhichItsConnected.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"No active remote node found for host {target_host}"
            }, status=status.HTTP_404_NOT_FOUND)

        print("Preparing follow activity for node:", node.url)

        # Make a deep copy of the follow activity to avoid mutating the original data
        follow_activity_copy = copy.deepcopy(follow_activity)

        # Update the 'object' field with the correct author URL for the target node
        follow_activity_copy['object']['id'] = f"{node.url.rstrip('/')}/authors/{author_uuid}"

        # Update the 'object' field's host if necessary
        follow_activity_copy['object']['host'] = node.url.rstrip('/')

        # Define the endpoint for the target node's inbox
        endpoint = f"api/authors/{author_uuid}/inbox/"

        # Send the follow request to the remote node's inbox using make_node_request
        response = make_node_request(
            base_url=node.url,
            endpoint=endpoint,
            method='POST',
            data=follow_activity_copy
        )

        print("Response from node:", response.status_code, response.text)

        if response.status_code in [200, 201]:
            return Response({
                "status": "completed",
                "message": "Follow request sent successfully."
            }, status=status.HTTP_200_OK)
        else:
            error_message = f"Failed to send follow request to {node.url}: Status {response.status_code}, Response: {response.text}"
            print(error_message)
            return Response({
                "status": "error",
                "message": error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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