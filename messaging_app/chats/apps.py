"""apps.py
Django application configuration for the chats app.
This file defines the configuration for the chats application within the messaging app.
It sets the default auto field type and the name of the application.
"""

from django.apps import AppConfig


class ChatsConfig(AppConfig):
    """Configuration for the chats application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "chats"
