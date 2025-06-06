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
from .permissions import IsActiveUser, IsConversationParticipant
from .serializers import (
    ConversationSerializer,
    CustomTokenSerializer,
    MessageSerializer,
)
from .auth import CustomJWTAuthentication


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

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["message_body", "sender__email", "receiver__email"]
    ordering_fields = ["sent_at", "created_at"]

    # Add permission classes to ensure only participants can access messages
    permission_classes = [IsActiveUser, IsConversationParticipant]

    def get_queryset(self) -> QuerySet[Message]:
        """
        Override to filter messages based on the conversation parameter.
        """
        queryset = self.queryset
        conversation_id = self.kwargs.get("conversation_pk")

        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)

        return queryset

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
    # Added authentication and permission classes
    # to authenticate users using JWT
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsActiveUser]
