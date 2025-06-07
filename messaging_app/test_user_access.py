#!/usr/bin/env python3
"""
Simple test script to validate that a user can only see conversations and messages they're part of.
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


def get_all_messages(token):
    """Get all messages the user has access to."""
    url = f"{BASE_URL}/api/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    print("Fetching all messages...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json()
        print(f"Found {len(messages)} messages")
        return messages
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


def test_user1_access():
    """Test if User1 can only see their own conversations and messages."""
    print("\n--- Testing User1 Access ---")

    # Get token for User1
    token = get_token("testuser@example.com", "testpass123")
    if not token:
        print("Failed to get token for User1")
        return

    # Get conversations for User1
    conversations = get_conversations(token)

    # For each conversation, verify User1 is a participant
    for i, conv in enumerate(conversations):
        print(f"\nConversation {i + 1} - ID: {conv['conversation_id']}")
        participants = [p["email"] for p in conv["participants"]]
        print(f"Participants: {participants}")

        if "testuser@example.com" in participants:
            print("✓ User1 is correctly a participant in this conversation")
        else:
            print("❌ ERROR: User1 can see a conversation they're not part of!")

    # Get all messages User1 can access
    messages = get_all_messages(token)

    # Verify messages are from conversations User1 is part of
    for i, msg in enumerate(messages):
        if i < 5:  # Limit output for readability
            print(f"\nMessage {i + 1} - ID: {msg['message_id']}")
            print(f"Conversation: {msg['conversation']}")
            print(f"Sender: {msg['sender']}")
            print(f"Receiver: {msg['receiver']}")

            # Find the conversation this message belongs to
            conv_match = [
                c for c in conversations if c["conversation_id"] == msg["conversation"]
            ]
            if conv_match:
                print("✓ Message belongs to a conversation User1 is part of")
            else:
                print(
                    "❌ ERROR: User1 can see a message from a conversation they're not part of!"
                )


def test_user2_access():
    """Test if User2 can only see their own conversations and messages."""
    print("\n--- Testing User2 Access ---")

    # Get token for User2
    token = get_token("testuser2@example.com", "testpass123")
    if not token:
        print("Failed to get token for User2")
        return

    # Get conversations for User2
    conversations = get_conversations(token)

    # For each conversation, verify User2 is a participant
    for i, conv in enumerate(conversations):
        print(f"\nConversation {i + 1} - ID: {conv['conversation_id']}")
        participants = [p["email"] for p in conv["participants"]]
        print(f"Participants: {participants}")

        if "testuser2@example.com" in participants:
            print("✓ User2 is correctly a participant in this conversation")
        else:
            print("❌ ERROR: User2 can see a conversation they're not part of!")

    # Get all messages User2 can access
    messages = get_all_messages(token)

    # Verify messages are from conversations User2 is part of
    for i, msg in enumerate(messages):
        if i < 5:  # Limit output for readability
            print(f"\nMessage {i + 1} - ID: {msg['message_id']}")
            print(f"Conversation: {msg['conversation']}")
            print(f"Sender: {msg['sender']}")
            print(f"Receiver: {msg['receiver']}")

            # Find the conversation this message belongs to
            conv_match = [
                c for c in conversations if c["conversation_id"] == msg["conversation"]
            ]
            if conv_match:
                print("✓ Message belongs to a conversation User2 is part of")
            else:
                print(
                    "❌ ERROR: User2 can see a message from a conversation they're not part of!"
                )


def test_cross_conversation_access():
    """Test that User2 cannot access User1's private conversations and messages."""
    print("\n--- Testing Cross-Conversation Access ---")

    # Get tokens for both users
    user1_token = get_token("testuser@example.com", "testpass123")
    user2_token = get_token("testuser2@example.com", "testpass123")

    if not user1_token or not user2_token:
        print("Failed to get tokens for both users")
        return

    # Get User1's conversations
    user1_conversations = get_conversations(user1_token)

    # Find a conversation that User1 is in but User2 is not
    user1_private_conv = None
    for conv in user1_conversations:
        participants = [p["email"] for p in conv["participants"]]
        if (
            "testuser@example.com" in participants
            and "testuser2@example.com" not in participants
        ):
            user1_private_conv = conv
            break

    if not user1_private_conv:
        print(
            "Could not find a private conversation for User1. Skipping cross-access test."
        )
        return

    # Try to access User1's private conversation with User2's token
    conv_id = user1_private_conv["conversation_id"]
    print(
        f"\nTrying to access User1's private conversation (ID: {conv_id}) with User2's token..."
    )

    url = f"{BASE_URL}/api/conversations/{conv_id}/messages/"
    headers = {"Authorization": f"Bearer {user2_token}"}

    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")

    if response.status_code in (403, 404):
        print("✓ Access correctly denied to User2")
    else:
        print(
            f"❌ ERROR: User2 was able to access User1's private conversation with status code {response.status_code}"
        )
        print(f"Response: {response.text}")


if __name__ == "__main__":
    print("=== Testing User Access Permissions ===\n")

    test_user1_access()
    test_user2_access()
    test_cross_conversation_access()

    print("\n=== Permission Tests Complete ===")
