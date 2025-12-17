import psycopg2
import time

DB_HOST = "db"
DB_NAME = "vehicles"
DB_USER = "user"
DB_PASS = "pass"

def init_db():
    while True:
        try:
            conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
            break
        except psycopg2.OperationalError:
            print("Database not ready, retrying in 2 seconds...")
            time.sleep(2)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_data (
            vin TEXT,
            latitude REAL,
            longitude REAL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
