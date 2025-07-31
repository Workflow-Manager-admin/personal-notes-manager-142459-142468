from django.contrib.auth.models import User
from rest_framework import serializers
from django.db import models

# PUBLIC_INTERFACE
class Note(models.Model):
    """
    Model for a personal note.

    Fields:
        title (str): The title of the note (max 200 chars).
        content (str): The content/body of the note.
        owner (User): ForeignKey to User - only owner can access/modify.
        created_at (datetime): When the note was created.
        updated_at (datetime): When the note was last modified.
    """

    title = models.CharField(max_length=200)
    content = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django's built-in User model."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# PUBLIC_INTERFACE
class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data.get('email', ''),
            password = validated_data['password'],
        )
        return user
