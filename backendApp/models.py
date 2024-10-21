from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

import uuid

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author' , null=True, blank=True)
    type = models.CharField(max_length=6,default="author",editable=False) 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.URLField()
    displayName = models.CharField(max_length=255)
    github = models.URLField()
    profileImage = models.URLField()
    page = models.URLField()

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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, default='post')
    title = models.CharField(max_length=200)
    page = models.URLField()
    description = models.TextField(blank=True, null=True) 
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)  # Field for image
    contentType = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    published = models.DateTimeField()
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES)

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
