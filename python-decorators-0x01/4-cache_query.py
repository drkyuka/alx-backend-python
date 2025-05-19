"""This module provides a decorator to manage SQLite database connections using a cache for query results"""

from hashlib import sha256
import logging
import time
import sqlite3
import functools


query_cache = {}

with_db_connection = __import__("1-with_db_connection").with_db_connection


def cache_query(func):
    """
    Decorator to cache query results.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if the query is already cached
        query = kwargs.get("query")
        query_hash = sha256(query.encode()).hexdigest()

        # check if the query is cached, return the cached result
        if query_hash in query_cache:
            logging.info("Using cached result for query: %s", query)
            return query_cache.get(query_hash)

        # Create a new cache entry
        logging.error("Failed to find query in cache, executing query: %s", query)
        query_result = func(*args, **kwargs)

        logging.info(f"Caching result for query: %s: %s", query_hash, query_result)
        query_cache[query_hash] = query_result
        logging.info("Cached result for query: %s", query_hash)
        return query_result

    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
