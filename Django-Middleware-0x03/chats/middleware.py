"""middleware.py
Django Middleware to log request method and path§
"""

import logging
import os
from datetime import datetime
from typing import Callable
from django.http import HttpResponseForbidden, HttpRequest, HttpResponse


RESTRICTED_TIME_START = 9  # 9 AM
RESTRICTED_TIME_END = 18  # 6 PM
MESSAGE_LIMIT = 5  # Example limit for messages


class RequestLoggingMiddleware:
    """
    Middleware to log the request method and path.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

        # Ensure the log file exists
        log_file = "requests.log"
        if not os.path.exists(log_file):
            open(log_file, "a").close()  # Create the file if it doesn't exist

        # Configure logging
        file_handler = logging.FileHandler(log_file, mode="a")  # Append mode
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """middleware that logs each user’s requests to a file,
        including the timestamp, user and the request path."""

        print(f"Middleware executed for path: {request.path}")  # Debug print

        # Get the user from the request, default to "Anonymous" if not authenticated

        user = (
            request.user
            if hasattr(request, "user") and request.user.is_authenticated
            else "Anonymous"
        )

        # Log the request method and path
        self.logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        # Call the next middleware or view
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the messaging up during
    certain hours of the day
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Middleware that restricts access to the messaging app
        during certain hours of the day.
        """

        # Check if the current time is within business hours (9 AM to 6 PM)
        if RESTRICTED_TIME_START <= datetime.now().hour < RESTRICTED_TIME_END:
            # Allow access during business hours (9 AM to 5 PM)
            response = self.get_response(request)
            return response

        return HttpResponseForbidden(
            "Access to the messaging app is restricted outside business hours (9 AM to 6 PM)."
        )


class OffensiveLanguageMiddleware:
    """
    Middleware that limits the number of chat messages a user can send within a certain time window, based on their IP address.


    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.ip_message_tracker: dict[str, dict[str, int]] = {}

    def __call__(self, request: HttpRequest):
        """
        Middleware that filters offensive language in messages.
        """
        if request.method == "POST":
            # Check if the user has exceeded the message limit
            ip = request.META.get("REMOTE_ADDR")
            now = datetime.now()

            # Use the minute as the key (year, month, day, hour, minute)
            minute_key = now.strftime("%Y%m%d%H%M")

            # Initialize dict for this IP if needed
            if ip not in self.ip_message_tracker:
                self.ip_message_tracker[ip] = {}

            # Clean up old minutes (keep only the current minute)
            self.ip_message_tracker[ip] = {
                k: v for k, v in self.ip_message_tracker[ip].items() if k == minute_key
            }

            # Increment count for this minute
            count = self.ip_message_tracker[ip].get(minute_key, 0) + 1
            self.ip_message_tracker[ip][minute_key] = count

            if count > MESSAGE_LIMIT:
                return HttpResponseForbidden(
                    f"You have exceeded the maximum of {MESSAGE_LIMIT} messages per minute."
                )

        return self.get_response(request)
