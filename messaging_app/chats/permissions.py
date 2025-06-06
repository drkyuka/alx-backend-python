"""permissions.py"""

from rest_framework import permissions

from .models import Conversation


class IsActiveUser(permissions.BasePermission):
    """
    Custom permission to only allow active users to access the view.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and active
        return request.user and request.user.is_authenticated and request.user.is_active


class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to:
    - View messages in the conversation
    - Send messages to the conversation
    - Update their own messages in the conversation
    - Delete their own messages in the conversation
    """

    def has_permission(self, request, view):
        """
        Check if the user is a participant in the conversation.
        This is used for list and create operations.
        """
        # First, check if the user is authenticated
        if not (request.user and request.user.is_authenticated):
            return False

        # Get the conversation_id from the URL parameters
        conversation_pk = view.kwargs.get("conversation_pk")
        if not conversation_pk:
            return False

        # Check if the user is a participant in the conversation
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_pk)
            return conversation.participants.filter(
                user_id=request.user.user_id
            ).exists()
        except Conversation.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions.
        This is used for retrieve, update, partial_update, and destroy operations.

        For update and delete operations, we also check if the user is the sender of the message.
        """
        # First check if the user is a participant in the conversation
        conversation = obj.conversation
        user_is_participant = conversation.participants.filter(
            user_id=request.user.user_id
        ).exists()

        if not user_is_participant:
            return False

        # For GET requests, being a participant is enough
        if request.method in permissions.SAFE_METHODS:
            return True

        # For PUT, PATCH, DELETE, the user must be the sender of the message
        return obj.sender.user_id == request.user.user_id
