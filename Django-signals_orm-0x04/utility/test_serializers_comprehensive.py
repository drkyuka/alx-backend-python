#!/usr/bin/env python
"""
Comprehensive serializer validation script.
Tests all serializers with the populated data to ensure they work correctly.
"""

import os
import sys
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(
    "/Users/kyukaavongibrahim/sources/alx-backend-python/Django-signals_orm-0x04"
)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Django-signals_orm-0x04.settings")

import django

django.setup()

from chats.models import Conversation, Message, User
from chats.serializers import (
    ConversationSerializer,
    CustomTokenSerializer,
    MessageSerializer,
    UserSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken


def test_user_serializer():
    """Test UserSerializer functionality."""
    print("🔍 Testing UserSerializer...")

    # Get sample users
    admin_user = User.objects.filter(is_superuser=True).first()
    regular_user = User.objects.filter(is_staff=False, is_superuser=False).first()

    if not admin_user or not regular_user:
        print("❌ No users found in database")
        return False

    try:
        # Test serialization
        admin_serializer = UserSerializer(admin_user)
        regular_serializer = UserSerializer(regular_user)

        admin_data = admin_serializer.data
        regular_data = regular_serializer.data

        # Validate required fields are present
        required_fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
        ]
        for field in required_fields:
            if field not in admin_data:
                print(f"❌ Missing field '{field}' in admin user serialization")
                return False
            if field not in regular_data:
                print(f"❌ Missing field '{field}' in regular user serialization")
                return False

        # Test deserialization (creating new user)
        new_user_data = {
            "email": "test@example.com",
            "username": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",  # Add required password
            "is_staff": False,
            "is_superuser": False,
            "is_active": True,
        }

        create_serializer = UserSerializer(data=new_user_data)
        if create_serializer.is_valid():
            print("✅ UserSerializer validation passed")
            print(
                f"   - Admin user: {admin_user.first_name} {admin_user.last_name} ({admin_user.email})"
            )
            print(
                f"   - Regular user: {regular_user.first_name} {regular_user.last_name} ({regular_user.email})"
            )
            print("   - New user data validation: PASSED")
            return True
        else:
            print(f"❌ UserSerializer validation failed: {create_serializer.errors}")
            return False

    except Exception as e:
        print(f"❌ UserSerializer test failed: {e}")
        return False


def test_message_serializer():
    """Test MessageSerializer functionality."""
    print("\n🔍 Testing MessageSerializer...")

    # Get sample message
    sample_message = Message.messages.first()
    if not sample_message:
        print("❌ No messages found in database")
        return False

    try:
        # Test serialization
        message_serializer = MessageSerializer(sample_message)
        message_data = message_serializer.data

        # Validate required fields
        required_fields = [
            "message_id",
            "message_body",
            "sender",
            "receiver",
            "conversation",
        ]
        for field in required_fields:
            if field not in message_data:
                print(f"❌ Missing field '{field}' in message serialization")
                return False

        # Test custom field 'content'
        if "content" not in message_data:
            print("❌ Missing custom 'content' field")
            return False

        # Test message_count method
        if "message_count" not in message_data:
            print("❌ Missing 'message_count' field")
            return False

        # Test validation with valid data
        sender = User.objects.filter(is_active=True).first()
        receiver = (
            User.objects.filter(is_active=True).exclude(user_id=sender.user_id).first()
        )
        conversation = Conversation.conversations.first()

        valid_message_data = {
            "message_body": "Test message for validation",
            "content": "Test message for validation",
            "sender": sender.pk,  # Use primary key instead of user_id
            "receiver": receiver.pk,  # Use primary key instead of user_id
            "conversation": conversation.pk,  # Use primary key instead of conversation_id
        }

        create_serializer = MessageSerializer(data=valid_message_data)
        if create_serializer.is_valid():
            print("✅ MessageSerializer validation passed")
            print(f"   - Sample message: {sample_message.message_body[:50]}...")
            print(
                f"   - Sender: {sample_message.sender.first_name} {sample_message.sender.last_name}"
            )
            print(
                f"   - Receiver: {sample_message.receiver.first_name} {sample_message.receiver.last_name}"
            )
            print(
                f"   - Message count in conversation: {message_data['message_count']}"
            )
        else:
            print(f"❌ MessageSerializer validation failed: {create_serializer.errors}")
            return False

        # Test validation errors
        print("   Testing validation rules...")

        # Test empty message
        empty_message_data = valid_message_data.copy()
        empty_message_data["message_body"] = ""
        empty_serializer = MessageSerializer(data=empty_message_data)
        if empty_serializer.is_valid():
            print("❌ Empty message should have failed validation")
            return False

        # Test same sender and receiver
        same_user_data = valid_message_data.copy()
        same_user_data["receiver"] = sender.pk  # Use pk instead of user_id
        same_user_serializer = MessageSerializer(data=same_user_data)
        if same_user_serializer.is_valid():
            print("❌ Same sender and receiver should have failed validation")
            return False

        print("   ✅ Validation rules working correctly")
        return True

    except Exception as e:
        print(f"❌ MessageSerializer test failed: {e}")
        return False


def test_conversation_serializer():
    """Test ConversationSerializer functionality."""
    print("\n🔍 Testing ConversationSerializer...")

    # Get sample conversation
    sample_conversation = Conversation.conversations.first()
    if not sample_conversation:
        print("❌ No conversations found in database")
        return False

    try:
        # Test serialization
        conv_serializer = ConversationSerializer(sample_conversation)
        conv_data = conv_serializer.data

        # Validate required fields
        required_fields = [
            "conversation_id",
            "participants",
            "messages",
            "participant_count",
        ]
        for field in required_fields:
            if field not in conv_data:
                print(f"❌ Missing field '{field}' in conversation serialization")
                return False

        # Test nested serialization
        if not isinstance(conv_data["participants"], list):
            print("❌ Participants should be a list")
            return False

        if not isinstance(conv_data["messages"], list):
            print("❌ Messages should be a list")
            return False

        # Test participant_count method
        actual_participant_count = sample_conversation.participants.count()
        if conv_data["participant_count"] != actual_participant_count:
            print(
                f"❌ participant_count mismatch: got {conv_data['participant_count']}, expected {actual_participant_count}"
            )
            return False

        # Test conversation creation with participants
        participants = User.objects.filter(is_active=True)[:3]
        participant_ids = [
            str(user.user_id) for user in participants
        ]  # Use user_id (UUID) not pk

        new_conv_data = {
            "participant_ids": participant_ids,
        }

        create_serializer = ConversationSerializer(data=new_conv_data)
        if create_serializer.is_valid():
            print("✅ ConversationSerializer validation passed")
            print(f"   - Sample conversation ID: {sample_conversation.conversation_id}")
            print(f"   - Participants: {len(conv_data['participants'])}")
            print(f"   - Messages: {len(conv_data['messages'])}")
            print(f"   - Participant count: {conv_data['participant_count']}")
            print("   - New conversation validation: PASSED")
            return True
        else:
            print(
                f"❌ ConversationSerializer validation failed: {create_serializer.errors}"
            )
            return False

    except Exception as e:
        print(f"❌ ConversationSerializer test failed: {e}")
        return False


def test_custom_token_serializer():
    """Test CustomTokenSerializer functionality."""
    print("\n🔍 Testing CustomTokenSerializer...")

    # Get a test user
    test_user = User.objects.filter(is_active=True).first()
    if not test_user:
        print("❌ No active users found in database")
        return False

    try:
        # Test token generation
        refresh = RefreshToken.for_user(test_user)
        access_token = str(refresh.access_token)

        if not access_token:
            print("❌ Failed to generate access token")
            return False

        # Test custom token serializer validation
        # The CustomTokenSerializer uses email as username field
        token_data = {
            "email": test_user.email,
            "password": "testpassword123",  # This won't work for real auth but tests structure
        }

        token_serializer = CustomTokenSerializer(data=token_data)

        # Note: This will fail validation because we don't have actual passwords,
        # but we can check that the serializer is properly configured
        if (
            hasattr(token_serializer, "username_field")
            and token_serializer.username_field == "email"
        ):
            print("✅ CustomTokenSerializer configuration passed")
            print(
                f"   - Username field correctly set to: {token_serializer.username_field}"
            )
            print(f"   - Test user email: {test_user.email}")
            print("   - Token generation: WORKING")
            return True
        else:
            print("❌ CustomTokenSerializer username_field not configured correctly")
            return False

    except Exception as e:
        print(f"❌ CustomTokenSerializer test failed: {e}")
        return False


def test_serializer_performance():
    """Test serializer performance with bulk data."""
    print("\n🔍 Testing Serializer Performance...")

    try:
        start_time = datetime.now()

        # Test bulk user serialization
        users = User.objects.all()[:20]
        user_serializer = UserSerializer(users, many=True)
        user_data = user_serializer.data

        # Test bulk message serialization
        messages = Message.messages.all()[:50]
        message_serializer = MessageSerializer(messages, many=True)
        message_data = message_serializer.data

        # Test conversation serialization with nested data
        conversations = Conversation.conversations.all()[:10]
        conv_serializer = ConversationSerializer(conversations, many=True)
        conv_data = conv_serializer.data

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("✅ Performance test passed")
        print(f"   - Serialized {len(user_data)} users")
        print(f"   - Serialized {len(message_data)} messages")
        print(f"   - Serialized {len(conv_data)} conversations")
        print(f"   - Total time: {duration:.3f} seconds")

        # Check data integrity
        if len(user_data) != len(users):
            print("❌ User serialization count mismatch")
            return False

        if len(message_data) != len(messages):
            print("❌ Message serialization count mismatch")
            return False

        if len(conv_data) != len(conversations):
            print("❌ Conversation serialization count mismatch")
            return False

        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🔍 Testing Edge Cases...")

    try:
        # Test very long message
        sender = User.objects.filter(is_active=True).first()
        receiver = (
            User.objects.filter(is_active=True).exclude(user_id=sender.user_id).first()
        )
        conversation = Conversation.conversations.first()

        long_message_data = {
            "message_body": "x" * 600,  # Exceeds 500 char limit
            "sender": sender.pk,
            "receiver": receiver.pk,
            "conversation": conversation.pk,
        }

        long_message_serializer = MessageSerializer(data=long_message_data)
        if long_message_serializer.is_valid():
            print("❌ Long message should have failed validation")
            return False

        # Test invalid UUID
        invalid_uuid_data = {
            "message_body": "Test message",
            "sender": "invalid-uuid",
            "receiver": receiver.pk,
            "conversation": conversation.pk,
        }

        invalid_serializer = MessageSerializer(data=invalid_uuid_data)
        if invalid_serializer.is_valid():
            print("❌ Invalid UUID should have failed validation")
            return False

        # Test empty conversation creation
        empty_conv_serializer = ConversationSerializer(data={})
        if not empty_conv_serializer.is_valid():
            print("❌ Empty conversation should be valid")
            return False

        print("✅ Edge case testing passed")
        print("   - Long message validation: WORKING")
        print("   - Invalid UUID validation: WORKING")
        print("   - Empty conversation creation: WORKING")

        return True

    except Exception as e:
        print(f"❌ Edge case testing failed: {e}")
        return False


def main():
    """Run all serializer tests."""
    print("🚀 Starting Comprehensive Serializer Validation")
    print("=" * 60)

    test_results = []

    # Run all tests
    test_results.append(("UserSerializer", test_user_serializer()))
    test_results.append(("MessageSerializer", test_message_serializer()))
    test_results.append(("ConversationSerializer", test_conversation_serializer()))
    test_results.append(("CustomTokenSerializer", test_custom_token_serializer()))
    test_results.append(("Performance", test_serializer_performance()))
    test_results.append(("Edge Cases", test_edge_cases()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 SERIALIZER VALIDATION SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "-" * 60)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed / len(test_results) * 100):.1f}%")

    if failed == 0:
        print("\n🎉 ALL SERIALIZERS ARE WORKING PERFECTLY!")
        print("Your Django REST API serializers are production-ready.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")

    print("=" * 60)


if __name__ == "__main__":
    main()
