import os
import mysql.connector
from mysql.connector import MySQLConnection
from urllib.parse import urlparse


def get_connection() -> MySQLConnection:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    url = urlparse(database_url)

    conn = mysql.connector.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        database=url.path.lstrip("/"),
    )

    return conn
