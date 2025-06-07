'''pagination.py
This module defines a custom pagination class for handling message sets in the messaging application.
It extends the `PageNumberPagination` class from Django REST Framework to provide pagination functionality for messages.
"""'''

from rest_framework.pagination import PageNumberPagination


class MessageSetPagination(PageNumberPagination):
    """
    Custom pagination class for messages.
    This can be used to limit the number of messages returned in a single request.
    """

    page_size = 20  # Default number of messages per page
    page_size_query_param = "page_size"
