#!/usr/bin/env python3
"""
Script to test permission checks in the messaging app:
1. Test that a non-participant cannot send messages to a conversation
2. Test that a non-participant cannot view messages in a conversation
3. Test that a participant cannot update another participant's messages
4. Test that a participant cannot delete another participant's messages
5. Test that a participant can view all messages in their conversations
"""

import argparse
import json
import sys
from typing import Dict, Any, List

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
        if hasattr(e, 'response') and e.response:
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
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        sys.exit(1)


def send_message(base_url: str, token: str, conversation_id: str, content: str) -> Dict[str, Any]:
    """Send a message to a specific conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "content": content
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return {
        "status_code": response.status_code,
        "response": response.json() if response.status_code < 300 else response.text
    }


def get_messages(base_url: str, token: str, conversation_id: str) -> Dict[str, Any]:
    """Get messages from a specific conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/"
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(url, headers=headers)
    return {
        "status_code": response.status_code,
        "response": response.json() if response.status_code < 300 else response.text
    }


def update_message(base_url: str, token: str, conversation_id: str, message_id: str, content: str) -> Dict[str, Any]:
    """Update a specific message."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/{message_id}/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "content": content
    }
    
    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    return {
        "status_code": response.status_code,
        "response": response.json() if response.status_code < 300 else response.text
    }


def delete_message(base_url: str, token: str, conversation_id: str, message_id: str) -> Dict[str, Any]:
    """Delete a specific message."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/{message_id}/"
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.delete(url, headers=headers)
    return {
        "status_code": response.status_code,
        "response": "" if response.status_code < 300 else response.text
    }


def test_non_participant_send_message(base_url: str, non_participant_token: str, conversation_id: str) -> None:
    """Test that a non-participant cannot send messages to a conversation."""
    print("\n=== Testing non-participant sending message ===")
    result = send_message(base_url, non_participant_token, conversation_id, "This message should be rejected")
    
    if result["status_code"] == 403:
        print("✓ Test passed: Non-participant was correctly forbidden from sending a message")
    else:
        print(f"✗ Test failed: Expected status code 403, got {result['status_code']}")
        print(f"Response: {result['response']}")


def test_non_participant_view_messages(base_url: str, non_participant_token: str, conversation_id: str) -> None:
    """Test that a non-participant cannot view messages in a conversation."""
    print("\n=== Testing non-participant viewing messages ===")
    result = get_messages(base_url, non_participant_token, conversation_id)
    
    if result["status_code"] == 403:
        print("✓ Test passed: Non-participant was correctly forbidden from viewing messages")
    else:
        print(f"✗ Test failed: Expected status code 403, got {result['status_code']}")
        print(f"Response: {result['response']}")


def test_participant_update_others_message(base_url: str, participant_token: str, conversation_id: str, other_user_message_id: str) -> None:
    """Test that a participant cannot update another participant's messages."""
    print("\n=== Testing participant updating another's message ===")
    result = update_message(base_url, participant_token, conversation_id, other_user_message_id, "Trying to modify someone else's message")
    
    if result["status_code"] == 403:
        print("✓ Test passed: Participant was correctly forbidden from updating another's message")
    else:
        print(f"✗ Test failed: Expected status code 403, got {result['status_code']}")
        print(f"Response: {result['response']}")


def test_participant_delete_others_message(base_url: str, participant_token: str, conversation_id: str, other_user_message_id: str) -> None:
    """Test that a participant cannot delete another participant's messages."""
    print("\n=== Testing participant deleting another's message ===")
    result = delete_message(base_url, participant_token, conversation_id, other_user_message_id)
    
    if result["status_code"] == 403:
        print("✓ Test passed: Participant was correctly forbidden from deleting another's message")
    else:
        print(f"✗ Test failed: Expected status code 403, got {result['status_code']}")
        print(f"Response: {result['response']}")


def test_participant_view_messages(base_url: str, participant_token: str, conversation_id: str) -> None:
    """Test that a participant can view all messages in their conversations."""
    print("\n=== Testing participant viewing messages ===")
    result = get_messages(base_url, participant_token, conversation_id)
    
    if result["status_code"] == 200:
        print(f"✓ Test passed: Participant can view messages (found {len(result['response'])} messages)")
    else:
        print(f"✗ Test failed: Expected status code 200, got {result['status_code']}")
        print(f"Response: {result['response']}")


def test_participant_send_and_update_own_message(base_url: str, participant_token: str, conversation_id: str) -> None:
    """Test that a participant can send and update their own message."""
    print("\n=== Testing participant sending and updating own message ===")
    
    # Send a message
    send_result = send_message(base_url, participant_token, conversation_id, "This is a test message")
    
    if send_result["status_code"] != 201:
        print(f"✗ Test failed: Could not send message, got status {send_result['status_code']}")
        print(f"Response: {send_result['response']}")
        return
    
    print("✓ Successfully sent a message")
    
    # Get the message ID
    message_id = send_result["response"]["message_id"]
    
    # Update the message
    update_result = update_message(base_url, participant_token, conversation_id, message_id, "This message was updated")
    
    if update_result["status_code"] == 200:
        print("✓ Test passed: Participant can update their own message")
    else:
        print(f"✗ Test failed: Expected status code 200, got {update_result['status_code']}")
        print(f"Response: {update_result['response']}")
    
    # Delete the message
    delete_result = delete_message(base_url, participant_token, conversation_id, message_id)
    
    if delete_result["status_code"] == 204:
        print("✓ Test passed: Participant can delete their own message")
    else:
        print(f"✗ Test failed: Expected status code 204, got {delete_result['status_code']}")
        print(f"Response: {delete_result['response']}")


def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test permission checks in the messaging app")
    parser.add_argument("--host", default="localhost", help="Host where the server is running")
    parser.add_argument("--port", default="8002", help="Port where the server is running")
    parser.add_argument("--user1-email", default="user1@example.com", help="Email for user 1 (participant)")
    parser.add_argument("--user1-password", default="test@123", help="Password for user 1")
    parser.add_argument("--user2-email", default="user2@example.com", help="Email for user 2 (participant)")
    parser.add_argument("--user2-password", default="test@123", help="Password for user 2")
    parser.add_argument("--user3-email", default="user3@example.com", help="Email for user 3 (non-participant)")
    parser.add_argument("--user3-password", default="test@123", help="Password for user 3")
    
    args = parser.parse_args()
    
    base_url = f"http://{args.host}:{args.port}"
    
    # Get tokens for all users
    print("Getting tokens for test users...")
    user1_token = get_token(base_url, args.user1_email, args.user1_password)["access"]
    user2_token = get_token(base_url, args.user2_email, args.user2_password)["access"]
    user3_token = get_token(base_url, args.user3_email, args.user3_password)["access"]
    
    # Get user1's conversations
    print("Getting conversations for user1...")
    user1_conversations = get_conversations(base_url, user1_token)
    
    if not user1_conversations:
        print("Error: No conversations found for user1. Please create a conversation first.")
        sys.exit(1)
    
    # Get the first conversation that includes user1 and user2 but not user3
    target_conversation = None
    for conversation in user1_conversations:
        participant_ids = [p["user_id"] for p in conversation["participants"]]
        
        # Check if we have at least 2 participants
        if len(participant_ids) >= 2:
            target_conversation = conversation
            break
    
    if not target_conversation:
        print("Error: Could not find a suitable conversation for testing. Please create a conversation with at least 2 participants.")
        sys.exit(1)
    
    conversation_id = target_conversation["conversation_id"]
    print(f"Using conversation {conversation_id} for testing")
    
    # Send a message from user2 to have a message ID for testing
    print("Sending a test message from user2...")
    user2_message = send_message(base_url, user2_token, conversation_id, "Test message from user2")
    
    if user2_message["status_code"] != 201:
        print(f"Error: Could not send message from user2. Status: {user2_message['status_code']}")
        print(f"Response: {user2_message['response']}")
        sys.exit(1)
    
    user2_message_id = user2_message["response"]["message_id"]
    
    # Run the tests
    test_participant_view_messages(base_url, user1_token, conversation_id)
    test_participant_send_and_update_own_message(base_url, user1_token, conversation_id)
    test_participant_update_others_message(base_url, user1_token, conversation_id, user2_message_id)
    test_participant_delete_others_message(base_url, user1_token, conversation_id, user2_message_id)
    test_non_participant_send_message(base_url, user3_token, conversation_id)
    test_non_participant_view_messages(base_url, user3_token, conversation_id)
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    main()
