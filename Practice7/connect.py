import psycopg2
from config import DB_CONFIG

def get_connection():
    try: 
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Connection failed: {e}")
        return None