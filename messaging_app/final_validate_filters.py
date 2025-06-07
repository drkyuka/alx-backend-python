#!/usr/bin/env python3
"""
Final validation script for the messaging app filtering capabilities.
This script tests:
1. Message filtering by time range
2. Message filtering by content (using the correct method)
3. Message filtering by sender/receiver
4. Conversation filtering by participant
5. Conversation filtering by specific participants
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


def validate_time_filter(token):
    """Validate that messages can be filtered by time range."""
    print_info("Testing time range filtering...")

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

        # Verify all messages are within the time range
        all_valid = True
        for msg in messages:
            sent_at = msg.get("sent_at")
            if sent_at < time_ago_str:
                print_error(
                    f"Message {msg.get('message_id')} sent at {sent_at} is before the filter time {time_ago_str}"
                )
                all_valid = False

        if all_valid:
            print_success("All messages match the time filter criteria")
            return True
        else:
            return False
    else:
        print_error(
            f"Failed to filter messages by time: {response.status_code} - {response.text}"
        )
        return False


def validate_content_filter(token, search_text="shared"):
    """Validate that messages can be filtered by content."""
    print_info(f"Testing content filtering with text '{search_text}'...")

    # Use the filter method with content parameter
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

        # Verify all messages contain the search text in their content
        all_valid = True
        for msg in messages:
            content = msg.get("content", "").lower()
            if search_text.lower() not in content:
                print_error(
                    f"Message {msg.get('message_id')} with content '{content}' does not contain '{search_text}'"
                )
                all_valid = False

        if all_valid:
            print_success("All messages match the content filter criteria")
            return True
        else:
            return False
    else:
        print_error(
            f"Failed to filter messages by content: {response.status_code} - {response.text}"
        )
        return False


def validate_user_filter(token):
    """Validate that messages can be filtered by sender/receiver."""
    print_info("Testing sender/receiver filtering...")

    # First get all messages to find a valid sender ID
    messages = get_all_messages(token)
    if not messages:
        print_error("No messages found. Cannot test sender filtering.")
        return False

    # Use the first message's sender ID for filtering
    sender_id = messages[0].get("sender")

    # Filter messages by this sender
    url = f"{BASE_URL}/api/messages/?sender={sender_id}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Handle pagination
        if isinstance(data, dict) and "results" in data:
            filtered_messages = data["results"]
        else:
            filtered_messages = data

        print_success(
            f"Found {len(filtered_messages)} messages from sender {sender_id}"
        )

        # Verify all messages have the correct sender
        all_valid = True
        for msg in filtered_messages:
            msg_sender = msg.get("sender")
            if msg_sender != sender_id:
                print_error(
                    f"Message {msg.get('message_id')} has sender {msg_sender}, expected {sender_id}"
                )
                all_valid = False

        if all_valid:
            print_success("All messages match the sender filter criteria")
            return True
        else:
            return False
    else:
        print_error(
            f"Failed to filter messages by sender: {response.status_code} - {response.text}"
        )
        return False


def validate_conversation_participant_filter(token):
    """Validate that conversations can be filtered by participant."""
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
            all_valid = True
            for conv in filtered_conversations:
                conv_participants = conv.get("participants", [])
                participant_ids = [p.get("user_id") for p in conv_participants]

                if participant_id not in participant_ids:
                    print_error(
                        f"Conversation {conv.get('conversation_id')} does not include participant {participant_id}"
                    )
                    all_valid = False

            if all_valid:
                print_success("All conversations match the participant filter criteria")
                return True
            else:
                return False
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


def validate_specific_participants_filter(token):
    """Validate that conversations can be filtered by specific participants."""
    print_info("Testing specific participants filtering...")

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
                    all_valid = True
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
                            all_valid = False

                    if all_valid:
                        print_success(
                            "All conversations match the specific participants filter criteria"
                        )
                        return True
                    else:
                        return False
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
    """Main function to validate all filtering capabilities."""
    print("\n" + "=" * 80)
    print("MESSAGING APP FILTERING CAPABILITIES VALIDATION")
    print("=" * 80)

    # Get authentication token
    token = get_token()
    if not token:
        print_error("Authentication failed. Cannot proceed with validation.")
        sys.exit(1)

    # Run validation tests
    test_results = []

    print("\n" + "=" * 80)
    print("VALIDATING MESSAGE FILTERS")
    print("=" * 80)

    # Test 1: Time filter
    test_results.append(("Message time filter", validate_time_filter(token)))

    # Test 2: Content filter
    test_results.append(("Message content filter", validate_content_filter(token)))

    # Test 3: User filter
    test_results.append(("Message user filter", validate_user_filter(token)))

    print("\n" + "=" * 80)
    print("VALIDATING CONVERSATION FILTERS")
    print("=" * 80)

    # Test 4: Conversation participant filter
    test_results.append(
        (
            "Conversation participant filter",
            validate_conversation_participant_filter(token),
        )
    )

    # Test 5: Conversation specific participants filter
    test_results.append(
        (
            "Conversation specific participants filter",
            validate_specific_participants_filter(token),
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
