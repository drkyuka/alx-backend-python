'''pagination.py
This module defines a custom pagination class
for handling message sets in the messaging application.
It extends the `PageNumberPagination` class
from Django REST Framework to provide pagination
functionality for messages.
"""'''

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MessageSetPagination(PageNumberPagination):
    """
    Custom pagination class for messages.
    This can be used to limit the number of messages returned in a single request.
    """

    page_size = 20  # Default number of messages per page
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
