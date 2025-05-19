"""
This script creates a decorator that logs database queries executed by any function
"""

import sqlite3, functools, datetime, logging

#### decorator to lof SQL queries
logfile = f'dbqquery-{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    filename=logfile,
    filemode='a'
    )



def log_queries(f):
    """
    Decorator to log SQL queries executed by the function
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):            
        query = args[0] if args else kwargs.get('query')

        # Check if the query is provided
        if not query:
            logging.error("No query provided to log.")
            return None
            
        logging.info(f"Query to be exexuted: {query}")
        try:
            result = f(*args, **kwargs)
            logging.info(f"Query executed successfully: {query}")
        except Exception as e:
            logging.error(f"Error executing query: {query}")
            logging.exception(e)
            return None

        # Call the original function
        return result
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