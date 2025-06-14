"""views.py
# Module for handling user-related views in the messaging application.
"""

from chats.models import User
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)


from messaging.models import Message

from .serializers import MessageSerializer


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user(request: Request) -> Response:
    """
    View to delete a user by ID.
    """

    try:
        user: User = request.user
        username = user.username
        user.delete()
        return Response(
            {"message": f"User {username} deleted successfully."},
            status=HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"error": f"Error deleting user: {str(e)}"},
            status=HTTP_404_NOT_FOUND,
        )


@cache_page(60)  # Cache the response for 60 seconds
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_unread_messages(request: Request) -> Response:
    """
    View to list unread messages for the authenticated user.
    """

    if not request:
        return Response(
            {"error": "Request object is missing."},
            status=HTTP_400_BAD_REQUEST,
        )

    user: User = request.user

    if not user.is_authenticated:
        return Response(
            {"error": "User is not authenticated."},
            status=HTTP_401_UNAUTHORIZED,
        )

    # Fetch unread messages for the user
    unread_messages = Message.unread.filter(recipient=user).only(
        "message_id", "sender", "recipient", "content", "timestamp"
    )

    serializer = MessageSerializer(unread_messages, many=True)
    return Response(serializer.data, status=HTTP_200_OK)


@cache_page(60)  # Cache the response for 60 seconds
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_user_messages(request: Request) -> Response:
    """
    View to get all messages for the authenticated user.
    """

    if not request:
        return Response(
            {"error": "Request object is missing."},
            status=HTTP_400_BAD_REQUEST,
        )

    user: User = request.user

    if not user.is_authenticated:
        return Response(
            {"error": "User is not authenticated."},
            status=HTTP_401_UNAUTHORIZED,
        )

    # Fetch all messages for the user (both sent and received)
    all_messages = Message.objects.filter(
        models.Q(sender=user) | models.Q(recipient=user)
    ).order_by("-timestamp")

    if not all_messages.exists():
        return Response(
            {"message": "No messages found for the user."},
            status=HTTP_404_NOT_FOUND,
        )

    serializer = MessageSerializer(all_messages, many=True)
    return Response(serializer.data, status=HTTP_200_OK)
