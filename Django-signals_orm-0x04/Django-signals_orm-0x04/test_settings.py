"""
Test settings for delete_user view validation.
This overrides specific settings to make testing easier.
"""

from .settings import *

# Disable time restriction middleware for testing
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "chats.middleware.RequestLoggingMiddleware",  # Keep logging
    # "chats.middleware.RestrictAccessByTimeMiddleware",  # DISABLED for testing
    # "chats.middleware.OffensiveLanguageMiddleware",  # DISABLED for testing
    # "chats.middleware.RolepermissionMiddleware",  # DISABLED for testing
]

from pathlib import Path

# Get the project BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Use test database file that persists
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}


# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
