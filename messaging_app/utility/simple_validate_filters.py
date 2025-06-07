#!/usr/bin/env python3
"""
Simple script to validate the message and conversation filters in the messaging app.
This script tests:
1. Message filtering by time range
2. Message filtering by content
3. Conversation filtering by participant
"""

import datetime
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


def test_message_time_filter(token):
    """Test filtering messages by time range."""
    print_info("Testing message time range filtering...")

    # Get a time 30 days ago
    time_ago = datetime.datetime.now() - datetime.timedelta(days=30)
    time_ago_str = time_ago.strftime("%Y-%m-%dT%H:%M:%S")

    # Filter messages sent after this time
    url = f"{BASE_URL}/api/messages/?sent_after={time_ago_str}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Handle pagination
        if isinstance(data, dict) and "results" in data:
            messages = data["results"]
        else:
            messages = data

        print_success(f"Found {len(messages)} messages sent after {time_ago_str}")
        return True
    else:
        print_error(
            f"Failed to filter messages by time: {response.status_code} - {response.text}"
        )
        return False


def test_message_content_filter(token, search_text="test"):
    """Test filtering messages by content."""
    print_info(f"Testing message content filtering with text '{search_text}'...")

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

        print_success(f"Found {len(messages)} messages containing '{search_text}'")

        # Verify that messages contain the search text
        if messages:
            for msg in messages:
                message_id = msg.get("message_id")
                message_body = msg.get("message_body", "")
                print_info(f"Message ID: {message_id}")
                print_info(f"Message body: '{message_body}'")
                if search_text.lower() not in message_body.lower():
                    print_error(
                        f"Message with ID {message_id} does not contain '{search_text}'"
                    )
                    return False

            print_success("All returned messages contain the search text")
        return True
    else:
        print_error(
            f"Failed to filter messages by content: {response.status_code} - {response.text}"
        )
        return False


def test_conversation_participant_filter(token):
    """Test filtering conversations by participant."""
    print_info("Testing conversation participant filtering...")

    # First, get a list of conversations
    url = f"{BASE_URL}/api/conversations/"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        all_conversations = response.json()

        # Handle pagination
        if isinstance(all_conversations, dict) and "results" in all_conversations:
            all_conversations = all_conversations["results"]

        if not all_conversations:
            print_info("No conversations found. Cannot test participant filtering.")
            return True

        # Get the ID of a participant from the first conversation
        conversation = all_conversations[0]
        participants = conversation.get("participants", [])

        if not participants:
            print_info(
                "No participants found in conversations. Cannot test participant filtering."
            )
            return True

        # Use the first participant's ID for filtering
        participant_id = participants[0].get("user_id")

        # Now filter conversations by this participant
        filter_url = f"{BASE_URL}/api/conversations/?participant={participant_id}"
        filter_response = requests.get(filter_url, headers=headers)

        if filter_response.status_code == 200:
            filtered_conversations = filter_response.json()

            # Handle pagination
            if (
                isinstance(filtered_conversations, dict)
                and "results" in filtered_conversations
            ):
                filtered_conversations = filtered_conversations["results"]

            print_success(
                f"Found {len(filtered_conversations)} conversations with participant {participant_id}"
            )

            # Verify that each conversation includes the participant
            for conv in filtered_conversations:
                conv_participants = conv.get("participants", [])
                participant_ids = [p.get("user_id") for p in conv_participants]

                if participant_id not in participant_ids:
                    print_error(
                        f"Conversation {conv.get('conversation_id')} does not include participant {participant_id}"
                    )
                    return False

            print_success(
                "All returned conversations include the specified participant"
            )
            return True
        else:
            print_error(
                f"Failed to filter conversations by participant: {filter_response.status_code} - {filter_response.text}"
            )
            return False
    else:
        print_error(
            f"Failed to get conversations: {response.status_code} - {response.text}"
        )
        return False


def test_specific_participants_filter(token):
    """Test filtering conversations by specific participants."""
    print_info("Testing conversation specific participants filtering...")

    # First, get a list of conversations
    url = f"{BASE_URL}/api/conversations/"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        all_conversations = response.json()

        # Handle pagination
        if isinstance(all_conversations, dict) and "results" in all_conversations:
            all_conversations = all_conversations["results"]

        if not all_conversations:
            print_info(
                "No conversations found. Cannot test specific participants filtering."
            )
            return True

        # Get the first conversation with at least 2 participants
        for conversation in all_conversations:
            participants = conversation.get("participants", [])
            if len(participants) >= 2:
                # Use the first two participants' IDs for filtering
                participant_id1 = participants[0].get("user_id")
                participant_id2 = participants[1].get("user_id")

                # Now filter conversations by these participants
                filter_url = f"{BASE_URL}/api/conversations/?specific_participants={participant_id1},{participant_id2}"
                filter_response = requests.get(filter_url, headers=headers)

                if filter_response.status_code == 200:
                    filtered_conversations = filter_response.json()

                    # Handle pagination
                    if (
                        isinstance(filtered_conversations, dict)
                        and "results" in filtered_conversations
                    ):
                        filtered_conversations = filtered_conversations["results"]

                    print_success(
                        f"Found {len(filtered_conversations)} conversations with both participants"
                    )

                    # Verify that each conversation includes both participants
                    for conv in filtered_conversations:
                        conv_participants = conv.get("participants", [])
                        participant_ids = [p.get("user_id") for p in conv_participants]

                        if (
                            participant_id1 not in participant_ids
                            or participant_id2 not in participant_ids
                        ):
                            print_error(
                                f"Conversation {conv.get('conversation_id')} does not include both participants"
                            )
                            return False

                    print_success(
                        "All returned conversations include both specified participants"
                    )
                    return True
                else:
                    print_error(
                        f"Failed to filter conversations by specific participants: {filter_response.status_code} - {filter_response.text}"
                    )
                    return False

        print_info(
            "No conversations with at least 2 participants found. Cannot test specific participants filtering."
        )
        return True
    else:
        print_error(
            f"Failed to get conversations: {response.status_code} - {response.text}"
        )
        return False


def main():
    """Main function to run all tests."""
    print("\n" + "=" * 80)
    print("MESSAGING APP FILTER VALIDATION")
    print("=" * 80)

    # Get authentication token
    token = get_token()
    if not token:
        print_error("Authentication failed. Cannot proceed with validation.")
        sys.exit(1)

    # Run tests
    test_results = []

    print("\n" + "=" * 80)
    print("TESTING MESSAGE FILTERS")
    print("=" * 80)

    # Test 1: Message time filter
    test_results.append(("Message time filter", test_message_time_filter(token)))

    # Test 2: Message content filter
    test_results.append(("Message content filter", test_message_content_filter(token)))

    print("\n" + "=" * 80)
    print("TESTING CONVERSATION FILTERS")
    print("=" * 80)

    # Test 3: Conversation participant filter
    test_results.append(
        ("Conversation participant filter", test_conversation_participant_filter(token))
    )

    # Test 4: Conversation specific participants filter
    test_results.append(
        (
            "Conversation specific participants filter",
            test_specific_participants_filter(token),
        )
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
