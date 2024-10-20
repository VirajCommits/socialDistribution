from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class Author(models.Model):
    # Link to Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Primary key using UUID
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Full ID constructed from host and UUID
    id = models.URLField(unique=True, blank=True)

    type = models.CharField(max_length=10, default='author')
    host = models.URLField(max_length=200, default=settings.HOST_URL)
    displayName = models.CharField(max_length=100)
    github = models.URLField(blank=True, null=True)
    profileImage = models.URLField(blank=True, null=True, default='https://via.placeholder.com/150')
    page = models.URLField(blank=True, null=True)  # HTML profile page URL
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            # Construct the full ID URL
            self.id = f"{self.host}api/authors/{self.uuid}"
        if not self.page:
            # Construct the profile page URL
            self.page = f"{self.host}authors/{self.uuid}"
        if not self.displayName:
            self.displayName = self.user.username
        super(Author, self).save(*args, **kwargs)

    def __str__(self):
        return self.displayName
    
class Post(models.Model):
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('FRIENDS', 'Friends'),
        ('PRIVATE', 'Private'),
        ('INVISIBLE', 'Invisible'),
    ]

    CONTENT_TYPE_CHOICES = [
        ('text/plain', 'Plain Text'),
        ('text/markdown', 'Markdown'),
        ('image/png;base64', 'PNG Image (Base64)'),
        ('image/jpeg;base64', 'JPEG Image (Base64)'),
    ]

    id = models.URLField(primary_key=True)
    type = models.CharField(max_length=10, default='post')
    title = models.CharField(max_length=200)
    page = models.URLField()
    description = models.TextField(blank=True, null=True)
    contentType = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    published = models.DateTimeField()
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES)
    unlisted = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if not self.id:
            # Generate a unique post ID based on the author's host and a new UUID
            post_uuid = uuid.uuid4()
            self.id = f"{self.author.host}/authors/{self.author.id.split('/')[-1]}/posts/{post_uuid}"
            print("This is self.id" , self.id)
        if not self.page:
            # Set the page URL to the post's ID or modify as needed
            self.page = self.id
        if not self.published:
            self.published = timezone.now()
        super(Post, self).save(*args, **kwargs)
