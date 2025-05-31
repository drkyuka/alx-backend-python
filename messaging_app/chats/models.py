"""models.py
Django models for the chats application.
This file defines the data models used in the chats application,
including the structure of the database tables.
"""

import uuid
from django.db import models


# Create your models here.
class User(models.Model):
    """
    Model representing a user in the messaging application.
    """

    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4(),
        editable=False,
        unique=True,
        help_text="Unique identifier for the user",
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        help_text="Email address of the user",
    )

    password = models.CharField(
        max_length=128,
        help_text="Password for the user account",
    )

    first_name = models.CharField(
        max_length=30,
        blank=False,
        help_text="First name of the user",
    )

    last_name = models.CharField(
        max_length=30,
        blank=False,
        help_text="Last name of the user",
    )

    phone_number = models.CharField(
        max_length=15,
        help_text="Phone number of the user",
    )


class Conversation(models.Model):
    """
    Model representing a conversation between users.
    """

    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4(),
        editable=False,
        unique=True,
        help_text="Unique identifier for the conversation",
    )

    participants = models.ManyToManyField(  # type: ignore
        to=User,
        related_name="conversations",
        help_text="Users participating in the conversation",
    )


class Message(models.Model):
    """
    Model representing a message in a conversation.
    """

    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4(),
        editable=False,
        unique=True,
        help_text="Unique identifier for the message",
    )

    message_body = models.ForeignKey(
        to=Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="Conversation to which the message belongs",
    )

    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the message was sent",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the message was created",
    )
