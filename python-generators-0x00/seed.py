import os
import uuid

# import mysql engine and environment variables
from mysql import connector
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")


def connect_db():
    # connects to the mysql database server
    try:
        connection = connector.connect(host=host, user=user, password=password)
        # print("MySQL connection successful")
        return connection
    except connector.Error as err:
        print(f"MySQL connection failed. Error: {err}")
        return


def create_database(connection):
    # creates the database ALX_prodev if it does not exist
    create_database_query = "CREATE DATABASE IF NOT EXISTS ALX_prodev"

    cursor = connection.cursor()
    try:
        cursor.execute(create_database_query)
        connection.commit()
        # print("Database ALX_prodev created successfully")
    except connection.Error as err:
        print(f"Failed to create database. Error: {err}")


def connect_to_prodev():
    # connects to the ALX_prodev database
    try:
        connection = connector.connect(
            host=host, user=user, password=password, database="ALX_prodev"
        )
        print("Connected to ALX_prodev database")
        print(f"Connection to ALX_prodev database open: {connection.is_connected()}")
        return connection
    except connection.Error as err:
        print(f"Failed to connect to ALX_prodev database. Error: {err}")
        return


def create_table(connection):
    # creates the user_data table if it does not exist
    create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age INTEGER NOT NULL
        );
        """
    create_index_query = """
        CREATE UNIQUE INDEX IF NOT EXIST idx_user_id ON user_data (id);
        """

    cursor = connection.cursor()
    try:
        cursor.execute(create_table_query)
        # cursor.execute(create_index_query)

        connection.commit()
        print("Table user_data created successfully")
        print(f'Connection after creating table open: {connection.is_connected()}')
    except connection.Error as err:
        print(f"Failed to create table. Error: {err}")


def insert_data(connection, data):
    print(f"Data to be inserted: {data}")
    print(f'Connection before inserting data open: {connection.is_connected()}')


    # inserts data from a CSV file into the user_data table
    insert_data_query = """
    INSERT INTO user_data (id, name, email, age)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        email = VALUES(email),
        age = VALUES(age);
    """
    cursor = connection.cursor()

    with open(data, "r") as file:

        # Skip the header row
        next(file)

        # Read each line from the CSV file and insert into the database
        for line in file:
            # generate a new UUID for each row
            id = uuid.uuid4()
            line_values = line.strip().split(",")

            # Build the values to be inserted
            values = [str(id), line_values[0].strip('"').strip(), line_values[1].strip('"').strip(), int(line_values[2].strip('"').strip())]

            # print values
            print(f"Values to be inserted: {values}")

            try:
                # Execute the insert query
                cursor.execute(insert_data_query, values)
            except connection.Error as err:
                print(f"Failed to insert data. Error: {err}")
                continue
        # Commit the changes to the database
        connection.commit()
    # print("Data inserted successfully")
