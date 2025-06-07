"""
Unit tests for the permission classes in the chats application.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Conversation, Message, User


class PermissionTests(APITestCase):
    """Test case for the permission classes."""

    def setUp(self):
        """Set up the test case."""
        # Create test users
        self.user1 = User.objects.create_user(
            email="testuser1@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User1",
            phone_number="1234567890",
        )

        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User2",
            phone_number="0987654321",
        )

        self.user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User3",
            phone_number="1122334455",
        )

        # Create test conversations
        self.conversation1 = Conversation.objects.create()
        self.conversation1.participants.add(self.user1, self.user2)

        self.conversation2 = Conversation.objects.create()
        self.conversation2.participants.add(self.user2, self.user3)

        # Create test messages
        self.message1 = Message.objects.create(
            message_body="Test message 1",
            conversation=self.conversation1,
            sender=self.user1,
            receiver=self.user2,
        )

        self.message2 = Message.objects.create(
            message_body="Test message 2",
            conversation=self.conversation1,
            sender=self.user2,
            receiver=self.user1,
        )

        self.message3 = Message.objects.create(
            message_body="Test message 3",
            conversation=self.conversation2,
            sender=self.user2,
            receiver=self.user3,
        )

        # Set up API clients
        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)

        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)

        self.client3 = APIClient()
        self.client3.force_authenticate(user=self.user3)

    def test_conversation_access(self):
        """Test that users can only access conversations they're part of."""
        # User1 should be able to access conversation1
        response = self.client1.get(
            reverse(
                "conversation-detail", kwargs={"pk": self.conversation1.conversation_id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User1 should not be able to access conversation2
        response = self.client1.get(
            reverse(
                "conversation-detail", kwargs={"pk": self.conversation2.conversation_id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # User2 should be able to access both conversations
        response = self.client2.get(
            reverse(
                "conversation-detail", kwargs={"pk": self.conversation1.conversation_id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client2.get(
            reverse(
                "conversation-detail", kwargs={"pk": self.conversation2.conversation_id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User3 should only be able to access conversation2
        response = self.client3.get(
            reverse(
                "conversation-detail", kwargs={"pk": self.conversation1.conversation_id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client3.get(
            reverse(
                "conversation-detail", kwargs={"pk": self.conversation2.conversation_id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_message_access_via_conversation(self):
        """Test that users can only access messages in conversations they're part of."""
        # User1 should be able to access messages in conversation1
        response = self.client1.get(
            reverse(
                "conversation-messages-list",
                kwargs={"conversation_pk": self.conversation1.conversation_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should see both messages

        # User1 should not be able to access messages in conversation2
        response = self.client1.get(
            reverse(
                "conversation-messages-list",
                kwargs={"conversation_pk": self.conversation2.conversation_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # User2 should be able to access messages in both conversations
        response = self.client2.get(
            reverse(
                "conversation-messages-list",
                kwargs={"conversation_pk": self.conversation1.conversation_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = self.client2.get(
            reverse(
                "conversation-messages-list",
                kwargs={"conversation_pk": self.conversation2.conversation_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_global_message_access(self):
        """Test that users can access all messages from conversations they're part of via the global endpoint."""
        # User1 should see only messages from conversation1
        response = self.client1.get(reverse("message-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # User2 should see messages from both conversations
        response = self.client2.get(reverse("message-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # User3 should see only messages from conversation2
        response = self.client3.get(reverse("message-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_message_modification_permissions(self):
        """Test that only the sender of a message can update or delete it."""
        # User1 should be able to update message1 (they are the sender)
        response = self.client1.patch(
            reverse(
                "conversation-messages-detail",
                kwargs={
                    "conversation_pk": self.conversation1.conversation_id,
                    "pk": self.message1.message_id,
                },
            ),
            {"content": "Updated message 1"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User2 should not be able to update message1 (they are not the sender)
        response = self.client2.patch(
            reverse(
                "conversation-messages-detail",
                kwargs={
                    "conversation_pk": self.conversation1.conversation_id,
                    "pk": self.message1.message_id,
                },
            ),
            {"content": "User2 trying to update message 1"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # User1 should be able to delete message1 (they are the sender)
        response = self.client1.delete(
            reverse(
                "conversation-messages-detail",
                kwargs={
                    "conversation_pk": self.conversation1.conversation_id,
                    "pk": self.message1.message_id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # User1 should not be able to delete message2 (they are not the sender)
        response = self.client1.delete(
            reverse(
                "conversation-messages-detail",
                kwargs={
                    "conversation_pk": self.conversation1.conversation_id,
                    "pk": self.message2.message_id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_direct_message_endpoint_permissions(self):
        """Test that the direct message endpoint respects the same permissions."""
        # User1 should be able to view message1 via direct endpoint
        response = self.client1.get(
            reverse("message-detail", kwargs={"pk": self.message1.message_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User3 should not be able to view message1 via direct endpoint (not in the conversation)
        response = self.client3.get(
            reverse("message-detail", kwargs={"pk": self.message1.message_id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # User2 should not be able to update message1 via direct endpoint (not the sender)
        response = self.client2.patch(
            reverse("message-detail", kwargs={"pk": self.message1.message_id}),
            {"content": "User2 trying to update message 1 via direct endpoint"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # User2 should be able to update message2 via direct endpoint (they are the sender)
        response = self.client2.patch(
            reverse("message-detail", kwargs={"pk": self.message2.message_id}),
            {"content": "Updated message 2 via direct endpoint"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
