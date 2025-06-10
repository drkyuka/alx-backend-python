from django_filters import rest_framework as filters
from django_filters.filterset import FilterSet

from .models import Conversation, Message, User


class MessageFilter(FilterSet):
    """
    Custom filter class for messages.
    Allows filtering messages by:
    - sender/receiver user
    - time range (sent_at)
    - message content
    - conversation participants
    """

    # Time range filters
    sent_after = filters.DateTimeFilter(field_name="sent_at", lookup_expr="gte")
    sent_before = filters.DateTimeFilter(field_name="sent_at", lookup_expr="lte")

    # User filters
    sender = filters.UUIDFilter(field_name="sender__user_id")
    receiver = filters.UUIDFilter(field_name="receiver__user_id")

    # Participant filter (user who is part of the conversation)
    participant = filters.CharFilter(method="filter_by_participant")

    # Content filter - works with both 'content' (from serializer) and 'message_body' (from DB)
    content = filters.CharFilter(field_name="message_body", lookup_expr="icontains")

    def filter_by_participant(self, queryset, name, value):
        """
        Filter messages by conversation participant.
        Returns messages from all conversations where the specified user is a participant.
        """
        try:
            # Find all conversations where the user is a participant
            conversations = Conversation.objects.filter(participants__user_id=value)

            # Return all messages in those conversations
            return queryset.filter(conversation__in=conversations).distinct()
        except (ValueError, User.DoesNotExist):
            return queryset.none()

    class Meta:
        model = Message
        fields = [
            "sender",
            "receiver",
            "participant",
            "sent_after",
            "sent_before",
            "content",
            "conversation",
        ]
