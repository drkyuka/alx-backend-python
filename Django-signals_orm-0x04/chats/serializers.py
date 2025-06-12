"""serializers.py
# Django serializers for the chats application.
# This file defines the serializers used to convert complex data types,
# such as Django models, into JSON or other content types that can be easily rendered into a response.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Conversation, Message, User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        """Meta class for UserSerializer."""

        model = User
        fields = "__all__"
        read_only_fields = ("user_id",)
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        """Create user with encrypted password."""
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update user with encrypted password."""
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model."""

    content = serializers.CharField(
        source="message_body",
        help_text="Content of the message",
        max_length=500,
        error_messages={
            "max_length": "Message content cannot exceed 500 characters.",
            "required": "Message content is required.",
            "blank": "Message content cannot be blank.",
        },
        required=True,
        allow_blank=False,
    )

    message_count = serializers.SerializerMethodField(method_name="get_message_count")

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
        return Message.messages.filter(conversation=obj.conversation).count()

    def validate(self, attrs):
        """Validate the message content and check sender/receiver."""

        # Check if message_body exists and is not blank
        message_body = attrs.get("message_body")
        if not message_body or not message_body.strip():
            raise serializers.ValidationError(
                {"content": "Message content cannot be blank."}
            )

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

    messages = MessageSerializer(
        many=True,
        read_only=True,
        help_text="Messages in the conversation",
    )

    participants = UserSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField(
        method_name="get_participant_count",
        help_text="Count of participants in the conversation",
    )

    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="List of participant user IDs for creating a conversation",
    )

    class Meta:
        """Meta class for ConversationSerializer."""

        model = Conversation
        fields = "__all__"
        read_only_fields = ("conversation_id",)

    def get_participant_count(self, obj) -> int:
        """Get the count of participants in the conversation."""
        return obj.participants.count()

    def create(self, validated_data):
        """Create a new conversation with participants."""
        participant_ids = validated_data.pop("participant_ids", [])
        conversation = Conversation.conversations.create(**validated_data)

        # Add participants to the conversation
        if participant_ids:
            for user_id in participant_ids:
                try:
                    user = User.objects.get(user_id=user_id)
                    conversation.participants.add(user)
                except User.DoesNotExist:
                    pass

        return conversation


class CustomTokenSerializer(TokenObtainPairSerializer):
    """Serializer for custom token generation."""

    username_field = "email"

    def validate(self, attrs):
        """Validate that the user exists."""
        # Call parent validate method which handles authentication
        # The parent class will use our username_field setting
        return super().validate(attrs)
