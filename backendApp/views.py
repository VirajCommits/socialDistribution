from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# from .serializers import PostSerializer
from .models import Author , Post
from django.shortcuts import get_object_or_404
from urllib.parse import urlparse
# from django.utils import timezone
from django.shortcuts import render
from urllib.parse import unquote
from rest_framework.pagination import PageNumberPagination
from .models import Comment, Like
from .serializers import CommentSerializer, LikeSerializer

def defaultPath(request):
    return render(request, "index.html")

@api_view(['GET'])
def sample_data(request):
    data = {
        'message': 'Hello from Django to Vue!'
    }
    return Response(data)

# @api_view(['POST'])
# def create_post(request, author_serial):
#     author_serial = unquote(author_serial)
#     print("This is serial author --------------------  " , author_serial)
    
#     data = request.data.copy()
    
#     # Fetch the author instance
#     author = get_object_or_404(Author, id=author_serial)
    
#     # Set the 'author_id' field to the author's ID (URL)
#     data['author_id'] = author.id  # This will be accepted by the serializer
    
#     # Remove fields that are generated automatically and 'author' if present
#     data.pop('id', None)
#     data.pop('page', None)
#     data.pop('published', None)
#     data.pop('type', None)
#     data.pop('author', None)
    
#     serializer = PostSerializer(data=data)
    
#     if serializer.is_valid():
#         post = serializer.save()
#         response_serializer = PostSerializer(post)
#         return Response(response_serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         print(serializer.errors)  # For debugging purposes
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# def vueTest(request):
#     return render(request, "index.html")


# @api_view(['GET' , 'DELETE' , 'PUT'])
# def post_detail(request , author_serial , post_serial):
#     print("GET POST DETAILS>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" , author_serial , post_serial)

#     # Get the author object or return 404 if not found
#     author = get_object_or_404(Author, id=author_serial)
    
#     # Get the post object or return 404 if not found
#     post = get_object_or_404(Post, author=author, id=post_serial)

#     print(" --------- " , request.method)
#     # Handle GET request
#     if request.method == 'GET':
#         # Directly allow access to public and friends-only posts
#         serializer = PostSerializer(post)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     # Handle DELETE request
#     elif request.method == 'DELETE':
#         # Directly delete the post without requiring authentication
#         post.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#     # Handle PUT request
#     elif request.method == 'PUT':
#         # Directly update the post without requiring authentication
#         serializer = PostSerializer(post, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# def get_all_posts(request, author_serial):
#     print(" ----------- >>>>" , author_serial)
#     author_serial = unquote(author_serial)
#     author = get_object_or_404(Author, id=author_serial)
#     posts = Post.objects.filter(author=author).order_by('-published')

#     # Pagination
#     paginator = PageNumberPagination()
#     paginator.page_size = 10  # Adjust as needed
#     result_page = paginator.paginate_queryset(posts, request)

#     serializer = PostSerializer(result_page, many=True)
#     return paginator.get_paginated_response({'type': 'posts', 'items': serializer.data})


@api_view(["POST"])
def create_comment(request, author_id, post_id):
    print("Received author_id:", author_id)
    print("Received post_id:", post_id)
    # Get the author instance or return 404 if not found
    author = get_object_or_404(Author, id=author_id)

    # Get the post instance or return 404 if not found
    post = get_object_or_404(Post, id=post_id)

    # Prepare the data for the serializer
    data = request.data.copy()
    data["author_id"] = str(author.id)  # Ensure it's passed as a string
    data["post_id"] = str(post.id)  # Ensure it's passed as a string

    serializer = CommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def like_post(request, author_id, post_id):
    # Print the incoming author_id and post_id to verify their values
    print("Received author_id:", author_id)
    print("Received post_id:", post_id)

    # Get the author instance or return 404 if not found
    author = get_object_or_404(Author, id=author_id)

    # Get the post instance or return 404 if not found
    post = get_object_or_404(Post, id=post_id)

    # Prepare the data for the serializer
    data = request.data.copy()
    data["author_id"] = str(author.id)  # Ensure it's passed as a string
    data["post_id"] = str(post.id)  # Ensure it's passed as a string
    data["post"] = post.id  # Set the actual post ID

    # Print the data being passed to the serializer for further verification
    print("Data being passed to serializer:", data)

    serializer = LikeSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        # Print the errors if the serializer is invalid
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_comments(request, author_id, post_id):
    author = get_object_or_404(Author, id=author_id)
    post = get_object_or_404(Post, id=post_id, author=author)
    comments = Comment.objects.filter(post=post).order_by("-published")

    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_likes(request, author_id, post_id):
    author = get_object_or_404(Author, id=author_id)
    post = get_object_or_404(Post, id=post_id, author=author)
    likes = Like.objects.filter(post=post).order_by("-published")

    serializer = LikeSerializer(likes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
