from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import Post, Author, FollowRequest, Comment, Like
from django.utils import timezone
from django.shortcuts import get_object_or_404


class AuthorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Author
        fields = ['id', 'uuid', 'host', 'displayName', 'github', 'profileImage', 'page', 'username', 'email', 'password']

        extra_kwargs = {
            "id": {"read_only": True},
            "page": {"read_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)


class PostSerializer(serializers.ModelSerializer):
    # Use AuthorSerializer for read operations
    author = AuthorSerializer(read_only=True)
    # Use author_id for write operations
    author_id = serializers.UUIDField(write_only=True)

    # Set auto-generated fields as read-only
    id = serializers.UUIDField(read_only=True)
    page = serializers.URLField(read_only=True)
    published = serializers.DateTimeField(read_only=True)
    type = serializers.CharField(default="post", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "type",
            "title",
            "page",
            "description",
            "contentType",
            "content",
            "image",
            "author",
            "author_id",
            "published",
            "visibility",
            "repost_count",
        ]

    def create(self, validated_data):
        author_id = validated_data.pop("author_id")
        author = get_object_or_404(Author, uuid=author_id)
        post = Post.objects.create(author=author, **validated_data)
        return post

    def get_post_url(self, obj):
        return obj.get_post_url()


class FollowRequestSerializer(serializers.ModelSerializer):
    actor = AuthorSerializer(read_only=True)
    object = AuthorSerializer(read_only=True)

    class Meta:
        model = FollowRequest
        fields = ['type', 'summary', 'actor', 'object', 'uuid', 'created_at', 'accepted']
        read_only_fields = ['uuid', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    # Use AuthorSerializer for nested author details
    author = AuthorSerializer(read_only=True)
    # Use CharField for author_id and post_id as they are 32-character strings
    author_id = serializers.CharField(write_only=True)
    post_id = serializers.CharField(write_only=True)

    id = serializers.CharField(read_only=True)
    published = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "author_id",
            "post_id",
            "content",
            "contentType",
            "published",
        ]
        read_only_fields = ["id", "published"]

    def create(self, validated_data):
        author_id = validated_data.pop("author_id")
        post_id = validated_data.pop("post_id")
        author = get_object_or_404(Author, id=author_id)
        post = get_object_or_404(Post, id=post_id)
        comment = Comment.objects.create(author=author, post=post, **validated_data)
        return comment


class LikeSerializer(serializers.ModelSerializer):
    # Use AuthorSerializer for nested author details
    author = AuthorSerializer(read_only=True)
    # Use CharField for author_id and post_id as they are 32-character strings
    author_id = serializers.CharField(write_only=True)
    post_id = serializers.CharField(write_only=True)

    id = serializers.CharField(read_only=True)
    published = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "author", "author_id", "post", "post_id", "published"]
        read_only_fields = ["id", "published"]

    def create(self, validated_data):
        author_id = validated_data.pop("author_id")
        post_id = validated_data.pop("post_id")
        author = get_object_or_404(Author, id=author_id)
        post = get_object_or_404(Post, id=post_id)

        # Remove 'post' from validated_data to prevent conflict
        validated_data.pop("post", None)

        # Create the Like instance with author and post
        like = Like.objects.create(author=author, post=post, **validated_data)
        return like


# class RemoteNodeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RemoteNode
#         fields = ["url", "username", "connected"]
