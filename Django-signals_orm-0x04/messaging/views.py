"""views.py
# Module for handling user-related views in the messaging application.
"""

from chats.models import User
from messaging.models import Message
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from .serializers import MessageSerializer


@api_view(["DELETE"])
# @permission_classes([IsAuthenticated])
def delete_user(request: Request) -> Response:
    """
    View to delete a user by ID.
    """

    try:
        user: User = request.user
        user.delete()
        return Response(
            {"message": f"User {user.username} deleted successfully."},
            status=HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response(
            {"error": f"User {user.username} not found."},
            status=HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
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

    # if not user.is_authenticated:
    #     return Response(
    #         {"error": "User is not authenticated."},
    #         status=HTTP_401_UNAUTHORIZED,
    #     )

    # Fetch unread messages for the user
    unread_messages = Message.unread.filter(recipient=user).only(
        "message_id", "sender", "recipient", "content", "timestamp"
    )

    return Response(unread_messages.data, status=HTTP_200_OK)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
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

    # if not user.is_authenticated:
    #     return Response(
    #         {"error": "User is not authenticated."},
    #         status=HTTP_401_UNAUTHORIZED,
    #     )

    # Fetch all messages for the user
    replies = MessageSerializer(Message.parent_message)

    if not replies:
        return Response(
            {"message": "No messages found for the user."},
            status=HTTP_404_NOT_FOUND,
        )

    return Response(replies.data, status=HTTP_200_OK)
