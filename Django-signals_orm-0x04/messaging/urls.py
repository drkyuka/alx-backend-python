"""urls.py
URL configuration for the messaging application.
This file defines URL patterns for messaging-related views.
"""

from django.urls import path

from . import views

app_name = "messaging"

urlpatterns = [
    path("api/messaging/delete-user/", views.delete_user, name="delete_user"),
    path(
        "api/messaging/unread-messages/",
        views.list_unread_messages,
        name="list_unread_messages",
    ),
]
