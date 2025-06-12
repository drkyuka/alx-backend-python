"""models.py
This file defines the models for the messaging application with Message model.
"""

from uuid import uuid4

from chats.models import User  # Assuming User model is defined in chat.models
from django.db import models

Message = type(
    "Message",
    (models.Model,),
    {
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
        ),
        "timestamp": models.DateTimeField(
            auto_now_add=True,
            help_text="Timestamp when the message was sent",
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

# Assuming Notification model is defined in the same module

Notification = type(
    "Notification",
    (models.Model,),
    {
        "notification_id": models.UUIDField(
            primary_key=True,
            default=uuid4,
            editable=False,
            unique=True,
            help_text="Unique identifier for the notification",
        ),
        "message": models.ForeignKey(
            Message,
            related_name="notifications",
            on_delete=models.CASCADE,
            help_text="Message associated with the notification",
        ),
        "recipient": models.ForeignKey(
            User,
            related_name="messaging_notifications",
            on_delete=models.CASCADE,
            help_text="User who will receive the notification",
        ),
        "is_read": models.BooleanField(
            default=False,
            help_text="Indicates whether the notification has been read",
        ),
        "timestamp": models.DateTimeField(
            auto_now_add=True,
            help_text="Timestamp when the notification was created",
        ),
        "Meta": type(
            "Meta",
            (),
            {
                "db_table": "messaging_notification",
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
            },
        ),
        "__module__": __name__,
        "__str__": lambda self: f"Notification {self.notification_id} for {self.recipient}",
    },
)
