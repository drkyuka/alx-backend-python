"""signals.py
Module for Django signals in the messaging application.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from messaging.models import (
    Message,  # Assuming Message model is defined in messaging.models
    Notification,  # Assuming Notification model is defined in messaging.models
)
