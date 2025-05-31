"""serializers.py
# Django serializers for the chats application.
# This file defines the serializers used to convert complex data types,
# such as Django models, into JSON or other content types that can be easily rendered into a response.
"""

from os import error
from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        """Meta class for UserSerializer."""

        model = User
        fields = "__all__"
        read_only_fields = ("user_id",)


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for the Conversation model."""

    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField(method_name="get_messages")

    def get_messages(self, obj):
        """Get messages for the conversation."""
        return MessageSerializer(obj.messages.all(), many=True).data

    class Meta:
        """Meta class for ConversationSerializer."""

        model = Conversation
        fields = "__all__"
        read_only_fields = ("conversation_id",)


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model."""

    class Meta:
        """Meta class for MessageSerializer."""

        model = Message
        fields = "__all__"
        read_only_fields = ("message_id",)
        extra_kwargs = {
            "sender": {"required": True},
            "receiver": {"required": True},
        }

    content = serializers.CharField(
        source="message_body",
        help_text="Content of the message",
        max_length=500,
        error_messages={
            "max_length": "Message content cannot exceed 500 characters.",
            "required": "Message content is required.",
        },
    )

    # validate messages without valid users
    def validate(self, attrs):
        """Validate that the sender and receiver are valid users."""

        if attrs["sender"] == attrs["receiver"]:
            raise serializers.ValidationError(
                "Sender and receiver cannot be the same user."
            )

        if not User.objects.filter(user_id=attrs["sender"].user_id).exists():
            raise serializers.ValidationError("Sender does not exist.")

        if not User.objects.filter(user_id=attrs["receiver"].user_id).exists():
            raise serializers.ValidationError("Receiver does not exist.")
