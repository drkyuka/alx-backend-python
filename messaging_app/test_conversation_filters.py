#!/usr/bin/env python3
"""
Test script to demonstrate filtering conversations in the messaging app.
This script demonstrates how to:
1. Filter conversations by participant
2. Filter conversations by creation date range
3. Filter conversations by specific participants
"""

import datetime
import json
from urllib.parse import urlencode

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


def get_users(token):
    """Get a list of users to use for filtering."""
    url = f"{BASE_URL}/api/users/"
    headers = {"Authorization": f"Bearer {token}"}

    print("Fetching users...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        users = response.json()
        print(f"Found {len(users)} users")
        return users
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


def filter_conversations(token, **filter_params):
    """Filter conversations using the provided parameters."""
    # Convert parameters to URL query string
    query_string = urlencode(filter_params)

    url = f"{BASE_URL}/api/conversations/?{query_string}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"\nFiltering conversations with parameters: {filter_params}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        conversations = response.json()

        # Handle pagination - results might be in 'results' field
        if isinstance(conversations, dict) and "results" in conversations:
            result_count = len(conversations["results"])
            print(f"Found {result_count} conversations matching the filter")
            return conversations["results"]
        else:
            print(f"Found {len(conversations)} conversations matching the filter")
            return conversations
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


def print_conversation_summary(conversations):
    """Print a summary of the filtered conversations."""
    if not conversations:
        print("No conversations found matching the filter")
        return

    print("\nConversation Summary:")
    print("-" * 80)
    for idx, conv in enumerate(conversations):
        print(f"{idx + 1}. Conversation ID: {conv.get('conversation_id')}")
        participants = conv.get("participants", [])
        participant_emails = [p.get("email") for p in participants]
        print(f"   Participants: {', '.join(participant_emails)}")
        print(f"   Message Count: {conv.get('message_count', 'N/A')}")
        print("-" * 80)


def main():
    """Main function demonstrating conversation filtering."""
    # Get token for authentication
    token = get_token("testuser@example.com", "testpass123")
    if not token:
        print("Failed to get token. Exiting.")
        return

    # Get users for filtering
    users = get_users(token)
    if not users:
        print("Failed to get users. Using example filters instead.")
        user_id1 = "example-user-id-1"  # Replace with actual user ID
        user_id2 = "example-user-id-2"  # Replace with actual user ID
    else:
        # Use the first two users for filtering examples
        user_id1 = users[0]["user_id"]
        user_id2 = users[1]["user_id"] if len(users) > 1 else user_id1

    # Example 1: Filter conversations by participant
    participant_filtered_conversations = filter_conversations(
        token, participant=user_id1
    )
    print_conversation_summary(participant_filtered_conversations)

    # Example 2: Filter conversations by creation date range (last week)
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    one_week_ago_str = one_week_ago.strftime("%Y-%m-%dT%H:%M:%S")

    date_filtered_conversations = filter_conversations(
        token, created_after=one_week_ago_str
    )
    print_conversation_summary(date_filtered_conversations)

    # Example 3: Filter conversations by specific participants (conversations with both users)
    specific_participants_filtered_conversations = filter_conversations(
        token, specific_participants=f"{user_id1},{user_id2}"
    )
    print_conversation_summary(specific_participants_filtered_conversations)

    # Example 4: Combine multiple filters
    combined_filtered_conversations = filter_conversations(
        token, participant=user_id1, created_after=one_week_ago_str
    )
    print_conversation_summary(combined_filtered_conversations)


if __name__ == "__main__":
    main()
