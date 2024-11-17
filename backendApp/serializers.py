from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import Post, Author, FollowRequest

from .models import Post, Author,Comment,Like, Inbox
from django.utils import timezone
from django.shortcuts import get_object_or_404


class AuthorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    # is_approved = serializers.BooleanField(read_only=True)

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
    type = serializers.CharField(default="follow")
    summary = serializers.CharField()
    actor = AuthorSerializer(read_only=True)
    object = AuthorSerializer(read_only=True)

    class Meta:
        model = FollowRequest
        fields = ['type', 'summary', 'actor', 'object']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure actor and object have the full structure
        for field in ['actor', 'object']:
            if field in data:
                author_data = data[field]
                author_data['type'] = 'author'
                # Ensure all required fields are present
                if 'page' not in author_data:
                    author_data['page'] = f"{author_data['host']}authors/{author_data['uuid']}"
                if 'profileImage' not in author_data:
                    author_data['profileImage'] = ""
        return data


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


class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields = ['author', 'posts', 'likes', 'comments', 'follow_requests']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['type'] = 'inbox'
        representation['items'] = []

        for post in instance.posts.all():
            post_data = PostSerializer(post).data
            post_data['type'] = 'post'
            representation['items'].append(post_data)

        for like in instance.likes.all():
            like_data = LikeSerializer(like).data
            like_data['type'] = 'Like'
            representation['items'].append(like_data)

        for comment in instance.comments.all():
            comment_data = CommentSerializer(comment).data
            comment_data['type'] = 'comment'
            representation['items'].append(comment_data)

        for follow in instance.follow_requests.all():
            follow_data = FollowRequestSerializer(follow).data
            follow_data['type'] = 'follow'
            representation['items'].append(follow_data)

        return representation