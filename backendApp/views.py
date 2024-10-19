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
