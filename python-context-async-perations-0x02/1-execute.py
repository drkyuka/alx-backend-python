"""This module creates a reusable context manager that takes a query as input and executes it, managing both connection and the query execution"""

import sqlite3
import os
import sys


class ExecuteQuery:
    """Context manager for SQLite database connection."""

    def __init__(self, sql_query, *sql_args):
        self.db_file: str = "../users.db"
        db_file_exists = os.path.exists(self.db_file)

        # Check if the database file exists
        # If not, raise an error
        # to avoid creating a new database
        if not db_file_exists:
            raise FileNotFoundError("Database file 'users.db' not found.")

        self.connection = None
        self.cursor = None
        self.query = sql_query
        self.args = sql_args

    def __enter__(self):
        """Open the database connection."""
        self.connection = sqlite3.connect(self.db_file)

        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(self.query, self.args)
            return self.cursor
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    # Example usage
    query: str = "SELECT * FROM users WHERE id > ?"

    with ExecuteQuery(query, 4) as cursor:
        if cursor is None:
            print("Failed to execute query.")
            sys.exit(1)

        result = cursor.fetchall()
        print(result)
