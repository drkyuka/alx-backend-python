"""views.py
This file contains the ViewSets for the chats application.
"""

from rest_framework import viewsets
from .models import Conversation
from .serializers import UserSerializer, MessageSerializer, ConversationSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

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
