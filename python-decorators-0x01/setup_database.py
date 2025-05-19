#!/usr/bin/env python3
"""
Script to set up the users database using the init.sqlite3 SQL file.
"""

import sqlite3
import os

# Path to the SQLite DB file
DB_FILE = "users.db"
SQL_INIT_FILE = "init.sqlite3"


def main():
    """Create and populate the users database."""
    # Remove existing database if it exists
    if os.path.exists(DB_FILE):
        print(f"Removing existing {DB_FILE}...")
        os.remove(DB_FILE)

    # Connect to the database (this creates the file if it doesn't exist)
    print(f"Connecting to {DB_FILE}...")
    conn = sqlite3.connect(DB_FILE)

    # Read the SQL from init.sqlite3
    print(f"Reading initialization SQL from {SQL_INIT_FILE}...")
    with open(SQL_INIT_FILE, "r") as f:
        sql_script = f.read()

    # Execute the script
    print("Executing SQL script...")
    conn.executescript(sql_script)
    conn.commit()

    # Verify the table was created and populated
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"Successfully created users table with {count} sample records.")

    # Close the connection
    conn.close()
    print("Database setup complete.")


if __name__ == "__main__":
    main()
