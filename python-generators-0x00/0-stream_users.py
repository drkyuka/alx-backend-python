#!/usr/bin/python3

# create a generator that streams rows from an SQL database one by one.
seed = __import__("seed")


def stream_users():
    # function that uses a generator to fetch rows one by one from the user_data table

    connection = seed.connect_to_prodev()

    # fetch the data from the database
    fetch_all_query = "SELECT * FROM user_data;"

    # Check if the connection was successful
    if connection:
        cursor = connection.cursor()
        cursor.execute(fetch_all_query)
        for row in cursor:
            yield row
        cursor.close()
        connection.close()
    else:
        # Handle the case where the connection fails
        print("Failed to connect to the database.")
