"""signals.py
Module for Django signals in the messaging application.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from messaging.models import (
    Message,
    Notification,
    MessageHistory,
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


# create a signal to log when message content is edited
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """Signal to log message edits."""

    if instance.pk:
        # Fetch the original message before it is saved
        old = Message.objects.get(pk=instance.pk)
        if old.content != instance.content:
            # Log the edit

            # update the instance edited field
            instance.edited = True

            # Create a history entry for the edited message
            _message_history = MessageHistory.objects.create(
                message=instance,
                edited_content=old.content,
                edited_by=instance.sender,
            )

            _message_history.save()

            print(
                f"Message history {_message_history.history_id} edited from '{_message_history.edited_content}' to '{instance.content}'"
            )
