#!/usr/bin/env python3
"""
Script to test both filtering and searching mechanisms for message content.
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


def test_search_mechanism(token, search_text="test"):
    """Test the search mechanism for finding messages."""
    print_info(f"Testing SEARCH mechanism with text '{search_text}'...")

    url = f"{BASE_URL}/api/messages/?search={search_text}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Handle pagination
        if isinstance(data, dict) and "results" in data:
            messages = data["results"]
        else:
            messages = data

        print_success(f"Search found {len(messages)} messages")

        # Print details of found messages
        for idx, msg in enumerate(messages):
            print(f"\nSearch Result #{idx + 1}:")
            print(f"ID: {msg.get('message_id')}")
            print(f"Content: '{msg.get('content')}'")
            print(f"Sender: {msg.get('sender')}")
            print(f"Receiver: {msg.get('receiver')}")
            print(f"Sent at: {msg.get('sent_at')}")
            print("-" * 40)

        return len(messages)
    else:
        print_error(f"Search failed: {response.status_code} - {response.text}")
        return 0


def test_filter_mechanism(token, search_text="test"):
    """Test the filter mechanism for finding messages."""
    print_info(f"Testing FILTER mechanism with text '{search_text}'...")

    url = f"{BASE_URL}/api/messages/?content={search_text}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Handle pagination
        if isinstance(data, dict) and "results" in data:
            messages = data["results"]
        else:
            messages = data

        print_success(f"Filter found {len(messages)} messages")

        # Print details of found messages
        for idx, msg in enumerate(messages):
            print(f"\nFilter Result #{idx + 1}:")
            print(f"ID: {msg.get('message_id')}")
            print(f"Content: '{msg.get('content')}'")
            print(f"Sender: {msg.get('sender')}")
            print(f"Receiver: {msg.get('receiver')}")
            print(f"Sent at: {msg.get('sent_at')}")
            print("-" * 40)

        return len(messages)
    else:
        print_error(f"Filter failed: {response.status_code} - {response.text}")
        return 0


def main():
    """Main function to test both filtering mechanisms."""
    print("\n" + "=" * 80)
    print("FILTERING MECHANISMS TEST")
    print("=" * 80)

    # Get authentication token
    token = get_token()
    if not token:
        print_error("Authentication failed. Cannot proceed.")
        sys.exit(1)

    # Test both mechanisms
    print("\n" + "=" * 80)
    print("TESTING WITH 'test'")
    print("=" * 80)

    search_count = test_search_mechanism(token, "test")
    filter_count = test_filter_mechanism(token, "test")

    # Now test with a more specific term that should only be in content
    print("\n" + "=" * 80)
    print("TESTING WITH 'user1'")
    print("=" * 80)

    search_count_user = test_search_mechanism(token, "user1")
    filter_count_user = test_filter_mechanism(token, "user1")

    # Provide a summary of results
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"'test' search results: {search_count}")
    print(f"'test' filter results: {filter_count}")
    print(f"'user1' search results: {search_count_user}")
    print(f"'user1' filter results: {filter_count_user}")

    # Provide recommendation
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)

    if filter_count > 0 and all(
        filter_count <= c
        for c in [search_count, search_count_user, filter_count_user]
        if c > 0
    ):
        print_success(
            "The FILTER mechanism (content=) appears to be more specific and accurate"
        )
        print_info("Use '?content=text' for exact content filtering")
    elif search_count > 0:
        print_success("The SEARCH mechanism (search=) appears to work better")
        print_info("Use '?search=text' for broader search capabilities")
    else:
        print_error(
            "Both mechanisms returned unexpected results, further investigation needed"
        )

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
