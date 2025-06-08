"""middleware.py
Django Middleware to log request method and path§
"""

import logging
from datetime import datetime


class RequestLoggingMiddleware:
    """
    Middleware to log the request method and path.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def __call__(self, request):
        """middleware that logs each user’s requests to a file,
        including the timestamp, user and the request path."""

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
