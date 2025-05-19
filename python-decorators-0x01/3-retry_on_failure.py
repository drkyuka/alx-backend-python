"""This module contains decorator that retries database operations if they fail due to transient errors"""

import functools
import logging
import sqlite3
import time

#### paste your with_db_decorator here

with_db_connection = __import__("1-with_db_connection").with_db_connection


def retry_on_failure(retries=3, delay=1):
    """
    Decorator to retry a function call if it fails due to a transient error.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    logging.info("Attempt %d of %d", attempt + 1, retries)
                    result = func(*args, **kwargs)
                    logging.info("Query successful: %s", result)
                    return result
                except sqlite3.Error as e:
                    logging.info("Attempt %d of %d", attempt + 1, retries)
                    if attempt < retries - 1:
                        time.sleep(delay)
                    else:
                        logging.error("All attempts failed. Error: %s", e)
                        raise
            return

        return wrapper

    return decorator


@retry_on_failure(retries=3, delay=1)
@with_db_connection
def fetch_users_with_retry(conn: sqlite3.Connection):
    """
    Fetch all users from the database with automatic retry on failure.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users lIMIT 5")
    return cursor.fetchall()


#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)
