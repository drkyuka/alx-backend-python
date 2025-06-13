"""signals.py
Module for Django signals in the messaging application.
"""

from django.db.models.signals import (
    post_save,
    pre_save,
    post_delete,
)
from django.db.models import Q
from django.dispatch import receiver
from messaging.models import (
    Message,
    Notification,
    MessageHistory,
)
from chats.models import User


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

    _ = kwargs  # Unused variable to avoid linting errors

    instance.full_clean()  # Ensure the instance is valid before saving

    if instance.pk:
        try:
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
        except Message.DoesNotExist:
            # If the message does not exist, it is a new message
            print(
                f"Creating new message: {instance.message_id} with content '{instance.content}'"
            )
            pass


# Signal to delete a user and their related data
@receiver(post_delete, sender=User)
def delete_user(sender, instance, **kwargs) -> None:
    """Signal to delete a user and their related data."""
    _ = kwargs  # Unused variable to avoid linting errors

    # Delete the user
    # instance.delete()
    Message.objects.filter(Q(sender=instance) | Q(recipient=instance)).delete()
    Notification.objects.filter(recipient=instance).delete()
    print(f"User {instance.username} deleted.")
