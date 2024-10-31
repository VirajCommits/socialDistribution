from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator

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
        print("This is the data: ----------------- " , data)
        data['content'] = markdown2.markdown(data['content'], extras=["fenced-code-blocks", "tables"])

    if 'title' in data:
        data['title'] = markdown2.markdown(data['title'], extras=["fenced-code-blocks", "tables"])
    
    if 'description' in data:
        data['description'] = markdown2.markdown(data['description'], extras=["fenced-code-blocks", "tables"])
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

@api_view(["GET", "DELETE", "PUT", "POST"])
def post_detail(request, author_serial, post_serial):
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
        
        data = request.data
        if "content" in data:
            markdown_content = data["content"]
            html_content = markdown2.markdown(markdown_content, extras=["fenced-code-blocks", "tables"])
            data["content"] = html_content  # Replace Markdown with HTML for saving
    
        serializer = PostSerializer(post, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # If the action doesn't match any known value
    return Response({"detail": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


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



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_follow_request(request, author_uuid):
    current_author = request.user  # The one sending the request
    target_author = get_object_or_404(Author, uuid=author_uuid)  # The one receiving the request
    
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_follow_request(request, author_uuid):
    current_author = request.user  # The one accepting
    requesting_author = get_object_or_404(Author, uuid=author_uuid)  # The one who sent request
    
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



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_follow_requests(request):
    current_author = request.user
    # Filter to only show pending follow requests
    pending_requests = FollowRequest.objects.filter(object=current_author, accepted=False)
    serializer = FollowRequestSerializer(pending_requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_authors(request):
    try:
        current_author = request.user
        # Exclude the current user and get all other authors
        authors = Author.objects.exclude(id=current_author.id)
        
        author_data = []
        for author in authors:
            # Serialize the author data
            serialized_author = AuthorSerializer(author).data
            
            # Add followers data
            followers = author.followers.all()
            serialized_author['followers'] = [
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
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = AuthorSerializer(data=request.data)
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
    
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
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

