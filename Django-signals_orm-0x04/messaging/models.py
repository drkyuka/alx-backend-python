"""models.py
This file defines the models for the messaging application with Message model.
"""

from uuid import uuid4

from chats.models import User  # Assuming User model is defined in chat.models
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .managers import UnreadMessagesManager

Message = type(
    "Message",
    (models.Model,),
    {
        "unread": UnreadMessagesManager(),
        "objects": models.Manager(),  # Default manager
        "message_id": models.UUIDField(
            primary_key=True,
            default=uuid4,
            editable=False,
            unique=True,
            help_text="Unique identifier for the message",
        ),
        "sender": models.ForeignKey(
            User,
            related_name="messaging_sent_messages",
            on_delete=models.CASCADE,
            help_text="User who sent the message",
        ),
        "recipient": models.ForeignKey(
            User,
            related_name="messaging_received_messages",
            on_delete=models.CASCADE,
            help_text="User who received the message",
        ),
        "content": models.TextField(
            help_text="Content of the message",
            editable=True,  # Allow editing of message content
        ),
        "timestamp": models.DateTimeField(
            auto_now_add=True,
            help_text="Timestamp when the message was sent",
        ),
        "edited": models.BooleanField(
            default=False,
            help_text="Indicates whether the message has been edited",
        ),
        "read": models.BooleanField(
            default=False,
            help_text="Indicates whether the message has been read",
        ),
        "parent_message": models.ForeignKey(
            "self",
            related_name="replies",
            on_delete=models.CASCADE,
            null=True,
            blank=True,
            help_text="Parent message for threaded conversations",
        ),
        "Meta": type(
            "Meta",
            (),
            {
                "db_table": "messaging_message",
                "verbose_name": "Message",
                "verbose_name_plural": "Messages",
            },
        ),
        "__module__": __name__,
        "__str__": lambda self: f"Message {self.message_id} from {self.sender} to {self.recipient}",
    },
)


class Notification(models.Model):
    """Notification model to represent notifications for messages."""

    notification_id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for the notification",
    )
    message = models.ForeignKey(
        Message,
        related_name="notifications",
        on_delete=models.CASCADE,
        help_text="Message associated with the notification",
    )
    recipient = models.ForeignKey(
        User,
        related_name="messaging_notifications",
        on_delete=models.CASCADE,
        help_text="User who will receive the notification",
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Indicates whether the notification has been read",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the notification was created",
    )

    class Meta:
        """Meta options for the Notification model."""

        db_table = "messaging_notification"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification {self.notification_id} for {self.recipient}"


MessageHistory = type(
    "MessageHistory",
    (models.Model,),
    {
        "history_id": models.UUIDField(
            primary_key=True,
            default=uuid4,
            editable=False,
            unique=True,
            help_text="Unique identifier for the message history entry",
        ),
        "message": models.ForeignKey(
            Message,
            related_name="history",
            on_delete=models.CASCADE,
            help_text="Message that was edited",
        ),
        "edited_content": models.TextField(
            help_text="Content of the message after editing",
        ),
        "edited_at": models.DateTimeField(
            auto_now_add=True,
            help_text="Timestamp when the message was edited",
        ),
        "edited_by": models.ForeignKey(
            User,
            related_name="messaging_edited_messages",
            on_delete=models.CASCADE,
            help_text="User who edited the message",
        ),
        "Meta": type(
            "Meta",
            (),
            {
                "db_table": "messaging_message_history",
                "verbose_name": "Message History",
                "verbose_name_plural": "Message Histories",
            },
        ),
        "__module__": __name__,
        "__str__": lambda self: f"History for {self.message.message_id} edited at {self.edited_at}",
    },
)


@receiver(post_save, sender=Message)
def new_message_created(sender, instance, created, **kwargs):
    """Signal handler to notify users when a message is sent."""
    _ = kwargs  # Mark kwargs as used to avoid unused argument warning
    if created:
        # Logic to notify users about the new message
        print(
            f"New message sent: {instance.content} from {instance.sender} to {instance.recipient}"
        )
