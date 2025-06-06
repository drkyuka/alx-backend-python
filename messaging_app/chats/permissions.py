"""permissions.py"""

from rest_framework import permissions


class IsActiveUser(permissions.BasePermission):
    """
    Custom permission to only allow active users to access the view.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and active
        return request.user and request.user.is_authenticated and request.user.is_active
