from rest_framework import serializers
from .models import Post, Author
from django.utils import timezone
from django.shortcuts import get_object_or_404


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'host', 'displayName', 'github', 'profileImage', 'page']

class PostSerializer(serializers.ModelSerializer):
    # Use AuthorSerializer for read operations
    author = AuthorSerializer(read_only=True)
    # Use author_id for write operations
    author_id = serializers.UUIDField(write_only=True)

    # Set auto-generated fields as read-only
    id = serializers.UUIDField(read_only=True)
    page = serializers.URLField(read_only=True)
    published = serializers.DateTimeField(read_only=True)
    type = serializers.CharField(default='post', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'type', 'title', 'page', 'description', 'contentType',
            'content', 'image', 'author', 'author_id', 'published', 'visibility'
        ]

    def create(self, validated_data):
        author_id = validated_data.pop('author_id')
        author = get_object_or_404(Author, id=author_id)
        post = Post.objects.create(author=author, **validated_data)
        return post