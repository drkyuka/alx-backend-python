"""models.py
This file defines the models for the messaging application with Message model.
"""

from django.db import models
from chats.models import User  # Assuming User model is defined in chat.models


Message = type(
    "Message",
    (models.Model,),
    {
        "messages": models.Manager(),
        "message_id": models.UUIDField(
            primary_key=True,
            default=models.UUIDField.default,
            editable=False,
            unique=True,
            help_text="Unique identifier for the message",
        ),
        "content": models.TextField(
            help_text="Content of the message",
        ),
        "timestamp": models.DateTimeField(
            auto_now_add=True,
            help_text="Timestamp when the message was created",
        ),
        "sender": models.ForeignKey(
            User,
            related_name="sent_messages",
            on_delete=models.CASCADE,
            help_text="User who sent the message",
        ),
        "receiver": models.ForeignKey(
            User,
            related_name="received_messages",
            on_delete=models.CASCADE,
            help_text="User who received the message",
        ),
        "Meta": type(
            "Meta",
            (),
            {
                "db_table": "message",
                "verbose_name": "Message",
                "verbose_name_plural": "Messages",
            },
        ),
        "__module__": __name__,
        "__str__": lambda self: f"Message {self.message_id} at {self.timestamp}",
    },
)
