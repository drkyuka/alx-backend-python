"""Module contains a decorator that manages database transactions by automatically committing or rolling back changes"""

import functools
import logging
import sqlite3

with_db_connection = __import__("1-with_db_connection").with_db_connection
get_user_by_id = __import__("1-with_db_connection").get_user_by_id


def transactional(func):
    """
    Decorator to manage database transactions
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Make sure we have a connection as the first argument
        if not args or not isinstance(args[0], sqlite3.Connection):
            raise ValueError("First argument must be a database connection")

        connection = args[0]
        try:
            logging.info("Starting transaction...")
            result = func(*args, **kwargs)
            connection.commit()
            logging.info("Transaction committed successfully.")
            return result
        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            logging.error("Transaction failed. Changes rolled back.")
            logging.error("Error: %s", e)
            logging.exception(e)
            raise e
        # Remove the finally block with connection.close()
        # because with_db_connection will handle closing the connection

    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


#### Update user's email with automatic transaction handling
update_user_email(user_id=1, new_email="Crawford_Cartwright@live.com")
print(get_user_by_id(1))
