#!/usr/bin/env python3
"""
Simple script to test token authentication with the API.
"""

import json
import sys

import requests


def get_token(base_url, email, password):
    """Get JWT token using email and password."""
    url = f"{base_url}/api/token/"
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    try:
        print(f"Sending request to {url} with payload: {json.dumps(payload)}")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return None


if __name__ == "__main__":
    base_url = "http://localhost:8001"
    email = "testuser@example.com"
    password = "testpass123"

    print(f"Testing token authentication for {email}")
    token = get_token(base_url, email, password)

    if token:
        print("Authentication successful!")
        print(f"Access token: {token.get('access')}")
        print(f"Refresh token: {token.get('refresh')}")
        sys.exit(0)
    else:
        print("Authentication failed!")
        sys.exit(1)
