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
        read_only_fields = ("user_id",)


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model."""

    message_count = serializers.SerializerMethodField(method_name="get_message_count")

    content = serializers.CharField(
        source="message_body",
        help_text="Content of the message",
        max_length=500,
        error_messages={
            "max_length": "Message content cannot exceed 500 characters.",
            "required": "Message content is required.",
        },
    )

    class Meta:
        """Meta class for MessageSerializer."""

        model = Message
        fields = "__all__"
        read_only_fields = ("message_id",)
        extra_kwargs = {
            "sender": {"required": True},
            "receiver": {"required": True},
        }

    def get_message_count(self, obj) -> int:
        """Get the count of messages in the conversation."""
        return obj.conversation.messages.count()

    def validate(self, attrs):
        sender = attrs.get("sender")
        receiver = attrs.get("receiver")

        if not sender or not receiver:
            raise serializers.ValidationError(
                "Both sender and receiver must be specified."
            )

        if sender == receiver:
            raise serializers.ValidationError(
                "Sender and receiver cannot be the same user."
            )

        # Check if sender and receiver exist
        if not User.objects.filter(user_id=getattr(sender, "user_id", sender)).exists():
            raise serializers.ValidationError("Sender user does not exist.")

        if not User.objects.filter(
            user_id=getattr(receiver, "user_id", receiver)
        ).exists():
            raise serializers.ValidationError("Receiver user does not exist.")

        return attrs


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for the Conversation model."""

    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)  # Nested messages

    class Meta:
        """Meta class for ConversationSerializer."""

        model = Conversation
        fields = "__all__"
        read_only_fields = ("conversation_id",)
