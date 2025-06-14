"""urls.py
URL configuration for the messaging application.
This file defines URL patterns for messaging-related views.
"""

from django.urls import path

from . import views

app_name = "messaging"

urlpatterns = [
    path("delete-user/", views.delete_user, name="delete_user"),
    path(
        "unread-messages/",
        views.list_unread_messages,
        name="list_unread_messages",
    ),
    path("messages/", views.get_all_user_messages, name="get_all_user_messages"),
]
