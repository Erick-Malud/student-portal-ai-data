"""
db_config.py

Central place for database connection configuration.
Change these values if your MySQL setup is different.
"""

import mysql.connector
from mysql.connector import MySQLConnection


def get_connection() -> MySQLConnection:
    """
    Create and return a new MySQL connection.

    Adjust host/user/password/database to match your XAMPP/MySQL setup.
    """
    conn = mysql.connector.connect(
        host="localhost",
        user="root",        # change if you use another user
        password="",        # change if your root has a password
        database="student_portal",
    )
    return conn
