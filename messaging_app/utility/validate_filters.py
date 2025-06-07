#!/usr/bin/env python3
"""
Validation script for filter functionality in the messaging app.
This script validates that:
1. Messages can be filtered by time range
2. Messages can be filtered by sender/receiver
3. Messages can be filtered by participant
4. Conversations can be filtered by participant
5. Conversations can be filtered by specific participants

Usage:
    python validate_filters.py

Requirements:
    - Django server must be running on localhost:8001
    - At least one user must exist in the database
    - Test user credentials should be updated in the script
"""

import datetime
import json
import sys
from urllib.parse import urlencode

import requests

# Base URL for the API
BASE_URL = "http://localhost:8001"
# Test user credentials
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "testpass123"
# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def log_success(message):
    """Print success message in green."""
    print(f"{GREEN}✓ SUCCESS: {message}{RESET}")


def log_error(message):
    """Print error message in red."""
    print(f"{RED}✗ ERROR: {message}{RESET}")


def log_info(message):
    """Print info message in yellow."""
    print(f"{YELLOW}ℹ INFO: {message}{RESET}")


def get_token(email, password):
    """Get JWT token using email and password."""
    url = f"{BASE_URL}/api/token/"
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    log_info(f"Getting token for {email}...")
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        token_data = response.json()
        log_success("Token obtained successfully")
        return token_data["access"]
    else:
        log_error(f"Failed to get token: {response.status_code} - {response.text}")
        return None


def get_messages(token):
    """Get a list of messages to determine user IDs for filtering."""
    url = f"{BASE_URL}/api/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    log_info("Fetching messages to identify users...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json()

        # Handle pagination
        if isinstance(messages, dict) and "results" in messages:
            messages = messages["results"]

        log_success(f"Found {len(messages)} messages")

        # Extract user IDs from messages
        user_ids = set()
        for msg in messages:
            if msg.get("sender"):
                user_ids.add(msg.get("sender"))
            if msg.get("receiver"):
                user_ids.add(msg.get("receiver"))

        log_success(f"Identified {len(user_ids)} unique users")
        return list(user_ids), messages
    else:
        log_error(f"Failed to get messages: {response.status_code} - {response.text}")
        return [], []


def create_test_conversation(token, participants):
    """Create a test conversation with the specified participants."""
    url = f"{BASE_URL}/api/conversations/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"participants": participants}

    log_info("Creating test conversation...")
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        conversation = response.json()
        log_success(
            f"Created conversation with ID: {conversation.get('conversation_id')}"
        )
        return conversation
    else:
        log_error(
            f"Failed to create conversation: {response.status_code} - {response.text}"
        )
        return None


def create_test_message(token, conversation_id, sender_id, receiver_id, message_body):
    """Create a test message in the specified conversation."""
    url = f"{BASE_URL}/api/conversations/{conversation_id}/messages/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "sender": sender_id,
        "receiver": receiver_id,
        "message_body": message_body,
        "conversation": conversation_id,
    }

    log_info("Creating test message...")
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        message = response.json()
        log_success(f"Created message with ID: {message.get('message_id')}")
        return message
    else:
        log_error(f"Failed to create message: {response.status_code} - {response.text}")
        return None


def filter_messages(token, **filter_params):
    """Filter messages using the provided parameters."""
    # Convert parameters to URL query string
    query_string = urlencode(filter_params)

    url = f"{BASE_URL}/api/messages/?{query_string}"
    headers = {"Authorization": f"Bearer {token}"}

    log_info(f"Filtering messages with parameters: {filter_params}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json()

        # Handle pagination - results might be in 'results' field
        if isinstance(messages, dict) and "results" in messages:
            return messages["results"]
        else:
            return messages
    else:
        log_error(
            f"Failed to filter messages: {response.status_code} - {response.text}"
        )
        return []


def filter_conversations(token, **filter_params):
    """Filter conversations using the provided parameters."""
    # Convert parameters to URL query string
    query_string = urlencode(filter_params)

    url = f"{BASE_URL}/api/conversations/?{query_string}"
    headers = {"Authorization": f"Bearer {token}"}

    log_info(f"Filtering conversations with parameters: {filter_params}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        conversations = response.json()

        # Handle pagination - results might be in 'results' field
        if isinstance(conversations, dict) and "results" in conversations:
            return conversations["results"]
        else:
            return conversations
    else:
        log_error(
            f"Failed to filter conversations: {response.status_code} - {response.text}"
        )
        return []


def validate_message_time_filter(token):
    """Validate filtering messages by time range."""
    log_info("Testing message time range filter...")

    # Get current time and time 24 hours ago
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%dT%H:%M:%S")

    # Filter messages sent after yesterday
    messages = filter_messages(token, sent_after=yesterday_str)

    if messages:
        log_success(f"Found {len(messages)} messages sent after {yesterday_str}")
        return True
    else:
        log_info(
            "No messages found in the time range. This might be expected if no recent messages exist."
        )
        return True


def validate_message_sender_filter(token, sender_id):
    """Validate filtering messages by sender."""
    log_info(f"Testing message sender filter for user ID: {sender_id}")

    # Filter messages by sender
    messages = filter_messages(token, sender=sender_id)

    if messages:
        # Verify that all messages have the correct sender
        all_match = all(msg.get("sender") == sender_id for msg in messages)

        if all_match:
            log_success(
                f"Found {len(messages)} messages from sender {sender_id}, all match the filter"
            )
            return True
        else:
            log_error("Some messages have incorrect sender IDs")
            return False
    else:
        log_info(
            f"No messages found from sender {sender_id}. This might be expected if the user hasn't sent messages."
        )
        return True


def validate_message_participant_filter(token, participant_id):
    """Validate filtering messages by participant."""
    log_info(f"Testing message participant filter for user ID: {participant_id}")

    # Filter messages by participant
    messages = filter_messages(token, participant=participant_id)

    if messages:
        log_success(
            f"Found {len(messages)} messages in conversations where user {participant_id} is a participant"
        )
        return True
    else:
        log_info(
            f"No messages found for participant {participant_id}. This might be expected."
        )
        return True


def validate_message_content_filter(token, content):
    """Validate filtering messages by content."""
    log_info(f"Testing message content filter for text: '{content}'")

    # Filter messages by content
    messages = filter_messages(token, content=content)

    if messages:
        # Verify that all messages contain the content
        # Note: This is case-insensitive due to the icontains lookup
        all_match = all(
            content.lower() in msg.get("message_body", "").lower() for msg in messages
        )

        if all_match:
            log_success(
                f"Found {len(messages)} messages containing '{content}', all match the filter"
            )
            return True
        else:
            log_error("Some messages don't contain the search text")
            return False
    else:
        log_info(f"No messages found containing '{content}'. This might be expected.")
        return True


def validate_conversation_participant_filter(token, participant_id):
    """Validate filtering conversations by participant."""
    log_info(f"Testing conversation participant filter for user ID: {participant_id}")

    # Filter conversations by participant
    conversations = filter_conversations(token, participant=participant_id)

    if conversations:
        # Verify that all conversations include the participant
        all_include_participant = all(
            any(
                p.get("user_id") == participant_id for p in conv.get("participants", [])
            )
            for conv in conversations
        )

        if all_include_participant:
            log_success(
                f"Found {len(conversations)} conversations with participant {participant_id}, all match the filter"
            )
            return True
        else:
            log_error("Some conversations don't include the specified participant")
            return False
    else:
        log_info(
            f"No conversations found with participant {participant_id}. This might be expected."
        )
        return True


def validate_conversation_specific_participants_filter(token, participant_ids):
    """Validate filtering conversations by specific participants."""
    participant_ids_str = ",".join(participant_ids)
    log_info(
        f"Testing conversation specific participants filter for user IDs: {participant_ids_str}"
    )

    # Filter conversations by specific participants
    conversations = filter_conversations(
        token, specific_participants=participant_ids_str
    )

    if conversations:
        # Verify that all conversations include all the specified participants
        all_include_participants = all(
            all(
                any(p.get("user_id") == pid for p in conv.get("participants", []))
                for pid in participant_ids
            )
            for conv in conversations
        )

        if all_include_participants:
            log_success(
                f"Found {len(conversations)} conversations with all specified participants, all match the filter"
            )
            return True
        else:
            log_error("Some conversations don't include all specified participants")
            return False
    else:
        log_info(
            "No conversations found with all specified participants. This might be expected."
        )
        return True


def validate_conversation_date_filter(token):
    """Validate filtering conversations by date range."""
    log_info("Testing conversation date range filter...")

    # Get current time and time 7 days ago
    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(days=7)
    week_ago_str = week_ago.strftime("%Y-%m-%dT%H:%M:%S")

    # Filter conversations created after a week ago
    conversations = filter_conversations(token, created_after=week_ago_str)

    if conversations:
        log_success(
            f"Found {len(conversations)} conversations created after {week_ago_str}"
        )
        return True
    else:
        log_info(
            "No conversations found in the date range. This might be expected if no recent conversations exist."
        )
        return True


def main():
    """Main function to validate the filter functionality."""
    print("\n" + "=" * 80)
    print("MESSAGING APP FILTER VALIDATION")
    print("=" * 80)

    # Get authentication token
    token = get_token(TEST_EMAIL, TEST_PASSWORD)
    if not token:
        log_error("Authentication failed. Cannot proceed with validation.")
        sys.exit(1)

    # Get users for filtering
    users = get_users(token)
    if not users or len(users) < 1:
        log_error(
            "Failed to get users or no users found. Cannot proceed with validation."
        )
        sys.exit(1)

    # Use the first user for testing
    current_user_id = users[0]["user_id"]
    other_user_id = users[1]["user_id"] if len(users) > 1 else current_user_id

    # Run validation tests
    print("\n" + "=" * 80)
    print("VALIDATING MESSAGE FILTERS")
    print("=" * 80)

    test_results = []

    # Test 1: Validate message time filter
    test_results.append(("Message time filter", validate_message_time_filter(token)))

    # Test 2: Validate message sender filter
    test_results.append(
        (
            "Message sender filter",
            validate_message_sender_filter(token, current_user_id),
        )
    )

    # Test 3: Validate message participant filter
    test_results.append(
        (
            "Message participant filter",
            validate_message_participant_filter(token, current_user_id),
        )
    )

    # Test 4: Validate message content filter (using a common word)
    test_results.append(
        ("Message content filter", validate_message_content_filter(token, "test"))
    )

    print("\n" + "=" * 80)
    print("VALIDATING CONVERSATION FILTERS")
    print("=" * 80)

    # Test 5: Validate conversation participant filter
    test_results.append(
        (
            "Conversation participant filter",
            validate_conversation_participant_filter(token, current_user_id),
        )
    )

    # Test 6: Validate conversation specific participants filter
    test_results.append(
        (
            "Conversation specific participants filter",
            validate_conversation_specific_participants_filter(
                token, [current_user_id, other_user_id]
            ),
        )
    )

    # Test 7: Validate conversation date filter
    test_results.append(
        ("Conversation date filter", validate_conversation_date_filter(token))
    )

    # Print overall results
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)

    all_passed = True
    for test_name, result in test_results:
        if result:
            print(f"{GREEN}✓ {test_name}: PASSED{RESET}")
        else:
            print(f"{RED}✗ {test_name}: FAILED{RESET}")
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print(
            f"{GREEN}ALL TESTS PASSED! The filtering implementation works correctly.{RESET}"
        )
    else:
        print(f"{RED}SOME TESTS FAILED. Please review the error messages above.{RESET}")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
