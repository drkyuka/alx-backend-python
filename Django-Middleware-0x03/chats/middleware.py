"""middleware.py
Django Middleware to log request method and path§
"""

import logging
import os
from datetime import datetime


class RequestLoggingMiddleware:
    """
    Middleware to log the request method and path.
    """

    def __init__(self, get_response):
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

    def __call__(self, request):
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
        response = self.get_response(request)

        return response
