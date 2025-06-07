#!/usr/bin/env python3
"""
Test script to demonstrate filtering in the messaging app.
This script demonstrates how to:
1. Filter messages by time range
2. Filter messages by sender/receiver
3. Filter messages by participant (conversations a user is part of)
4. Filter messages by content
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


def filter_messages(token, **filter_params):
    """Filter messages using the provided parameters."""
    # Convert parameters to URL query string
    query_string = urlencode(filter_params)

    url = f"{BASE_URL}/api/messages/?{query_string}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"\nFiltering messages with parameters: {filter_params}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json()

        # Handle pagination - results might be in 'results' field
        if isinstance(messages, dict) and "results" in messages:
            result_count = len(messages["results"])
            print(f"Found {result_count} messages matching the filter")
            return messages["results"]
        else:
            print(f"Found {len(messages)} messages matching the filter")
            return messages
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


def print_message_summary(messages):
    """Print a summary of the filtered messages."""
    if not messages:
        print("No messages found matching the filter")
        return

    print("\nMessage Summary:")
    print("-" * 80)
    for idx, msg in enumerate(messages):
        print(f"{idx + 1}. Message ID: {msg.get('message_id')}")
        print(f"   Content: {msg.get('content')}")
        print(f"   Sender: {msg.get('sender')}")
        print(f"   Sent at: {msg.get('sent_at')}")
        print(f"   Conversation: {msg.get('conversation')}")
        print("-" * 80)


def main():
    """Main function demonstrating message filtering."""
    # Get token for authentication
    token = get_token("testuser@example.com", "testpass123")
    if not token:
        print("Failed to get token. Exiting.")
        return

    # Example 1: Filter messages by time range (last 24 hours)
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%dT%H:%M:%S")

    time_filtered_messages = filter_messages(token, sent_after=yesterday_str)
    print_message_summary(time_filtered_messages)

    # Example 2: Filter messages by sender
    # Note: You need to replace this with an actual sender ID from your database
    sender_filtered_messages = filter_messages(
        token,
        sender="user-id-here",  # Replace with an actual user ID
    )
    print_message_summary(sender_filtered_messages)

    # Example 3: Filter messages by participant (all messages in conversations where a specific user is a participant)
    # Note: You need to replace this with an actual user ID from your database
    participant_filtered_messages = filter_messages(
        token,
        participant="user-id-here",  # Replace with an actual user ID
    )
    print_message_summary(participant_filtered_messages)

    # Example 4: Filter messages by content (containing specific text)
    content_filtered_messages = filter_messages(
        token,
        content="hello",  # Replace with text you want to search for
    )
    print_message_summary(content_filtered_messages)

    # Example 5: Combine multiple filters
    combined_filtered_messages = filter_messages(
        token, sent_after=yesterday_str, content="hello"
    )
    print_message_summary(combined_filtered_messages)


if __name__ == "__main__":
    main()
