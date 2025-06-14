"""views.py
# Module for handling user-related views in the messaging application.
"""

from chats.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.request import Request


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def list_unread_messages(request: Request) -> Response:
    """
    View to list unread messages for the authenticated user.
    """

    user: User = request.user

    if not user.is_authenticated:
        return Response(
            {"error": "User is not authenticated."},
            status=HTTP_404_NOT_FOUND,
        )

    # Fetch unread messages for the user
    unread_messages = Messages.unread.filter(recipient=user).only(
        "message_id", "sender", "recipient", "content", "timestamp"
    )

    return Response(unread_messages.data, status=HTTP_200_OK)
