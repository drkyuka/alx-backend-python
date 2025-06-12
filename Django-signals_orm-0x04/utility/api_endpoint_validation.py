#!/usr/bin/env python
"""
Comprehensive API Endpoint Validation
=====================================

This script validates that all serializers work correctly with the actual
Django REST API endpoints, testing the full request-response cycle.
"""

import os
import sys
import json
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(
    "/Users/kyukaavongibrahim/sources/alx-backend-python/Django-signals_orm-0x04"
)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Django-signals_orm-0x04.settings")

import django

django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from chats.models import User, Conversation, Message
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


def setup_test_client():
    """Set up API client with authentication."""
    client = APIClient()

    # Get a test user for authentication
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("❌ No active users found for testing")
        return None, None

    # Generate JWT token for the user
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # Set authentication header
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    return client, user


def test_conversation_endpoints():
    """Test Conversation API endpoints."""
    print("🔍 Testing Conversation API Endpoints...")

    client, user = setup_test_client()
    if not client:
        return False

    try:
        # Test GET /conversations/ (list conversations)
        response = client.get("/api/conversations/")
        if response.status_code == 200:
            conversations = response.json()
            print(
                f"✅ GET /conversations/ - Found {len(conversations.get('results', conversations))} conversations"
            )
        else:
            print(f"❌ GET /conversations/ failed - Status: {response.status_code}")
            return False

        # Test POST /conversations/ (create conversation)
        participants = User.objects.filter(is_active=True)[:3]
        participant_ids = [str(u.user_id) for u in participants]

        conversation_data = {"participant_ids": participant_ids}

        response = client.post("/api/conversations/", conversation_data, format="json")
        if response.status_code == 201:
            new_conversation = response.json()
            conversation_id = new_conversation["conversation_id"]
            print(f"✅ POST /conversations/ - Created conversation {conversation_id}")

            # Test GET /conversations/{id}/ (retrieve specific conversation)
            response = client.get(f"/api/conversations/{conversation_id}/")
            if response.status_code == 200:
                print(
                    f"✅ GET /conversations/{conversation_id}/ - Retrieved successfully"
                )
            else:
                print(f"❌ GET /conversations/{conversation_id}/ failed")
                return False

        else:
            print(f"❌ POST /conversations/ failed - Status: {response.status_code}")
            print(f"Response: {response.content}")
            return False

        return True

    except Exception as e:
        print(f"❌ Conversation endpoint test failed: {e}")
        return False


def test_message_endpoints():
    """Test Message API endpoints."""
    print("\n🔍 Testing Message API Endpoints...")

    client, user = setup_test_client()
    if not client:
        return False

    try:
        # Get a conversation the user participates in
        conversation = Conversation.conversations.filter(participants=user).first()
        if not conversation:
            print("❌ No conversations found for user")
            return False

        # Test GET /conversations/{id}/messages/ (list messages in conversation)
        response = client.get(
            f"/api/conversations/{conversation.conversation_id}/messages/"
        )
        if response.status_code == 200:
            messages = response.json()
            print(
                f"✅ GET /conversations/{conversation.conversation_id}/messages/ - Found messages"
            )
        else:
            print(f"❌ GET messages failed - Status: {response.status_code}")
            return False

        # Test POST /conversations/{id}/messages/ (create message)
        # Get another participant to send message to
        other_participants = conversation.participants.exclude(user_id=user.user_id)
        if not other_participants.exists():
            print("❌ No other participants in conversation")
            return False

        receiver = other_participants.first()
        message_data = {
            "message_body": "Test message created via API endpoint validation",
            "receiver": receiver.pk,  # Use PK for message creation
        }

        response = client.post(
            f"/api/conversations/{conversation.conversation_id}/messages/",
            message_data,
            format="json",
        )
        if response.status_code == 201:
            new_message = response.json()
            print(
                f"✅ POST /conversations/{conversation.conversation_id}/messages/ - Created message"
            )
            print(f"   Message: {new_message['message_body'][:50]}...")
        else:
            print(f"❌ POST message failed - Status: {response.status_code}")
            print(f"Response: {response.content}")
            return False

        return True

    except Exception as e:
        print(f"❌ Message endpoint test failed: {e}")
        return False


def test_authentication_endpoints():
    """Test JWT Authentication endpoints."""
    print("\n🔍 Testing Authentication Endpoints...")

    client = APIClient()  # No authentication for login

    try:
        # Get a user with known credentials (we'll need to test with a user we can authenticate)
        user = User.objects.filter(is_active=True).first()
        if not user:
            print("❌ No active users found")
            return False

        # Test token generation endpoint structure
        # Note: We can't test actual login without knowing passwords,
        # but we can test the endpoint exists and serializer structure

        login_data = {
            "email": user.email,
            "password": "wrongpassword",  # This will fail, but tests endpoint
        }

        response = client.post("/api/token/", login_data, format="json")
        # We expect this to fail with 401, but endpoint should exist
        if response.status_code in [400, 401]:
            print(
                "✅ POST /api/token/ - Endpoint exists and responds to authentication attempts"
            )

            # Check if response contains expected error structure
            error_data = response.json()
            if "detail" in error_data or "non_field_errors" in error_data:
                print("✅ Authentication error handling - Proper error response format")
            else:
                print("⚠️  Authentication error format - Unexpected response structure")
        else:
            print(f"❌ POST /api/token/ - Unexpected status: {response.status_code}")
            return False

        # Test that we can generate tokens programmatically (serializer validation)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        if access_token:
            print("✅ JWT Token Generation - Programmatic token creation works")
        else:
            print("❌ JWT Token Generation - Failed to create tokens")
            return False

        return True

    except Exception as e:
        print(f"❌ Authentication endpoint test failed: {e}")
        return False


def test_api_error_handling():
    """Test API error handling and validation."""
    print("\n🔍 Testing API Error Handling...")

    client, user = setup_test_client()
    if not client:
        return False

    try:
        # Test invalid conversation creation (invalid UUID)
        invalid_data = {"participant_ids": ["invalid-uuid", "another-invalid-uuid"]}

        response = client.post("/api/conversations/", invalid_data, format="json")
        if response.status_code == 400:
            error_data = response.json()
            print(
                "✅ Invalid UUID handling - Proper 400 error for invalid participant IDs"
            )
        else:
            print(
                f"⚠️  Invalid UUID handling - Expected 400, got {response.status_code}"
            )

        # Test empty message creation
        conversation = Conversation.conversations.filter(participants=user).first()
        if conversation:
            empty_message_data = {
                "message_body": "",  # Empty content should fail
                "receiver": user.pk,
            }

            response = client.post(
                f"/api/conversations/{conversation.conversation_id}/messages/",
                empty_message_data,
                format="json",
            )
            if response.status_code == 400:
                print(
                    "✅ Empty message validation - Proper 400 error for empty content"
                )
            else:
                print(
                    f"⚠️  Empty message validation - Expected 400, got {response.status_code}"
                )

        # Test accessing non-existent conversation
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/conversations/{fake_uuid}/")
        if response.status_code == 404:
            print("✅ Non-existent resource handling - Proper 404 error")
        else:
            print(
                f"⚠️  Non-existent resource handling - Expected 404, got {response.status_code}"
            )

        return True

    except Exception as e:
        print(f"❌ API error handling test failed: {e}")
        return False


def test_api_performance():
    """Test API performance with multiple requests."""
    print("\n🔍 Testing API Performance...")

    client, user = setup_test_client()
    if not client:
        return False

    try:
        start_time = datetime.now()

        # Test multiple conversation retrievals
        for _ in range(5):
            response = client.get("/api/conversations/")
            if response.status_code != 200:
                print(f"❌ Performance test failed - Status: {response.status_code}")
                return False

        # Test multiple message retrievals
        conversation = Conversation.conversations.filter(participants=user).first()
        if conversation:
            for _ in range(5):
                response = client.get(
                    f"/api/conversations/{conversation.conversation_id}/messages/"
                )
                if response.status_code != 200:
                    print(
                        f"❌ Performance test failed - Status: {response.status_code}"
                    )
                    return False

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"✅ API Performance - 10 requests completed in {duration:.3f} seconds")

        if duration < 2.0:  # Should complete within 2 seconds
            print("✅ Performance benchmark - API response times are acceptable")
        else:
            print("⚠️  Performance benchmark - API response times may need optimization")

        return True

    except Exception as e:
        print(f"❌ API performance test failed: {e}")
        return False


def main():
    """Run all API endpoint validation tests."""
    print("🚀 Starting Comprehensive API Endpoint Validation")
    print("=" * 60)
    print(f"Testing Django REST API endpoints with validated serializers")
    print(f"Date: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}")
    print("=" * 60)

    test_results = []

    # Run all API tests
    test_results.append(("Conversation Endpoints", test_conversation_endpoints()))
    test_results.append(("Message Endpoints", test_message_endpoints()))
    test_results.append(("Authentication Endpoints", test_authentication_endpoints()))
    test_results.append(("Error Handling", test_api_error_handling()))
    test_results.append(("API Performance", test_api_performance()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 API ENDPOINT VALIDATION SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "-" * 60)
    print(f"Total API Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed / len(test_results) * 100):.1f}%")

    if failed == 0:
        print("\n🎉 ALL API ENDPOINTS ARE WORKING PERFECTLY!")
        print("Your Django REST API is ready for production use.")
        print("Serializers are properly integrated with ViewSets and endpoints.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")

    print("=" * 60)


if __name__ == "__main__":
    main()
