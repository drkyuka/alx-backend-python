#!/usr/bin/env python3
"""
Direct API test for message permissions
"""

import requests
import json
import sys
from typing import Dict, Any

def get_token(base_url: str, email: str, password: str) -> Dict[str, str]:
    """Get JWT token using email and password."""
    url = f"{base_url}/api/token/"
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Token response: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Token error: {response.text}")
        return {}

def get_conversations(base_url: str, token: str) -> Dict[str, Any]:
    """Get all conversations for the authenticated user."""
    url = f"{base_url}/api/conversations/"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    print(f"Get conversations response: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Get conversations error: {response.text}")
        return []

def get_messages(base_url: str, token: str, conversation_id: str) -> Dict[str, Any]:
    """Get all messages for a specific conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    print(f"Get messages response: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Get messages error: {response.text}")
        return []

def main():
    base_url = "http://localhost:8001"
    
    # Get tokens for both users
    print("\n=== Getting tokens ===")
    user1_tokens = get_token(base_url, "testuser@example.com", "testpass123")
    user2_tokens = get_token(base_url, "testuser2@example.com", "testpass123")
    
    if not user1_tokens or not user2_tokens:
        print("Failed to get tokens. Exiting.")
        sys.exit(1)
    
    user1_token = user1_tokens["access"]
    user2_token = user2_tokens["access"]
    
    # Get conversations for user1
    print("\n=== User1's conversations ===")
    user1_conversations = get_conversations(base_url, user1_token)
    
    if not user1_conversations:
        print("No conversations found for User1")
        sys.exit(1)
    
    # Get conversations for user2
    print("\n=== User2's conversations ===")
    user2_conversations = get_conversations(base_url, user2_token)
    
    # Print conversation details
    print("\n=== Conversation details ===")
    for i, conv in enumerate(user1_conversations):
        conv_id = conv["conversation_id"]
        participants = [p["email"] for p in conv["participants"]]
        print(f"User1 Conversation {i+1}: {conv_id}")
        print(f"  Participants: {', '.join(participants)}")
    
    # Find a shared conversation
    shared_conv = None
    user1_only_conv = None
    
    for conv in user1_conversations:
        participants = [p["email"] for p in conv["participants"]]
        if "testuser2@example.com" in participants:
            shared_conv = conv
        else:
            user1_only_conv = conv
    
    # Test 1: User1 can access messages in shared conversation
    if shared_conv:
        print("\n=== Test 1: User1 can access messages in shared conversation ===")
        shared_conv_id = shared_conv["conversation_id"]
        messages = get_messages(base_url, user1_token, shared_conv_id)
        if messages:
            print(f"Success! User1 can view messages in shared conversation")
            print(f"Messages: {json.dumps(messages, indent=2)}")
        else:
            print("Failure: User1 should be able to view messages in shared conversation")
    
    # Test 2: User2 can access messages in shared conversation
    if shared_conv:
        print("\n=== Test 2: User2 can access messages in shared conversation ===")
        shared_conv_id = shared_conv["conversation_id"]
        messages = get_messages(base_url, user2_token, shared_conv_id)
        if messages:
            print(f"Success! User2 can view messages in shared conversation")
            print(f"Messages: {json.dumps(messages, indent=2)}")
        else:
            print("Failure: User2 should be able to view messages in shared conversation")
    
    # Test 3: User1 can access messages in user1-only conversation
    if user1_only_conv:
        print("\n=== Test 3: User1 can access messages in user1-only conversation ===")
        user1_only_conv_id = user1_only_conv["conversation_id"]
        messages = get_messages(base_url, user1_token, user1_only_conv_id)
        if messages:
            print(f"Success! User1 can view messages in user1-only conversation")
            print(f"Messages: {json.dumps(messages, indent=2)}")
        else:
            print("Failure: User1 should be able to view messages in user1-only conversation")
    
    # Test 4: User2 cannot access messages in user1-only conversation
    if user1_only_conv:
        print("\n=== Test 4: User2 cannot access messages in user1-only conversation ===")
        user1_only_conv_id = user1_only_conv["conversation_id"]
        messages = get_messages(base_url, user2_token, user1_only_conv_id)
        if not messages:
            print(f"Success! User2 cannot view messages in user1-only conversation")
        else:
            print("Failure: User2 should not be able to view messages in user1-only conversation")
            print(f"Messages: {json.dumps(messages, indent=2)}")

if __name__ == "__main__":
    main()
