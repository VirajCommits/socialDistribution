from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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


# @api_view(["GET", "DELETE", "PUT"])
# def post_detail(request, author_serial, post_serial):
#     print(
#         "GET POST DETAILS>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", author_serial, post_serial
#     )
#     segments = post_serial.split("/")
#     post_id = segments[0]  # This should be the UUID part
#     action = segments[1] if len(segments) > 1 else None

#     # Get the author object or return 404 if not found
#     author = get_object_or_404(Author, uuid=author_serial)

#     # Get the post object or return 404 if not found
#     post = get_object_or_404(Post, author=author, id=post_serial)

#     print("FOUND AUTHOR AND POST")

#     print(" --------- ", request.method)
#     if request.method == "GET":
#         # Serialize the post
#         post_serializer = PostSerializer(post)

#         # Fetch related comments and likes
#         comments = Comment.objects.filter(post=post).order_by("-published")
#         likes = Like.objects.filter(post=post)

#         comments_serializer = CommentSerializer(comments, many=True)
#         likes_serializer = LikeSerializer(likes, many=True)

#         # Combine post, comments, and likes into one response
#         response_data = {
#             "post": post_serializer.data,
#             "comments": comments_serializer.data,
#             "likes": likes_serializer.data,
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

#     elif request.method == "DELETE":
#         post.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


#     elif request.method == "PUT":
#         serializer = PostSerializer(post, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(["GET", "DELETE", "PUT", "POST"])
def post_detail(request, author_serial, post_serial):
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
    print(" ----------- >>>>", author_serial)
    author_serial = unquote(author_serial)
    author = get_object_or_404(Author, uuid=author_serial)
    posts = Post.objects.filter(author=author).order_by("-published")

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Adjust as needed
    result_page = paginator.paginate_queryset(posts, request)

    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response({"type": "posts", "items": serializer.data})


# UUID_REGEX = re.compile(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}")


# def extract_uuid_from_url(url):
#     parsed_url = urlparse(url)
#     path_parts = parsed_url.path.split("/")
#     # Find a UUID in the path
#     for part in path_parts:
#         if UUID_REGEX.match(part):
#             return part
#     return None


# @api_view(["POST"])
# def create_comment(request, author_id, post_id):
#     print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
#     # Parse the author_id URL and extract the UUID part
#     parsed_author_id = urlparse(author_id).path.split("/")[-1]
#     print("Parsed author_id:", parsed_author_id)
#     print("Received post_id:", post_id)

#     # Get the author instance or return 404 if not found
#     author = get_object_or_404(Author, uuid=parsed_author_id)

#     # Get the post instance or return 404 if not found
#     post = get_object_or_404(Post, id=post_id)

#     # Prepare the data for the serializer
#     data = request.data.copy()
#     data["author_id"] = str(author.id)
#     data["post_id"] = str(post.id)

#     serializer = CommentSerializer(data=data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["POST"])
# def like_post(request, author_id, post_id):
#     # Parse the author_id URL and extract the UUID part
#     parsed_author_id = urlparse(author_id).path.split("/")[-1]
#     print("Parsed author_id:", parsed_author_id)
#     print("Received post_id:", post_id)

#     # Get the author instance or return 404 if not found
#     author = get_object_or_404(Author, uuid=parsed_author_id)

#     # Get the post instance or return 404 if not found
#     post = get_object_or_404(Post, id=post_id)

#     # Prepare the data for the serializer
#     data = request.data.copy()
#     data["author_id"] = str(author.id)
#     data["post_id"] = str(post.id)
#     data["post"] = post.id  # Set the actual post ID

#     print("Data being passed to serializer:", data)

#     serializer = LikeSerializer(data=data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         print("Serializer errors:", serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["GET"])
# def get_comments(request, author_id, post_id):
#     # decoded_author_id = unquote(author_id)
#     # author_uuid = extract_uuid_from_url(decoded_author_id)
#     author_uuid = urlparse(author_id).path.split("/")[-1]

#     if not author_uuid:
#         return Response(
#             {"detail": "Invalid author ID"}, status=status.HTTP_400_BAD_REQUEST
#         )

#     author = get_object_or_404(Author, uuid=author_uuid)
#     post = get_object_or_404(Post, id=post_id, author=author)
#     comments = Comment.objects.filter(post=post).order_by("-published")

#     serializer = CommentSerializer(comments, many=True, context={'request': request})
#     return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(["GET"])
# def get_likes(request, author_id, post_id):
#     author_uuid = urlparse(author_id).path.split("/")[-1]

#     if not author_uuid:
#         return Response(
#             {"detail": "Invalid author ID"}, status=status.HTTP_400_BAD_REQUEST
#         )

#     author = get_object_or_404(Author, uuid=author_uuid)
#     post = get_object_or_404(Post, id=post_id, author=author)
#     likes = Like.objects.filter(post=post).order_by("-published")

#     serializer = LikeSerializer(likes, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


class SignupView(APIView):
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
