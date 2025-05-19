"""
This script creates a decorator that logs database queries executed by any function
"""

import sqlite3
import functools

#### decorator to lof SQL queries
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_queries(func):
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