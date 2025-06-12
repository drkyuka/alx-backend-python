"""models.py
Django models for the chats application.
This file defines the data models used in the chats application,
including the structure of the database tables.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


# Extend user_id field to the User model
user_id_field = models.UUIDField(
    default=uuid.uuid4,
    editable=False,
    unique=True,
    help_text="Unique identifier for the user",
)

# Extend email field to the User model
email_field = models.EmailField(
    unique=True,
)

# create the User model using functional approach
User = type(
    "User",
    (AbstractUser,),
    {
        "user_id": user_id_field,
        "email": email_field,
        "USERNAME_FIELD": "email",
        "REQUIRED_FIELDS": [],
        "Meta": type(
            "Meta",
            (),
            {
                "db_table": "user",
                "verbose_name": "User",
                "verbose_name_plural": "Users",
            },
        ),
        "__module__": __name__,
        "__str__": lambda self: f"{self.user_id} - {self.email}",
    },
)


# dynamically create the Message model using functional approach

Conversation = type(
    "Conversation",
    (models.Model,),
    {
        "conversations": models.Manager(),
        "conversation_id": models.UUIDField(
            primary_key=True,
            default=uuid.uuid4,
            editable=False,
            unique=True,
            help_text="Unique identifier for the conversation",
        ),
        "participants": models.ManyToManyField(
            to=User,
            help_text="Users participating in the conversation",
        ),
        "Meta": type(
            "Meta",
            (object,),
            {
                "db_table": "conversation",
                "verbose_name": "Conversation",
                "verbose_name_plural": "Conversations",
            },
        ),
        "__module__": __name__,
        "__str__": lambda self: f"Conversation {self.conversation_id} with {self.participants.count()} participants",
    },
)


# creating the Message model using functional approach

Message = type(
    "Message",
    (models.Model,),
    {
        "messages": models.Manager(),
        "message_id": models.UUIDField(
            primary_key=True,
            default=uuid.uuid4,
            editable=False,
            unique=True,
            help_text="Unique identifier for the message",
        ),
        "message_body": models.TextField(
            help_text="Content of the message",
        ),
        "conversation": models.ForeignKey(
            Conversation,
            related_name="messages",
            on_delete=models.CASCADE,
            help_text="Conversation to which the message belongs",
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
        "sent_at": models.DateTimeField(
            auto_now_add=True,
            help_text="Timestamp when the message was sent",
        ),
        "created_at": models.DateTimeField(
            auto_now_add=True,
            help_text="Timestamp when the message was created",
        ),
        "Meta": type(
            "Meta",
            (object,),
            {
                "db_table": "message",
                "verbose_name": "Message",
                "verbose_name_plural": "Messages",
            },
        ),
        "__module__": __name__,
        "__str__": lambda self: f"Message {self.message_id} from {self.sender} to {self.receiver}",
    },
)
