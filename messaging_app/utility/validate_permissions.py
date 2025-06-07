#!/usr/bin/env python3
"""
Comprehensive permission validation script for the messaging app.
This script tests:
1. Users can only see their own conversations
2. Users can only see messages in conversations they're part of
3. Users cannot see other users' private conversations
4. Users cannot see messages in conversations they're not part of
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

import requests


def get_token(base_url: str, email: str, password: str) -> Dict[str, str]:
    """Get JWT token using email and password."""
    url = f"{base_url}/api/token/"
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    try:
        print(f"Sending request to {url} with payload: {json.dumps(payload)}")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)


def get_conversations(base_url: str, token: str) -> List[Dict[str, Any]]:
    """Get all conversations for the authenticated user."""
    url = f"{base_url}/api/conversations/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching conversations: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        return []


def get_messages(base_url: str, token: str) -> List[Dict[str, Any]]:
    """Get all messages the user has access to."""
    url = f"{base_url}/api/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        return []


def get_conversation_messages(
    base_url: str, token: str, conversation_id: str
) -> Optional[List[Dict[str, Any]]]:
    """Get all messages for a specific conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages for conversation {conversation_id}: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def create_user(
    base_url: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    phone_number: str,
) -> Optional[Dict[str, Any]]:
    """Create a new user for testing."""
    url = f"{base_url}/api/users/"
    headers = {"Content-Type": "application/json"}
    payload = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating user: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def create_conversation(
    base_url: str, token: str, participant_ids: List[str]
) -> Optional[Dict[str, Any]]:
    """Create a new conversation with specified participants."""
    url = f"{base_url}/api/conversations/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"participant_ids": participant_ids}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating conversation: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def send_message(
    base_url: str, token: str, conversation_id: str, receiver_id: str, content: str
) -> Optional[Dict[str, Any]]:
    """Send a message to a conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"receiver": receiver_id, "content": content}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def test_conversation_permissions(
    base_url: str, user1_credentials: Dict[str, str], user2_credentials: Dict[str, str]
) -> None:
    """
    Test that a user can only see their own conversations.
    """
    print("\n=== Testing Conversation Visibility Permissions ===\n")

    # Get tokens for both users
    print(f"Getting token for User 1 ({user1_credentials['email']})...")
    user1_token = get_token(
        base_url, user1_credentials["email"], user1_credentials["password"]
    )["access"]

    print(f"Getting token for User 2 ({user2_credentials['email']})...")
    user2_token = get_token(
        base_url, user2_credentials["email"], user2_credentials["password"]
    )["access"]

    # Get conversations for both users
    print("\nFetching User 1's conversations...")
    user1_conversations = get_conversations(base_url, user1_token)
    print(f"User 1 has {len(user1_conversations)} conversations")

    print("\nFetching User 2's conversations...")
    user2_conversations = get_conversations(base_url, user2_token)
    print(f"User 2 has {len(user2_conversations)} conversations")

    # Check if conversations are properly filtered
    if len(user1_conversations) > 0:
        print("\nChecking if User 1's conversations are properly filtered...")
        for i, conv in enumerate(user1_conversations):
            participants = [p["email"] for p in conv["participants"]]
            print(f"Conversation {i + 1} participants: {', '.join(participants)}")
            if user1_credentials["email"] not in participants:
                print("❌ ERROR: User 1 can see a conversation they're not part of!")
            else:
                print("✓ User 1 is correctly part of this conversation")

    if len(user2_conversations) > 0:
        print("\nChecking if User 2's conversations are properly filtered...")
        for i, conv in enumerate(user2_conversations):
            participants = [p["email"] for p in conv["participants"]]
            print(f"Conversation {i + 1} participants: {', '.join(participants)}")
            if user2_credentials["email"] not in participants:
                print("❌ ERROR: User 2 can see a conversation they're not part of!")
            else:
                print("✓ User 2 is correctly part of this conversation")

    print("\n=== Conversation Visibility Test Complete ===\n")


def test_message_permissions(
    base_url: str, user1_credentials: Dict[str, str], user2_credentials: Dict[str, str]
) -> None:
    """
    Test that a user can only see messages in conversations they're part of.
    """
    print("\n=== Testing Message Visibility Permissions ===\n")

    # Get tokens for both users
    print(f"Getting token for User 1 ({user1_credentials['email']})...")
    user1_token = get_token(
        base_url, user1_credentials["email"], user1_credentials["password"]
    )["access"]

    print(f"Getting token for User 2 ({user2_credentials['email']})...")
    user2_token = get_token(
        base_url, user2_credentials["email"], user2_credentials["password"]
    )["access"]

    # Get all messages for both users
    print("\nFetching all accessible messages for User 1...")
    user1_messages = get_messages(base_url, user1_token)
    print(f"User 1 can access {len(user1_messages)} messages")

    print("\nFetching all accessible messages for User 2...")
    user2_messages = get_messages(base_url, user2_token)
    print(f"User 2 can access {len(user2_messages)} messages")

    # Get conversations for User 1
    print("\nFetching User 1's conversations...")
    user1_conversations = get_conversations(base_url, user1_token)

    # Test message access for each conversation
    for i, conv in enumerate(user1_conversations):
        conv_id = conv["conversation_id"]
        participants = [p["email"] for p in conv["participants"]]

        print(f"\nTesting message access for conversation {i + 1} (ID: {conv_id})")
        print(f"Participants: {', '.join(participants)}")

        # User 1 should be able to access messages
        print("Testing User 1's access to messages...")
        user1_conv_messages = get_conversation_messages(base_url, user1_token, conv_id)

        if user1_conv_messages is not None:
            print(
                f"✓ User 1 can access messages in this conversation ({len(user1_conv_messages)} messages)"
            )
        else:
            print("❌ ERROR: User 1 cannot access messages in their own conversation!")

        # Check User 2's access based on participation
        print("Testing User 2's access to messages...")
        if user2_credentials["email"] in participants:
            # User 2 should be able to access messages
            user2_conv_messages = get_conversation_messages(
                base_url, user2_token, conv_id
            )
            if user2_conv_messages is not None:
                print(
                    f"✓ User 2 can access messages in shared conversation ({len(user2_conv_messages)} messages)"
                )
            else:
                print(
                    "❌ ERROR: User 2 cannot access messages in a conversation they're part of!"
                )
        else:
            # User 2 should NOT be able to access messages
            try:
                response = requests.get(
                    f"{base_url}/api/conversations/{conv_id}/messages/",
                    headers={"Authorization": f"Bearer {user2_token}"},
                )
                if response.status_code in (403, 404):
                    print(
                        f"✓ User 2 correctly denied access to conversation they're not part of (Status: {response.status_code})"
                    )
                else:
                    print(
                        f"❌ ERROR: User 2 got unexpected status code ({response.status_code}) when accessing messages in a conversation they're not part of!"
                    )
                    print(f"Response: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Error testing User 2's access: {e}")

    print("\n=== Message Visibility Test Complete ===\n")


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Test permissions for messaging app")
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8001",
        help="Base URL of the API",
    )
    parser.add_argument(
        "--user1-email",
        type=str,
        default="testuser@example.com",
        help="Email for test user 1",
    )
    parser.add_argument(
        "--user1-password",
        type=str,
        default="testpass123",
        help="Password for test user 1",
    )
    parser.add_argument(
        "--user2-email",
        type=str,
        default="testuser2@example.com",
        help="Email for test user 2",
    )
    parser.add_argument(
        "--user2-password",
        type=str,
        default="testpass123",
        help="Password for test user 2",
    )

    args = parser.parse_args()

    user1_credentials = {
        "email": args.user1_email,
        "password": args.user1_password,
    }

    user2_credentials = {
        "email": args.user2_email,
        "password": args.user2_password,
    }

    # Test conversation permissions
    test_conversation_permissions(args.base_url, user1_credentials, user2_credentials)

    # Test message permissions
    test_message_permissions(args.base_url, user1_credentials, user2_credentials)


if __name__ == "__main__":
    main()
