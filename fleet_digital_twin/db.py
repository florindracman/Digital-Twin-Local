import psycopg2

DB_HOST = "db_fleet"
DB_NAME = "fleet"
DB_USER = "user"
DB_PASS = "pass"

def init_db():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_data (
            id SERIAL PRIMARY KEY,
            vin TEXT,
            latitude REAL,
            longitude REAL,
            giro REAL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def write_vehicle_data(vin, lat, lon, giro):
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    cur.execute("INSERT INTO vehicle_data (vin, latitude, longitude, giro) VALUES (%s, %s, %s, %s)",
                (vin, lat, lon, giro))
    conn.commit()
    cur.close()
    conn.close()

def read_all_vehicle_data():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    cur.execute("SELECT vin, latitude, longitude, giro FROM vehicle_data")
    last_row = cur.fetchone
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def read_last_vehicle_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()

    cur.execute("""
        SELECT vin, latitude, longitude, giro
        FROM vehicle_data
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row

