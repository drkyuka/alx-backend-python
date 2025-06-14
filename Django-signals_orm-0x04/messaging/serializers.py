"""serializers.py
This file defines serializers for the messaging application.
"""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import Message


class MessageSerializer(ModelSerializer):
    """Serializer for the Message model."""

    parent_message = SerializerMethodField(method_name="get_replies")

    def get_replies(self, instance):
        """Get replies for a message instance."""

        parent_message = (
            Message.objects.filter(parent_message=instance)
            .select_related("sender")
            .prefetch_related("parent_message")
            .order_by("-timestamp")
        )

        return MessageSerializer(parent_message, many=True, context=self.context).data

    class Meta:
        """Meta class for MessageSerializer."""

        model = Message
        fields = "__all__"
