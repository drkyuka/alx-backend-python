"""auth.py
Module for handling authentication in the messaging app
using Django's JWT authentication system.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class that extends the default JWTAuthentication
    from rest_framework_simplejwt. This can be used to add custom behavior
    or logging in the future if needed.
    """

    pass
