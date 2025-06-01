"""views.py
This file contains the ViewSets for the chats application.
"""

from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

# Create your views here.


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Provides CRUD operations for Conversation model.
    """

    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def get_queryset(self):
        """
        Override to filter conversations based on the authenticated user.
        """
        return self.queryset.filter(
            participants__user_id=self.request.user.user_id
        ).distinct()

    def create(self, request, *args, **kwargs):
        """
        Override create method to handle conversation creation.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Provides CRUD operations for Message model.
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_queryset(self):
        """
        Override to filter messages based on the conversation parameter.
        """
        queryset = self.queryset
        conversation_id = self.kwargs.get("conversation_pk")

        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Override create method to handle message creation.
        Set the conversation based on the URL.
        """
        conversation_id = self.kwargs.get("conversation_pk")
        data = request.data.copy()

        if conversation_id:
            # Get the conversation
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
                data["conversation"] = str(conversation.conversation_id)
            except Conversation.DoesNotExist:
                return Response(
                    {"detail": "Conversation not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
