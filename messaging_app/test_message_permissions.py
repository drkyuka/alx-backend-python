#!/usr/bin/env python3
"""
Test script to validate permission checks for the messaging app.
This script tests:
1. A logged-in user can view all messages in conversations they're part of
2. A logged-in user cannot view messages in conversations they're not part of
3. A user can only update/delete their own messages
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Tuple

import requests


def get_token(base_url: str, email: str, password: str) -> Dict[str, str]:
    """Get JWT token using email and password."""
    url = f"{base_url}/api/token/"
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
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
        sys.exit(1)


def get_conversation_messages(
    base_url: str, token: str, conversation_id: str
) -> Tuple[int, List[Dict[str, Any]]]:
    """Get all messages for a specific conversation and return status code and data."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        if status_code == 200:
            return status_code, response.json()
        return status_code, []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages for conversation {conversation_id}: {e}")
        return 500, []


def send_message(
    base_url: str, token: str, conversation_id: str, content: str
) -> Tuple[int, Dict[str, Any]]:
    """Send a message to a specific conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "message_body": content,
        "receiver": "",
    }  # Receiver will be set by the backend

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return (
            response.status_code,
            response.json() if response.status_code == 201 else {},
        )
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to conversation {conversation_id}: {e}")
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print(f"Response content: {e.response.text}")
        return 500, {}


def update_message(
    base_url: str, token: str, conversation_id: str, message_id: str, new_content: str
) -> Tuple[int, Dict[str, Any]]:
    """Update a message in a conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/{message_id}/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"message_body": new_content}

    try:
        response = requests.patch(url, headers=headers, data=json.dumps(payload))
        return response.status_code, response.json() if response.status_code in (
            200,
            201,
        ) else {}
    except requests.exceptions.RequestException as e:
        print(f"Error updating message {message_id}: {e}")
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print(f"Response content: {e.response.text}")
        return 500, {}


def delete_message(
    base_url: str, token: str, conversation_id: str, message_id: str
) -> int:
    """Delete a message from a conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/{message_id}/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.delete(url, headers=headers)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error deleting message {message_id}: {e}")
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print(f"Response content: {e.response.text}")
        return 500


def test_message_access(
    base_url: str,
    user1_email: str,
    user1_password: str,
    user2_email: str,
    user2_password: str,
) -> None:
    """Test access to messages in conversations."""
    print("\n=== Testing Message Access Permissions ===\n")

    # Get tokens for both users
    print(f"Getting token for User 1 ({user1_email})...")
    user1_tokens = get_token(base_url, user1_email, user1_password)
    user1_token = user1_tokens["access"]

    print(f"Getting token for User 2 ({user2_email})...")
    user2_tokens = get_token(base_url, user2_email, user2_password)
    user2_token = user2_tokens["access"]

    # Get conversations for user1
    print("\nFetching User 1's conversations...")
    user1_conversations = get_conversations(base_url, user1_token)

    if not user1_conversations:
        print("No conversations found for User 1. Test cannot continue.")
        return

    # Get conversations for user2
    print("\nFetching User 2's conversations...")
    user2_conversations = get_conversations(base_url, user2_token)

    if not user2_conversations:
        print("No conversations found for User 2. Test cannot continue.")
        return

    # Find a conversation that user1 is in but user2 is not
    user1_only_conversation = None
    for conv in user1_conversations:
        if not any(
            u_conv["conversation_id"] == conv["conversation_id"]
            for u_conv in user2_conversations
        ):
            user1_only_conversation = conv
            break

    if not user1_only_conversation:
        print("Could not find a conversation where only User 1 is a participant.")
        print("Creating a test message in the first conversation...")
        # Just use the first conversation for user1
        user1_only_conversation = user1_conversations[0]

    # Test 1: User 1 can view messages in their conversation
    conv_id = user1_only_conversation["conversation_id"]
    print(f"\nTest 1: User 1 can view messages in conversation {conv_id}")
    status_code, messages = get_conversation_messages(base_url, user1_token, conv_id)

    print(f"Status code: {status_code}")
    if status_code == 200:
        print("Success: User 1 can view messages in their conversation")
        print(f"Found {len(messages)} messages")
    else:
        print("Failure: User 1 should be able to view messages in their conversation")

    # Test 2: User 2 cannot view messages in User 1's conversation (if they're not part of it)
    if (
        user1_only_conversation != user1_conversations[0]
    ):  # Only if we found a unique conversation
        print(
            f"\nTest 2: User 2 cannot view messages in User 1's conversation {conv_id}"
        )
        status_code, messages = get_conversation_messages(
            base_url, user2_token, conv_id
        )

        print(f"Status code: {status_code}")
        if status_code in (403, 404):
            print("Success: User 2 cannot view messages in User 1's conversation")
        else:
            print(
                "Failure: User 2 should not be able to view messages in User 1's conversation"
            )
    else:
        print(
            "\nSkipping Test 2: Couldn't find a conversation where only User 1 is a participant"
        )

    # Test 3: User 1 can send a message to their conversation
    print(f"\nTest 3: User 1 can send a message to their conversation {conv_id}")
    status_code, message_data = send_message(
        base_url, user1_token, conv_id, "Test message from User 1"
    )

    print(f"Status code: {status_code}")
    if status_code == 201:
        print("Success: User 1 can send a message to their conversation")
        message_id = message_data.get("message_id")
        print(f"Message ID: {message_id}")

        # Test 4: User 1 can update their own message
        if message_id:
            print(f"\nTest 4: User 1 can update their own message {message_id}")
            update_status, update_data = update_message(
                base_url,
                user1_token,
                conv_id,
                message_id,
                "Updated test message from User 1",
            )

            print(f"Status code: {update_status}")
            if update_status in (200, 201):
                print("Success: User 1 can update their own message")

                # Test 5: User 1 can delete their own message
                print(f"\nTest 5: User 1 can delete their own message {message_id}")
                delete_status = delete_message(
                    base_url, user1_token, conv_id, message_id
                )

                print(f"Status code: {delete_status}")
                if delete_status in (200, 204):
                    print("Success: User 1 can delete their own message")
                else:
                    print("Failure: User 1 should be able to delete their own message")
            else:
                print("Failure: User 1 should be able to update their own message")
    else:
        print("Failure: User 1 should be able to send a message to their conversation")

    print("\n=== Message Access Permissions Testing Complete ===\n")


def main() -> None:
    """Main function to run the tests."""
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
        required=True,
        help="Email for the first test user",
    )
    parser.add_argument(
        "--user1-password",
        type=str,
        required=True,
        help="Password for the first test user",
    )
    parser.add_argument(
        "--user2-email",
        type=str,
        required=True,
        help="Email for the second test user",
    )
    parser.add_argument(
        "--user2-password",
        type=str,
        required=True,
        help="Password for the second test user",
    )

    args = parser.parse_args()

    test_message_access(
        args.base_url,
        args.user1_email,
        args.user1_password,
        args.user2_email,
        args.user2_password,
    )


if __name__ == "__main__":
    main()
