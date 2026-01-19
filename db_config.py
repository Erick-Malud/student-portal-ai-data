import os
import mysql.connector
from mysql.connector import MySQLConnection
from urllib.parse import urlparse


def get_connection() -> MySQLConnection:
    database_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    result = urlparse(database_url)

    host = result.hostname
    user = result.username
    password = result.password
    dbname = result.path.lstrip("/") if result.path else None
    port = result.port if result.port is not None else 3306  # ✅ None бол 3306

    if not host or not user or not dbname:
        raise RuntimeError(f"Invalid DATABASE_URL: {database_url}")

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=dbname,
        port=port,
    )
