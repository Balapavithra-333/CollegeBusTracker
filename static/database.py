import sqlite3


def create_database():

    conn = sqlite3.connect("bus_tracker.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT,
            route TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_id INTEGER,
            stop_name TEXT,
            arrival_time TEXT,
            stop_order INTEGER
        )
    """)

    conn.commit()
    conn.close()


create_database()

print("Database created successfully!")