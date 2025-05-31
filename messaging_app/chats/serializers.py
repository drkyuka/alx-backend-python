"""serializers.py
# Django serializers for the chats application.
# This file defines the serializers used to convert complex data types,
# such as Django models, into JSON or other content types that can be easily rendered into a response.
"""

from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        """Meta class for UserSerializer."""

        model = User
        fields = "__all__"


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for the Conversation model."""

    class Meta:
        """Meta class for ConversationSerializer."""

        model = Conversation
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model."""

    class Meta:
        """Meta class for MessageSerializer."""

        model = Message
        fields = "__all__"
