#!/usr/bin/env python3
"""
Script to fetch user1's conversations and messages using JWT authentication.
This script demonstrates a complete JWT authentication workflow:
1. Obtaining tokens using email/password authentication
2. Using the access token to fetch protected resources
3. Refreshing the token when needed
4. Error handling and retry mechanisms
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests


def get_token(base_url: str, email: str, password: str) -> Dict[str, str]:
    """Get JWT token using email and password."""
    url = f"{base_url}/api/token/"
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
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
        sys.exit(1)


def get_conversation_messages(
    base_url: str, token: str, conversation_id: str
) -> List[Dict[str, Any]]:
    """Get all messages for a specific conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages for conversation {conversation_id}: {e}")
        return []


def refresh_access_token(base_url: str, refresh: str, max_retries: int = 3) -> str:
    """Refresh the access token using the refresh token with retry mechanism."""
    url = f"{base_url}/api/token/refresh/"
    payload = {"refresh": refresh}
    headers = {"Content-Type": "application/json"}

    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()["access"]
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries >= max_retries:
                print(f"Error refreshing token after {max_retries} attempts: {e}")
                sys.exit(1)
            print(f"Retry {retries}/{max_retries} after token refresh error: {e}")
            time.sleep(1)  # Wait before retrying

    # This should never be reached due to the sys.exit in the exception handler
    # Adding it to satisfy type checking
    raise RuntimeError("Failed to refresh token after maximum retries")


def save_tokens_to_file(tokens: Dict[str, str], filename: str = ".tokens.json") -> None:
    """Save tokens to a file for later use."""
    try:
        with open(filename, "w") as f:
            # Add expiry timestamp to help determine when refresh is needed
            tokens_with_timestamp = tokens.copy()
            tokens_with_timestamp["saved_at"] = datetime.now().isoformat()
            json.dump(tokens_with_timestamp, f)
        print(f"Tokens saved to {filename}")
    except Exception as e:
        print(f"Error saving tokens to file: {e}")


def load_tokens_from_file(filename: str = ".tokens.json") -> Optional[Dict[str, str]]:
    """Load tokens from a file if available and not expired."""
    try:
        if not os.path.exists(filename):
            return None

        with open(filename, "r") as f:
            tokens = json.load(f)

        # Check if tokens are older than 12 hours (better to refresh in that case)
        saved_at = datetime.fromisoformat(tokens.get("saved_at", ""))
        now = datetime.now()
        if (now - saved_at).total_seconds() > 43200:  # 12 hours in seconds
            print("Tokens are older than 12 hours, will get new ones")
            return None

        return tokens
    except Exception as e:
        print(f"Error loading tokens from file: {e}")
        return None


def send_message(
    base_url: str, token: str, conversation_id: str, content: str
) -> Dict[str, Any]:
    """Send a message to a specific conversation."""
    url = f"{base_url}/api/conversations/{conversation_id}/messages/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"content": content}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to conversation {conversation_id}: {e}")
        if hasattr(e.response, "text"):
            print(f"Response content: {e.response.text}")
        raise


def main() -> None:
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Fetch user's conversations and messages using JWT authentication"
    )
    parser.add_argument(
        "--host", default="localhost", help="Host where the server is running"
    )
    parser.add_argument(
        "--port", default="8002", help="Port where the server is running"
    )
    parser.add_argument(
        "--email", default="user1@example.com", help="User email for authentication"
    )
    parser.add_argument(
        "--password", default="test@123", help="User password for authentication"
    )
    parser.add_argument(
        "--max-conversations", type=int, help="Maximum number of conversations to fetch"
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        help="Maximum number of messages to fetch per conversation",
    )
    parser.add_argument(
        "--token-file", default=".tokens.json", help="File to store/load tokens"
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Do not use cached tokens"
    )
    parser.add_argument(
        "--refresh-only", action="store_true", help="Only refresh the token and exit"
    )

    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    email = args.email
    password = args.password

    # Try to load tokens from file first, unless --no-cache is specified
    access_token = None
    refresh_token = None

    if not args.no_cache:
        cached_tokens = load_tokens_from_file(args.token_file)
        if cached_tokens:
            print("Using cached tokens from file")
            access_token = cached_tokens["access"]
            refresh_token = cached_tokens["refresh"]

    # If no cached tokens or --no-cache, get new tokens
    if not access_token or not refresh_token:
        print("Getting new JWT token...")
        try:
            tokens = get_token(base_url, email, password)
            access_token = tokens["access"]
            refresh_token = tokens["refresh"]
            print("Token obtained successfully!")

            # Save tokens to file
            save_tokens_to_file(tokens, args.token_file)
        except Exception as e:
            print(f"Failed to obtain token: {e}")
            sys.exit(1)

    # If --refresh-only, refresh the token and exit
    if args.refresh_only:
        try:
            print("Refreshing access token...")
            new_access_token = refresh_access_token(base_url, refresh_token)
            print("Token refreshed successfully!")

            # Save the refreshed token
            updated_tokens = {"access": new_access_token, "refresh": refresh_token}
            save_tokens_to_file(updated_tokens, args.token_file)
            print("Updated tokens saved to file")
            sys.exit(0)
        except Exception as e:
            print(f"Error during token refresh: {e}")
            sys.exit(1)

    # Step 2: Get all conversations
    print("\nFetching conversations...")
    try:
        conversations = get_conversations(base_url, access_token)
        if args.max_conversations:
            conversations = conversations[: args.max_conversations]
        print(f"Found {len(conversations)} conversations")
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        sys.exit(1)

    # Step 3: Get messages for each conversation
    for i, conversation in enumerate(conversations):
        conversation_id = conversation["conversation_id"]
        participants = [
            f"{p['first_name']} {p['last_name']}" for p in conversation["participants"]
        ]

        print(f"\nConversation {i + 1}: {conversation_id}")
        print(f"Participants: {', '.join(participants)}")

        # Get messages for this conversation
        try:
            messages = get_conversation_messages(
                base_url, access_token, conversation_id
            )
            if args.max_messages:
                messages = messages[: args.max_messages]
            print(f"Messages in this conversation: {len(messages)}")

            # Display messages
            for j, message in enumerate(messages):
                sender_id = message["sender"]
                sender = next(
                    (
                        p
                        for p in conversation["participants"]
                        if p["user_id"] == sender_id
                    ),
                    None,
                )
                sender_name = (
                    f"{sender['first_name']} {sender['last_name']}"
                    if sender
                    else "Unknown"
                )

                print(f"  Message {j + 1}: From {sender_name}")
                print(f"  Content: {message['content']}")
                print(f"  Sent at: {message['sent_at']}")
                print()
        except Exception as e:
            print(f"Error fetching messages for conversation {conversation_id}: {e}")
            continue

    # Demonstrate token refresh
    print("\nDemonstrating token refresh...")
    try:
        new_access_token = refresh_access_token(base_url, refresh_token)
        print("Token refreshed successfully!")

        # Save the refreshed token
        updated_tokens = {"access": new_access_token, "refresh": refresh_token}
        save_tokens_to_file(updated_tokens, args.token_file)

        # Use the new token to fetch conversations again
        print("\nFetching conversations with refreshed token...")
        conversations = get_conversations(base_url, new_access_token)
        print(
            f"Successfully fetched {len(conversations)} conversations with the refreshed token"
        )
    except Exception as e:
        print(f"Error during token refresh demonstration: {e}")
        sys.exit(1)

    # Load tokens from file and use them
    print("\nLoading tokens from file...")
    loaded_tokens = load_tokens_from_file(args.token_file)
    if loaded_tokens:
        print("Tokens loaded from file:")
        print(f"Access Token: {loaded_tokens['access'][:20]}... (truncated)")
        print(f"Refresh Token: {loaded_tokens['refresh'][:20]}... (truncated)")
        print(f"Saved at: {loaded_tokens.get('saved_at', 'Unknown')}")
    else:
        print("No valid tokens found in file, please login again")


if __name__ == "__main__":
    main()
