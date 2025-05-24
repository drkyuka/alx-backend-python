#!/usr/bin/env python3
"""
This module allows multiple database queries concurrently using asyncio.gather.
"""

import asyncio
import aiosqlite
import os

# Database file
user_db = "../users.db"

# Check if the database file exists
db_file_exists = os.path.exists(user_db)

if not db_file_exists:
    raise FileNotFoundError("Database file 'users.db' not found.")


async def async_fetch_users():
    """
    Fetch all users from the database asynchronously.
    """
    async with aiosqlite.connect(user_db) as db_conn:
        cursor = await db_conn.cursor()

        # Fetch all rows from the executed query
        await cursor.execute("SELECT * FROM users")
        result = await cursor.fetchone()
        print(result)

        # Close the cursor and connection
        # to avoid resource leaks
        await cursor.close()
        await db_conn.close()

        # Return the result
        return result


async def async_fetch_older_users():
    """
    Fetch users older than 40 from the database asynchronously.
    """
    async with aiosqlite.connect(user_db) as db_conn:
        cursor = await db_conn.cursor()

        # Fetch all rows from the executed query
        await cursor.execute("SELECT * FROM users WHERE age > 40")
        result = await cursor.fetchone()
        print(result)

        # Close the cursor and connection
        # to avoid resource leaks
        await cursor.close()
        await db_conn.close()

        # Return the result
        return result


async def fetch_concurrently():
    """
    Fetch data concurrently from multiple sources.
    """
    await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users(),
    )


if __name__ == "__main__":
    # Example usage
    asyncio.run(fetch_concurrently())
