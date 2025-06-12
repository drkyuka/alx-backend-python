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
def notify_users(sender, instance, created, **kwargs):
    """Signal handler to notify users when a message is sent."""
    _ = kwargs  # Mark kwargs as used to avoid unused argument warning
    if created:
        # Logic to notify users about the new message
        print(
            f"New message sent: {instance.content} from {instance.sender} to {instance.recipient}"
        )

        # Here you can implement actual notification logic, e.g., sending an email or a push notification
        notification = Notification.objects.create(
            message=instance,
            recipient=instance.recipient,
        )

        notification.save()
        print(
            f"Notification created: {notification.notification_id} for {instance.recipient}"
        )
