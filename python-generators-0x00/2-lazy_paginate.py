"""Seed script to populate the database with user data from a CSV file."""

#!/usr/bin/python3

seed = __import__("seed")


def paginate_users(page_size: int, offset: int):
    """Function to paginate through user data."""

    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_paginate(page_size: int):
    """Generator function to paginate through user data."""
    offset: int = 0
    while True:
        rows = paginate_users(page_size, offset)
        # print(rows)

        if not rows:
            break

        # yield results
        yield rows

        # increment offset
        offset += page_size
