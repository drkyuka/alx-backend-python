"""views.py
This file contains the ViewSets for the chats application.
"""

from typing import Any

from django.db.models import QuerySet
from rest_framework import filters, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Conversation, Message
from .permissions import CanAccessMessages, IsActiveUser, IsConversationParticipant
from .serializers import (
    ConversationSerializer,
    CustomTokenSerializer,
    MessageSerializer,
)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Provides CRUD operations for Conversation model.
    """

    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsActiveUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "participants__email",
        "participants__first_name",
        "participants__last_name",
    ]
    ordering_fields = ["conversation_id"]

    def get_queryset(self) -> QuerySet[Conversation]:
        """
        Override to filter conversations based on the authenticated user.
        Returns conversations where the current user is a participant.
        """
        return self.queryset.filter(participants=self.request.user).distinct()

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Override create method to handle conversation creation.
        """
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Provides CRUD operations for Message model.
    """

    # Get all messages - permissions will filter access
    queryset = Message.objects.all().distinct()

    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["message_body", "sender__email", "receiver__email"]
    ordering_fields = ["sent_at", "created_at"]

    # Add permission classes based on the endpoint
    def get_permissions(self):
        """
        Set different permissions based on the route.
        - For nested routes under conversations, use IsConversationParticipant
        - For direct message access, use CanAccessMessages
        """
        if self.kwargs.get("conversation_pk"):
            # This is a nested route under a conversation
            return [IsActiveUser(), IsConversationParticipant()]
        else:
            # This is the direct messages endpoint
            return [IsActiveUser(), CanAccessMessages()]

    def get_queryset(self) -> QuerySet[Message]:
        """
        Override to filter messages based on the conversation parameter.
        """
        user = self.request.user
        if not user.is_authenticated or not user.is_active:
            return Message.objects.none()

        # For direct message access, return all messages from conversations the user is part of
        if not self.kwargs.get("conversation_pk"):
            # Get all conversations the user is part of
            conversations = Conversation.objects.filter(participants=user)
            if not conversations.exists():
                return Message.objects.none()

            # Return all messages from those conversations
            return Message.objects.filter(conversation__in=conversations).distinct()

        # For nested routes under a conversation, filter by the conversation ID
        conversation_id = self.kwargs.get("conversation_pk")
        return Message.objects.filter(
            conversation__conversation_id=conversation_id
        ).distinct()

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Override create method to handle message creation.
        Validates that the sender is a participant in the conversation.
        """
        data = request.data.copy()
        conversation_id = self.kwargs.get("conversation_pk")

        if conversation_id:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)

                # Check if the current user is a participant in the conversation
                if not conversation.participants.filter(
                    user_id=request.user.user_id
                ).exists():
                    return Response(
                        {"detail": "You are not a participant in this conversation."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # Set the sender to the current user
                data["sender"] = str(request.user.user_id)
                data["conversation"] = str(conversation.conversation_id)

                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Conversation.DoesNotExist:
                return Response(
                    {"detail": "Conversation not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(
            {"detail": "Conversation ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CustomTokenView(TokenObtainPairView):
    """
    Custom Token Obtain Pair View to handle token generation.
    This view can be extended to include additional fields or logic.
    """

    serializer_class = CustomTokenSerializer
    # Token generation endpoints should not require authentication
    authentication_classes = []
    permission_classes = []
