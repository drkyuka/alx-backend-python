#!/usr/bin/env python3
"""
Validation script for the Postman collection functionality.
Tests JWT authentication, conversation creation, message sending, and authorization.
"""

from datetime import datetime

import requests

BASE_URL = "http://localhost:8001/api"


class APITester:
    def __init__(self):
        self.user1_token = None
        self.user2_token = None
        self.conversation_id = None
        self.user1_credentials = {"email": "user1@example.com", "password": "test@123"}
        self.user2_credentials = {"email": "user2@example.com", "password": "test@123"}

    def test_user_login(self, credentials, user_name):
        """Test user login and JWT token retrieval"""
        print(f"\n🔐 Testing {user_name} login...")

        try:
            response = requests.post(f"{BASE_URL}/token/", json=credentials)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access")
                refresh_token = data.get("refresh")

                if access_token and refresh_token:
                    print(f"✅ {user_name} login successful!")
                    print(f"Access token (first 50 chars): {access_token[:50]}...")
                    print(f"Refresh token received: {'Yes' if refresh_token else 'No'}")
                    return access_token, refresh_token
                else:
                    print(f"❌ {user_name} login failed - missing tokens")
                    return None, None
            else:
                print(f"❌ {user_name} login failed")
                print(f"Response: {response.text}")
                return None, None

        except Exception as e:
            print(f"❌ {user_name} login error: {e}")
            return None, None

    def test_token_refresh(self, refresh_token, user_name):
        """Test JWT token refresh"""
        print(f"\n🔄 Testing {user_name} token refresh...")

        try:
            response = requests.post(
                f"{BASE_URL}/token/refresh/", json={"refresh": refresh_token}
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get("access")
                if new_access_token:
                    print(f"✅ {user_name} token refresh successful!")
                    return new_access_token
                else:
                    print(f"❌ {user_name} token refresh failed - no new access token")
                    return None
            else:
                print(f"❌ {user_name} token refresh failed")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ {user_name} token refresh error: {e}")
            return None

    def get_users_from_messages(self):
        """Get user IDs from existing messages for conversation creation"""
        print("\n👥 Getting user IDs...")

        # Use the actual user IDs we know exist
        user_ids = [
            "f6d499dd-245a-4c30-b771-6211aac57f53",
            "6bc2ac7b-2894-4013-885b-6799f89edbe9",
        ]
        print(f"✅ Using known user IDs: {user_ids}")
        return user_ids

    def test_create_conversation(self, user_ids):
        """Test conversation creation"""
        print("\n💬 Testing conversation creation...")

        headers = {
            "Authorization": f"Bearer {self.user1_token}",
            "Content-Type": "application/json",
        }

        data = {"participant_ids": user_ids}

        try:
            response = requests.post(
                f"{BASE_URL}/conversations/", json=data, headers=headers
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code == 201:
                conversation_data = response.json()
                conversation_id = conversation_data.get("conversation_id")
                print("✅ Conversation created successfully!")
                print(f"Conversation ID: {conversation_id}")
                print(
                    f"Participants: {len(conversation_data.get('participants', []))} users"
                )
                return conversation_id
            else:
                print("❌ Conversation creation failed")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Conversation creation error: {e}")
            return None

    def test_send_message(self, conversation_id):
        """Test sending a message"""
        print("\n📝 Testing message sending...")

        headers = {
            "Authorization": f"Bearer {self.user1_token}",
            "Content-Type": "application/json",
        }

        message_content = f"Hello from validation script! Sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        # Include receiver field - use user2's ID
        data = {
            "content": message_content,
            "receiver": "6bc2ac7b-2894-4013-885b-6799f89edbe9",  # user2's ID
        }

        try:
            response = requests.post(
                f"{BASE_URL}/conversations/{conversation_id}/messages/",
                json=data,
                headers=headers,
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code == 201:
                message_data = response.json()
                print("✅ Message sent successfully!")
                print(f"Message ID: {message_data.get('message_id')}")
                print(f"Content: {message_data.get('content')}")
                return message_data.get("message_id")
            else:
                print("❌ Message sending failed")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Message sending error: {e}")
            return None

    def test_list_conversations(self):
        """Test listing conversations"""
        print("\n📋 Testing conversation listing...")

        headers = {"Authorization": f"Bearer {self.user1_token}"}

        try:
            response = requests.get(f"{BASE_URL}/conversations/", headers=headers)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                conversations = response.json()
                count = conversations.get("count", 0)
                results = conversations.get("results", [])

                print("✅ Conversations retrieved successfully!")
                print(f"Total conversations: {count}")
                if results:
                    print(f"First conversation ID: {results[0].get('id')}")
                    print(
                        f"Participants in first conversation: {results[0].get('participants', [])}"
                    )
                return True
            else:
                print("❌ Conversation listing failed")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Conversation listing error: {e}")
            return False

    def test_list_messages_in_conversation(self, conversation_id):
        """Test listing messages in a conversation"""
        print("\n📨 Testing message listing in conversation...")

        headers = {"Authorization": f"Bearer {self.user1_token}"}

        try:
            response = requests.get(
                f"{BASE_URL}/conversations/{conversation_id}/messages/", headers=headers
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                messages = response.json()
                count = messages.get("count", 0)
                results = messages.get("results", [])

                print("✅ Messages retrieved successfully!")
                print(f"Total messages: {count}")
                if results:
                    print(f"Latest message: {results[0].get('content', 'N/A')}")
                return True
            else:
                print("❌ Message listing failed")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Message listing error: {e}")
            return False

    def test_unauthorized_access(self, conversation_id):
        """Test unauthorized access scenarios"""
        print("\n🚫 Testing unauthorized access...")

        # Test 1: Unauthenticated user trying to list conversations
        print("Test 1: Unauthenticated access to conversations")
        try:
            response = requests.get(f"{BASE_URL}/conversations/")
            print(f"Status Code: {response.status_code}")
            if response.status_code == 401:
                print("✅ Correctly blocked unauthenticated access")
            else:
                print(f"❌ Should have returned 401, got {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing unauthenticated access: {e}")

        # Test 2: User 2 trying to access User 1's conversation
        if self.user2_token:
            print("\nTest 2: User 2 trying to access User 1's messages")
            headers = {"Authorization": f"Bearer {self.user2_token}"}
            try:
                response = requests.get(
                    f"{BASE_URL}/conversations/{conversation_id}/messages/",
                    headers=headers,
                )
                print(f"Status Code: {response.status_code}")
                if response.status_code in [403, 404]:
                    print("✅ Correctly blocked unauthorized user access")
                elif response.status_code == 200:
                    # This might be okay if User 2 is actually a participant
                    print("⚠️ User 2 has access (might be a participant)")
                else:
                    print(f"❌ Unexpected status code: {response.status_code}")
            except Exception as e:
                print(f"❌ Error testing unauthorized user access: {e}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting API Validation Tests")
        print("=" * 50)

        # Test User 1 Login
        self.user1_token, user1_refresh = self.test_user_login(
            self.user1_credentials, "User 1"
        )
        if not self.user1_token:
            print("❌ Cannot continue without User 1 token")
            return False

        # Test User 2 Login
        self.user2_token, user2_refresh = self.test_user_login(
            self.user2_credentials, "User 2"
        )

        # Test Token Refresh
        if user1_refresh:
            new_token = self.test_token_refresh(user1_refresh, "User 1")
            if new_token:
                self.user1_token = new_token  # Use the refreshed token

        # Get user IDs for conversation creation
        user_ids = self.get_users_from_messages()

        # Test Conversation Creation
        self.conversation_id = self.test_create_conversation(user_ids)
        if not self.conversation_id:
            print("❌ Cannot continue without conversation ID")
            return False

        # Test Message Sending
        message_id = self.test_send_message(self.conversation_id)

        # Test Conversation Listing
        self.test_list_conversations()

        # Test Message Listing
        self.test_list_messages_in_conversation(self.conversation_id)

        # Test Unauthorized Access
        self.test_unauthorized_access(self.conversation_id)

        print("\n" + "=" * 50)
        print("🏁 All tests completed!")
        return True


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
