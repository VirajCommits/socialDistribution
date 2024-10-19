from django.db import models
import uuid
from django.utils import timezone

class Author(models.Model):
    type = models.CharField(max_length=6,default="author",editable=False) 
    id = models.URLField(primary_key=True)
    host = models.URLField(db_index=True)
    displayName = models.CharField(max_length=255,db_index=True,unique=True)
    github = models.URLField(db_index=True,blank=True,null=True,unique=True)
    profileImage = models.URLField(blank=True,null=True)
    page = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.displayName


class Post(models.Model):
    VISIBILITY_CHOICES = [
        ("PUBLIC", "Public"),
        ("FRIENDS", "Friends"),
        ("PRIVATE", "Private"),
    ]

    CONTENT_TYPE_CHOICES = [
        ("text/plain", "Plain Text"),
        ("text/markdown", "Markdown"),
        ("image/png;base64", "PNG Image (Base64)"),
        ("image/jpeg;base64", "JPEG Image (Base64)"),
    ]

    id = models.URLField(primary_key=True)
    type = models.CharField(max_length=10, default="post")
    title = models.CharField(max_length=200)
    page = models.URLField()
    description = models.TextField(blank=True, null=True)
    contentType = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    content = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="posts")
    published = models.DateTimeField()
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            # Generate a unique post ID based on the author's host and a new UUID
            post_uuid = uuid.uuid4()
            self.id = f"{self.author.host}/authors/{self.author.id.split('/')[-1]}/posts/{post_uuid}"
        if not self.page:
            # Set the page URL to the post's ID or modify as needed
            self.page = self.id
        if not self.published:
            self.published = timezone.now()
        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    published = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.displayName} on {self.post.title}"


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.displayName} liked {self.post.title}"
