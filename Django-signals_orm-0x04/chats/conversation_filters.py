from django_filters import rest_framework as filters
from django_filters.filterset import FilterSet

from .models import Conversation


class ConversationFilter(FilterSet):
    """
    Custom filter class for conversations.
    Allows filtering conversations by:
    - participant (user who is part of the conversation)
    - creation date range
    - has_unread_messages (boolean)
    """

    # User filter
    participant = filters.UUIDFilter(field_name="participants__user_id")

    # Date range filters for when the conversation was created
    created_after = filters.DateTimeFilter(
        field_name="messages__created_at", lookup_expr="gte", distinct=True
    )
    created_before = filters.DateTimeFilter(
        field_name="messages__created_at", lookup_expr="lte", distinct=True
    )

    # Specific participant filter
    specific_participants = filters.CharFilter(method="filter_by_specific_participants")

    def filter_by_specific_participants(self, queryset, name, value):
        """
        Filter conversations that include specific participants.
        Value should be a comma-separated list of user IDs.
        """
        if not value:
            return queryset

        user_ids = [user_id.strip() for user_id in value.split(",")]

        for user_id in user_ids:
            queryset = queryset.filter(participants__user_id=user_id)

        return queryset.distinct()

    class Meta:
        model = Conversation
        fields = ["participant", "created_after", "created_before"]
