import mysql.connector

def get_db_connection():
    """Establish a connection to the MySQL database."""
    return mysql.connector.connect(
        host='localhost',
        user='root',  # Updated MySQL username
        password='',  # No password
        database='resume_parser'
    )
