"""signals.py
Module for Django signals in the messaging application.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from messaging.models import (
    Message,  # Assuming Message model is defined in messaging.models
    Notification,  # Assuming Notification model is defined in messaging.models
)


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """Signal to create a notification when a new message is saved."""

    if created:
        # Create a notification for the recipient
        notification = Notification.objects.create(
            recipient=instance.recipient,
            message=instance,
        )

        notification.save()
        # Print a message to indicate the signal was triggered
        print(
            f"Notification created: {notification.notification_id} for {notification.recipient}"
        )
