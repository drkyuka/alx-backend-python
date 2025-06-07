#!/usr/bin/env python3
"""
Simple permission test script for the messaging app.
"""

import json
import sys

import requests


def get_token(base_url, email, password):
    """Get JWT token using email and password."""
    url = f"{base_url}/api/token/"
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    print(f"Sending request to {url} with payload: {json.dumps(payload)}")
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")

    if response.status_code == 200:
        return response.json()
    else:
        print("Error: Failed to get token")
        return None


def get_conversations(base_url, token):
    """Get all conversations for the authenticated user."""
    url = f"{base_url}/api/conversations/"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Fetching conversations from {url}")
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return []


def get_messages(base_url, token):
    """Get all messages the user has access to."""
    url = f"{base_url}/api/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Fetching messages from {url}")
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return []


def get_conversation_messages(base_url, token, conversation_id):
    """Get all messages for a specific conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Fetching messages for conversation {conversation_id}")
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None


def main():
    """Main function to run the script."""
    base_url = "http://localhost:8001"

    # Test User 1
    print("\n=== Testing User 1 ===")
    user1_email = "testuser@example.com"
    user1_password = "testpass123"

    # Get token for User 1
    print(f"\nGetting token for User 1 ({user1_email})...")
    user1_tokens = get_token(base_url, user1_email, user1_password)

    if not user1_tokens:
        print("Failed to get token for User 1. Exiting.")
        sys.exit(1)

    user1_token = user1_tokens["access"]

    # Get conversations for User 1
    print("\nFetching User 1's conversations...")
    user1_conversations = get_conversations(base_url, user1_token)

    print(f"\nUser 1 has {len(user1_conversations)} conversations")
    for i, conv in enumerate(user1_conversations):
        conv_id = conv["conversation_id"]
        participants = [p["email"] for p in conv["participants"]]
        print(f"\nConversation {i + 1}: {conv_id}")
        print(f"Participants: {', '.join(participants)}")

        # Verify User 1 is in the conversation
        if user1_email in participants:
            print("✓ User 1 is a participant in this conversation")
        else:
            print("❌ ERROR: User 1 can see a conversation they're not part of!")

    # Get all messages User 1 has access to
    print("\nFetching all messages User 1 has access to...")
    user1_messages = get_messages(base_url, user1_token)
    print(f"\nUser 1 has access to {len(user1_messages)} messages globally")

    # Test User 2
    print("\n\n=== Testing User 2 ===")
    user2_email = "testuser2@example.com"
    user2_password = "testpass123"

    # Get token for User 2
    print(f"\nGetting token for User 2 ({user2_email})...")
    user2_tokens = get_token(base_url, user2_email, user2_password)

    if not user2_tokens:
        print("Failed to get token for User 2. Exiting.")
        sys.exit(1)

    user2_token = user2_tokens["access"]

    # Get conversations for User 2
    print("\nFetching User 2's conversations...")
    user2_conversations = get_conversations(base_url, user2_token)

    print(f"\nUser 2 has {len(user2_conversations)} conversations")
    for i, conv in enumerate(user2_conversations):
        conv_id = conv["conversation_id"]
        participants = [p["email"] for p in conv["participants"]]
        print(f"\nConversation {i + 1}: {conv_id}")
        print(f"Participants: {', '.join(participants)}")

        # Verify User 2 is in the conversation
        if user2_email in participants:
            print("✓ User 2 is a participant in this conversation")
        else:
            print("❌ ERROR: User 2 can see a conversation they're not part of!")

    # Get all messages User 2 has access to
    print("\nFetching all messages User 2 has access to...")
    user2_messages = get_messages(base_url, user2_token)
    print(f"\nUser 2 has access to {len(user2_messages)} messages globally")

    # Test cross-user access permissions
    print("\n\n=== Testing Cross-User Access ===")

    # Check if User 1 has any private conversations (where User 2 is not a participant)
    user1_private_convs = []
    for conv in user1_conversations:
        if user2_email not in [p["email"] for p in conv["participants"]]:
            user1_private_convs.append(conv)

    # Test User 2's access to User 1's private conversations
    if user1_private_convs:
        print(f"\nFound {len(user1_private_convs)} private conversations for User 1")
        for i, conv in enumerate(user1_private_convs):
            conv_id = conv["conversation_id"]
            print(
                f"\nTesting User 2's access to User 1's private conversation {i + 1}: {conv_id}"
            )

            # User 2 should NOT be able to access messages in this conversation
            url = f"{base_url}/api/conversations/{conv_id}/messages/"
            headers = {"Authorization": f"Bearer {user2_token}"}

            response = requests.get(url, headers=headers)
            status_code = response.status_code

            print(f"Response status code: {status_code}")
            if status_code in (403, 404):
                print(
                    "✓ User 2 correctly denied access to User 1's private conversation"
                )
            else:
                print(
                    f"❌ ERROR: User 2 got unexpected status code ({status_code}) when accessing User 1's private conversation!"
                )
                print(f"Response: {response.text}")
    else:
        print("\nNo private conversations found for User 1 to test cross-user access")


if __name__ == "__main__":
    main()
