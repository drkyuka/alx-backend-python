"""managers.py
Custom manager for unread messages in a messaging application.
This file defines a custom manager for the Message model to filter unread messages.
"""

from django.db.models import Manager, QuerySet


class UnreadMessagesManager(Manager):
    """Custom manager for unread messages."""

    def get_queryset(self) -> QuerySet:
        """Return a queryset of unread messages."""

        return super().get_queryset().filter(read=False)
