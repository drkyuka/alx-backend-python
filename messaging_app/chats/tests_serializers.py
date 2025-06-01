"""
Tests for the serializers in the chats application.
"""

from django.test import TestCase

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer


class SerializerTestCase(TestCase):
    """Test case for the serializers."""

    def setUp(self):
        """Set up test data."""
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

        # Create a conversation
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

        # Create a message
        self.message = Message.objects.create(
            message_body="Test message",
            conversation=self.conversation,
            sender=self.user1,
            receiver=self.user2,
        )

    def test_user_serializer(self):
        """Test UserSerializer."""
        serializer = UserSerializer(instance=self.user1)
        data = serializer.data

        # Check if the serialized data includes expected fields
        self.assertEqual(data["email"], self.user1.email)
        self.assertEqual(data["first_name"], self.user1.first_name)
        self.assertEqual(data["last_name"], self.user1.last_name)
        self.assertEqual(data["phone_number"], self.user1.phone_number)

    def test_conversation_serializer(self):
        """Test ConversationSerializer."""
        serializer = ConversationSerializer(instance=self.conversation)
        data = serializer.data

        # Check if the serialized data includes expected fields
        self.assertEqual(
            data["conversation_id"], str(self.conversation.conversation_id)
        )
        self.assertEqual(len(data["participants"]), 2)
        self.assertEqual(data["participant_count"], 2)

        # Check if participants are correctly serialized
        participant_emails = [p["email"] for p in data["participants"]]
        self.assertIn(self.user1.email, participant_emails)
        self.assertIn(self.user2.email, participant_emails)

    def test_message_serializer(self):
        """Test MessageSerializer."""
        serializer = MessageSerializer(instance=self.message)
        data = serializer.data

        # Check if the serialized data includes expected fields
        self.assertEqual(data["message_id"], str(self.message.message_id))
        self.assertEqual(data["content"], self.message.message_body)
        self.assertEqual(data["message_count"], 1)

    def test_message_serializer_validation(self):
        """Test validation in MessageSerializer."""
        # Test valid data
        valid_data = {
            "content": "Valid message",
            "conversation": self.conversation.conversation_id,
            "sender": self.user1.user_id,
            "receiver": self.user2.user_id,
        }

        serializer = MessageSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        # Test invalid data - empty message
        invalid_data = valid_data.copy()
        invalid_data["content"] = ""

        serializer = MessageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

        # Test invalid data - same sender and receiver
        invalid_data = valid_data.copy()
        invalid_data["receiver"] = self.user1.user_id

        serializer = MessageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "Sender and receiver cannot be the same user", str(serializer.errors)
        )

    def test_conversation_serializer_with_messages(self):
        """Test ConversationSerializer with included messages."""
        # Create additional messages
        Message.objects.create(
            message_body="Second message",
            conversation=self.conversation,
            sender=self.user2,
            receiver=self.user1,
        )

        Message.objects.create(
            message_body="Third message",
            conversation=self.conversation,
            sender=self.user1,
            receiver=self.user2,
        )

        serializer = ConversationSerializer(instance=self.conversation)
        data = serializer.data

        # Check if messages are included in the serialized data
        self.assertEqual(len(data["messages"]), 3)

        # Check if the message count is correct
        message_bodies = [m["content"] for m in data["messages"]]
        self.assertIn("Test message", message_bodies)
        self.assertIn("Second message", message_bodies)
        self.assertIn("Third message", message_bodies)
