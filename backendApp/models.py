from django.db import models

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