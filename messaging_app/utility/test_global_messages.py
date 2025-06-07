#!/usr/bin/env python3
"""
Test script to validate global message endpoint permissions:
1. Users can access all messages from conversations they're part of through the global messages endpoint
2. Users cannot access messages from conversations they're not part of
3. The global messages endpoint respects the same update/delete permissions
"""

import json

import requests

# Base URL for the API
BASE_URL = "http://localhost:8001"


def get_token(email, password):
    """Get JWT token using email and password."""
    url = f"{BASE_URL}/api/token/"
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    print(f"Getting token for {email}...")
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        token_data = response.json()
        print("Token obtained successfully!")
        return token_data["access"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def get_conversations(token):
    """Get all conversations for the authenticated user."""
    url = f"{BASE_URL}/api/conversations/"
    headers = {"Authorization": f"Bearer {token}"}

    print("Fetching conversations...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        conversations = response.json()
        print(f"Found {len(conversations)} conversations")
        return conversations
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


def get_messages_in_conversation(token, conversation_id):
    """Get all messages in a specific conversation."""
    url = f"{BASE_URL}/api/conversations/{conversation_id}/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Fetching messages for conversation {conversation_id}...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json()
        print(f"Found {len(messages)} messages in conversation")
        return messages
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


def get_all_messages(token):
    """Get all messages the user has access to via global messages endpoint."""
    url = f"{BASE_URL}/api/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    print("Fetching all messages via global endpoint...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json()
        print(f"Found {len(messages)} messages via global endpoint")
        return messages
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


def get_message_by_id(token, message_id):
    """Get a specific message by ID via the global endpoint."""
    url = f"{BASE_URL}/api/messages/{message_id}/"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Fetching message {message_id} via global endpoint...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        message = response.json()
        print(f"Successfully retrieved message {message_id}")
        return message
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def update_message_global(token, message_id, new_content):
    """Update a message via the global messages endpoint."""
    url = f"{BASE_URL}/api/messages/{message_id}/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {"content": new_content}

    print(f"Attempting to update message {message_id} via global endpoint...")
    response = requests.patch(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("✓ Message updated successfully")
        return True, response.json()
    else:
        print(f"✗ Failed to update message: {response.status_code} - {response.text}")
        return False, None


def delete_message_global(token, message_id):
    """Delete a message via the global messages endpoint."""
    url = f"{BASE_URL}/api/messages/{message_id}/"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Attempting to delete message {message_id} via global endpoint...")
    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print("✓ Message deleted successfully")
        return True
    else:
        print(f"✗ Failed to delete message: {response.status_code} - {response.text}")
        return False


def send_message(token, conversation_id, content, receiver_id):
    """Send a new message in a conversation."""
    url = f"{BASE_URL}/api/conversations/{conversation_id}/messages/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {"content": content, "receiver": receiver_id}

    print(f"Sending message to conversation {conversation_id}...")
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print("✓ Message sent successfully")
        return response.json()
    else:
        print(f"✗ Failed to send message: {response.status_code} - {response.text}")
        return None


def test_global_messages_access():
    """Test that users can access all their messages through the global endpoint."""
    print("\n=== Testing Global Messages Access ===")

    # Get tokens for both users
    user1_token = get_token("testuser@example.com", "testpass123")
    user2_token = get_token("testuser2@example.com", "testpass123")

    if not user1_token or not user2_token:
        print("Failed to get tokens. Skipping test.")
        return

    # Get all messages for User1 via global endpoint
    user1_global_messages = get_all_messages(user1_token)

    # Get all messages for User1 via individual conversations
    user1_conversations = get_conversations(user1_token)
    user1_conv_messages = []

    for conv in user1_conversations:
        messages = get_messages_in_conversation(user1_token, conv["conversation_id"])
        user1_conv_messages.extend(messages)

    # Compare the counts
    print(f"\nUser1 global messages count: {len(user1_global_messages)}")
    print(f"User1 messages from all conversations: {len(user1_conv_messages)}")

    if len(user1_global_messages) == len(user1_conv_messages):
        print(
            "✓ Global messages endpoint returns all messages from user's conversations"
        )
    else:
        print("✗ Global messages count doesn't match conversation messages count")

    # Do the same check for User2
    user2_global_messages = get_all_messages(user2_token)

    user2_conversations = get_conversations(user2_token)
    user2_conv_messages = []

    for conv in user2_conversations:
        messages = get_messages_in_conversation(user2_token, conv["conversation_id"])
        user2_conv_messages.extend(messages)

    print(f"\nUser2 global messages count: {len(user2_global_messages)}")
    print(f"User2 messages from all conversations: {len(user2_conv_messages)}")

    if len(user2_global_messages) == len(user2_conv_messages):
        print(
            "✓ Global messages endpoint returns all messages from user's conversations"
        )
    else:
        print("✗ Global messages count doesn't match conversation messages count")


def test_global_message_permissions():
    """Test permission checks on the global messages endpoint."""
    print("\n=== Testing Global Message Permissions ===")

    # Get tokens for both users
    user1_token = get_token("testuser@example.com", "testpass123")
    user2_token = get_token("testuser2@example.com", "testpass123")

    if not user1_token or not user2_token:
        print("Failed to get tokens. Skipping test.")
        return

    # Find a shared conversation between User1 and User2
    user1_conversations = get_conversations(user1_token)
    shared_conversation = None

    for conv in user1_conversations:
        participants = [p["email"] for p in conv["participants"]]
        if (
            "testuser@example.com" in participants
            and "testuser2@example.com" in participants
        ):
            shared_conversation = conv
            break

    if not shared_conversation:
        print("Could not find a shared conversation. Skipping test.")
        return

    # User1 sends a message to the shared conversation
    user2_id = next(
        p["user_id"]
        for p in shared_conversation["participants"]
        if p["email"] == "testuser2@example.com"
    )
    new_message = send_message(
        user1_token,
        shared_conversation["conversation_id"],
        "This is a test message from User1 for global endpoint test",
        user2_id,
    )

    if not new_message:
        print("Failed to send test message. Skipping test.")
        return

    message_id = new_message["message_id"]
    print(f"Created test message with ID: {message_id}")

    # Test 1: User1 (sender) should be able to retrieve their message via global endpoint
    message = get_message_by_id(user1_token, message_id)

    print("\nTest 1: Sender retrieving their message via global endpoint")
    if message:
        print(
            "✓ User1 (sender) successfully retrieved their message via global endpoint"
        )
    else:
        print("✗ User1 (sender) failed to retrieve their message via global endpoint")

    # Test 2: User2 (participant but not sender) should be able to retrieve the message via global endpoint
    message = get_message_by_id(user2_token, message_id)

    print("\nTest 2: Participant retrieving message via global endpoint")
    if message:
        print(
            "✓ User2 (participant) successfully retrieved the message via global endpoint"
        )
    else:
        print(
            "✗ User2 (participant) failed to retrieve the message via global endpoint"
        )

    # Test 3: User1 (sender) should be able to update their message via global endpoint
    success, updated_message = update_message_global(
        user1_token,
        message_id,
        "This message was updated by User1 (sender) via global endpoint",
    )

    print("\nTest 3: Sender updating their message via global endpoint")
    if success:
        print("✓ User1 (sender) successfully updated their message via global endpoint")
    else:
        print("✗ User1 (sender) failed to update their message via global endpoint")

    # Test 4: User2 (not sender) should NOT be able to update User1's message via global endpoint
    success, _ = update_message_global(
        user2_token,
        message_id,
        "This should fail - User2 trying to update User1's message via global endpoint",
    )

    print("\nTest 4: Non-sender trying to update message via global endpoint")
    if not success:
        print(
            "✓ User2 (non-sender) correctly prevented from updating message via global endpoint"
        )
    else:
        print(
            "✗ ERROR: User2 (non-sender) was able to update message via global endpoint!"
        )

    # Test 5: User2 (not sender) should NOT be able to delete User1's message via global endpoint
    success = delete_message_global(user2_token, message_id)

    print("\nTest 5: Non-sender trying to delete message via global endpoint")
    if not success:
        print(
            "✓ User2 (non-sender) correctly prevented from deleting message via global endpoint"
        )
    else:
        print(
            "✗ ERROR: User2 (non-sender) was able to delete message via global endpoint!"
        )

    # Test 6: User1 (sender) should be able to delete their own message via global endpoint
    success = delete_message_global(user1_token, message_id)

    print("\nTest 6: Sender deleting their message via global endpoint")
    if success:
        print("✓ User1 (sender) successfully deleted their message via global endpoint")
    else:
        print("✗ User1 (sender) failed to delete their message via global endpoint")


if __name__ == "__main__":
    print("=== Starting Global Messages Endpoint Tests ===\n")

    test_global_messages_access()
    test_global_message_permissions()

    print("\n=== Global Messages Endpoint Tests Complete ===")
