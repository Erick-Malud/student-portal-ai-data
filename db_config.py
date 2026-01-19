import os
import mysql.connector
from mysql.connector import MySQLConnection
from urllib.parse import urlparse


def get_connection() -> MySQLConnection:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    result = urlparse(database_url)

    # Debug logging for connection issues
    print(f"[INFO] Connecting to database at host: {result.hostname}")

    return mysql.connector.connect(
        host=result.hostname,
        user=result.username,
        password=result.password,
        database=result.path.lstrip("/"),
        port=result.port or 3306,   # 🔴 ЭНЭ Л АЛДААГ ЗАСНА
    )
