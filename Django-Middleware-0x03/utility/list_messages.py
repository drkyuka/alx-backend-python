#!/usr/bin/env python3
"""
Script to list all messages and their content to understand the search results.
"""

import json
import sys

import requests

# Base URL for the API
BASE_URL = "http://localhost:8001"
# Test user credentials
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "testpass123"

# ANSI colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_success(message):
    """Print a success message."""
    print(f"{GREEN}✓ SUCCESS: {message}{RESET}")


def print_error(message):
    """Print an error message."""
    print(f"{RED}✗ ERROR: {message}{RESET}")


def print_info(message):
    """Print an info message."""
    print(f"{YELLOW}ℹ INFO: {message}{RESET}")


def get_token():
    """Get a JWT token for authentication."""
    url = f"{BASE_URL}/api/token/"
    payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    headers = {"Content-Type": "application/json"}

    print_info(f"Getting token for {TEST_EMAIL}...")
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        token_data = response.json()
        print_success("Token obtained successfully")
        return token_data["access"]
    else:
        print_error(f"Failed to get token: {response.status_code} - {response.text}")
        return None


def get_all_messages(token):
    """Get all messages."""
    url = f"{BASE_URL}/api/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    print_info("Getting all messages...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Handle pagination
        if isinstance(data, dict) and "results" in data:
            messages = data["results"]
        else:
            messages = data

        print_success(f"Retrieved {len(messages)} messages")
        return messages
    else:
        print_error(f"Failed to get messages: {response.status_code} - {response.text}")
        return []


def main():
    """Main function to list all messages."""
    print("\n" + "=" * 80)
    print("MESSAGE LISTING")
    print("=" * 80)

    # Get authentication token
    token = get_token()
    if not token:
        print_error("Authentication failed. Cannot proceed.")
        sys.exit(1)

    # Get all messages
    messages = get_all_messages(token)
    if not messages:
        print_error("No messages found. Cannot proceed.")
        sys.exit(1)

    # Print details of all messages
    print("\n" + "=" * 80)
    print("ALL MESSAGES")
    print("=" * 80)

    for idx, msg in enumerate(messages):
        print(f"\nMessage #{idx + 1}:")
        print(f"ID: {msg.get('message_id')}")
        print(f"Content: '{msg.get('content')}'")
        print(f"Sender: {msg.get('sender')}")
        print(f"Receiver: {msg.get('receiver')}")
        print(f"Sent at: {msg.get('sent_at')}")
        print("-" * 40)

    print("\n" + "=" * 80)
    print("SEARCH TEST")
    print("=" * 80)

    # Now test search with "test"
    search_text = "test"
    url = f"{BASE_URL}/api/messages/?search={search_text}"
    headers = {"Authorization": f"Bearer {token}"}

    print_info(f"Searching for messages containing '{search_text}'...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Handle pagination
        if isinstance(data, dict) and "results" in data:
            search_results = data["results"]
        else:
            search_results = data

        print_success(
            f"Found {len(search_results)} messages containing '{search_text}'"
        )

        for idx, msg in enumerate(search_results):
            print(f"\nSearch Result #{idx + 1}:")
            print(f"ID: {msg.get('message_id')}")
            print(f"Content: '{msg.get('content')}'")
            print(f"Sender: {msg.get('sender')}")
            print(f"Receiver: {msg.get('receiver')}")
            print(f"Sent at: {msg.get('sent_at')}")
            print("-" * 40)
    else:
        print_error(f"Search failed: {response.status_code} - {response.text}")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
