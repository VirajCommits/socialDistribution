from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Author
        fields = ['id', 'host', 'displayName', 'github', 'profileImage', 'page', 'username', 'email', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'page': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)
