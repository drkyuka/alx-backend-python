"""
This script creates a decorator that logs database queries executed by any function
"""

import sqlite3
import functools

#### decorator to lof SQL queries
import logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    )


def log_queries():
    """
    Decorator to log SQL queries executed by the function
    """
    def logging_decorator(f):
        
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            query = args[0] if args else kwargs.get('query')

            # Check if the query is provided
            if not query:
                logging.error("No query provided to log.")
                return None
            
            logging.info(f"Query to be exexuted: {query}")

            # Call the original function
            return func(*args, **kwargs)
        return wrapper
    return logging_decorator


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")

print(users)