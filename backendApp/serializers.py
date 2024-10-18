from rest_framework import serializers
from .models import Post, Author
from django.utils import timezone

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'host', 'displayName', 'github', 'profileImage', 'page']

class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Post
        exclude = ['image']  # Exclude image as we'll handle it separately

    def create(self, validated_data):
        author_data = validated_data.pop('author')
        author, created = Author.objects.get_or_create(id=author_data['id'], defaults=author_data)

        # Generate a new unique ID for the post
        import uuid
        post_uuid = uuid.uuid4()
        post_id = f"{author_data['id']}/posts/{post_uuid}"

        # Handle base64 image decoding if contentType is an image
        content_type = validated_data.get('contentType', '')
        content = validated_data.get('content', '')

        post = Post(
            id=post_id,
            type='post',
            page=post_id.replace('/api/', '/'),
            author=author,
            published=validated_data.get('published', timezone.now()),
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            contentType=content_type,
            visibility=validated_data['visibility'],
        )

        # if 'image' in content_type:
        #     import base64
        #     from django.core.files.base import ContentFile

        #     try:
        #         format, imgstr = content.split(';base64,')
        #     except ValueError:
        #         imgstr = content  # If content doesn't have 'data:image/...;base64,' prefix
        #         ext = content_type.split('/')[-1].split(';')[0]
        #     else:
        #         ext = format.split('/')[-1]
        #     img_data = ContentFile(base64.b64decode(imgstr), name=f"{post_uuid}.{ext}")
        #     post.image = img_data
        #     post.content = ''
        # else:
        post.content = content

        post.save()
        return post