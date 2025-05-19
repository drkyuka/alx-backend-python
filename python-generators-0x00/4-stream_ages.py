"""Generates a memory-efficient aggregate function i.e average age for a large dataset"""

users = __import__("0-stream_users").stream_users


def stream_user_ages():
    """Generator function to stream user from the database."""
    yield from users()


def compute_average_age():
    """Function to compute the average age of users."""
    total_age = 0
    count = 0

    for user in stream_user_ages():
        total_age += user[3]
        count += 1

    if count == 0:
        return 0

    return total_age / count
