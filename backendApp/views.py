from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse,HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Post, Author, Comment,Like
import json
from django.utils import timezone


def index(request):
    return HttpResponse("Hello, world. This is the index page.")


def vueTest(request):
    # Render the 'index.html' file from your templates directory or return a simple response for testing
    return HttpResponse(
        "This is the vueTest view. If you're integrating Vue, replace this with a template rendering function."
    )


@csrf_exempt
def add_comment(request, author_id, post_id):
    print("sanket")
    author_full_url = f"http://127.0.0.1:8000/authors/{author_id}"
    full_post_id = f"http://127.0.0.1:8000/authors/{author_id}/posts/{post_id}"
    print("sanky")
    if request.method == "POST":
        print("x")
        try:
            data = json.loads(request.body)
            comment_author_id = data.get("author_id")
            content = data.get("content")

            # Get the post, ensuring it belongs to the specified author
            post = get_object_or_404(
                Post, id=full_post_id, author__id=author_full_url, is_deleted=False
            )

            # Get the author who is making the comment
            comment_author = get_object_or_404(Author, id=comment_author_id)

            # Create the comment
            comment = Comment.objects.create(
                post=post, author=comment_author, content=content
            )

            comment_data = {
                "type": "comment",
                "id": f"{comment_author.host}/api/authors/{comment_author.id.split('/')[-1]}/commented/{comment.id}",
                "author": {
                    "type": "author",
                    "id": comment_author.id,
                    "displayName": comment_author.displayName,
                    "github": comment_author.github,
                    "profileImage": comment_author.profileImage,
                },
                "content": comment.content,
                "published": comment.published.isoformat(),
                "post": post.id,
            }
            return JsonResponse(comment_data, status=201)
        except (KeyError, ValueError):
            return HttpResponseBadRequest("Invalid data format.")
    return HttpResponseBadRequest("Invalid request method.")


def get_comments_by_post(request, post_id):
    print(f"Looking for Post with ID: {post_id}")

    try:
        # Try finding the post using the post_id format
        post = Post.objects.filter(id__endswith=post_id).first()

        if not post:
            print("No Post matches the given ID.")
            return JsonResponse(
                {"error": "No Post matches the given query."}, status=404
            )

        print(f"Found Post: {post}")

        # Retrieve all comments for the post
        comments = post.comments.all()
        comments_data = [
            {
                "type": "comment",
                "id": f"{comment.author.host}/api/authors/{comment.author.id.split('/')[-1]}/commented/{comment.id}",
                "author": {
                    "type": "author",
                    "id": comment.author.id,
                    "page": comment.author.page,
                    "host": comment.author.host,
                    "displayName": comment.author.displayName,
                    "github": comment.author.github,
                    "profileImage": comment.author.profileImage,
                },
                "comment": comment.content,
                "contentType": "text/plain",
                "published": comment.published.isoformat(),
                "post": post.id,
                "page": f"{post.page}",
            }
            for comment in comments
        ]
        return JsonResponse({"type": "comments", "items": comments_data}, safe=False)
    except Exception as e:
        print(f"Error in get_comments_by_post: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def like_post(request, author_id, post_id):
    if request.method == "POST":
        try:
            # Construct the full URLs for the author and post
            author_full_url = f"http://127.0.0.1:8000/authors/{author_id}"
            full_post_id = f"http://127.0.0.1:8000/authors/{author_id}/posts/{post_id}"

            # Get the author and post objects
            author = get_object_or_404(Author, id=author_full_url)
            post = get_object_or_404(Post, id=full_post_id, is_deleted=False)

            # Check if the like already exists
            if Like.objects.filter(author=author, post=post).exists():
                return JsonResponse(
                    {"message": "Post already liked by this author."}, status=400
                )

            # Create the like
            like = Like.objects.create(author=author, post=post)

            like_data = {
                "type": "like",
                "id": str(like.id),
                "author": {
                    "type": "author",
                    "id": author.id,
                    "displayName": author.displayName,
                    "github": author.github,
                    "profileImage": author.profileImage,
                },
                "post": post.id,
                "created_at": like.created_at.isoformat(),
            }

            return JsonResponse(like_data, status=201)
        except (KeyError, ValueError):
            return HttpResponseBadRequest("Invalid data format.")
    return HttpResponseBadRequest("Invalid request method.")


def get_likes_for_public_post(request, post_id):
    try:
        # Retrieve the post based on the full post ID
        post = get_object_or_404(Post, id__endswith=post_id, visibility="PUBLIC")

        # Get all the likes for this post
        likes = post.likes.all()
        likes_data = [
            {
                "type": "Like",
                "author": {
                    "id": like.author.id,
                    "displayName": like.author.displayName,
                    "profileImage": like.author.profileImage,
                },
                "timestamp": like.created_at.isoformat(),
            }
            for like in likes
        ]
        return JsonResponse({"type": "likes", "items": likes_data}, safe=False)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found or is not public."}, status=404)
    except Exception as e:
        print(f"Error retrieving likes: {e}")
        return JsonResponse({"error": str(e)}, status=500)
