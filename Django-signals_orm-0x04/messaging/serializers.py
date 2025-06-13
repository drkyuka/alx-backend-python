"""serializers.py
This file defines serializers for the messaging application.
"""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import Message


class MessageSerializer(ModelSerializer):
    """Serializer for the Message model with nested replies."""

    replies = SerializerMethodField(method_name="get_replies")

    class Meta:
        """Meta class for MessageSerializer."""

        model = Message
        fields = "__all__"

    def get_replies(self, instance):
        """Retrieve nested replies for a message instance.
        This method fetches all replies to the message, including nested replies,
        and serializes them using the same serializer to maintain consistency."""

        replies = (
            instance.replies.select_related("sender", "recipient")
            .prefetch_related("replies__sender", "replies__recipient")
            .order_by("-timestamp")
        )
        return MessageSerializer(replies, many=True, context=self.context).data
