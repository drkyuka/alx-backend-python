"""
Test file for the messaging app views.
"""

from chats.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from messaging.models import Message


class MessagingViewsTestCase(TestCase):
    """Test case for messaging views."""

    def setUp(self):
        """Set up test data."""
        # Create test users
        self.sender = User.objects.create_user(
            username="testsender",
            email="sender@test.com",
            password="testpassword123",
        )
        self.recipient = User.objects.create_user(
            username="testrecipient",
            email="recipient@test.com",
            password="testpassword123",
        )

        # Create a test message
        self.message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            content="Test message content",
            read=False,
        )

        # Create a test message with parent message
        self.reply_message = Message.objects.create(
            sender=self.recipient,
            recipient=self.sender,
            content="Reply to test message",
            read=False,
            parent_message=self.message,
        )

        self.client = APIClient()

        # Generate tokens
        self.sender_token = RefreshToken.for_user(self.sender).access_token
        self.recipient_token = RefreshToken.for_user(self.recipient).access_token

    def test_delete_user(self):
        """Test delete_user view."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.sender_token}")
        self.client.defaults["HTTP_X_USER_ROLE"] = "admin"
        response = self.client.delete(reverse("messaging:delete_user"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("deleted successfully", response.data["message"])
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email="sender@test.com")

    def test_list_unread_messages(self):
        """Test list_unread_messages view."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.recipient_token}")
        self.client.defaults["HTTP_X_USER_ROLE"] = "admin"
        response = self.client.get(reverse("messaging:list_unread_messages"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should have one unread message
        self.assertEqual(response.data[0]["content"], "Test message content")

    def test_get_all_user_messages(self):
        """Test get_all_user_messages view."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.sender_token}")
        self.client.defaults["HTTP_X_USER_ROLE"] = "admin"
        response = self.client.get(reverse("messaging:get_all_user_messages"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should have both messages

    def test_unauthenticated_access(self):
        """Test unauthenticated access to views."""
        # No credentials or role header set
        response = self.client.delete(reverse("messaging:delete_user"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(reverse("messaging:list_unread_messages"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(reverse("messaging:get_all_user_messages"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
