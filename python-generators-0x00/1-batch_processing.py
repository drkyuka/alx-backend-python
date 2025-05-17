"""Batch processing script to create a generator to fetch and process data in batches from the users database"""

# import seed module to connect to the database
# from typing import Any

seed = __import__("seed")


def batch_processing(batch_size: int):
    """Function to process each batch to filter users over the age of 25"""
    # print(f"Processing users in batches of {batch_size}...")

    # Convert the for loop to a generator comprehension
    results = (row for row in stream_users_in_batches(batch_size) if row[3] > 25)

    # Print the filtered users
    for result in results:
        print(result)
    
    return


def stream_users_in_batches(batch_size: int):
    """Function to process data in batches."""

    # Create a connection to the database
    connection = seed.connect_to_prodev()
    # print(f"Connected to {connection}: {connection.is_connected()}")

    # Check if the connection was successful
    if connection:
        cursor = connection.cursor()

        # SQL query to fetch data in batches
        query_batch_size = "SELECT * FROM user_data LIMIT %s"

        # Execute the query with the specified batch size
        cursor.execute(query_batch_size, (batch_size,))

        # Fetch the data in batches
        for row in cursor:
            yield row

        cursor.close()
        connection.close()
    else:
        # Handle the case where the connection fails
        print("Failed to connect to the database.")
