"""apps.py
Django application configuration for the messaging app.
This file defines the configuration for the chats application within the messaging app.
It sets the default auto field type and the name of the application.
"""

from django.apps import AppConfig


class MessagingConfig(AppConfig):
    """Configuration for the chats application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "messaging"

    def ready(self):
        """Ready method to perform any startup tasks."""
        # Import signals to ensure they are registered
        import messaging.signals
