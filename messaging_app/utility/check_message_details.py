#!/usr/bin/env python3
"""
Script to check the message details to understand the search results.
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


def get_message_details(token, message_id):
    """Get detailed information about a specific message."""
    url = f"{BASE_URL}/api/messages/{message_id}/"
    headers = {"Authorization": f"Bearer {token}"}

    print_info(f"Getting details for message {message_id}...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        message = response.json()
        print_success("Message details retrieved successfully")
        return message
    else:
        print_error(
            f"Failed to get message details: {response.status_code} - {response.text}"
        )
        return None


def main():
    """Main function to get message details."""
    print("\n" + "=" * 80)
    print("MESSAGE DETAILS CHECK")
    print("=" * 80)

    # Get authentication token
    token = get_token()
    if not token:
        print_error("Authentication failed. Cannot proceed.")
        sys.exit(1)

    # Message ID that's returning unexpected results
    message_id = "55ee20c6-7dc4-494b-8810-84a115e21bc6"

    # Get message details
    message = get_message_details(token, message_id)
    if not message:
        print_error("Failed to get message details. Cannot proceed.")
        sys.exit(1)

    # Print all details to understand why it's matching with "test"
    print("\n" + "=" * 80)
    print("MESSAGE DETAILS")
    print("=" * 80)

    for key, value in message.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 80)
    print("SEARCH ISSUE ANALYSIS")
    print("=" * 80)

    # Check if any field contains "test"
    found_test = False
    for key, value in message.items():
        if isinstance(value, str) and "test" in value.lower():
            print_info(f"Found 'test' in field '{key}': {value}")
            found_test = True

    if not found_test:
        print_error("Could not find 'test' in any message field!")
        print_info(
            "The search might be matching on related fields like sender/receiver emails."
        )

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
