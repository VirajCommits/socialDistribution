from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import AdminSettings
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from .models import Author, Post, Comment, Like, FollowRequest


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

        # Handle DELETE request to delete the post
        elif request.method == "DELETE" and not action:
            post.delete()  # Now delete the original post or repost
            return Response(status=status.HTTP_204_NO_CONTENT)

            
        # Handle DELETE request to delete the post
        elif request.method == "DELETE" and not action:
            post.delete()  # Now delete the original post or repost
            return Response(status=status.HTTP_204_NO_CONTENT)
            
    # Handle PUT request to update the post
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
    current_author = request.user  # The one sending the request
    # The one receiving the request
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
    current_author = request.user  # The one accepting
    requesting_author = get_object_or_404(
        Author, uuid=author_uuid)  # The one who sent request

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
            {"detail": "An error occurred while fetching authors."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='get',
    operation_summary="Fetch the stream of posts for a specific author",
    operation_description="API to retrieve a stream of posts based on the following relationships of the author.",
    manual_parameters=[
        openapi.Parameter(
            'author_id',
            openapi.IN_PATH,
            description="UUID of the author to fetch the stream for",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully fetched posts.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of posts'),
                    'next': openapi.Schema(type=openapi.TYPE_STRING, description='URL to the next page of results'),
                    'previous': openapi.Schema(type=openapi.TYPE_STRING, description='URL to the previous page of results'),
                    'results': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_STRING, description='Post ID'),
                                'author': openapi.Schema(type=openapi.TYPE_OBJECT, description='Post author details', 
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_STRING, description='Author ID'),
                                        'displayName': openapi.Schema(type=openapi.TYPE_STRING, description='Author display name'),
                                        'profileImage': openapi.Schema(type=openapi.TYPE_STRING, description='URL to author profile image')
                                    }
                                ),
                                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Post title'),
                                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Post description'),
                                'contentType': openapi.Schema(type=openapi.TYPE_STRING, description='Content type of the post'),
                                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Main content of the post'),
                                'visibility': openapi.Schema(type=openapi.TYPE_STRING, description='Visibility of the post'),
                                'published': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Post publication timestamp'),
                                'repost_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Count of reposts'),
                            }
                        )
                    )
                }
            )
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
    },
    tags=["Stream"]
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
        visibility__in=["PUBLIC", "PRIVATE", "UNLISTED", "FRIENDS"]
    )

    # Posts from authors the current author is following (but not mutual friends) with visibility PUBLIC and UNLISTED
    other_following_authors = following_authors.exclude(
        id__in=mutual_friends.values("id"))
    other_following_posts = Post.objects.filter(
        author__in=other_following_authors,
        visibility__in=["PUBLIC", "UNLISTED"]
    )

    # Public posts from any author (visible to everyone)
    public_posts = Post.objects.filter(visibility="PUBLIC")

    # Current author's own posts (including private)
    personal_posts = Post.objects.filter(author=current_author)

    # Combine all posts and avoid duplicates
    all_posts = (public_posts |
                 mutual_friends_posts | other_following_posts | personal_posts
                 ).distinct().order_by("-edited_at")

    # Paginate and return response
    paginator = PageNumberPagination()
    paginator.page_size = 10
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

        # Notify the user about their approval status
        if user.is_approved:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User created and approved.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": AuthorSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "message": "User created. Your account is pending admin approval.",
            "user": AuthorSerializer(user).data
        }, status=status.HTTP_201_CREATED)
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
    user = authenticate(username=username, password=password)

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
    method='get',
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
                        'id': openapi.Schema(type=openapi.TYPE_STRING, description='Unique identifier for the follow request'),
                        'actor': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                            'uuid': openapi.Schema(type=openapi.TYPE_STRING, description='UUID of the actor'),
                            'displayName': openapi.Schema(type=openapi.TYPE_STRING, description='Display name of the actor'),
                        }),
                        'object': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                            'uuid': openapi.Schema(type=openapi.TYPE_STRING, description='UUID of the target author'),
                            'displayName': openapi.Schema(type=openapi.TYPE_STRING, description='Display name of the target author'),
                        }),
                        'accepted': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if the follow request is accepted'),
                    }
                )
            )
        ),
        401: "Unauthorized",
    },
    tags=["Follow Requests"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_requests(request):
    """Get all pending follow requests sent by the current user"""
    current_author = request.user
    pending_requests = FollowRequest.objects.filter(
        actor=current_author,
        accepted=False
    )
    serializer = FollowRequestSerializer(pending_requests, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='delete',
    operation_summary="Remove a follow request",
    operation_description="Remove a pending follow request.",
    manual_parameters=[
        openapi.Parameter(
            'author_uuid',
            openapi.IN_PATH,
            description="UUID of the author whose follow request is to be removed",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Follow request successfully removed.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Confirmation message')
                }
            )
        ),
        404: openapi.Response(
            description="No follow request found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Follow Requests"]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_follow_request(request, author_uuid):
    """Remove a pending follow request"""
    current_author = request.user
    target_author = get_object_or_404(Author, uuid=author_uuid)

    follow_requests = FollowRequest.objects.filter(
        actor=current_author,
        object=target_author,
        accepted=False
    )

    if not follow_requests.exists():
        return Response(
            {'detail': 'No follow request found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Delete all pending requests from this user
    follow_requests.delete()

    # Notify the target author through WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{target_author.uuid}",
        {
            'type': 'follow_request_notification',
            'count': FollowRequest.objects.filter(
                object=target_author,
                accepted=False
            ).count(),
            'message': f'{current_author.displayName} removed their follow request'
        }
    )

    return Response({'detail': 'Follow request removed.'}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='delete',
    operation_summary="Unfollow an Author",
    operation_description="Unfollow an author.",
    manual_parameters=[
        openapi.Parameter(
            'author_id',
            openapi.IN_PATH,
            description="UUID of the author to unfollow",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully unfollowed the author.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                }
            )
        ),
        400: openapi.Response(
            description="You are not following this author.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Follow Requests"]
)
@api_view(['DELETE'])
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
                    'type': 'follow_request_notification',
                    'count': FollowRequest.objects.filter(
                        object=target_author,
                        accepted=False
                    ).count(),
                    'message': f'{current_author.displayName} unfollowed you'
                }
            )

            return Response({
                "detail": f"Successfully unfollowed {target_author.displayName}"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "detail": "You are not following this author"
            }, status=status.HTTP_400_BAD_REQUEST)

    except Author.DoesNotExist:
        return Response({
            "detail": "Author not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "detail": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_summary="Check Relationship Status",
    operation_description="Check the relationship status between the current user and a target author.",
    manual_parameters=[
        openapi.Parameter(
            'author_uuid',
            openapi.IN_PATH,
            description="UUID of the author to check the relationship with",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Relationship status retrieved successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'is_following': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='True if the current user is following the target author'),
                    'is_followed_by': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='True if the target author is following the current user'),
                    'is_friend': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='True if both users are following each other')
                }
            )
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Relationships"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_relationship_status(request, author_uuid):
    """Check complete relationship status between current user and target author"""
    try:
        current_author = request.user
        target_author = get_object_or_404(Author, uuid=author_uuid)
        
        is_following = target_author.followers.filter(id=current_author.id).exists()
        is_followed_by = current_author.followers.filter(id=target_author.id).exists()
        is_friend = is_following and is_followed_by
        
        return Response({
            'is_following': is_following,
            'is_followed_by': is_followed_by,
            'is_friend': is_friend
        })
    except Author.DoesNotExist:
        return Response({'error': 'Author not found'}, status=404)

@swagger_auto_schema(
    method='get',
    operation_summary="Get Author Statistics",
    operation_description="Retrieve statistics about the specified author's relationships.",
    manual_parameters=[
        openapi.Parameter(
            'author_uuid',
            openapi.IN_PATH,
            description="UUID of the author for whom to retrieve statistics",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Author statistics retrieved successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'followers': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of followers'),
                    'following': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of users the author is following'),
                    'friends': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of mutual followers (friends)')
                }
            )
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Author Stats"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_author_stats(request, author_uuid):
    try:
        author = get_object_or_404(Author, uuid=author_uuid)
        followers_count = author.followers.count()
        following_count = author.following.count()
        friends_count = author.followers.filter(id__in=author.following.values('id')).count()
        
        return Response({
            'followers': followers_count,
            'following': following_count,
            'friends': friends_count
        })
    except Author.DoesNotExist:
        return Response({'error': 'Author not found'}, status=404)
    
@swagger_auto_schema(
    method='post',
    operation_summary="Repost a Post",
    operation_description="Create a repost of an existing post. The original post must be public.",
    manual_parameters=[
        openapi.Parameter(
            'post_id',
            openapi.IN_PATH,
            description="ID of the post to repost",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Post reposted successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                    'repost_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Updated repost count of the original post')
                }
            )
        ),
        400: openapi.Response(
            description="You have already reposted this post.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        403: openapi.Response(
            description="Post is not public.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        404: openapi.Response(
            description="Post not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Posts"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def repost_post(request, post_id):
    reposted_post = get_object_or_404(Post, id=post_id)

    # Determine the original post
    if reposted_post.is_repost:
        original_post = get_object_or_404(Post, id=reposted_post.original_post_id)
    else:
        original_post = reposted_post

    # Check if the original post is public
    if original_post.visibility != 'PUBLIC':
        return Response({'error': 'Post is not public.'}, status=403)

    # Check if the user has already reposted the original post
    if request.user in original_post.reposted_by.all():
        return Response({'error': 'You have already reposted this post.'}, status=400)

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

    return Response({
        'message': 'Post reposted successfully.',
        'repost_count': original_post.repost_count
    }, status=200)

@swagger_auto_schema(
    method='get',
    operation_summary="Get Author Followers",
    operation_description="Retrieve the list of followers for a specific author.",
    manual_parameters=[
        openapi.Parameter(
            'author_uuid',
            openapi.IN_PATH,
            description="UUID of the author to retrieve followers for",
            type=openapi.TYPE_STRING,
            required=True
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
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the author'),
                        'uuid': openapi.Schema(type=openapi.TYPE_STRING, description='UUID of the author'),
                        'host': openapi.Schema(type=openapi.TYPE_STRING, description='Host of the author'),
                        'displayName': openapi.Schema(type=openapi.TYPE_STRING, description='Display name of the author'),
                        'github': openapi.Schema(type=openapi.TYPE_STRING, description='GitHub URL of the author'),
                        'profileImage': openapi.Schema(type=openapi.TYPE_STRING, description='Profile image URL of the author'),
                        'page': openapi.Schema(type=openapi.TYPE_STRING, description='Page URL of the author'),
                        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the author'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the author'),
                    }
                )
            )
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Authors"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_author_followers(request, author_uuid):
    try:
        author = get_object_or_404(Author, uuid=author_uuid)
        followers = author.followers.all()
        serializer = AuthorSerializer(followers, many=True)
        return Response(serializer.data)
    except Author.DoesNotExist:
        return Response({'error': 'Author not found'}, status=404)

@swagger_auto_schema(
    method='get',
    operation_summary="Get Authors Following",
    operation_description="Retrieve the list of authors that a specific author is following.",
    manual_parameters=[
        openapi.Parameter(
            'author_uuid',
            openapi.IN_PATH,
            description="UUID of the author to retrieve following authors for",
            type=openapi.TYPE_STRING,
            required=True
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
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the author'),
                        'uuid': openapi.Schema(type=openapi.TYPE_STRING, description='UUID of the author'),
                        'host': openapi.Schema(type=openapi.TYPE_STRING, description='Host of the author'),
                        'displayName': openapi.Schema(type=openapi.TYPE_STRING, description='Display name of the author'),
                        'github': openapi.Schema(type=openapi.TYPE_STRING, description='GitHub URL of the author'),
                        'profileImage': openapi.Schema(type=openapi.TYPE_STRING, description='Profile image URL of the author'),
                        'page': openapi.Schema(type=openapi.TYPE_STRING, description='Page URL of the author'),
                        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the author'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the author'),
                    }
                )
            )
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Authors"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_author_following(request, author_uuid):
    try:
        author = get_object_or_404(Author, uuid=author_uuid)
        following = author.following.all()
        serializer = AuthorSerializer(following, many=True)
        return Response(serializer.data)
    except Author.DoesNotExist:
        return Response({'error': 'Author not found'}, status=404)

@swagger_auto_schema(
    method='get',
    operation_summary="Get Author Friends",
    operation_description="Retrieve the list of friends for a specific author. Friends are defined as those who are both following and followed by the author.",
    manual_parameters=[
        openapi.Parameter(
            'author_uuid',
            openapi.IN_PATH,
            description="UUID of the author to retrieve friends for",
            type=openapi.TYPE_STRING,
            required=True
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
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the friend author'),
                        'uuid': openapi.Schema(type=openapi.TYPE_STRING, description='UUID of the friend author'),
                        'host': openapi.Schema(type=openapi.TYPE_STRING, description='Host of the friend author'),
                        'displayName': openapi.Schema(type=openapi.TYPE_STRING, description='Display name of the friend author'),
                        'github': openapi.Schema(type=openapi.TYPE_STRING, description='GitHub URL of the friend author'),
                        'profileImage': openapi.Schema(type=openapi.TYPE_STRING, description='Profile image URL of the friend author'),
                        'page': openapi.Schema(type=openapi.TYPE_STRING, description='Page URL of the friend author'),
                        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the friend author'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the friend author'),
                    }
                )
            )
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Authors"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_author_friends(request, author_uuid):
    try:
        author = get_object_or_404(Author, uuid=author_uuid)
        followers = author.followers.all()
        following = author.following.all()
        friends = followers.filter(id__in=following.values('id'))
        serializer = AuthorSerializer(friends, many=True)
        return Response(serializer.data)
    except Author.DoesNotExist:
        return Response({'error': 'Author not found'}, status=404)

@swagger_auto_schema(
    method='post',
    operation_summary="Update Author Profile",
    operation_description="Update the profile of the specified author. Only the author can update their profile.",
    manual_parameters=[
        openapi.Parameter(
            'author_uuid',
            openapi.IN_PATH,
            description="UUID of the author whose profile is to be updated",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'host': openapi.Schema(type=openapi.TYPE_STRING, description='Host of the author'),
            'displayName': openapi.Schema(type=openapi.TYPE_STRING, description='Display name of the author'),
            'github': openapi.Schema(type=openapi.TYPE_STRING, description='GitHub URL of the author'),
            'profileImage': openapi.Schema(type=openapi.TYPE_STRING, description='Profile image URL of the author'),
            'page': openapi.Schema(type=openapi.TYPE_STRING, description='Page URL of the author'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the author'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the author'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the author (if updating)', write_only=True)
        },
        required=[]  # Specify fields that are required if any
    ),
    responses={
        200: openapi.Response(
            description="Successfully updated the author's profile.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the author'),
                    'uuid': openapi.Schema(type=openapi.TYPE_STRING, description='UUID of the author'),
                    'host': openapi.Schema(type=openapi.TYPE_STRING, description='Host of the author'),
                    'displayName': openapi.Schema(type=openapi.TYPE_STRING, description='Display name of the author'),
                    'github': openapi.Schema(type=openapi.TYPE_STRING, description='GitHub URL of the author'),
                    'profileImage': openapi.Schema(type=openapi.TYPE_STRING, description='Profile image URL of the author'),
                    'page': openapi.Schema(type=openapi.TYPE_STRING, description='Page URL of the author'),
                    'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the author'),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the author'),
                }
            )
        ),
        403: openapi.Response(
            description="Permission denied.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        404: openapi.Response(
            description="Author not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        400: openapi.Response(
            description="Invalid input data.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: "Unauthorized",
    },
    tags=["Authors"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_author_profile(request, author_uuid):
    try:
        author = Author.objects.get(uuid=author_uuid)
        if request.user != author:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Author.DoesNotExist:
        return Response({"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='get',
    operation_summary="Fetch a Post by ID",
    operation_description="Retrieve a post by its ID. The post must be either public or unlisted.",
    manual_parameters=[
        openapi.Parameter(
            'post_id',
            openapi.IN_PATH,
            description="ID of the post to retrieve",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Post retrieved successfully.",
            schema=PostSerializer()  # Use the PostSerializer schema
        ),
        403: openapi.Response(
            description="You are not authorized to view this post.",
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
    },
    tags=["Posts"]
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_post_by_link(request, post_id):
    """
    Fetch a post by ID if it's either public or unlisted.
    """
    # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
    post = get_object_or_404(Post, id=post_id)

    # Check if the post is public or unlisted
    if post.visibility in ["PUBLIC", "UNLISTED"]:
        serializer = PostSerializer(post)
        return Response(serializer.data, status=200)

    # If the post is private or friends-only, return a 403 Forbidden
    return Response({"detail": "You are not authorized to view this post."}, status=403)
