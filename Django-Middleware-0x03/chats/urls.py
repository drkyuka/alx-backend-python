"""urls.py
chats application URL configuration.
This file defines the URL patterns for the chats application,
including the endpoints for managing conversations, messages, and users.
"""

from django.urls import include, path
from rest_framework_nested.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter as NestedDefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import ConversationViewSet, CustomTokenView, MessageViewSet

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")


conversations_router = NestedDefaultRouter(
    router, r"conversations", lookup="conversation"
)
conversations_router.register(
    r"messages", MessageViewSet, basename="conversation-messages"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(conversations_router.urls)),
]

urlpatterns += [
    path("token/", CustomTokenView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
