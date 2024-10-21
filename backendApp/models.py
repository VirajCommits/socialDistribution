from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class Author(AbstractUser):
    type = models.CharField(max_length=6, default="author", editable=False)
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    id = models.URLField(primary_key=True, max_length=200)
    host = models.URLField(default="http://localhost:8000/project/")
    displayName = models.CharField(max_length=255)
    github = models.URLField(blank=True)
    profileImage = models.URLField(blank=True)
    page = models.URLField(max_length=200)

    def __str__(self):
        return self.displayName

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"{self.host}authors/{self.uuid}"
        if not self.page:
            self.page = f"{self.host.replace('project/', '')}authors/{self.username}"
        super().save(*args, **kwargs)
