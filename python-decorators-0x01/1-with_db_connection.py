"""This module provides a decorator to manage SQLite database connections"""

import sqlite3
import functools
import logging
from datetime import datetime

#### decorator to lof SQL queries
logfile = f"logs/dbqquery-{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    filename=logfile,
    filemode="a",
)


def with_db_connection(func):
    """your code goes here"""
    userdb: str = "users.db"

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # print(*args)
        try:
            conn: sqlite3.Connection = sqlite3.connect(userdb)
            logging.info("Connection to %s successful", userdb)

            # Pass the connection as the first argument, then all args and kwargs
            result = func(conn, *args, **kwargs)
            logging.info("Query successful: %s", result)
            return result
        except sqlite3.Error as e:
            logging.error("Connection to %s failed. Error: %s", userdb, e)
            raise
        finally:
            if conn:
                conn.close()

    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


#### Fetch user by ID with automatic connection handling

user = get_user_by_id(user_id=1)
print(user)
