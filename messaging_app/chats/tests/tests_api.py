"""
Tests for the conversation and message endpoints.
"""

import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Conversation, Message, User


class ConversationAPITestCase(TestCase):
    """Test case for the conversation API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create(
            email="user1@example.com",
            password="testpassword1",
            first_name="Test",
            last_name="User1",
            phone_number="1234567890",
        )

        self.user2 = User.objects.create(
            email="user2@example.com",
            password="testpassword2",
            first_name="Test",
            last_name="User2",
            phone_number="9876543210",
        )

        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

        # URL for creating conversations
        self.conversations_url = reverse("conversation-list")

    def test_create_conversation(self):
        """Test creating a new conversation."""
        # Data for creating a new conversation
        data = {"participant_ids": [str(self.user1.user_id), str(self.user2.user_id)]}

        # Make the API request
        response = self.client.post(self.conversations_url, data, format="json")

        # Check if the conversation was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)

        # Check if the participants were added correctly
        conversation = Conversation.objects.get()
        self.assertEqual(conversation.participants.count(), 2)
        self.assertIn(self.user1, conversation.participants.all())
        self.assertIn(self.user2, conversation.participants.all())

    def test_send_message_to_conversation(self):
        """Test sending a message to an existing conversation."""
        # Create a conversation first
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        # URL for sending messages to the conversation
        messages_url = reverse(
            "conversation-messages-list",
            kwargs={"conversation_pk": conversation.conversation_id},
        )

        # Data for sending a new message
        data = {
            "content": "Hello, this is a test message!",
            "sender": str(self.user1.user_id),
            "receiver": str(self.user2.user_id),
        }

        # Make the API request
        response = self.client.post(messages_url, data, format="json")

        # Print the response data for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")

        # Check if the message was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)

        # Check message details
        message = Message.objects.get()
        self.assertEqual(message.message_body, "Hello, this is a test message!")
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.conversation, conversation)

    def test_send_message_to_nonexistent_conversation(self):
        """Test sending a message to a nonexistent conversation."""
        # Generate a random UUID for a nonexistent conversation
        nonexistent_id = uuid.uuid4()

        # URL for sending messages to a nonexistent conversation
        messages_url = reverse(
            "conversation-messages-list", kwargs={"conversation_pk": nonexistent_id}
        )

        # Data for sending a new message
        data = {
            "message_body": "This message should not be sent.",
            "sender": str(self.user1.user_id),
            "receiver": str(self.user2.user_id),
        }

        # Make the API request
        response = self.client.post(messages_url, data, format="json")

        # Check if the request failed with a 404 status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Message.objects.count(), 0)

    def test_list_conversations(self):
        """Test listing conversations for the authenticated user."""
        # Create conversations with different participants
        conversation1 = Conversation.objects.create()
        conversation1.participants.add(self.user1, self.user2)

        conversation2 = Conversation.objects.create()
        conversation2.participants.add(self.user1)

        # Create a conversation that shouldn't be visible to user1
        conversation3 = Conversation.objects.create()
        conversation3.participants.add(self.user2)

        # Make the API request
        response = self.client.get(self.conversations_url)

        # Check if only the conversations with user1 are returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Check that the conversation IDs match the expected conversations
        response_ids = [conv["conversation_id"] for conv in response.data]
        self.assertIn(str(conversation1.conversation_id), response_ids)
        self.assertIn(str(conversation2.conversation_id), response_ids)
        self.assertNotIn(str(conversation3.conversation_id), response_ids)

    def test_list_messages_in_conversation(self):
        """Test listing messages in a conversation."""
        # Create a conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        # Create messages in the conversation
        message1 = Message.objects.create(
            message_body="First message",
            conversation=conversation,
            sender=self.user1,
            receiver=self.user2,
        )

        message2 = Message.objects.create(
            message_body="Second message",
            conversation=conversation,
            sender=self.user2,
            receiver=self.user1,
        )

        # URL for listing messages in the conversation
        messages_url = reverse(
            "conversation-messages-list",
            kwargs={"conversation_pk": conversation.conversation_id},
        )

        # Make the API request
        response = self.client.get(messages_url)

        # Check if the messages are returned correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Check message details
        message_bodies = [msg["content"] for msg in response.data]
        self.assertIn(message1.message_body, message_bodies)
        self.assertIn(message2.message_body, message_bodies)


class ConversationMessagesIntegrationTestCase(TestCase):
    """Integration test for adding and listing messages in a conversation via API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create(
            email="user1@example.com",
            password="testpassword1",
            first_name="Test",
            last_name="User1",
            phone_number="1234567890",
        )

        self.user2 = User.objects.create(
            email="user2@example.com",
            password="testpassword2",
            first_name="Test",
            last_name="User2",
            phone_number="9876543210",
        )

        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

        # Create conversation
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

        # URL for sending messages to the conversation
        self.messages_url = reverse(
            "conversation-messages-list",
            kwargs={"conversation_pk": self.conversation.conversation_id},
        )

    def test_add_and_list_multiple_messages(self):
        """Test adding and listing multiple messages in a conversation."""
        # Add first message
        data1 = {
            "content": "Hello from user1!",
            "sender": str(self.user1.user_id),
            "receiver": str(self.user2.user_id),
        }
        response1 = self.client.post(self.messages_url, data1, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Add second message
        data2 = {
            "content": "Reply from user2!",
            "sender": str(self.user2.user_id),
            "receiver": str(self.user1.user_id),
        }
        self.client.force_authenticate(user=self.user2)
        response2 = self.client.post(self.messages_url, data2, format="json")
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # Add third message
        data3 = {
            "content": "Another message from user1!",
            "sender": str(self.user1.user_id),
            "receiver": str(self.user2.user_id),
        }
        self.client.force_authenticate(user=self.user1)
        response3 = self.client.post(self.messages_url, data3, format="json")
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)

        # List messages
        response = self.client.get(self.messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # Check message contents
        contents = [msg["content"] for msg in response.data]
        self.assertIn("Hello from user1!", contents)
        self.assertIn("Reply from user2!", contents)
        self.assertIn("Another message from user1!", contents)


class SeededDataValidationTestCase(TestCase):
    """Test seeded data for conversations and messages integrity."""

    def setUp(self):
        from django.core.management import call_command

        call_command("seed_chats")

    def test_conversations_and_messages_integrity(self):
        conversations = Conversation.objects.all()
        self.assertGreaterEqual(conversations.count(), 12)
        for convo in conversations:
            participants = list(convo.participants.all())
            self.assertGreaterEqual(len(participants), 2)
            messages = convo.messages.all()
            self.assertGreaterEqual(messages.count(), 1)
            for msg in messages:
                self.assertIn(msg.sender, participants)
                self.assertIn(msg.receiver, participants)
                self.assertNotEqual(msg.sender, msg.receiver)
                self.assertTrue(msg.message_body)
