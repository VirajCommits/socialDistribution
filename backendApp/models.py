from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from urllib.parse import urlparse
from cryptography.fernet import Fernet
from django.conf import settings

class Author(AbstractUser):
    type = models.CharField(max_length=6, default="author", editable=False)
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    id = models.URLField(primary_key=True, max_length=500)
    host = models.URLField(default="http://localhost:8000/")
    displayName = models.CharField(max_length=255)
    github = models.URLField(blank=True)
    is_approved = models.BooleanField(default=False)
    profileImage = models.URLField(blank=True, max_length=500)
    page = models.URLField(max_length=500)
    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='following', blank=True)

    def __str__(self):
        return self.displayName or self.username

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"{self.host}authors/{self.uuid}"
        if not self.page:
            self.page = f"{self.host.replace('project/', '')}authors/{self.username}"
        if not self.displayName:
            self.displayName = self.username
        super().save(*args, **kwargs)

    def accept_follow_request(self, requester):
        """Accept a follow request from another author."""
        self.followers.add(requester)
        self.save()

    def is_friend_with(self, other_author):
        """Check if this author and other_author are mutual followers (friends)"""
        return (self.followers.filter(id=other_author.id).exists() and 
                other_author.followers.filter(id=self.id).exists())

    @property
    def github_username(self):
        if self.github:
            # Parse the GitHub URL to get the path and extract the username
            path_parts = urlparse(self.github).path.strip("/").split("/")
            if path_parts:  # Ensure there is a username in the path
                return path_parts[-1]  # The username should be the last part of the URL
        return None


class Post(models.Model):
    VISIBILITY_CHOICES = [
        ("PUBLIC", "Public"),
        ("FRIENDS", "Friends"),
        ("UNLISTED", "Unlisted"),
        ("INVISIBLE", "Invisible"),
    ]

    CONTENT_TYPE_CHOICES = [
        ("text/plain", "Plain Text"),
        ("text/markdown", "Markdown"),
        ("image/png;base64", "PNG Image (Base64)"),
        ("image/jpeg;base64", "JPEG Image (Base64)"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    type = models.CharField(max_length=10, default="post")
    title = models.CharField(max_length=200)
    page = models.URLField()
    description = models.TextField(blank=True, null=True)
    contentType = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="posts")
    published = models.DateTimeField()
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES)
    edited_at = models.DateTimeField(auto_now=True)
    reposted_by = models.ManyToManyField(
        Author, related_name='reposted_posts', blank=True)
    repost_count = models.PositiveIntegerField(default=0)
    is_repost = models.BooleanField(default=False)
    original_post = models.ForeignKey(
        'self', null=True, blank=True, related_name='reposts', on_delete=models.CASCADE
    )
    # is_github_post = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            # Generate a unique post ID based on the author's host and a new UUID
            post_uuid = uuid.uuid4()
            self.id = f"{self.author.host}/authors/{self.author.id.split('/')[-1]}/posts/{post_uuid}"
            print("This is self.id", self.id)
        if not self.page:
            # Set the page URL to the post's ID or modify as needed
            self.page = self.id
        if not self.published:
            self.published = timezone.now()
        super(Post, self).save(*args, **kwargs)

    def repost(self, author):
        self.reposted_by.add(author)
        self.save()

    def get_post_url(self):
        return f"{self.author.host}service/api/posts/{self.id}/link/"


class FollowRequest(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, default='follow')
    summary = models.CharField(max_length=256, blank=True)
    actor = models.ForeignKey(
        Author, related_name='sent_follow_requests', on_delete=models.CASCADE)
    object = models.ForeignKey(
        Author, related_name='received_follow_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.actor.displayName} wants to follow {self.object.displayName}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField()
    contentType = models.CharField(
        max_length=50, choices=Post.CONTENT_TYPE_CHOICES)
    published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.author.displayName} on {self.post.title}"


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes")
    published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Like by {self.author.displayName} on {self.post.title}"


class AdminSettings(models.Model):
    user_approval_required = models.BooleanField(default=True)

    def __str__(self):
        return f"User Approval Required: {self.user_approval_required}"


class GitHubPost(models.Model):
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="github_posts"
    )
    activity_type = models.CharField(
        max_length=50
    )  # e.g., 'PushEvent', 'PullRequestEvent'
    activity_data = models.JSONField()  # Store event data in JSON format
    created_at = models.DateTimeField(auto_now_add=True)
    github_event_id = models.CharField(
        max_length=100, unique=True
    )  # Ensure we don't repost the same event

    def __str__(self):
        return f"{self.author.displayName}'s GitHub {self.activity_type}"


# class RemoteNode(models.Model):
#     url = models.URLField(unique=True)
#     username = models.CharField(max_length=255)
#     _password = models.TextField()  # Store encrypted password
#     connected = models.BooleanField(default=False)

#     def set_password(self, raw_password):
#         """Encrypt and save the password."""
#         cipher = Fernet(settings.FERNET_KEY)
#         self._password = cipher.encrypt(raw_password.encode()).decode()

#     def get_password(self):
#         """Decrypt and retrieve the password."""
#         cipher = Fernet(settings.FERNET_KEY)
#         return cipher.decrypt(self._password.encode()).decode()

#     def save(self, *args, **kwargs):
#         """Automatically encrypt the password if it's not encrypted before saving."""
#         if self._password and not self._password.startswith("gAAAA"):
#             self.set_password(self._password)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Remote Node at {self.url} (Connected: {self.connected})"
