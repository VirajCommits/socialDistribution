from rest_framework import serializers
from .models import Author, Post, FollowRequest

class AuthorSerializer(serializers.ModelSerializer):
    following = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['type', 'id', 'uuid', 'host', 'displayName', 'github', 'profileImage', 'page', 'following', 'followers']
        read_only_fields = ['type', 'id', 'host', 'page', 'following', 'followers']

class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['type', 'title', 'id', 'uuid', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'categories', 'count', 'comments', 'published', 'visibility', 'unlisted']
        read_only_fields = ['type', 'id', 'uuid', 'source', 'origin', 'count', 'comments', 'published']

class FollowRequestSerializer(serializers.ModelSerializer):
    actor = AuthorSerializer()
    object = AuthorSerializer()

    class Meta:
        model = FollowRequest
        fields = ['type', 'summary', 'actor', 'object', 'uuid', 'created_at']
        read_only_fields = ['type', 'uuid', 'created_at']