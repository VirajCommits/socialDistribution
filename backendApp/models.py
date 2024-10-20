from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import uuid

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
