import mysql.connector
from mysql.connector import Error

def create_connection(database_config):
    try:
        connection = mysql.connector.connect(
            host=database_config['host'],
            user=database_config['user'],
            password=database_config['password'],
            database=database_config['database']
        )
        return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None
