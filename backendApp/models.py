from django.db import models

class Author(models.Model):
    type = models.CharField(max_length=6,default="author",editable=False) 
    id = models.URLField(primary_key=True)
    host = models.URLField()
    displayName = models.CharField(max_length=255)
    github = models.URLField()
    profileImage = models.URLField()
    page = models.URLField()

    def __str__(self):
        return self.displayName