
import psycopg2
from config import DB_CONFIG


def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as exc:
        print(f"[DB] Connection failed: {exc}")
        return None
